import subprocess

# ---------- helpers ----------

def dig_ok(args):
    try:
        r = subprocess.run(
            ["dig"] + args,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            timeout=3
        )
        return r.returncode == 0 and r.stdout.strip() != ""
    except Exception:
        return False


# ---------- EXTERNAL ----------

def check_dns_ext_fwd(team_id: int) -> bool:
    name = f"www.team{team_id}.ncaecybergames.org"
    expected_ip = f"172.18.13.{team_id}"
    return dig_ok([name, "@172.18.0.12", "+short"]) and expected_ip in subprocess.getoutput(
        f"dig {name} @172.18.0.12 +short"
    )


def check_dns_ext_rev(team_id: int) -> bool:
    ip = f"172.18.13.{team_id}"
    expected = f"www.team{team_id}.ncaecybergames.org."
    return dig_ok(["-x", ip, "@172.18.0.12", "+short"]) and expected in subprocess.getoutput(
        f"dig -x {ip} @172.18.0.12 +short"
    )


# ---------- INTERNAL ----------

def check_dns_int_fwd(team_id: int) -> bool:
    name = f"web.team{team_id}.internal"
    expected_ip = f"192.168.{team_id}.5"
    return dig_ok([name, "@192.168.{team_id}.12", "+short"]) and expected_ip in subprocess.getoutput(
        f"dig {name} @192.168.{team_id}.12 +short"
    )


def check_dns_int_rev(team_id: int) -> bool:
    ip = f"192.168.{team_id}.5"
    expected = f"web.team{team_id}.internal."
    return dig_ok(["-x", ip, "@192.168.{team_id}.12", "+short"]) and expected in subprocess.getoutput(
        f"dig -x {ip} @192.168.{team_id}.12 +short"
    )

