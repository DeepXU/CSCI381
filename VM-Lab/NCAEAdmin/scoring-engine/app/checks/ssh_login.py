import subprocess

SSH_TEST_USERS = [
    "camille_jenatzy",
    "henry_ford",
    "andy_green"
]

KEY_PATH = "/opt/scoring-engine/keys/scoring_id_rsa"

def check_ssh_login(team_id: int) -> str:
    host = f"172.18.14.{team_id}"

    for user in SSH_TEST_USERS:
        try:
            result = subprocess.run(
                [
                    "ssh",
                    "-i", KEY_PATH,
                    "-o", "BatchMode=yes",
                    "-o", "StrictHostKeyChecking=no",
                    "-o", "UserKnownHostsFile=/dev/null",
                    "-o", "ConnectTimeout=5",
                    f"{user}@{host}",
                    "true"
                ],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=6
            )

            if result.returncode == 0:
                return "green"

        except subprocess.TimeoutExpired:
            continue
        except Exception:
            continue

    return "yellow"

