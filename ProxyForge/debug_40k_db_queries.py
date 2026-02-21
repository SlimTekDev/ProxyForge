"""
Run key 40K builder queries and print DB outputs. Use to verify joins and view results.

Run from ProxyForge:  python debug_40k_db_queries.py [list_id] [datasheet_id]
If list_id is omitted, uses the first 40K list. Optional datasheet_id for unit-detail queries.
"""

import sys
import os

# Run from ProxyForge directory
if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database_utils import get_db_connection
from w40k_roster import get_debug_query_results


def _pp(name, rows, err, max_rows=15):
    """Print a section: query name, row count, sample rows or error."""
    print("\n" + "=" * 60)
    print(f"  {name}")
    print("=" * 60)
    if err:
        print(f"  ERROR: {err}")
        return
    print(f"  Row count: {len(rows)}")
    if not rows:
        print("  (no rows)")
        return
    if isinstance(rows[0], dict):
        cols = list(rows[0].keys())
        print(f"  Columns: {cols}")
    else:
        print(f"  Columns: (tuple)")
    for row in rows[:max_rows]:
        if isinstance(row, dict):
            line = "  " + " | ".join(f"{k}={repr(row[k])[:40]}" for k in cols)
        else:
            line = "  " + str(row)
        print(line)
    if len(rows) > max_rows:
        print(f"  ... and {len(rows) - max_rows} more rows")


def main():
    list_id = int(sys.argv[1]) if len(sys.argv) > 1 else None
    datasheet_id = sys.argv[2] if len(sys.argv) > 2 else None

    conn = get_db_connection()

    # Resolve list_id from first 40K list if not provided
    if list_id is None:
        cur = conn.cursor(dictionary=True)
        cur.execute(
            "SELECT list_id FROM play_armylists WHERE game_system = '40K_10E' ORDER BY list_id LIMIT 1"
        )
        row = cur.fetchone()
        cur.close()
        if row:
            list_id = row["list_id"]
            print(f"  >> Using first 40K list_id = {list_id}")
        else:
            print("  No 40K list found. Create a list in the app or pass list_id.")
            conn.close()
            return

    sections = get_debug_query_results(conn, list_id, datasheet_id=datasheet_id)
    for sec in sections:
        _pp(sec["name"], sec["rows"], sec["error"], max_rows=20)

    print("\n" + "=" * 60)
    print("  Done. Use these outputs to verify joins and view logic.")
    print("=" * 60 + "\n")

    conn.close()


if __name__ == "__main__":
    main()
