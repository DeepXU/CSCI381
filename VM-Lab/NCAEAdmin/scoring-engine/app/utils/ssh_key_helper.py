from app.utils.cmd_exec import run_cmd

KEY_PATH = "/opt/scoring-engine/keys/scoring_id_rsa"

def ssh_key_login(user: str, host: str) -> bool:
    cmd = [
        "ssh",
        "-i", KEY_PATH,
        "-o", "BatchMode=yes",
        "-o", "StrictHostKeyChecking=no",
        "-o", "UserKnownHostsFile=/dev/null",
        "-o", "ConnectTimeout=3",
        f"{user}@{host}",
        "true"
    ]

    return run_cmd(cmd, timeout=4) == 0

