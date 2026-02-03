# NCAE Scoring Engine – Full Rebuild & Reference Guide

---

## Purpose of This Document

This document serves as the **authoritative rebuild guide** for the NCAE Scoring Engine.

It exists so that:
- The scoring server can be **fully recreated** if lost or corrupted
- The logic and architecture choices are **clearly documented**
- Common errors encountered during development are **explicitly addressed**
- Future maintainers understand **why things are done this way**, not just how

If followed from top to bottom, this guide will reproduce the **exact working state**
of the scoring engine currently deployed.

---

## What This Scoring Engine Does

The scoring engine is responsible for:
- Actively checking team infrastructure services
- Writing authoritative service state into PostgreSQL
- Serving a read-only scoreboard UI via FastAPI
- Enforcing router-based gating (no router = no scoring)

Important design principles:
- The UI NEVER probes infrastructure
- The API NEVER mutates state
- The runner is the ONLY component allowed to score
- PostgreSQL is the single source of truth
- Teams that do not exist must never appear as scored

This mirrors real NCAE scoring behavior.

---

## Target Environment

- OS: Rocky Linux 9
- Python: 3.9
- Database: PostgreSQL 13+
- Network: 172.18.0.0/16
- Install Path: /opt/scoring-engine

---

## Current Directory Structure (AUTHORITATIVE)

This is the exact layout expected by all services:
```text
scoring-engine/
├── app
│   ├── checks
│   │   ├── dns_external.py
│   │   ├── dns_internal.py
│   │   ├── dns.py
│   │   ├── __init__.py
│   │   ├── postgres_access.py
│   │   ├── __pycache__
│   │   │   ├── dns_external.cpython-39.pyc
│   │   │   ├── dns_internal.cpython-39.pyc
│   │   │   ├── __init__.cpython-39.pyc
│   │   │   ├── postgres_access.cpython-39.pyc
│   │   │   ├── router_icmp.cpython-39.pyc
│   │   │   ├── smb_login.cpython-39.pyc
│   │   │   ├── smb_read.cpython-39.pyc
│   │   │   ├── smb_write.cpython-39.pyc
│   │   │   ├── ssh_login.cpython-39.pyc
│   │   │   └── web_http.cpython-39.pyc
│   │   ├── router_icmp.py
│   │   ├── smb_common.py
│   │   ├── smb_login.py
│   │   ├── smb_read.py
│   │   ├── smb_write.py
│   │   ├── ssh_login.py
│   │   └── web_http.py
│   ├── db.py
│   ├── __init__.py
│   ├── main.py
│   ├── __pycache__
│   │   ├── db.cpython-39.pyc
│   │   ├── __init__.cpython-39.pyc
│   │   ├── main.cpython-39.pyc
│   │   └── runner.cpython-39.pyc
│   ├── runner.py
│   ├── services.py
│   └── utils
│       ├── cmd_exec.py
│       ├── __init__.py
│       ├── proc.py
│       ├── __pycache__
│       │   ├── cmd_exec.cpython-39.pyc
│       │   ├── __init__.cpython-39.pyc
│       │   ├── proc.cpython-39.pyc
│       │   ├── ssh_helper.cpython-39.pyc
│       │   └── ssh_key_helper.cpython-39.pyc
│       ├── ssh_helper.py
│       └── ssh_key_helper.py
├── etc
│   ├── root_ca.pem
│   └── scoring.yaml
├── keys
│   ├── scoring_id_rsa
│   └── scoring_id_rsa.pub
├── logs
│   └── runner.log
├── requirements.txt
├── reset_db.sql
├── secrets
│   └── runtime.env
└── test
```
```
/etc/systemd/system
```
---

## High-Level Architecture

systemd timer
→ scoring-runner.service
→ Python runner (app/runner.py)
→ Service checks (app/checks/*)
→ PostgreSQL service_status table
→ FastAPI API (read-only)
→ HTML scoreboard

---

## Step 1 – Install System Dependencies

Update the system and install required packages:
```bash
sudo dnf update -y
sudo dnf install -y \
  python3 \
  python3-virtualenv \
  postgresql-server \
  postgresql \
  iputils \
  tree
```
Initialize PostgreSQL:
```bash
sudo postgresql-setup --initdb
sudo systemctl enable --now postgresql
```
![postgresRunning](./img/postgresRunning.png)

---

## Step 2 – PostgreSQL Database Setup

Login as the PostgreSQL administrative user:
```bash
sudo -u postgres psql
```
Create the scoring database and user:
```bash
CREATE DATABASE scoring;
CREATE USER scoring_user WITH PASSWORD 'scoring_pass';
GRANT ALL PRIVILEGES ON DATABASE scoring TO scoring_user;
\q
```
---

## Step 3 – Create Required Scoring Table

Login to the scoring database:
```bash
sudo -u postgres psql scoring
```
Create the service status table:
```bash
CREATE TABLE service_status (
    team_id INTEGER,
    service_id TEXT,
    status TEXT,
    PRIMARY KEY (team_id, service_id)
);

\q
```
Why this table exists:
- Each row represents ONE service for ONE team
- No rows exist unless the runner explicitly writes them
- This prevents phantom scoring for nonexistent teams

![serviceStatusTable](./img/serviceStatusTable.png)

---

## Step 4 – Create Python Virtual Environment

Move to the install directory:
```bash
cd /opt
mkdir scoring-engine
cd scoring-engine
```
Create and activate the virtual environment:
```bash
python3 -m venv .venv
source .venv/bin/activate
```
---

## Step 5 – Python Dependencies

Create requirements.txt:
```text
fastapi
uvicorn
psycopg[binary]
pyyaml
```
Install dependencies:
```bash
pip install -r requirements.txt
```
---

## Step 6 – Database Helper Module

File: app/db.py

Purpose:
- Centralizes database access
- Forces dictionary-based rows
- Prevents tuple indexing errors
```text
import psycopg
from psycopg.rows import dict_row

def get_db():
    return psycopg.connect(
        "dbname=scoring user=scoring_user password=scoring_pass host=127.0.0.1",
        row_factory=dict_row
    )
```
Why dict_row is REQUIRED:
- Early errors occurred when tuple rows were accessed as dictionaries
- This guarantees row["status"] always works

---

## Step 7 – Router ICMP Check

File: app/checks/router_icmp.py

This check determines whether ANY other service should be evaluated.
```text
import subprocess

def router_up(ip):
    result = subprocess.run(
        ["ping", "-c", "1", "-W", "1", ip],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    return result.returncode == 0
```
Why router gating exists:
- If the router is down, the team is effectively offline
- Scoring ANY service beyond this point would be misleading
- This matches NCAE behavior exactly

---

## Step 8 – Scoring Runner

File: app/runner.py

This is the ONLY component allowed to write scoring data.
```text
import subprocess
from app.db import get_db
from app.checks.router_icmp import router_up

TEAMS = [1, 2, 3, 4, 5]

def router_ip(team):
    return f"172.18.13.{team}"

def write_status(team, service, status):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO service_status (team_id, service_id, status) "
            "VALUES (%s, %s, %s) "
            "ON CONFLICT (team_id, service_id) "
            "DO UPDATE SET status = EXCLUDED.status",
            (team, service, status)
        )
        conn.commit()

def run_team(team):
    if not router_up(router_ip(team)):
        write_status(team, "router_icmp", "red")
        return

    write_status(team, "router_icmp", "green")

    for service in [
        "dns_ext_fwd", "dns_ext_rev",
        "dns_int_fwd", "dns_int_rev",
        "postgres_access",
        "smb_login", "smb_read", "smb_write",
        "ssh_login",
        "www_content", "www_port_80", "www_ssl"
    ]:
        write_status(team, service, "red")

def run_scoring_cycle():
    for team in TEAMS:
        run_team(team)

if __name__ == "__main__":
    run_scoring_cycle()
```
Important behavior:
- Only teams listed in TEAMS are evaluated
- No team data is pre-populated
- Only Team 2 showed activity during testing because only Team 2 existed

![runnerLogic](./img/runnerLogic.png)

---

## Step 9 – FastAPI Application

File: app/main.py

This service is READ-ONLY.
```text
from fastapi import FastAPI
from app.db import get_db

app = FastAPI()

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/api/scoreboard")
def scoreboard():
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT team_id, service_id, status "
            "FROM service_status "
            "ORDER BY team_id, service_id"
        )
        return cur.fetchall()

@app.get("/scoreboard")
def scoreboard_page():
    with open("app/services.py") as f:
        return f.read()
```
Why the API never writes:
- Prevents UI bugs from affecting scoring
- Prevents accidental scoring manipulation
- Runner remains authoritative

![apiScoreboard](./img/apiScoreboard.png)

---

## Step 10 – Systemd Runner Service

File: /etc/systemd/system/scoring-runner.service
```file
[Unit]
Description=NCAE Scoring Engine Runner

[Service]
Type=oneshot
ExecStart=/opt/scoring-engine/.venv/bin/python -m app.runner
WorkingDirectory=/opt/scoring-engine
```
---

## Step 11 – Systemd Timer

File: /etc/systemd/system/scoring-runner.timer
```text
[Unit]
Description=Run Scoring Engine Every Minute

[Timer]
OnBootSec=30
OnUnitActiveSec=60

[Install]
WantedBy=timers.target
```
---

## Step 12 – API Service

File: /etc/systemd/system/scoring-api.service
```text
[Unit]
Description=NCAE Scoring API

[Service]
ExecStart=/opt/scoring-engine/.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8080
WorkingDirectory=/opt/scoring-engine
Restart=always

[Install]
WantedBy=multi-user.target
```
---

## Step 13 – Enable Everything
```bash
sudo systemctl daemon-reload
sudo systemctl enable --now scoring-runner.timer
sudo systemctl enable --now scoring-api
```
![systemdEnabled](./img/systemdEnabled.png)

---

## Verification

Check service status:
```bash
systemctl status scoring-api
systemctl status scoring-runner.timer
```
Verify API:
```bash
curl http://127.0.0.1:8080/health
curl http://127.0.0.1:8080/api/scoreboard
```
![finalDashboard](./img/finalDashboard.png)

---

## Common Issues Encountered

Router shows down:
- IP was incorrectly assumed to be .1
- Correct router IP is 172.18.13.t

Phantom teams showing status:
- Caused by pre-populating database rows
- Fixed by runner-only writes

Tuple index errors:
- Caused by psycopg default row type
- Fixed using dict_row

---