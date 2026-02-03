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


/ip firewall nat
add chain=dstnat \
    src-address=172.18.134.43 \
    dst-address=172.18.13.2 \
    protocol=tcp \
    dst-port=22 \
    action=dst-nat \
    to-addresses=172.18.14.2 \
    to-ports=22 \
    comment="NCAE SSH scoring → Team 2 DB"
