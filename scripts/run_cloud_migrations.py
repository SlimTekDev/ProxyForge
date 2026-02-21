#!/usr/bin/env python3
"""
Run cloud post-restore migration files (views and procedures) against the DB
specified by an env file (e.g. .env.cloud). Uses mysql-connector-python only;
no mysql CLI needed. For DigitalOcean, set MYSQL_PORT and use SSL.

Usage (from repo root):
  python scripts/run_cloud_migrations.py --env-file .env.cloud
  python scripts/run_cloud_migrations.py --env-file .env.cloud --full   # all 20 migrations
"""
from __future__ import annotations

import argparse
import os
import re
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
MIGRATIONS_DIR = REPO_ROOT / "ProxyForge" / "migrations"

# Required-only (11 files) in dependency order
REQUIRED_FILES = [
    "create_view_master_picker.sql",
    "recreate_view_40k_datasheet_complete_first_model.sql",
    "recreate_view_40k_unit_composition_with_max.sql",
    "add_chapter_subfaction_and_validation_view.sql",
    "create_view_40k_enhancement_picker.sql",
    "create_view_40k_army_rules.sql",
    "create_view_40k_army_rule_registry.sql",
    "create_view_40k_stratagems.sql",
    "create_view_opr_master_picker.sql",
    "create_view_opr_unit_rules_detailed.sql",
    "create_procedure_AddUnit.sql",
]

# Full parity (all 20) — required + optional views + GetArmyRoster
FULL_FILES = REQUIRED_FILES + [
    "create_view_40k_model_stats.sql",
    "create_view_master_picker_40k.sql",
    "create_view_opr_unit_complete.sql",
    "create_view_opr_unit_rules_complete.sql",
    "create_view_unit_selector.sql",
    "create_view_active_list_options.sql",
    "create_view_list_validation.sql",
    "create_view_master_army_command.sql",
    "create_procedure_GetArmyRoster.sql",
]


def _load_env(env_file: str) -> dict:
    path = REPO_ROOT / env_file
    if not path.exists():
        raise SystemExit(f"Env file not found: {path}. Create it with MYSQL_* for the cloud DB.")
    if dotenv_values is None:
        raise SystemExit("python-dotenv is required. pip install python-dotenv")
    values = dotenv_values(path)
    return {**{k: str(v) for k, v in values.items() if v is not None}, **os.environ}


def _run_file(conn, path: Path) -> None:
    """Execute a migration file. Handles DELIMITER ;; for procedure files."""
    raw = path.read_text(encoding="utf-8", errors="replace")
    # Remove DELIMITER lines (mysql CLI only)
    lines = [
        line for line in raw.split("\n")
        if not line.strip().upper().startswith("DELIMITER ")
    ]
    content = "\n".join(lines)

    # Procedure file: contains "END ;;" — run DROP then CREATE PROCEDURE ... END as one statement
    if "END ;;" in content or "END;;" in content:
        content_nodelim = re.sub(r"END\s*;;\s*", "END; ", content, flags=re.IGNORECASE)
        cursor = conn.cursor()
        try:
            # Execute DROP PROCEDURE if present (single statement)
            for line in content_nodelim.split("\n"):
                s = line.strip()
                if s.upper().startswith("DROP PROCEDURE"):
                    cursor.execute(s)
                    break
            # Execute CREATE PROCEDURE ... END; as one statement (procedure body has semicolons)
            create_start = content_nodelim.upper().find("CREATE PROCEDURE")
            if create_start >= 0:
                proc_block = content_nodelim[create_start:].strip()
                if not proc_block.endswith(";"):
                    proc_block = proc_block + ";"
                cursor.execute(proc_block)
            conn.commit()
        finally:
            cursor.close()
        return

    # View file: split by semicolon-newline and execute each
    statements = [s.strip() for s in content.split(";\n") if s.strip() and not s.strip().startswith("--")]
    cursor = conn.cursor()
    try:
        for stmt in statements:
            if not stmt.rstrip().endswith(";"):
                stmt = stmt + ";"
            try:
                cursor.execute(stmt)
            except mysql.connector.errors.DatabaseError as e:
                # Duplicate column / already exists — skip
                if getattr(e, "errno", None) in (1060, 1050):
                    continue
                raise
        conn.commit()
    finally:
        cursor.close()


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Run cloud post-restore migrations (views/procedures) using .env.cloud"
    )
    ap.add_argument("--env-file", default=os.environ.get("PROXYFORGE_ENV_FILE", ".env.cloud"), help="Env file with MYSQL_*")
    ap.add_argument("--full", action="store_true", help="Run all 20 migrations (full parity); default is 11 required-only")
    args = ap.parse_args()

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

    files = FULL_FILES if args.full else REQUIRED_FILES
    print(f"Connecting to {host}:{port} database={database} (SSL={use_ssl}) ...")
    conn = mysql.connector.connect(**conn_kw)
    try:
        for i, name in enumerate(files, 1):
            path = MIGRATIONS_DIR / name
            if not path.exists():
                print(f"  [{i}/{len(files)}] SKIP {name} (not found)", file=sys.stderr)
                continue
            print(f"  [{i}/{len(files)}] {name} ...")
            _run_file(conn, path)
        print("Done.")
    finally:
        conn.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
