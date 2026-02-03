# Week 3 – DNS (BIND9) Cheatsheet & Reference

---

## Prerequisites (Quick Check)

- MikroTik Router VM installed
- Rocky or Ubuntu VM with a web service installed
- Rocky or Ubuntu VM acting as DNS Server
- Two virtual networks:
  - LAN
  - WAN

Note: Review `Week2.md` for router and host networking configuration if needed.

`t = team number`

---

## DNS Install (BIND9)

### Install DNS Server
```bash
sudo apt update && sudo apt install bind9 -y
```
---

### DNS Configuration Directory
```text
/etc/bind
```
Common files:
- named.conf
- named.conf.options
- named.conf.default-zones
- db.empty

---

## DNS Concepts (Reference)

- Forward lookup: Domain → IP
- Reverse lookup: IP → Domain

Records used:
- A record: Domain → IPv4 address
- PTR record: IPv4 address → Domain

---

## DNS Internal Configuration (LAN)

---

### Define DNS Zones

Edit:
```text
/etc/bind/named.conf.default-zones
```
Add zones:

```bash
zone "team2.org" IN {
    type master;
    file "/etc/bind/zones/forward.team2.org";
    allow-update { none; };
};

zone "t.168.192.in-addr.arpa" IN {
    type master;
    file "/etc/bind/zones/reverse.team2.org";
    allow-update { none; };
};
```
---

### Create Zone Directory and Files

Create zones directory:
```bash
sudo mkdir /etc/bind/zones
```
Copy templates:

Forward zone:
```bash
sudo cp /etc/bind/db.empty /etc/bind/zones/forward.team2.org
```
Reverse zone:
```bash
sudo cp /etc/bind/db.empty /etc/bind/zones/reverse.team2.org
```
---

### Set Hostname (DNS Server)
```bash
sudo hostnamectl set-hostname ncae-lab2026
```
Verify:
```bash
hostname
```
---

### Forward Zone (A Records)

File:
```text
/etc/bind/zones/forward.team2.org
```
Required changes:
```text
- Change localhost → team2.org
- Change root.localhost. → root
- Increment serial number
- Replace localhost. with hostname
```
Records to add:
```bash
ncae-lab2026    IN A    192.168.t.12
www             IN A    192.168.t.5
```
---

### Reverse Zone (PTR Records)

File:
```text
/etc/bind/zones/reverse.team2.org
```
Required changes:
```text
- localhost → ncae-lab2026.team2.org
- root.localhost. → root.team2.org.
- Increment serial number
- Replace localhost. with hostname
```
Record to add:
```bash
12  IN PTR ncae-lab2026.team2.org
```
---

### Reload / Restart DNS

```bash
sudo systemctl restart bind9
```
---

## Internal DNS Testing

Set DNS on internal client:
```bash
nmcli connection modify "Wired Connection 1" ipv4.dns "192.168.t.12"
```
Test resolution:
```bash
nslookup 192.168.t.5
nslookup www.team2.org
nslookup ncae-lab2026.team2.org
```
---

## DNS External Configuration (WAN Access)

---

### MikroTik – Port Forward DNS (UDP 53)

Navigation:
Advanced → IP → Firewall → NAT → New

General:
```text
- Chain: dstnat
- Protocol: udp
- In. Interface: WAN
```
Action:
```text
- Action: dst-nat
- To Address: 192.168.t.12
- To Port: 53
```
---

### MikroTik – Firewall Filter Rule

Navigation:
Advanced → IP → Firewall → Filter Rules → New

General:
```text
- Protocol: udp
- Dst. Port: 53
- Out. Interface: LAN
```
Action:
```text
- Action: accept
```
---

### External DNS Record

Add to forward zone file:
```bash
external    IN A    172.18.13.t
```
Restart DNS:
```bash
sudo systemctl restart bind9
```
---

## External DNS Testing

From an external machine:
```bash
dig external.team2.org
nslookup external.team2.org
```
Browser test:
http://external.team2.org

---

## Verification & Troubleshooting Commands

### Check DNS Service Status
```bash
systemctl status bind9
```
---

### Validate Zone Files
```bash
named-checkzone team2.org /etc/bind/zones/forward.team2.org
named-checkzone t.168.192.in-addr.arpa /etc/bind/zones/reverse.team2.org
```
---

### Validate BIND Configuration
```bash
named-checkconf
```
---

### Check Listening Ports
```bash
ss -tulnp | grep :53
netstat -tulnp | grep :53
```
---

### Query DNS Locally (Bypass Client DNS)
```bash
dig @127.0.0.1 team2.org
dig @127.0.0.1 www.team2.org
dig -x 192.168.t.5
```
---

### Check Firewall (DNS Server)
```bash
sudo ufw status
sudo firewall-cmd --list-all
```
---

### Common Issues Quick Fixes

- No response from DNS:
  - Check bind9 is running
  - Check UDP port 53 forwarding
  - Verify filter rule allows UDP 53

- SERVFAIL:
  - Serial number not incremented
  - Syntax error in zone file
  - Run named-checkzone

- External resolution fails:
  - NAT rule order incorrect
  - Missing external A record
  - Filter rule missing