import subprocess
import logging

SSH_USER = "ncae-lab2026"
SSH_PASS = "NCAE"

def ssh_exec(team: int, command: str, target_ip: str) -> bool:
    try:
        ssh_cmd = [
            "sshpass", "-p", SSH_PASS,
            "ssh",
            "-o", "StrictHostKeyChecking=no",
            "-o", "ConnectTimeout=10",
            f"{SSH_USER}@{target_ip}",
            command
        ]

        result = subprocess.run(
            ssh_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=15
        )

        if result.returncode != 0:
            logging.warning(
                f"[SSH] Team {team} failed: {result.stderr.decode().strip()}"
            )
            return False

        return True

    except Exception as e:
        logging.warning(f"[SSH] Team {team} exception: {e}")
        return False

