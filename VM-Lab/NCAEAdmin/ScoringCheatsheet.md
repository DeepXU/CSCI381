sudo systemctl daemon-reexec
sudo systemctl daemon-reload

sudo systemctl stop scoring-runner.timer
sudo systemctl stop scoring-runner.service

sudo systemctl start scoring-runner.service

journalctl -u scoring-runner -n 20 --no-pager



sudo -u postgres psql scoring

BEGIN;

TRUNCATE TABLE service_status;

COMMIT;
--

INSERT INTO service_status (team_id, service_id, status)
SELECT
    t.id,
    s.id,
    'red'
FROM teams t
CROSS JOIN services s;



SSH ALLOW:

/ip firewall nat add chain=dstnat in-interface=WAN protocol=tcp dst-port=22 action=dst-nat to-addresses=192.168.2.7 to-ports=22 comment="SSH WAN to 192.168.2.7"

/ip firewall filter add chain=forward src-address=172.18.134.43 dst-address=192.168.2.7 protocol=tcp dst-port=22 action=accept comment="Allow SSH from WAN host"
