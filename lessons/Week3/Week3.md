# Week 3 Summary

---

## Prerequisites

- Mikrotik Router ISO Installed in a VM
- Rocky or Ubuntu ISO Installed in a VM with a web service installed
- Rocky or Ubuntu ISO Installed in a VM (DNS Server)
- Three Virtual Network Adapters (2 virtual networks total)
  - LAN
  - WAN

**Note:** Please review `Week2.md` if you are unsure how to configure the router or host networking.

`t = team number`

---

## DNS Install

**Note:** The IP address values and topology may change depending on the environment.  
The image below showcases the network configuration for the example machine.

![ipDNS.png](./img/ipDNS.png)

---

### 1. Install BIND9

If not installed already, install bind9:
```bash
sudo apt update && sudo apt install bind9 -y
```
![bind9Install.png](./img/bind9Install.png)

---

### 2. Review DNS Configuration Directory

The service configuration files are stored in:
```text
/etc/bind
```
![bindDirectoryFiles.png](./img/bindDirectoryFiles.png)

---

### DNS Concepts (Quick Reference)

DNS uses **zones** to map specific namespaces (domains) to IP addresses and vice versa.

For the scope of the competition, there are two types of queries a host can make:

- **Forward lookup**  
  The host is asking: *What is the IP address of a domain?*  
  Example: `google.com → 8.8.8.8`

- **Reverse lookup**  
  The host is asking: *What is the domain name of an IP address?*  
  Example: `8.8.8.8 → google.com`

To map this information, DNS uses **records**.

For this competition, you only need to concern yourself with:

- **A Record** – IPv4 address mapping to a domain name  
- **PTR Record** – IPv4 address mapping back to a domain  

**NOTE:** When you see `→`, think *resolve*.

---

## DNS Internal Configuration

---

### 3. Define DNS Zones

To configure the records for our DNS server, modify:
```text
/etc/bind/named.conf.default-zones
```
Add the following entries **to the bottom** of the file:

![addZonesConfig.png](./img/addZonesConfig.png)
```text
zone "team2.org" IN {
	type master;
	file "/etc/bind/zones/forward.team2.org";
	allow-update { none; };
};
```
```text
zone "t.168.192.in-addr.arpa" IN {
	type master;
	file "/etc/bind/zones/reverse.team2.org";
	allow-update { none; };
};
```
![zonesAdded.png](./img/zonesAdded.png)

---

### 4. Create Zone Files

Create the directory for zone files:
```bash
sudo mkdir /etc/bind/zones
```
Linux provides a template file called `db.empty`. We will copy it instead of creating files manually.

Create the forward lookup file:
```bash
sudo cp /etc/bind/db.empty /etc/bind/zones/forward.team2.org
```
Create the reverse lookup file:
```bash
sudo cp /etc/bind/db.empty /etc/bind/zones/reverse.team2.org
```
![recordCreate.png](./img/recordCreate.png)

---

### 5. Set Hostname

Change the system hostname to something easier to remember:
```bash
sudo hostnamectl set-hostname ncae-lab2026
```
![hostnameChange.png](./img/hostnameChange.png)

---

### 6. Configure Forward Lookup Zone (A Record)

Open `forward.team2.org` and make the following changes:

![beforeA.png](./img/beforeA.png)
```text
- Change the 7th line from `localhost` to `team2.org`  
- Change `root.localhost.` to `root`
- Increment the serial number on line 8 to `2`
- Change line 14 (`localhost.`) to your hostname  
  (verify using `hostname`)
```
![hostname.png](./img/hostname.png)

Add the following records:
```text
ncae-lab2026    IN A    192.168.t.12  
www             IN A    192.168.t.5
```
![afterA.png](./img/afterA.png)

Mimic the image above if you get stuck.

---

### 7. Configure Reverse Lookup Zone (PTR Record)

Open `reverse.team2.org`:

![beforePTR.png](./img/beforePTR.png)
```text
- Change the 7th line from `localhost` to `ncae-lab2026.team2.org`
- Change `root.localhost.` to `root.team2.org.`
- Increment the serial number on line 8 to `2`
- Change line 14 to your hostname
```
![hostname.png](./img/hostname.png)

Add the following record:
```text
3   IN  PTR ncae-lab2026.team2.org
```
![afterPTR.png](./img/afterPTR.png)

Mimic the image above if you get stuck.

---

### 8. Reload and Restart DNS Service

Reload and restart the DNS service to apply changes.

![bindRunning.png](./img/bindRunning.png)

---

### 9. Test Internal DNS Resolution

On another internal machine, set the DNS server and test name resolution:
```bash
nmcli connection modify "Wired Connection 1" ipv4.dns "192.168.t.12"

nslookup 192.168.t.5
```
---

## DNS External Configuration

---

### 10. Configure Port Forwarding for DNS (WAN → LAN)

To allow external devices to use the internal DNS server, configure a DST-NAT rule.

Navigation path:

Go to **Advanced** → **IP** → **Firewall** → **NAT** → **New**

![dnsGeneral.png](./img/dnsGeneral.png)

General Tab:
```text
- Chain: dstnat
- Protocol: udp
- In. Interface: WAN
```
![dnsAction.png](./img/dnsAction.png)

Action Tab:
```text
- Action: dst-nat
- To Addresses: 192.168.t.3
- To Ports: 53
```
---

### 11. Add Firewall Filter Rule

Allow DNS traffic to exit the LAN:

Navigation path:

Go to **Advanced** → **IP** → **Firewall** → **Filter Rules** → **New**

![dnsFilterRuleGeneral.png](./img/dnsFilterRuleGeneral.png)

General Tab:
```text
- Protocol: udp
- Dst. Port: 53
- Out. Interface: LAN
```
![dnsFilterRuleAction.png](./img/dnsFilterRuleAction.png)

Action Tab:
```text
- Action: accept
```
---

### 12. Add External DNS Record

External clients do not see private IP addresses.

Add an external-facing A record to handle WAN-based queries.

![forwardExternal.png](./img/forwardExternal.png)

Add the following entry to the forward zone file:
```text
external    IN  A   172.18.13.t
```
![externalAdded.png](./img/externalAdded.png)

---

### 13. Restart DNS Service

Restart the bind9 service to apply all changes:
```bash
sudo systemctl restart bind9
```
![bind9servicerestart.png](./img/bind9servicerestart.png)

---

### 14. Test

From an external machine you can perform the following commands:
```bash
dig external.team2.org  
nslookup external.team2.org
```
![digCommands.png](./img/digCommands.png)
![webResolve.png](./img/webResolve.png)
