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
    "http://localhost:5173,http://localhost:3000"
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
    """Apply known pincode→ward fixes that may be absent from the initial seed.
    Uses INSERT OR IGNORE so it is fully idempotent — safe to run on every startup."""
    corrections = [
        ("411058", 32),   # Warje Malwadi was missing from pincode 411058 seed data
    ]
    try:
        from .database import get_connection
        conn = get_connection()
        try:
            # Remove duplicate (pin_code, ward_id) rows keeping the lowest id
            conn.execute("""
                DELETE FROM pincode_ward_mapping
                WHERE id NOT IN (
                    SELECT MIN(id) FROM pincode_ward_mapping GROUP BY pin_code, ward_id
                )
            """)
            # Ensure unique index exists so future inserts stay clean
            conn.execute("""
                CREATE UNIQUE INDEX IF NOT EXISTS idx_pincode_ward_unique
                ON pincode_ward_mapping(pin_code, ward_id)
            """)
            for pin, ward_num in corrections:
                ward = conn.execute(
                    "SELECT id FROM wards WHERE ward_number = ?", (ward_num,)
                ).fetchone()
                if ward:
                    conn.execute(
                        "INSERT OR IGNORE INTO pincode_ward_mapping (pin_code, ward_id) VALUES (?, ?)",
                        (pin, ward["id"])
                    )
            conn.commit()
            print("[seed] pincode corrections applied")
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
