from app.utils.cmd_exec import run_cmd

SMB_PASS = "cnyrocks"
TEST_USER = "plato"

FILES = ["paris.data", "berlin.data", "rome.data"]

def check_smb_read(team: int) -> str:
    ip = f"172.18.14.{team}"
    failures = 0

    for f in FILES:
        cmd = [
            "smbclient",
            f"//{ip}/files",
            "-U", f"{TEST_USER}%{SMB_PASS}",
            "-c", f"get {f} /tmp/{f}"
        ]

        rc = run_cmd(cmd, timeout=4)
        if rc != 0:
            failures += 1

    if failures == 0:
        return "green"
    if failures < len(FILES):
        return "yellow"
    return "red"

