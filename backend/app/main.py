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
    r"https://samvaad[\w-]*\.vercel\.app"
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
        "411058": [10, 32],
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


@app.on_event("startup")
def startup():
    init_db()
    _auto_seed_if_empty()
    _apply_pincode_corrections()


@app.get("/health")
def health():
    return {"status": "ok", "version": "1.0.0"}
