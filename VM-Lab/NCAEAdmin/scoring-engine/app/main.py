from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse

from app.db import get_db

app = FastAPI()

# Order matters: this defines column order on the scoreboard
SERVICES = [
    "dns_ext_fwd",
    "dns_ext_rev",
    "dns_int_fwd",
    "dns_int_rev",
    "postgres_access",
    "router_icmp",
    "smb_login",
    "smb_read",
    "smb_write",
    "ssh_login",
    "www_content",
    "www_port_80",
    "www_ssl",
]

TEAMS = [1, 2, 3, 4, 5]


def fetch_scoreboard_data():
    """
    Returns:
    {
        team_id: {
            service_id: status
        }
    }
    """
    data = {}

    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT team_id, service_id, status
            FROM service_status
        """)
        rows = cur.fetchall()

    for row in rows:
        team = row["team_id"]
        service = row["service_id"]
        status = row["status"]

        data.setdefault(team, {})[service] = status

    return data


@app.get("/api/scoreboard")
def api_scoreboard():
    return JSONResponse(fetch_scoreboard_data())


@app.get("/scoreboard", response_class=HTMLResponse)
def scoreboard_page():
    data = fetch_scoreboard_data()

    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>NCAE Scoreboard</title>
        <style>
            body {
                background: #0b0b0b;
                color: #e0e0e0;
                font-family: Arial, sans-serif;
            }
            h1 {
                text-align: center;
            }
            table {
                margin: auto;
                border-collapse: collapse;
                min-width: 90%;
            }
            th, td {
                border: 1px solid #333;
                padding: 6px 8px;
                text-align: center;
            }
            th {
                background: #111;
                position: sticky;
                top: 0;
            }
            tr:nth-child(even) {
                background: #111;
            }
        </style>
    </head>
    <body>
        <h1>NCAE Scoring Dashboard</h1>
        <table>
            <tr>
                <th>Team</th>
    """

    # Header row
    for service in SERVICES:
        html += f"<th>{service}</th>"
    html += "</tr>"

    # Team rows
    for team in TEAMS:
        html += f"<tr><td>Team {team}</td>"

        for service in SERVICES:
            status = data.get(team, {}).get(service, "unknown")

            icon = {
                "green": "🟢",
                "red": "🔴",
                "yellow": "🟡",
            }.get(status, "⚫")

            html += f"<td>{icon}</td>"

        html += "</tr>"

    html += """
        </table>
    </body>
    </html>
    """

    return HTMLResponse(html)


@app.get("/health")
def health():
    return {"status": "ok"}

