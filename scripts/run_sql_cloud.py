#!/usr/bin/env python3
"""
Run a single SQL query (or SQL from a file) against the cloud DB using .env.cloud.
No mysql CLI or Workbench needed. Uses mysql-connector-python and SSL for DigitalOcean.

Usage (from repo root):
  python scripts/run_sql_cloud.py "SELECT COUNT(*) FROM waha_datasheets"
  python scripts/run_sql_cloud.py "SELECT DISTINCT faction FROM view_master_picker WHERE game_system = '40K'"
  python scripts/run_sql_cloud.py --file path/to/query.sql
  python scripts/run_sql_cloud.py --env-file .env.cloud "SHOW TABLES"
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

try:
    from dotenv import dotenv_values
except ImportError:
    dotenv_values = None

try:
    import mysql.connector
except ImportError:
    mysql = None

REPO_ROOT = Path(__file__).resolve().parents[1]


def _load_env(env_file: str) -> dict:
    path = REPO_ROOT / env_file
    if not path.exists():
        raise SystemExit(f"Env file not found: {path}. Create it with MYSQL_* for the cloud DB.")
    if dotenv_values is None:
        raise SystemExit("python-dotenv is required. pip install python-dotenv")
    values = dotenv_values(path)
    return {**{k: str(v) for k, v in values.items() if v is not None}, **os.environ}


def main() -> int:
    ap = argparse.ArgumentParser(description="Run SQL against cloud DB (uses .env.cloud)")
    ap.add_argument("query", nargs="?", help="SQL query to run (or use --file)")
    ap.add_argument("--env-file", default=os.environ.get("PROXYFORGE_ENV_FILE", ".env.cloud"), help="Env file with MYSQL_*")
    ap.add_argument("--file", "-f", type=Path, help="Path to .sql file (run its contents)")
    args = ap.parse_args()

    if args.file:
        sql = (REPO_ROOT / args.file if not args.file.is_absolute() else args.file).read_text(encoding="utf-8", errors="replace").strip()
    elif args.query:
        sql = args.query.strip()
    else:
        ap.print_help()
        return 0

    env = _load_env(args.env_file)
    host = (env.get("MYSQL_HOST") or "localhost").strip()
    port = int((env.get("MYSQL_PORT") or "3306").strip())
    user = (env.get("MYSQL_USER") or "root").strip()
    password = (env.get("MYSQL_PASSWORD") or "").strip().strip("\ufeff").replace("\r", "").replace("\n", "").strip()
    database = (env.get("MYSQL_DATABASE") or "wargaming_erp").strip()

    if mysql is None:
        raise SystemExit("mysql-connector-python is required. pip install mysql-connector-python")

    use_ssl = host not in ("localhost", "127.0.0.1")
    conn_kw = {
        "host": host,
        "port": port,
        "user": user,
        "password": password,
        "database": database,
        "connection_timeout": 15,
    }
    if use_ssl:
        conn_kw["ssl_disabled"] = False
        if (env.get("MYSQL_SSL_VERIFY") or "1").strip() in ("0", "false", "no"):
            conn_kw["ssl_verify_cert"] = False

    conn = mysql.connector.connect(**conn_kw)
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(sql)
        rows = cursor.fetchall()
        if rows:
            for r in rows:
                print("\t".join(str(v) for v in r.values()))
            print(f"({len(rows)} row(s))")
        else:
            print("(0 rows)")
        conn.commit()
    except mysql.connector.errors.ProgrammingError as e:
        print(e, file=sys.stderr)
        return 1
    finally:
        cursor.close()
        conn.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
