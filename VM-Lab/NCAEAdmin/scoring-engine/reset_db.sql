BEGIN;

TRUNCATE TABLE service_status;

INSERT INTO service_status (team_id, service_id, status)
SELECT
    t.id,
    s.id,
    'red'
FROM teams t
CROSS JOIN services s;

COMMIT;

