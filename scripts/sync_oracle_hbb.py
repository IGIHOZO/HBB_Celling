#!/usr/bin/env python3
"""
Sync Oracle HBB customers -> PostgreSQL hbb_customers table.

Environment variables required (from .env):
  ORACLE_USER, ORACLE_PASSWORD, ORACLE_HOST, ORACLE_PORT, ORACLE_SERVICE_NAME
  DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT

Usage:
  python3 sync_oracle_hbb.py           # full sync
  python3 sync_oracle_hbb.py --dry-run # show count only
"""

import os
import sys
import argparse
from datetime import datetime
from typing import List, Tuple, Optional

def build_oracle_query(schema: str = "") -> str:
    """Build Oracle query with optional schema prefix for tables."""
    p = f"{schema}." if schema else ""
    return f"""
SELECT
    msisdn,
    product_name,
    product_code,
    customer_name,
    price_plan_order_date,
    rn
FROM (
    SELECT
        '250' || so.acc_nbr AS msisdn,
        pp.price_plan_name AS product_name,
        pp.price_plan_code AS product_code,
        c.cust_name AS customer_name,
        so.state_date AS price_plan_order_date,
        ROW_NUMBER() OVER (
            PARTITION BY so.acc_nbr
            ORDER BY so.state_date DESC
        ) AS rn
    FROM {p}subs_order so
    JOIN {p}subs s
        ON s.subs_id = so.subs_id
    JOIN {p}cust c
        ON c.cust_id = s.cust_id
    LEFT JOIN (
        SELECT
            subs_id,
            price_plan_id
        FROM (
            SELECT
                sui.subs_id,
                sui.price_plan_id,
                ROW_NUMBER() OVER (
                    PARTITION BY sui.subs_id
                    ORDER BY sui.eff_date DESC, sui.subs_upp_inst_id DESC
                ) AS rnk
            FROM {p}subs_upp_inst sui
            WHERE sui.eff_date < TRUNC(SYSDATE)
        )
        WHERE rnk = 1
    ) latest_sui
        ON latest_sui.subs_id = so.subs_id
    JOIN {p}price_plan pp
        ON pp.price_plan_id = NVL(latest_sui.price_plan_id, so.price_plan_id)
    WHERE so.state_date < TRUNC(SYSDATE)
      AND (
          UPPER(pp.price_plan_name) LIKE '%HOME%'
          OR UPPER(pp.price_plan_name) LIKE '%HBB%'
      )
)
WHERE rn = 1
ORDER BY price_plan_order_date DESC
"""

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def load_env(path: str = None) -> dict:
    """Read KEY=VALUE pairs from .env file."""
    env = {}
    if path is None:
        # Try project root relative to this script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(script_dir, "..", ".env")
    if not os.path.exists(path):
        print(f"[ERROR] .env not found at {path}")
        sys.exit(1)
    with open(path, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, val = line.split("=", 1)
                env[key.strip()] = val.strip()
    return env


def oracle_connect(env: dict):
    import oracledb
    user = env.get("ORACLE_USER")
    pw = env.get("ORACLE_PASSWORD")
    host = env.get("ORACLE_HOST", "").strip()
    port = env.get("ORACLE_PORT", "1521")
    service = env.get("ORACLE_SERVICE_NAME", "").strip()
    sid = env.get("ORACLE_SID", "").strip()
    db = env.get("ORACLE_DB", "CC").strip()

    if not user or not pw:
        raise ValueError("ORACLE_USER and ORACLE_PASSWORD must be set in .env")

    if not host:
        raise ValueError(
            "ORACLE_HOST is not set in .env.\n"
            "Add your Oracle server IP or hostname, e.g.:\n"
            "  ORACLE_HOST=10.20.30.40\n"
            "  ORACLE_HOST=oracle.mycompany.local"
        )

    # Try SERVICE_NAME first, then SID, then DB as fallback
    attempts = []
    if service:
        attempts.append(("SERVICE_NAME", f"{host}:{port}/{service}"))
    if sid:
        attempts.append(("SID", f"{host}:{port}:{sid}"))
    attempts.append(("SERVICE_NAME", f"{host}:{port}/{db}"))

    last_err = None
    for mode, dsn in attempts:
        print(f"[INFO] Trying Oracle {mode}: {user}@{dsn}")
        try:
            conn = oracledb.connect(user=user, password=pw, dsn=dsn)
            print(f"[INFO] Oracle connected via {mode}.")
            return conn
        except Exception as e:
            last_err = e
            msg = str(e)
            # Common errors: print hint
            if "ORA-12514" in msg or "not registered" in msg or "DPY-6001" in msg:
                print(f"[WARN] {mode} '{dsn.split('/')[-1] if '/' in dsn else dsn.split(':')[-1]}' not registered on listener.")
            elif "ORA-12541" in msg or "refused" in msg or "DPY-6005" in msg:
                print(f"[WARN] Cannot reach Oracle at {host}:{port} — check VPN/firewall.")
            else:
                print(f"[WARN] Connection failed: {e}")

    print(f"[ERROR] All Oracle connection attempts failed. Last error: {last_err}")
    print("[HINT] Verify ORACLE_SERVICE_NAME, ORACLE_SID, or ORACLE_DB in .env")
    raise last_err


def pg_connect(env: dict):
    import psycopg2
    conn = psycopg2.connect(
        dbname=env.get("DB_NAME"),
        user=env.get("DB_USER"),
        password=env.get("DB_PASSWORD"),
        host=env.get("DB_HOST", "localhost"),
        port=env.get("DB_PORT", "5432"),
    )
    print("[INFO] PostgreSQL connected.")
    return conn


def fetch_oracle_data(ora_conn, schema: str = "", dry_run: bool = False) -> Tuple[int, List[Tuple]]:
    query = build_oracle_query(schema)
    cursor = ora_conn.cursor()
    print("[INFO] Counting Oracle records ...")
    count_sql = f"SELECT COUNT(*) FROM ({query})"
    try:
        cursor.execute(count_sql)
        total = cursor.fetchone()[0]
        print(f"[INFO] Oracle records to sync: {total:,}")
    except Exception as e:
        msg = str(e)
        cursor.close()
        if "ORA-00942" in msg or "table or view does not exist" in msg:
            print(f"[ERROR] Oracle tables not found for schema '{schema or '(default)'}'.")
            print("[HINT] The tables (subs_order, subs, cust, subs_upp_inst, price_plan)")
            print("       may belong to a different schema. Add to .env:")
            print(f"         ORACLE_SCHEMA=OWNER_NAME")
            print("       Ask your DBA for the correct schema name.")
        else:
            print(f"[ERROR] Oracle count query failed: {e}")
        raise

    if dry_run:
        cursor.close()
        return total, []

    print("[INFO] Fetching Oracle records ...")
    cursor.execute(query)
    rows = cursor.fetchall()
    cursor.close()
    return total, rows


def sync_to_postgres(pg_conn, rows: List[Tuple]) -> dict:
    cur = pg_conn.cursor()
    stats = {"deleted": 0, "inserted": 0, "errors": 0}

    # 1. Clear existing hbb_customers data
    print("[INFO] Truncating hbb_customers ...")
    cur.execute("DELETE FROM hbb_customers;")
    stats["deleted"] = cur.rowcount
    print(f"[INFO] Deleted {stats['deleted']:,} old records.")

    # 2. Batch insert
    insert_sql = """
        INSERT INTO hbb_customers
            (msisdn, product_name, product_code, customer_name,
             price_plan_order_date, rn, created_at)
        VALUES (%s, %s, %s, %s, %s, %s, NOW())
    """

    batch_size = 5000
    for i in range(0, len(rows), batch_size):
        batch = rows[i : i + batch_size]
        try:
            cur.executemany(insert_sql, batch)
            pg_conn.commit()
            stats["inserted"] += len(batch)
            print(f"[INFO] Inserted batch {i+1}-{i+len(batch)} / {len(rows):,}")
        except Exception as e:
            pg_conn.rollback()
            stats["errors"] += len(batch)
            print(f"[ERROR] Batch {i}-{i+len(batch)} failed: {e}")

    cur.close()
    return stats


def main():
    parser = argparse.ArgumentParser(description="Sync HBB customers from Oracle to PostgreSQL")
    parser.add_argument("--dry-run", action="store_true", help="Count only, no import")
    parser.add_argument("--env", default=None, help="Path to .env file")
    args = parser.parse_args()

    env = load_env(args.env)

    t0 = datetime.now()
    print(f"[START] {t0.isoformat()}")

    # --- Oracle fetch ---
    ora_conn = oracle_connect(env)
    schema = env.get("ORACLE_SCHEMA", "").strip()
    total, rows = fetch_oracle_data(ora_conn, schema=schema, dry_run=args.dry_run)
    ora_conn.close()

    if args.dry_run:
        print(f"[DRY-RUN] Would import {total:,} records. Exiting.")
        return

    if not rows:
        print("[WARN] No records fetched from Oracle. Nothing to import.")
        return

    # --- PostgreSQL import ---
    pg_conn = pg_connect(env)
    stats = sync_to_postgres(pg_conn, rows)
    pg_conn.close()

    # --- Summary ---
    t1 = datetime.now()
    duration = (t1 - t0).total_seconds()
    print()
    print("=" * 50)
    print("           SYNC SUMMARY")
    print("=" * 50)
    print(f"  Duration            : {duration:.1f}s")
    print(f"  Oracle records      : {total:,}")
    print(f"  Deleted (PG)        : {stats['deleted']:,}")
    print(f"  Inserted (PG)       : {stats['inserted']:,}")
    print(f"  Errors              : {stats['errors']:,}")
    print("=" * 50)

    if stats["errors"] > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
