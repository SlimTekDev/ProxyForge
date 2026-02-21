#!/usr/bin/env python3
"""
Run all hydrators against the database specified by an env file (e.g. .env.cloud).
Use this to populate your external/cloud DB before or after deploying to Streamlit Cloud.

Prerequisites (on this machine):
  - data/wahapedia/ with Wahapedia CSVs (for 40K)
  - data/opr/data.json (for OPR units)
  - data/opr/army_details.json (for OPR Army Book; from fetch_opr_json.py)

Usage:
  # Use .env.cloud (default) for DB credentials; run from repo root
  python scripts/run_hydrators_for_cloud.py

  # Use a different env file
  set PROXYFORGE_ENV_FILE=.env.remote
  python scripts/run_hydrators_for_cloud.py

  # Skip OPR or 40K (if data not present)
  python scripts/run_hydrators_for_cloud.py --skip-opr
  python scripts/run_hydrators_for_cloud.py --skip-40k

Important: The env file (e.g. .env.cloud) must contain MYSQL_HOST, MYSQL_USER,
MYSQL_PASSWORD, MYSQL_DATABASE for the external DB. Do not commit this file.
If you also have a .env in the repo with local DB credentials, the child scripts
will merge it when they run; to ensure only remote credentials are used, run
from a copy of the repo without .env, or point .env at the same remote DB.
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

try:
    from dotenv import dotenv_values
except ImportError:
    dotenv_values = None

REPO_ROOT = Path(__file__).resolve().parents[1]


def _load_env(env_file: str) -> dict:
    path = REPO_ROOT / env_file
    if not path.exists():
        raise SystemExit(f"Env file not found: {path}. Create it with MYSQL_* for the remote DB.")
    if dotenv_values is None:
        raise SystemExit("python-dotenv is required. pip install python-dotenv")
    values = dotenv_values(path)
    # Merge with current env so PATH etc. are preserved
    return {**os.environ, **{k: str(v) for k, v in values.items() if v is not None}}


def _run(env: dict, *cmd: str, optional: bool = False) -> bool:
    cmd_list = [sys.executable] + list(cmd)
    print(f"  Running: {' '.join(cmd_list)}")
    result = subprocess.run(cmd_list, cwd=REPO_ROOT, env=env)
    if result.returncode != 0 and not optional:
        print(f"  Failed with exit code {result.returncode}")
        return False
    return True


def main() -> int:
    ap = argparse.ArgumentParser(description="Run all hydrators for cloud DB (40K + OPR)")
    ap.add_argument("--env-file", default=os.environ.get("PROXYFORGE_ENV_FILE", ".env.cloud"),
                    help="Env file with MYSQL_* (default: .env.cloud or PROXYFORGE_ENV_FILE)")
    ap.add_argument("--skip-40k", action="store_true", help="Skip 40K Wahapedia hydrators")
    ap.add_argument("--skip-opr", action="store_true", help="Skip OPR hydrators")
    ap.add_argument("--dry-run", action="store_true", help="Only run 40K full hydrator with --dry-run")
    args = ap.parse_args()

    env = _load_env(args.env_file)
    print(f"Loaded env from {args.env_file} (MYSQL_HOST={env.get('MYSQL_HOST', '?')})")
    print()

    if not args.skip_40k:
        print("[1/4] Wahapedia full pipeline (40K)...")
        dry = ["--dry-run"] if args.dry_run else []
        if not _run(env, "scripts/wahapedia/hydrate_waha_full.py", *dry):
            return 1
        print()

        print("[2/4] Wahapedia datasheets extra (legend, loadout, transport)...")
        if not args.dry_run and not _run(env, "scripts/wahapedia/hydrate_waha_datasheets_extra.py"):
            return 1
        print()
    else:
        print("[1/4] [2/4] 40K skipped.")
        print()

    if not args.skip_opr:
        print("[3/4] OPR units (newest_hydrator)...")
        if not _run(env, "ProxyForge/newest_hydrator.py", optional=True):
            print("  (OPR data.json missing or error; continuing)")
        print()

        print("[4/4] OPR army detail (Army Book)...")
        if not _run(env, "scripts/opr/hydrate_opr_army_detail.py", optional=True):
            print("  (army_details.json missing or error; continuing)")
        print()
    else:
        print("[3/4] [4/4] OPR skipped.")
        print()

    print("Hydration run finished.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
