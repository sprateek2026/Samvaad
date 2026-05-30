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
    """On a fresh database (e.g. a new Railway disk), populate ward, PIN,
    representative and category data so GIS lookups work — no manual shell
    commands needed. Idempotent: skips when wards already exist. Never raises,
    so a seeding problem can't stop the API from starting."""
    try:
        from .database import get_connection
        conn = get_connection()
        try:
            row = conn.execute("SELECT COUNT(*) FROM wards").fetchone()
            ward_count = row[0] if row else 0
        finally:
            conn.close()
        if ward_count > 0:
            return

        repo_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        seed_path = os.path.join(repo_root, "tools", "seed_database.py")
        if not os.path.exists(seed_path):
            print(f"[seed] script not found at {seed_path}; skipping auto-seed")
            return

        print("[seed] wards table empty — running auto-seed...")
        import importlib.util
        spec = importlib.util.spec_from_file_location("seed_database", seed_path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        mod.main()
        print("[seed] auto-seed complete")
    except BaseException as e:  # includes SystemExit from the seed script
        print(f"[seed] auto-seed skipped due to error: {e}")


@app.on_event("startup")
def startup():
    init_db()
    _auto_seed_if_empty()


@app.get("/health")
def health():
    return {"status": "ok", "version": "1.0.0"}
