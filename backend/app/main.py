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


@app.on_event("startup")
def startup():
    init_db()


@app.get("/health")
def health():
    return {"status": "ok", "version": "1.0.0"}
