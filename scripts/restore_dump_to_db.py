#!/usr/bin/env python3
"""
Restore a mysqldump .sql file into the database specified by an env file (e.g. .env.cloud).
Uses mysql-connector-python only (no mysql CLI needed). For DigitalOcean, set MYSQL_PORT and
use SSL (script enables SSL by default for non-localhost hosts).

Usage (from repo root):
  python scripts/restore_dump_to_db.py
  python scripts/restore_dump_to_db.py --dump path/to/dump.sql --env-file .env.cloud
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
        raise SystemExit(f"Env file not found: {path}. Create it with MYSQL_* for the remote DB.")
    if dotenv_values is None:
        raise SystemExit("python-dotenv is required. pip install python-dotenv")
    values = dotenv_values(path)
    # File first, then os.environ so MYSQL_PASSWORD set in shell overrides .env (for testing)
    return {**{k: str(v) for k, v in values.items() if v is not None}, **os.environ}


def main() -> int:
    ap = argparse.ArgumentParser(description="Restore mysqldump SQL file into DB using .env.cloud (or similar)")
    ap.add_argument("--dump", type=Path, default=REPO_ROOT / "wargaming_erp_dump.sql", help="Path to .sql dump file")
    ap.add_argument("--env-file", default=os.environ.get("PROXYFORGE_ENV_FILE", ".env.cloud"), help="Env file with MYSQL_*")
    args = ap.parse_args()

    dump_path = args.dump.resolve()
    if not dump_path.exists():
        raise SystemExit(f"Dump file not found: {dump_path}")

    env = _load_env(args.env_file)
    host = (env.get("MYSQL_HOST") or "localhost").strip()
    port = int((env.get("MYSQL_PORT") or "3306").strip())
    user = (env.get("MYSQL_USER") or "root").strip()
    # Strip BOM, CRLF, and spaces so .env file issues don't break the password
    password = (env.get("MYSQL_PASSWORD") or "").strip().strip("\ufeff").replace("\r", "").replace("\n", "").strip()
    database = (env.get("MYSQL_DATABASE") or "wargaming_erp").strip()

    # Optional: only check what we're using (no connect)
    if os.environ.get("PROXYFORGE_RESTORE_CHECK_ENV"):
        print(f"Env file: {REPO_ROOT / args.env_file}")
        print(f"  MYSQL_HOST={host!r}")
        print(f"  MYSQL_PORT={port}")
        print(f"  MYSQL_USER={user!r}")
        print(f"  MYSQL_DATABASE={database!r}")
        print(f"  MYSQL_PASSWORD length={len(password)} (empty={not password})")
        print("If Access denied: try passing password in shell to bypass .env:")
        print('  PowerShell: $env:MYSQL_PASSWORD="yourpassword"; python scripts/restore_dump_to_db.py')
        return 0

    if mysql is None:
        raise SystemExit("mysql-connector-python is required. pip install mysql-connector-python")

    # SSL for remote hosts (e.g. DigitalOcean); longer timeout for large restores
    use_ssl = host not in ("localhost", "127.0.0.1")
    conn_timeout = int((env.get("MYSQL_CONNECTION_TIMEOUT") or "600").strip())
    conn_kw = {
        "host": host,
        "port": port,
        "user": user,
        "password": password,
        "database": database,
        "connection_timeout": conn_timeout,
    }
    if use_ssl:
        conn_kw["ssl_disabled"] = False
        # If certificate verification fails, set MYSQL_SSL_VERIFY=0 in env
        if (env.get("MYSQL_SSL_VERIFY") or "1").strip() in ("0", "false", "no"):
            conn_kw["ssl_verify_cert"] = False

    def connect():
        return mysql.connector.connect(**conn_kw)

    def run_session_init(c):
        cur = c.cursor()
        try:
            cur.execute("SET SESSION sql_require_primary_key = 0")
        except Exception:
            pass
        try:
            cur.execute("SET SESSION wait_timeout = 3600")
        except Exception:
            pass
        try:
            cur.execute("SET SESSION max_allowed_packet = 268435456")
        except Exception:
            pass
        cur.close()

    print(f"Reading {dump_path} ...")
    # Detect encoding (dump may be UTF-16 on Windows if redirected with wrong encoding)
    raw = dump_path.read_bytes()
    if raw.startswith(b"\xff\xfe"):
        sql = raw.decode("utf-16-le", errors="replace")
    elif raw.startswith(b"\xfe\xff"):
        sql = raw.decode("utf-16-be", errors="replace")
    else:
        sql = raw.decode("utf-8-sig", errors="replace")
    # Normalize line endings so ";\n" split works (dump may have \r\n from Windows)
    sql = sql.replace("\r\n", "\n").replace("\r", "\n")
    # Remove mysqldump DELIMITER directives
    lines = []
    for line in sql.split("\n"):
        if line.strip().upper().startswith("DELIMITER "):
            continue
        lines.append(line)
    sql = "\n".join(lines)
    # Split into statements (semicolon at end of line); works with connectors that don't support multi=True
    statements = [
        s.strip() for s in sql.split(";\n")
        if s.strip() and not s.strip().startswith("--")
    ]
    # Skip statements that look like binary/garbage (e.g. UTF-16 read as UTF-8) or pure comments
    def is_executable_sql(stmt: str) -> bool:
        if "\x00" in stmt:
            return False
        start = stmt.lstrip()[:20].upper()
        return any(start.startswith(k) for k in ("CREATE", "INSERT", "SET ", "DROP", "ALTER", "USE ", "LOCK", "UNLOCK", "/*!", "REPLACE"))

    statements = [s for s in statements if is_executable_sql(s)]
    print(f"  {len(statements)} executable statements (after filtering).")
    print(f"Connecting to {host}:{port} (database={database}), SSL={use_ssl}, timeout={conn_timeout}s ...")
    conn = connect()
    try:
        run_session_init(conn)
        cursor = conn.cursor()
        count = 0
        for stmt in statements:
            if not stmt.strip():
                continue
            try:
                cursor.execute(stmt)
                count += 1
                if count % 100 == 0:
                    print(f"  Executed {count} statements ...")
            except (mysql.connector.errors.ProgrammingError, mysql.connector.errors.DatabaseError) as e:
                errno = getattr(e, "errno", None)
                # Lost connection (2013): reconnect and retry once; common with large restores to managed MySQL
                if errno == 2013:
                    print("  Lost connection; reconnecting and retrying ...")
                    try:
                        cursor.close()
                        conn.close()
                    except Exception:
                        pass
                    conn = connect()
                    run_session_init(conn)
                    cursor = conn.cursor()
                    try:
                        cursor.execute(stmt)
                        count += 1
                        if count % 100 == 0:
                            print(f"  Executed {count} statements ...")
                    except Exception as e2:
                        print(f"  Retry failed: {e2}. Skipping statement (first 80 chars): {stmt[:80]!r}...", file=sys.stderr)
                        count += 1
                    continue
                # Skip harmless errors: table exists, unknown table, duplicate column/key/entry
                if errno in (1050, 1051, 1060, 1061, 1062, 1022):
                    count += 1
                    continue
                # Syntax error: often from splitting on ";\n" inside procedure body or string
                if errno == 1064:
                    preview = (stmt[:80] + "..." if len(stmt) > 80 else stmt).replace("\n", " ")
                    print(f"  Skipping statement with syntax error (split?): {preview!r}")
                    count += 1
                    continue
                # DEFINER / SUPER: managed DB (e.g. DigitalOcean) does not allow CREATE with DEFINER=root@localhost
                if errno == 1227:
                    preview = (stmt[:80] + "..." if len(stmt) > 80 else stmt).replace("\n", " ")
                    print(f"  Skipping statement requiring SUPER/DEFINER: {preview!r}")
                    count += 1
                    continue
                # character_set_client etc. set to NULL in dump; managed DB rejects (errno 1231)
                if errno == 1231:
                    count += 1
                    continue
                raise
        print(f"Done. Executed {count} statements.")
        cursor.close()
        try:
            conn.commit()
        except mysql.connector.errors.OperationalError as e:
            if getattr(e, "errno", None) == 2013:
                print("  Warning: connection lost before commit; some changes may not be saved. Re-run restore if needed.", file=sys.stderr)
            else:
                raise
    finally:
        try:
            conn.close()
        except Exception:
            pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
