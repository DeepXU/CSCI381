import logging
from app.db import get_db

from app.checks.router_icmp import check_router_icmp

from app.checks.web_http import (
    check_www_port_80,
    check_www_content,
    check_www_ssl
)

from app.checks.dns_internal import (
    check_dns_int_fwd,
    check_dns_int_rev
)

from app.checks.dns_external import (
    check_dns_ext_fwd,
    check_dns_ext_rev
)

from app.checks.postgres_access import check_postgres_access

from app.checks.smb_login import check_smb_login
from app.checks.smb_read import check_smb_read
from app.checks.smb_write import check_smb_write

from app.checks.ssh_login import check_ssh_login


LOG_PATH = "/opt/scoring-engine/logs/runner.log"

logging.basicConfig(
    filename=LOG_PATH,
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

# Teams to score
TEAMS = [2, 3, 4, 5, 6]

# Services that require the router to be up
DEPENDENT_SERVICES = [
    "www_port_80", "www_content", "www_ssl",
    "dns_int_fwd", "dns_int_rev",
    "dns_ext_fwd", "dns_ext_rev",
    "postgres_access",
    "smb_login", "smb_read", "smb_write",
    "ssh_login"
]


def set_status(cur, team_id: int, service_id: str, status: str):
    cur.execute(
        """
        UPDATE service_status
        SET status = %s
        WHERE team_id = %s
          AND service_id = %s
        """,
        (status, team_id, service_id)
    )


def run_scoring_cycle():
    logging.info("Scoring cycle started")

    conn = get_db()
    cur = conn.cursor()

    for team_id in TEAMS:
        logging.info(f"Scoring team {team_id}")

        # --------------------
        # Router ICMP (GATEKEEPER)
        # --------------------
        router_up = False
        try:
            router_up = check_router_icmp(team_id)
            set_status(
                cur,
                team_id,
                "router_icmp",
                "green" if router_up else "red"
            )
        except Exception as e:
            logging.error(f"[router_icmp] Team {team_id}: {e}")
            set_status(cur, team_id, "router_icmp", "red")

        # 🚨 HARD STOP — DO NOT TOUCH THE TEAM IF ROUTER IS DOWN
        if not router_up:
            logging.warning(
                f"Team {team_id} router down — skipping all dependent services"
            )

            for svc in DEPENDENT_SERVICES:
                set_status(cur, team_id, svc, "red")

            continue  # 🔑 THIS prevents hanging forever

        # --------------------
        # WWW
        # --------------------
        try:
            set_status(
                cur,
                team_id,
                "www_port_80",
                "green" if check_www_port_80(team_id) else "red"
            )
        except Exception as e:
            logging.error(f"[www_port_80] Team {team_id}: {e}")
            set_status(cur, team_id, "www_port_80", "red")

        try:
            set_status(
                cur,
                team_id,
                "www_content",
                "green" if check_www_content(team_id) else "red"
            )
        except Exception as e:
            logging.error(f"[www_content] Team {team_id}: {e}")
            set_status(cur, team_id, "www_content", "red")

        try:
            set_status(
                cur,
                team_id,
                "www_ssl",
                "green" if check_www_ssl(team_id) else "red"
            )
        except Exception as e:
            logging.error(f"[www_ssl] Team {team_id}: {e}")
            set_status(cur, team_id, "www_ssl", "red")

        # --------------------
        # DNS INTERNAL
        # --------------------
        try:
            set_status(
                cur,
                team_id,
                "dns_int_fwd",
                "green" if check_dns_int_fwd(team_id) else "red"
            )
        except Exception as e:
            logging.error(f"[dns_int_fwd] Team {team_id}: {e}")
            set_status(cur, team_id, "dns_int_fwd", "red")

        try:
            set_status(
                cur,
                team_id,
                "dns_int_rev",
                "green" if check_dns_int_rev(team_id) else "red"
            )
        except Exception as e:
            logging.error(f"[dns_int_rev] Team {team_id}: {e}")
            set_status(cur, team_id, "dns_int_rev", "red")

        # --------------------
        # DNS EXTERNAL
        # --------------------
        try:
            set_status(
                cur,
                team_id,
                "dns_ext_fwd",
                "green" if check_dns_ext_fwd(team_id) else "red"
            )
        except Exception as e:
            logging.error(f"[dns_ext_fwd] Team {team_id}: {e}")
            set_status(cur, team_id, "dns_ext_fwd", "red")

        try:
            set_status(
                cur,
                team_id,
                "dns_ext_rev",
                "green" if check_dns_ext_rev(team_id) else "red"
            )
        except Exception as e:
            logging.error(f"[dns_ext_rev] Team {team_id}: {e}")
            set_status(cur, team_id, "dns_ext_rev", "red")

        # --------------------
        # POSTGRES
        # --------------------
        try:
            set_status(
                cur,
                team_id,
                "postgres_access",
                check_postgres_access(team_id)
            )
        except Exception as e:
            logging.error(f"[postgres_access] Team {team_id}: {e}")
            set_status(cur, team_id, "postgres_access", "red")

        # --------------------
        # SMB
        # --------------------
        try:
            set_status(
                cur,
                team_id,
                "smb_login",
                check_smb_login(team_id)
            )
        except Exception as e:
            logging.error(f"[smb_login] Team {team_id}: {e}")
            set_status(cur, team_id, "smb_login", "red")

        try:
            set_status(
                cur,
                team_id,
                "smb_read",
                check_smb_read(team_id)
            )
        except Exception as e:
            logging.error(f"[smb_read] Team {team_id}: {e}")
            set_status(cur, team_id, "smb_read", "red")

        try:
            set_status(
                cur,
                team_id,
                "smb_write",
                check_smb_write(team_id)
            )
        except Exception as e:
            logging.error(f"[smb_write] Team {team_id}: {e}")
            set_status(cur, team_id, "smb_write", "red")

        # --------------------
        # SSH LOGIN
        # --------------------
        try:
            set_status(
                cur,
                team_id,
                "ssh_login",
                check_ssh_login(team_id)
            )
        except Exception as e:
            logging.error(f"[ssh_login] Team {team_id}: {e}")
            set_status(cur, team_id, "ssh_login", "red")

    conn.commit()
    cur.close()
    conn.close()

    logging.info("Scoring cycle completed")


if __name__ == "__main__":
    run_scoring_cycle()

