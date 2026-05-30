"""
Step 1: Delete test data from our sessions
Step 2: Remove extra wards 42-58 (Pune has 41 wards)
Step 3: Bulk-insert corporator names from seed data into representatives table
"""
import sqlite3
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))
from app.config import DATABASE_PATH

DB = os.path.join(os.path.dirname(__file__), "..", "backend", DATABASE_PATH)
conn = sqlite3.connect(DB)
cur = conn.cursor()

# ── Step 1: Cleanup test data ──────────────────────────────────
print("=== Step 1: Cleanup test data ===")

# Delete test user Test C
cur.execute("DELETE FROM users WHERE id = 7 AND mobile = '9999999001'")
print(f"Deleted test user rows: {cur.rowcount}")

# ── Step 2: Remove extra wards (42-58) ─────────────────────────
print("\n=== Step 2: Remove extra wards 42-58 ===")

# Get internal IDs of wards with ward_number >= 42
cur.execute("SELECT id FROM wards WHERE ward_number >= 42")
extra_ids = [r[0] for r in cur.fetchall()]
print(f"Extra ward internal IDs: {extra_ids}")

if extra_ids:
    ids_str = ",".join(str(i) for i in extra_ids)

    cur.execute(f"DELETE FROM pincode_ward_mapping WHERE ward_id IN ({ids_str})")
    print(f"Deleted PIN mappings: {cur.rowcount}")

    cur.execute(f"DELETE FROM representative_mapping WHERE ward_id IN ({ids_str})")
    print(f"Deleted rep mappings: {cur.rowcount}")

    cur.execute(f"DELETE FROM representatives WHERE ward_id IN ({ids_str})")
    print(f"Deleted representatives: {cur.rowcount}")

    cur.execute(f"DELETE FROM complaints WHERE ward_id IN ({ids_str})")
    print(f"Deleted complaints: {cur.rowcount}")

    cur.execute(f"DELETE FROM users WHERE ward_id IN ({ids_str})")
    print(f"Deleted users: {cur.rowcount}")

    cur.execute(f"DELETE FROM wards WHERE ward_number >= 42")
    print(f"Deleted ward rows: {cur.rowcount}")

conn.commit()

# Verify ward count
cur.execute("SELECT COUNT(*) FROM wards")
print(f"\nWard count after cleanup: {cur.fetchone()[0]}")

# ── Step 3: Bulk-insert corporator A names ─────────────────────
print("\n=== Step 3: Bulk-insert corporator A names ===")

cur.execute("""
    SELECT id, ward_number, ward_name, corporator_a_name, corporator_a_party
    FROM wards
    WHERE corporator_a_name IS NOT NULL AND corporator_a_name != ''
    ORDER BY ward_number
""")
wards = cur.fetchall()
print(f"Wards with corporator_a data: {len(wards)}")

inserted = 0
skipped = 0
for row in wards:
    ward_id, ward_number, ward_name, name, party = row

    # Check if already exists
    existing = cur.execute(
        "SELECT id FROM representatives WHERE ward_id = ? AND type = 'corporator' AND label = 'A'",
        (ward_id,)
    ).fetchone()
    if existing:
        skipped += 1
        print(f"  SKIP Ward {ward_number}: {name} (already exists as id={existing[0]})")
        continue

    cur.execute(
        """INSERT INTO representatives (ward_id, type, name, party, label)
           VALUES (?, 'corporator', ?, ?, 'A')""",
        (ward_id, name.strip(), party.strip() if party else None)
    )
    inserted += 1
    print(f"  INSERT Ward {ward_number}: {name}")

# Also ensure representative_mapping exists for all 41 wards
cur.execute("""
    INSERT OR IGNORE INTO representative_mapping (ward_id, mla_name, mla_constituency, mp_name, mp_constituency)
    SELECT id, '', '', '', '' FROM wards
""")

conn.commit()
print(f"\nInserted: {inserted}, Skipped (already exist): {skipped}")

# Final summary
cur.execute("""
    SELECT w.ward_number, w.ward_name, r.name, r.party
    FROM representatives r
    JOIN wards w ON w.id = r.ward_id
    WHERE r.type = 'corporator' AND r.label = 'A'
    ORDER BY w.ward_number
""")
print("\n=== Final Representatives List ===")
for r in cur.fetchall():
    print(f"  Ward {r[0]} ({r[1]}): {r[2]} ({r[3] or 'no party'})")

conn.close()
print("\nDone!")
