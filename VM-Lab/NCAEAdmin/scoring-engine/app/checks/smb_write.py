from app.utils.cmd_exec import run_cmd
import uuid

SMB_PASS = "cnyrocks"
TEST_USER = "aristotle"

def check_smb_write(team: int) -> str:
    ip = f"172.18.14.{team}"
    filename = f"scoring_{uuid.uuid4().hex}.txt"

    cmd = [
        "smbclient",
        f"//{ip}/files",
        "-U", f"{TEST_USER}%{SMB_PASS}",
        "-c", f"put /etc/hostname {filename}"
    ]

    rc = run_cmd(cmd, timeout=4)

    if rc == 0:
        return "green"
    if rc == -1:
        return "red"
    return "yellow"

