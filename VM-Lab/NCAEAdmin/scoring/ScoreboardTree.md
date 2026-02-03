```bash
/opt/scoring-engine
├── app
│   ├── __init__.py
│   │
│   ├── runner.py                     # Main scoring loop (called by systemd)
│   │
│   ├── db.py                         # PostgreSQL connection to scoring DB
│   │
│   ├── checks                        # ALL scoring logic lives here
│   │   ├── __init__.py
│   │
│   │   ├── router_icmp.py            # Router WAN ICMP check
│   │
│   │   ├── web_http.py               # www_port_80, www_content, www_ssl
│   │
│   │   ├── dns_internal.py           # DNS INT FWD + REV
│   │
│   │   ├── dns_external.py           # DNS EXT FWD + REV
│   │
│   │   ├── postgres_access.py        # PostgreSQL via SSH helper (Option B)
│   │
│   │   ├── smb_login.py              # SMB login check
│   │   ├── smb_read.py               # SMB read check
│   │   ├── smb_write.py              # SMB write check
│   │
│   │   └── ssh_login.py              # SSH public-key login check (shell server)
│   │
│   ├── utils
│   │   ├── __init__.py
│   │
│   │   ├── ssh_helper.py             # SSH helper (password-based, DB VM)
│   │
│   │   ├── ssh_key_helper.py          # SSH key login helper (shell server)
│   │
│   │   └── cmd_exec.py               # Safe subprocess wrapper w/ timeout
│   │
│   └── __pycache__                   # Python bytecode (safe to ignore)
│
├── logs
│   └── runner.log                    # Scoring engine execution log
│
├── keys
│   ├── scoring_id_rsa                # SSH private key for ssh_login scoring
│   └── scoring_id_rsa.pub            # Matching public key
│
├── secrets
│   └── runtime.env                   # Optional env vars (DB creds if used)
│
├── .venv                             # Python virtual environment
│
├── requirements.txt                  # Python dependencies
│
└── README.md                         # (Optional) build + ops documentation
```