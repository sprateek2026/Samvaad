from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .database import init_db
from .config import UPLOAD_DIR
from .routers import auth, complaints, dashboard, gis, admin, categories, suggestions

app = FastAPI(title="Samvaad API", version="1.0.0")

import os

_raw_origins = os.environ.get(
    "ALLOWED_ORIGINS",
    "http://localhost:5173,http://localhost:5174,http://localhost:5175,http://localhost:3000"
)
_allowed_origins = [o.strip() for o in _raw_origins.split(",") if o.strip()]

# Match every Vercel URL for this project (immutable hash deploys, git-branch
# aliases, the production domain, and any samvaad*.vercel.app custom domain) so
# we don't have to list each one in ALLOWED_ORIGINS and redeploy. Override via
# ALLOWED_ORIGIN_REGEX if the frontend ever moves off *.vercel.app.
_origin_regex = os.environ.get(
    "ALLOWED_ORIGIN_REGEX",
    r"https://samvaad[\w-]*\.vercel\.app|http://localhost:\d+"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins,
    allow_origin_regex=_origin_regex,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])
app.include_router(complaints.router, prefix="/api/complaints", tags=["Complaints"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Dashboard"])
app.include_router(gis.router, prefix="/api/gis", tags=["GIS"])
app.include_router(admin.router, prefix="/api/admin", tags=["Admin"])
app.include_router(categories.router, prefix="/api/categories", tags=["Categories"])
app.include_router(suggestions.router, prefix="/api/suggestions", tags=["Suggestions"])


def _auto_seed_if_empty():
    """On a fresh database (e.g. a new Railway disk), populate the full Pune
    reference dataset so GIS lookups and representative lookups work — no manual
    shell commands needed. Runs the same three seed scripts as a local setup, in
    order, ending at the correct 41-ward delimitation with authoritative
    corporator/MLA/MP data. Idempotent (skips when wards already exist) and never
    raises, so a seeding problem can't stop the API from starting."""
    # PMC 2025/26 delimitation = 41 wards. Any other count (0 = fresh disk,
    # or 58 = base seed before cleanup) means the data is missing or stale, so
    # re-run the chain to converge on the correct state.
    EXPECTED_WARDS = 41
    try:
        from .database import get_connection
        conn = get_connection()
        try:
            row = conn.execute("SELECT COUNT(*) FROM wards").fetchone()
            ward_count = row[0] if row else 0
        finally:
            conn.close()
        if ward_count == EXPECTED_WARDS:
            return

        import subprocess
        import sys
        repo_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        tools_dir = os.path.join(repo_root, "tools")
        # Order matters: base seed (58 wards) -> trim to 41 + names -> authoritative reps.
        scripts = ["seed_database.py", "cleanup_and_seed.py", "seed_all_corporators.py"]
        # Force UTF-8 so the scripts' ✓/emoji prints can't crash on non-UTF-8 stdout.
        env = dict(os.environ, PYTHONIOENCODING="utf-8")

        print(f"[seed] wards={ward_count} (expected {EXPECTED_WARDS}) — running auto-seed chain...")
        for name in scripts:
            path = os.path.join(tools_dir, name)
            if not os.path.exists(path):
                print(f"[seed] {name} not found; skipping")
                continue
            result = subprocess.run(
                [sys.executable, path], env=env,
                capture_output=True, text=True, timeout=180,
            )
            if result.returncode == 0:
                print(f"[seed] {name} OK")
            else:
                print(f"[seed] {name} failed (rc={result.returncode}): "
                      f"{(result.stderr or '')[-600:]}")
        print("[seed] auto-seed chain complete")
    except BaseException as e:
        print(f"[seed] auto-seed skipped due to error: {e}")


def _apply_pincode_corrections():
    """Replace pincode→ward mapping with authoritative PMC 2025/26 data.
    Idempotent: skips if mapping already has the correct 60 rows keyed to ward 13
    for pincode 411001 (sentinel that old wrong data used wards 17-19).
    """
    # (pin_code, [ward_numbers]) — ward_number per 41-ward PMC 2025/26 delimitation
    CORRECT = {
        "411001": [13, 24],
        "411002": [23, 24],
        "411003": [8],
        "411004": [29],
        "411005": [12],
        "411006": [6],
        "411007": [7, 8],
        "411008": [9, 10],
        "411009": [27, 36],
        "411011": [24, 25],
        "411012": [8],
        "411013": [16, 17],
        "411014": [3, 5],
        "411015": [1, 2],
        "411016": [7, 12],
        "411019": [2],
        "411020": [8],
        "411021": [9, 10],
        "411023": [33],
        "411024": [33],
        "411025": [4],
        "411027": [8],
        "411028": [16],
        "411030": [25, 27],
        "411032": [3],
        "411036": [14],
        "411037": [20, 21],
        "411038": [10, 31],
        "411040": [17, 18],
        "411041": [34],
        "411042": [25, 26],
        "411043": [37],
        "411045": [9],
        "411046": [38],
        "411047": [3],
        "411048": [19, 40],
        "411051": [30],
        "411052": [30],
        "411057": [9],
        "411058": [32],
        "411060": [41],
        "411067": [1],
    }
    try:
        from .database import get_connection
        conn = get_connection()
        try:
            # Sentinel: if 411001 already maps to ward_number 13, data is correct
            sentinel = conn.execute(
                "SELECT 1 FROM pincode_ward_mapping pwm "
                "JOIN wards w ON w.id = pwm.ward_id "
                "WHERE pwm.pin_code = '411001' AND w.ward_number = 13"
            ).fetchone()
            if sentinel:
                # Still enforce unique index to keep DB clean
                conn.execute("""
                    CREATE UNIQUE INDEX IF NOT EXISTS idx_pincode_ward_unique
                    ON pincode_ward_mapping(pin_code, ward_id)
                """)
                conn.commit()
                return

            # Full replacement with correct data
            conn.execute("DELETE FROM pincode_ward_mapping")
            count = 0
            for pin, ward_nums in CORRECT.items():
                for wn in ward_nums:
                    ward = conn.execute(
                        "SELECT id FROM wards WHERE ward_number = ?", (wn,)
                    ).fetchone()
                    if ward:
                        conn.execute(
                            "INSERT OR IGNORE INTO pincode_ward_mapping (pin_code, ward_id) VALUES (?, ?)",
                            (pin, ward["id"])
                        )
                        count += 1
            conn.execute("""
                CREATE UNIQUE INDEX IF NOT EXISTS idx_pincode_ward_unique
                ON pincode_ward_mapping(pin_code, ward_id)
            """)
            conn.commit()
            print(f"[seed] pincode mapping replaced: {count} rows")
        finally:
            conn.close()
    except Exception as e:
        print(f"[seed] pincode corrections skipped: {e}")


def _seed_complaints_if_empty():
    """Seed 30 sample complaints on a fresh DB where wards are already present
    but no complaints exist (e.g. Railway after auto-seed ran in a previous boot).
    Idempotent — skips when any complaint exists."""
    try:
        from .database import get_connection
        conn = get_connection()
        try:
            count = conn.execute("SELECT COUNT(*) FROM complaints").fetchone()[0]
        finally:
            conn.close()
        if count > 0:
            return

        import subprocess
        import sys
        repo_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        seed_script = os.path.join(repo_root, "tools", "seed_database.py")
        if not os.path.exists(seed_script):
            print("[seed] seed_database.py not found; skipping complaint seed")
            return
        env = dict(os.environ, PYTHONIOENCODING="utf-8")
        result = subprocess.run(
            [sys.executable, seed_script], env=env,
            capture_output=True, text=True, timeout=120,
        )
        if result.returncode == 0:
            print("[seed] sample complaints seeded OK")
        else:
            print(f"[seed] complaint seed failed: {(result.stderr or '')[-400:]}")
    except BaseException as e:
        print(f"[seed] complaint seed skipped: {e}")


def _seed_suggestions_if_empty():
    """Seed sample suggestions on a fresh/existing DB where none exist yet.
    Idempotent — skips when any suggestion exists."""
    SAMPLE = [
        ("Install more dustbins near FC Road",
         "The footpath area near FC Road has very few dustbins. People end up littering. Requesting PMC to install at least 5 more bins along the 500m stretch.", 5),
        ("Dedicated cycling lane on Baner Road",
         "With rising traffic, a dedicated cycling track on Baner Road would encourage greener commute and reduce road accidents involving cyclists.", 8),
        ("Solar lights for Saras Baug garden",
         "The garden is dark after sunset. Installing solar-powered lights would make it safer for evening walkers and families.", 3),
        ("Free Wi-Fi at PMC ward office",
         "Most citizens visit the ward office for document work. Providing free Wi-Fi would help them fill online forms and reduce paper usage.", 6),
        ("Rainwater harvesting mandate for new buildings",
         "PMC should make rainwater harvesting mandatory for any new construction above 300 sqm to help recharge groundwater.", 10),
        ("Community composting centre near vegetable market",
         "A centralised composting unit near Mandai market would turn daily vegetable waste into useful manure for city gardens.", 4),
        ("Digital display boards for bus arrival times",
         "Adding real-time PMPML bus arrival display boards at major stops like Shivajinagar and Deccan would improve public transport usage.", 7),
    ]
    try:
        from .database import get_connection
        from datetime import datetime, timedelta
        conn = get_connection()
        try:
            count = conn.execute("SELECT COUNT(*) FROM suggestions").fetchone()[0]
            if count > 0:
                return

            citizen = conn.execute(
                "SELECT id, ward_id FROM users WHERE firebase_uid IN ('dev-user-001','dev-user-9999999999') LIMIT 1"
            ).fetchone()
            if not citizen:
                return

            now = datetime.utcnow()
            inserted = 0
            for title, description, days_ago in SAMPLE:
                created = (now - timedelta(days=days_ago)).strftime("%Y-%m-%d %H:%M:%S")
                conn.execute(
                    "INSERT OR IGNORE INTO suggestions (citizen_id, ward_id, title, description, created_at) VALUES (?, ?, ?, ?, ?)",
                    (citizen["id"], citizen["ward_id"], title, description, created)
                )
                inserted += 1
            conn.commit()
            print(f"[seed] seeded {inserted} sample suggestion(s)")
        finally:
            conn.close()
    except Exception as e:
        print(f"[seed] suggestion seed skipped: {e}")


def _backfill_complaint_coords():
    """One-time backfill: update seeded complaints that have NULL coords.
    Idempotent — UPDATE WHERE location_lat IS NULL touches nothing once done."""
    COORDS = {
        "PMC-20260515-0001": (18.5195, 73.8553), "PMC-20260516-0002": (18.5158, 73.8630),
        "PMC-20260517-0003": (18.5308, 73.8475), "PMC-20260518-0004": (18.5210, 73.8600),
        "PMC-20260519-0005": (18.5590, 73.7876), "PMC-20260520-0006": (18.5180, 73.8553),
        "PMC-20260520-0007": (18.5074, 73.8477), "PMC-20260521-0008": (18.5308, 73.8475),
        "PMC-20260521-0009": (18.4980, 73.8280), "PMC-20260522-0010": (18.4973, 73.8209),
        "PMC-20260522-0011": (18.5143, 73.8580), "PMC-20260523-0012": (18.4996, 73.8358),
        "PMC-20260523-0013": (18.5282, 73.8431), "PMC-20260524-0014": (18.5590, 73.8076),
        "PMC-20260524-0015": (18.5238, 73.8475), "PMC-20260525-0016": (18.5504, 73.8727),
        "PMC-20260525-0017": (18.5195, 73.8605), "PMC-20260526-0018": (18.5143, 73.8490),
        "PMC-20260526-0019": (18.6298, 73.7997), "PMC-20260527-0020": (18.5018, 73.9260),
        "PMC-20260527-0021": (18.5250, 73.8650), "PMC-20260527-0022": (18.5679, 73.9143),
        "PMC-20260528-0023": (18.5093, 73.9308), "PMC-20260528-0024": (18.4528, 73.8601),
        "PMC-20260528-0025": (18.5188, 73.8559), "PMC-20260529-0026": (18.5509, 73.9489),
        "PMC-20260529-0027": (18.5988, 73.7616), "PMC-20260530-0028": (18.4860, 73.8267),
        "PMC-20260530-0029": (18.5074, 73.8053), "PMC-20260531-0030": (18.5204, 73.8567),
    }
    try:
        from .database import get_connection
        conn = get_connection()
        try:
            updated = 0
            for cid, (lat, lng) in COORDS.items():
                cur = conn.execute(
                    "UPDATE complaints SET location_lat=?, location_lng=? WHERE complaint_id=? AND location_lat IS NULL",
                    (lat, lng, cid)
                )
                updated += cur.rowcount
            if updated:
                conn.commit()
                print(f"[seed] backfilled coords for {updated} complaint(s)")
        finally:
            conn.close()
    except Exception as e:
        print(f"[seed] coord backfill skipped: {e}")


@app.on_event("startup")
def startup():
    init_db()
    _auto_seed_if_empty()
    _apply_pincode_corrections()
    _seed_complaints_if_empty()
    _seed_suggestions_if_empty()
    _backfill_complaint_coords()


@app.get("/health")
def health():
    return {"status": "ok", "version": "1.0.0"}
