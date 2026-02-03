import logging
from app.utils.ssh_helper import ssh_exec

POSTGRES_USER = "bill_kaplan"
POSTGRES_PASS = "b1ackjack!"
POSTGRES_DB   = "db"
POSTGRES_HOST = "127.0.0.1"   # local to DB machine

def check_postgres_access(team: int) -> str:
    """
    PostgreSQL scoring logic (CORRECT):

    RED:
      - Cannot SSH to DB machine
      - PostgreSQL not listening on 5432

    YELLOW:
      - PostgreSQL reachable but auth fails
      - Read OR write fails

    GREEN:
      - Login, read, and write all succeed
    """

    wan_ip = f"172.18.13.{team}"

    logging.info(f"[POSTGRES] Team {team}: starting PostgreSQL access check")

    # 0️⃣ SSH reachability test (CRITICAL)
    if not ssh_exec(team, "echo ssh_ok", target_ip=wan_ip):
        logging.error(f"[POSTGRES] Team {team}: SSH unreachable")
        return "red"

    # 1️⃣ PostgreSQL listening check
    listen_cmd = "ss -lnt | grep ':5432 '"
    if not ssh_exec(team, listen_cmd, target_ip=wan_ip):
        logging.error(f"[POSTGRES] Team {team}: PostgreSQL not listening on 5432")
        return "red"

    # 2️⃣ Authentication check
    auth_cmd = (
        f"PGPASSWORD='{POSTGRES_PASS}' "
        f"psql -h {POSTGRES_HOST} -U {POSTGRES_USER} "
        f"-d {POSTGRES_DB} -c '\\q'"
    )

    if not ssh_exec(team, auth_cmd, target_ip=wan_ip):
        logging.warning(f"[POSTGRES] Team {team}: authentication failed")
        return "yellow"

    # 3️⃣ Read test
    read_cmd = (
        f"PGPASSWORD='{POSTGRES_PASS}' "
        f"psql -h {POSTGRES_HOST} -U {POSTGRES_USER} "
        f"-d {POSTGRES_DB} -c 'SELECT 1 FROM users LIMIT 1;'"
    )

    if not ssh_exec(team, read_cmd, target_ip=wan_ip):
        logging.warning(f"[POSTGRES] Team {team}: read failed")
        return "yellow"

    # 4️⃣ Write test (safe, idempotent)
    write_cmd = (
        f"PGPASSWORD='{POSTGRES_PASS}' "
        f"psql -h {POSTGRES_HOST} -U {POSTGRES_USER} "
        f"-d {POSTGRES_DB} -c "
        "\"INSERT INTO users (username) VALUES ('scoring_test') "
        "ON CONFLICT DO NOTHING;\""
    )

    if not ssh_exec(team, write_cmd, target_ip=wan_ip):
        logging.warning(f"[POSTGRES] Team {team}: write failed")
        return "yellow"

    logging.info(f"[POSTGRES] Team {team}: PASSED all checks")
    return "green"

