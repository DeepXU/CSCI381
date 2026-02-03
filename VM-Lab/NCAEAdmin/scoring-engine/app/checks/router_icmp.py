import subprocess

def check_router_icmp(team_id: int) -> bool:
    """
    ICMP check against team router WAN IP.
    Router WAN is always: 172.18.13.<team_id>
    """

    router_ip = f"172.18.13.{team_id}"

    try:
        result = subprocess.run(
            ["ping", "-c", "1", "-W", "1", router_ip],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=2
        )
        return result.returncode == 0
    except Exception:
        return False

