import subprocess

# --------------------------------------------------
# Configuration
# --------------------------------------------------

SSH_USER = "ncae-lab2026"
SSH_PASS = "NCAE"

# Internal DNS server IP
DNS_SERVER_IP_TEMPLATE = "192.168.{t}.12"


# --------------------------------------------------
# SSH Helper
# --------------------------------------------------

def ssh_exec(team_id: int, command: str) -> str:
    """
    Execute a command on the team's internal helper machine over SSH.
    Uses sshpass for password-based auth.
    """
    target_ip = f"172.18.13.{team_id}"

    ssh_cmd = [
        "sshpass", "-p", SSH_PASS,
        "ssh",
        "-o", "StrictHostKeyChecking=no",
        "-o", "UserKnownHostsFile=/dev/null",
        f"{SSH_USER}@{target_ip}",
        command
    ]

    try:
        result = subprocess.run(
            ssh_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=10,
            text=True
        )
        return result.stdout.strip()
    except Exception as e:
        print(f"SSH exec failed for team {team_id}: {e}")
        return ""


# --------------------------------------------------
# Internal DNS Forward Check
# --------------------------------------------------

def check_dns_int_fwd(team_id: int) -> bool:
    """
    Internal forward DNS:
      www.team<t>.net -> 192.168.<t>.5
      db.team<t>.net  -> 192.168.<t>.7
      ns1.team<t>.net -> 192.168.<t>.12
    """

    dns_ip = DNS_SERVER_IP_TEMPLATE.format(t=team_id)

    checks = {
        f"www.team{team_id}.net": f"192.168.{team_id}.5",
        f"db.team{team_id}.net":  f"192.168.{team_id}.7",
        f"ns1.team{team_id}.net": f"192.168.{team_id}.12",
    }

    for hostname, expected_ip in checks.items():
        cmd = f"dig @{dns_ip} {hostname} +short"
        out = ssh_exec(team_id, cmd)

        if not out:
            return False

        ips = [line.strip() for line in out.splitlines() if line.strip()]

        if expected_ip not in ips:
            return False

    return True


# --------------------------------------------------
# Internal DNS Reverse Check
# --------------------------------------------------

def check_dns_int_rev(team_id: int) -> bool:
    """
    Internal reverse DNS.
    Accepts PTRs like:
      www.team2.net.2.168.192.in-addr.arpa.
    """

    dns_ip = DNS_SERVER_IP_TEMPLATE.format(t=team_id)

    checks = {
        f"192.168.{team_id}.5":  f"www.team{team_id}.net.",
        f"192.168.{team_id}.7":  f"db.team{team_id}.net.",
        f"192.168.{team_id}.12": f"ns1.team{team_id}.net.",
    }

    for ip, expected_prefix in checks.items():
        cmd = f"dig -x {ip} @{dns_ip} +short"
        out = ssh_exec(team_id, cmd)

        if not out:
            return False

        ptrs = [line.strip() for line in out.splitlines() if line.strip()]

        # PTR must start with hostname (reverse zone suffix allowed)
        if not any(ptr.startswith(expected_prefix) for ptr in ptrs):
            return False

    return True

