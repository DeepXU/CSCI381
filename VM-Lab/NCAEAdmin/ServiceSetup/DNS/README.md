# Team 2 – BIND9 DNS Configuration

This document tracks all forward and reverse DNS zone files used for the  
Team 2 CNY Hackathon / NCAE Lab 2026 environment.

All zones are **master zones**, **static**, and **disallow dynamic updates**.

Zone files live in:

```text
/etc/bind/zones/
```

---

## Forward Zones

### forward.team2.cnyhackathon.org

**Zone:** `team2.cnyhackathon.org`  
**Purpose:** External-facing services (172.18.x.x)

**Create file:**
```bash
sudo cp /etc/bind/db.empty /etc/bind/zones/forward.team2.cnyhackathon.org
```
---

### forward.team2.net

**Zone:** `team2.net`  
**Purpose:** Internal network services (192.168.2.0/24)

**Create file:**
```bash
sudo cp /etc/bind/db.empty /etc/bind/zones/forward.team2.net
```
---

## Reverse (PTR) Zones

### reverse.team2.net

**Zone:** `2.168.192.in-addr.arpa`  
**Network:** 192.168.2.0/24  
**Purpose:** Internal PTR records

**Create file:**
```bash
sudo cp /etc/bind/db.empty /etc/bind/zones/reverse.team2.net
```
---

### reverse.cnyhackathon.org

**Zone:** `13.18.172.in-addr.arpa`  
**Network:** 172.18.13.0/24  
**Purpose:** External PTR records

**Create file:**
```bash
sudo cp /etc/bind/db.empty /etc/bind/zones/reverse.cnyhackathon.org
```
---

### reverse2.cnyhackathon.org

**Zone:** `14.18.172.in-addr.arpa`  
**Network:** 172.18.14.0/24  
**Purpose:** External PTR records (secondary segment)

**Create file:**
```bash
sudo cp /etc/bind/db.empty /etc/bind/zones/reverse2.cnyhackathon.org
```
---

## Permissions (Required)

Ensure BIND owns and can read all zone files.

```bash
sudo chown bind:bind /etc/bind/zones/*
sudo chmod 644 /etc/bind/zones/*
```
---

## Validation (Strongly Recommended)

Validate configuration before reload or restart.

### Check main configuration
```bash
sudo named-checkconf
```
### Check forward zones
```bash
sudo named-checkzone team2.cnyhackathon.org /etc/bind/zones/forward.team2.cnyhackathon.org
sudo named-checkzone team2.net /etc/bind/zones/forward.team2.net
```
### Check reverse zones
```bash
sudo named-checkzone 2.168.192.in-addr.arpa /etc/bind/zones/reverse.team2.net
sudo named-checkzone 13.18.172.in-addr.arpa /etc/bind/zones/reverse.cnyhackathon.org
sudo named-checkzone 14.18.172.in-addr.arpa /etc/bind/zones/reverse2.cnyhackathon.org
```
---

## Reload / Restart BIND9

### Reload systemd units (safe)
```bash
sudo systemctl daemon-reexec
```
### Reload DNS zones without full restart
```bash
sudo rndc reload
```
### Full restart (if required)
```bash
sudo systemctl restart bind9
```
### Verify service status
```bash
systemctl status bind9
```
---

## Notes

- Dynamic updates are disabled (`allow-update { none; };`)
- Split-horizon DNS is implemented via separate forward and reverse zones
- PTR records align with scoring-engine validation expectations
