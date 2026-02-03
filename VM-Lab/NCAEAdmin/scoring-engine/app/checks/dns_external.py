import subprocess
import logging

DIG_TIMEOUT = 3

def _dig(server: str, query: str) -> str:
    try:
        result = subprocess.run(
            ["dig", f"@{server}", query, "+short"],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            timeout=DIG_TIMEOUT,
            text=True
        )
        return result.stdout.strip()
    except subprocess.TimeoutExpired:
        return ""


def _dig_reverse(server: str, ip: str) -> str:
    try:
        result = subprocess.run(
            ["dig", "-x", ip, f"@{server}", "+short"],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            timeout=DIG_TIMEOUT,
            text=True
        )
        return result.stdout.strip()
    except subprocess.TimeoutExpired:
        return ""


# -----------------------------
# External DNS Forward
# -----------------------------

def check_dns_ext_fwd(team: int) -> bool:
    dns_ip = f"172.18.13.{team}"

    expected = {
        f"ns1.team{team}.cnyhackathon.org": f"172.18.13.{team}",
        f"www.team{team}.cnyhackathon.org": f"172.18.13.{team}",
        f"shell.team{team}.cnyhackathon.org": f"172.18.14.{team}",
        f"files.team{team}.cnyhackathon.org": f"172.18.14.{team}",
    }

    for name, ip in expected.items():
        out = _dig(dns_ip, name)
        if ip not in out:
            logging.warning(f"[DNS EXT FWD] Team {team} failed {name} → {ip} (got '{out}')")
            return False

    return True


# -----------------------------
# External DNS Reverse
# -----------------------------

def check_dns_ext_rev(team: int) -> bool:
    dns_ip = f"172.18.13.{team}"

    ptr_13 = _dig_reverse(dns_ip, f"172.18.13.{team}")
    ptr_14 = _dig_reverse(dns_ip, f"172.18.14.{team}")

    ok_13 = f"ns1.team{team}.cnyhackathon.org" in ptr_13
    ok_14 = (
        f"shell.team{team}.cnyhackathon.org" in ptr_14
        or f"files.team{team}.cnyhackathon.org" in ptr_14
    )

    if not ok_13:
        logging.warning(f"[DNS EXT REV] Team {team} PTR failed for 172.18.13.{team}: {ptr_13}")

    if not ok_14:
        logging.warning(f"[DNS EXT REV] Team {team} PTR failed for 172.18.14.{team}: {ptr_14}")

    return ok_13 and ok_14

