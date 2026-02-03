from app.utils.cmd_exec import run_cmd

SMB_PASS = "cnyrocks"
TEST_USER = "benjamin_franklin"

def check_smb_login(team: int) -> str:
    ip = f"172.18.14.{team}"

    cmd = [
        "smbclient",
        f"//{ip}/files",
        "-U", f"{TEST_USER}%{SMB_PASS}",
        "-c", "ls"
    ]

    rc = run_cmd(cmd, timeout=4)

    if rc == 0:
        return "green"
    if rc == -1:
        return "red"
    return "yellow"

