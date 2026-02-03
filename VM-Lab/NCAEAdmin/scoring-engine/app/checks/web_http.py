import subprocess

def _router_ip(team_id: int) -> str:
    return f"172.18.13.{team_id}"

def check_www_port_80(team_id: int) -> bool:
    try:
        result = subprocess.run(
            ["curl", "-s", "--connect-timeout", "2", f"http://{_router_ip(team_id)}"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        return result.returncode == 0
    except Exception:
        return False

def check_www_content(team_id: int) -> bool:
    expected = f"NCAE-CYBERGAMES-TEAM{team_id}-WEBSITE"

    try:
        result = subprocess.run(
            ["curl", "-s", f"http://{_router_ip(team_id)}"],
            capture_output=True,
            text=True,
            timeout=2
        )

        if result.returncode != 0:
            return False

        return expected in result.stdout
    except Exception:
        return False

def check_www_ssl(team_id: int) -> bool:
    try:
        result = subprocess.run(
            ["curl", "-k", "-s", "--connect-timeout", "2", f"https://{_router_ip(team_id)}"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        return result.returncode == 0
    except Exception:
        return False

