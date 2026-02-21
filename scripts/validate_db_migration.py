#!/usr/bin/env python3
"""
Validate database migration integrity: compare schema and data between source (e.g. local)
and target (e.g. cloud) DBs to ensure no dropped tables/columns or corrupted data.

Modes:
  --baseline FILE   Connect using --env-file, capture tables/columns/row counts (and
                    optional checksums), save to FILE. Use this on your source DB (e.g. local).
  --compare FILE    Connect using --env-file, load baseline from FILE, compare target DB
                    to baseline. Report missing/extra tables, column diffs, row count diffs.
  (no mode)         Report: connect and print table list + row counts (and views) for manual check.

Usage (from repo root):
  # Capture local DB state (source of truth before migration)
  python scripts/validate_db_migration.py --env-file .env --baseline migration_baseline.json

  # Compare cloud DB to that baseline (after restore + view migrations)
  python scripts/validate_db_migration.py --env-file .env.cloud --compare migration_baseline.json

  # Quick report of current DB (e.g. cloud)
  python scripts/validate_db_migration.py --env-file .env.cloud

  # Include table checksums in baseline/compare (slower but detects corruption)
  python scripts/validate_db_migration.py --env-file .env --baseline migration_baseline.json --checksum
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
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
        raise SystemExit(f"Env file not found: {path}")
    if dotenv_values is None:
        raise SystemExit("python-dotenv is required. pip install python-dotenv")
    values = dotenv_values(path)
    return {**{k: str(v) for k, v in values.items() if v is not None}, **os.environ}


def _get_conn(env: dict):
    if mysql is None:
        raise SystemExit("mysql-connector-python is required. pip install mysql-connector-python")
    host = (env.get("MYSQL_HOST") or "localhost").strip()
    port = int((env.get("MYSQL_PORT") or "3306").strip())
    user = (env.get("MYSQL_USER") or "root").strip()
    password = (env.get("MYSQL_PASSWORD") or "").strip().strip("\ufeff").replace("\r", "").replace("\n", "").strip()
    database = (env.get("MYSQL_DATABASE") or "wargaming_erp").strip()
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
    return mysql.connector.connect(**conn_kw), database, host, port


def _get_tables_and_views(conn, database: str):
    """Return (list of base table names, list of view names)."""
    cur = conn.cursor()
    cur.execute(
        "SELECT TABLE_NAME, TABLE_TYPE FROM information_schema.TABLES WHERE TABLE_SCHEMA = %s ORDER BY TABLE_NAME",
        (database,),
    )
    tables = []
    views = []
    for name, typ in cur.fetchall():
        if typ == "BASE TABLE":
            tables.append(name)
        elif typ == "VIEW":
            views.append(name)
    cur.close()
    return tables, views


def _get_columns(conn, database: str, table: str):
    """Return list of (column_name, data_type)."""
    cur = conn.cursor()
    cur.execute(
        """SELECT COLUMN_NAME, DATA_TYPE FROM information_schema.COLUMNS
           WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s ORDER BY ORDINAL_POSITION""",
        (database, table),
    )
    out = [{"name": row[0], "type": row[1]} for row in cur.fetchall()]
    cur.close()
    return out


def _get_row_count(conn, table: str):
    cur = conn.cursor()
    try:
        cur.execute(f"SELECT COUNT(*) FROM `{table}`")  # table name from information_schema, safe
        return cur.fetchone()[0]
    finally:
        cur.close()


def _get_checksum(conn, table: str):
    """Return checksum from CHECKSUM TABLE, or None if not supported."""
    cur = conn.cursor()
    try:
        cur.execute(f"CHECKSUM TABLE `{table}`")
        row = cur.fetchone()
        return row[1] if row and row[1] is not None else None
    except Exception:
        return None
    finally:
        cur.close()


def run_baseline(conn, database: str, host: str, port: int, checksum: bool, verbose: bool) -> dict:
    tables, views = _get_tables_and_views(conn, database)
    payload = {
        "database": database,
        "host": host,
        "port": port,
        "captured_at": datetime.now(timezone.utc).isoformat(),
        "tables": {},
        "views": views,
    }
    for i, table in enumerate(tables):
        if verbose:
            print(f"  [{i+1}/{len(tables)}] {table} ...")
        cols = _get_columns(conn, database, table)
        try:
            row_count = _get_row_count(conn, table)
        except Exception as e:
            row_count = None
            if verbose:
                print(f"    row count failed: {e}")
        rec = {"columns": cols, "row_count": row_count}
        if checksum:
            rec["checksum"] = _get_checksum(conn, table)
        payload["tables"][table] = rec
    return payload


def run_compare(conn, database: str, baseline: dict, checksum: bool, verbose: bool) -> tuple[bool, list[str]]:
    """Compare current DB to baseline. Return (ok, list of message lines)."""
    messages = []
    tables_baseline = set(baseline.get("tables", {}))
    tables_target, views_baseline_list = _get_tables_and_views(conn, database)
    views_baseline = set(baseline.get("views", []))
    views_target = set(views_baseline_list)

    missing_tables = tables_baseline - set(tables_target)
    extra_tables = set(tables_target) - tables_baseline
    if missing_tables:
        messages.append(f"Missing tables (in baseline, not in target): {sorted(missing_tables)}")
    if extra_tables:
        messages.append(f"Extra tables (in target, not in baseline): {sorted(extra_tables)}")

    missing_views = views_baseline - views_target
    if missing_views:
        messages.append(f"Missing views (in baseline, not in target): {sorted(missing_views)}")
        messages.append("  → Run docs/Cloud-Post-Restore-Migration-Plan.md to create views on cloud.")

    common_tables = tables_baseline & set(tables_target)
    for table in sorted(common_tables):
        rec = baseline["tables"][table]
        cols_baseline = {c["name"]: c["type"] for c in rec.get("columns", [])}
        cols_target = _get_columns(conn, database, table)
        cols_target_d = {c["name"]: c["type"] for c in cols_target}
        missing_cols = set(cols_baseline) - set(cols_target_d)
        extra_cols = set(cols_target_d) - set(cols_baseline)
        if missing_cols:
            messages.append(f"Table {table}: missing columns {sorted(missing_cols)}")
        if extra_cols:
            messages.append(f"Table {table}: extra columns (in target) {sorted(extra_cols)}")
        type_mismatch = [c for c in cols_baseline if c in cols_target_d and cols_baseline[c] != cols_target_d[c]]
        if type_mismatch:
            messages.append(f"Table {table}: type mismatch for columns {type_mismatch}")

        row_count_b = rec.get("row_count")
        if row_count_b is not None:
            try:
                row_count_t = _get_row_count(conn, table)
                if row_count_t != row_count_b:
                    messages.append(f"Table {table}: row count baseline={row_count_b} target={row_count_t}")
            except Exception as e:
                messages.append(f"Table {table}: row count error {e}")

        if checksum and rec.get("checksum") is not None:
            cs = _get_checksum(conn, table)
            if cs is not None and cs != rec["checksum"]:
                messages.append(f"Table {table}: checksum mismatch (data may differ)")

    ok = len(messages) == 0
    return ok, messages


def run_report(conn, database: str, host: str, port: int):
    tables, views = _get_tables_and_views(conn, database)
    print(f"Database: {database} @ {host}:{port}")
    print(f"Base tables: {len(tables)}")
    print(f"Views: {len(views)}")
    print()
    print(f"{'Table':<45} {'Rows':>12}")
    print("-" * 58)
    for table in sorted(tables):
        try:
            n = _get_row_count(conn, table)
            print(f"{table:<45} {n:>12}")
        except Exception as e:
            print(f"{table:<45} {'error':>12}  # {e}")
    if views:
        print()
        print("Views:", ", ".join(sorted(views)))


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Validate DB migration: baseline (save source state) or compare target to baseline"
    )
    ap.add_argument("--env-file", default=os.environ.get("PROXYFORGE_ENV_FILE", ".env"), help="Env file with MYSQL_*")
    ap.add_argument("--baseline", type=Path, metavar="FILE", help="Capture current DB state to JSON file (source)")
    ap.add_argument("--compare", type=Path, metavar="FILE", help="Compare current DB to baseline JSON (target)")
    ap.add_argument("--checksum", action="store_true", help="Include CHECKSUM TABLE in baseline/compare (slower)")
    ap.add_argument("-q", "--quiet", action="store_true", help="Less output")
    args = ap.parse_args()

    env = _load_env(args.env_file)
    conn, database, host, port = _get_conn(env)
    verbose = not args.quiet

    try:
        if args.baseline:
            out_path = args.baseline if args.baseline.is_absolute() else REPO_ROOT / args.baseline
            if verbose:
                print(f"Capturing baseline from {host}:{port} database={database} ...")
            payload = run_baseline(conn, database, host, port, args.checksum, verbose)
            out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
            if verbose:
                print(f"Baseline saved to {out_path} ({len(payload['tables'])} tables, {len(payload.get('views', []))} views)")
            return 0

        if args.compare:
            base_path = args.compare if args.compare.is_absolute() else REPO_ROOT / args.compare
            if not base_path.exists():
                print(f"Baseline file not found: {base_path}", file=sys.stderr)
                return 1
            baseline = json.loads(base_path.read_text(encoding="utf-8"))
            if verbose:
                print(f"Comparing {host}:{port} database={database} to baseline from {baseline.get('captured_at', '?')} ...")
            ok, messages = run_compare(conn, database, baseline, args.checksum, verbose)
            if ok:
                if verbose:
                    print("OK: Target matches baseline (tables, columns, row counts" + (" and checksums" if args.checksum else "") + ").")
                return 0
            for m in messages:
                print(m, file=sys.stderr)
            return 1

        run_report(conn, database, host, port)
        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    sys.exit(main())
