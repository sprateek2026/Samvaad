# Samvaad — Agent Instructions

## Project
AI-driven citizen grievance governance platform for Pune. Citizens register complaints with text/images, AI classifies & routes to corporators.

## Stack
- **Backend:** FastAPI (Python 3.14) + SQLite
- **Frontend:** React 19 + Vite 8 + **Tailwind CSS v3** (PostCSS JIT)
- **Maps:** MapLibre GL
- **Charts:** Recharts (BarChart, PieChart/donut, AreaChart, LineChart)
- **AI:** Hybrid rule engine → Ollama gemma3:4b fallback
- **i18n:** i18next with `en`/`mr`/`hi` JSON files
- **Icons:** lucide-react throughout

## Commands
```bash
# Backend
cd backend && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Frontend dev
cd frontend && npx vite --host 0.0.0.0 --port 5173

# Frontend lint
cd frontend && npm run lint

# Frontend build
cd frontend && npm run build

# Seed database (run once after clone)
cd tools && python seed_database.py

# Clean up extra wards & seed corporator names (run after clone if needed)
cd tools && python cleanup_and_seed.py && python seed_all_corporators.py

# Verify API endpoint (list categories)
python tools/verify_api.py /api/categories

# Verify sub-categories for a category
python tools/verify_api.py /api/categories/1/sub

# Verify all 41 wards with 4 corporators each
python tools/verify_api.py /api/admin/representatives
```

## URLs
- **API:** http://localhost:8000 | Swagger: http://localhost:8000/docs
- **Frontend:** http://localhost:5173
- **Health:** http://localhost:8000/health

## Deployment (Production)
- **Frontend → Vercel.** Stable shareable URL: **`https://samvaad-pune.vercel.app`** (always serves latest `main`). Root directory = `frontend`. `frontend/vercel.json` has the SPA rewrite (all routes → `index.html`).
  - **Immutable-URL gotcha:** every deploy also gets a frozen `samvaad-<hash>-...vercel.app` that serves that exact build forever — never share those. Only the production domain / `samvaad-git-main-...` auto-update.
  - **Vercel env vars are baked at BUILD time** — changing one requires a redeploy. Required: `VITE_API_URL=https://samvaad-production-52e5.up.railway.app/api`, `VITE_MAPTILER_API_KEY` (the map silently falls back to keyless OpenFreeMap via `src/mapStyle.js` if absent).
  - **Deployment Protection / Vercel Authentication** must be OFF (Settings → Deployment Protection) or visitors hit an SSO login wall.
- **Backend → Railway.** `https://samvaad-production-52e5.up.railway.app` (API under `/api`, health `/health`). Root = `backend`; Nixpacks detects Python via the **root** `requirements.txt`. Start cmd in `nixpacks.toml`. GitHub-connected; usually auto-deploys `main` but sometimes needs a manual **Deploy** from the Deployments tab.
- **GitHub:** `https://github.com/sprateek2026/Samvaad` — commit + push every change (clean messages, `Co-Authored-By: Claude`).
- **CORS:** `main.py` reads `ALLOWED_ORIGINS` (comma list) **and** an `allow_origin_regex` (default `https://samvaad[\w-]*\.vercel\.app`), so every Vercel URL for this project is accepted without editing the list. Override via `ALLOWED_ORIGIN_REGEX`.
- **MapTiler key** is domain-restricted in MapTiler Cloud (allowed origins must list each Vercel host: samvaad-pune, samvaad-gamma, git-main, `localhost:5173`, and `?` for no-Origin). A 403 on the style URL = the requesting domain isn't on that allow-list.
- **Persistence:** no Railway Volume = SQLite + uploads are ephemeral (wiped each redeploy), but auto-seed (below) re-creates reference data on boot — only user complaints/images would be lost. For durability add a Volume at `/data` with `DATABASE_PATH=/data/samvaad.db`, `UPLOAD_DIR=/data/uploads`.

## Gotchas

### Auth
- `DEV_MODE=true` (default in code, **not in `.env`**): any Bearer token accepted. Token format `dev-user-{mobile}` (e.g., `dev-user-9876543210`).
- Auth middleware (`backend/app/middleware/auth.py:10`) extracts UID via `authorization[7:]` (slices `"Bearer "` prefix). Do NOT split by `-` — breaks `dev-user-9876543210`.
- Firebase phone auth not wired; dev mode always on.

### Backend
- **Router must be defined:** `backend/app/routers/admin.py` line 11 requires `router = APIRouter()` at module level before any route decorators. Missing this causes `NameError: name 'router' is not defined` on startup.
- **Python 3.14+FastAPI quirk:** Synchronous `get_db()` generator dependency does NOT work with `async def` endpoints. All complaint/CRUD endpoints MUST be `def`, not `async def`. (`img.file.read()` instead of `await img.read()`.)
- `get_db()` is a bare generator WITHOUT `@contextmanager` decorator (causes `TypeError` in Python 3.14).
- DB schema (`init_db()` at startup) creates all tables if missing — no Alembic/migrations.
- **Auto-seed on startup:** `main.py` `_auto_seed_if_empty()` runs after `init_db()`. If `COUNT(*) FROM wards != 41` it runs the full chain (`seed_database.py` → `cleanup_and_seed.py` → `seed_all_corporators.py`) via **subprocess** with `PYTHONIOENCODING=utf-8`, converging on 41 wards + 247 named reps. Self-heals a fresh/stale DB (so Railway needs no manual seeding); skips when already at 41. Never raises — a seed failure can't block API boot. Requires committed `backend/data/pune-2022-wards.geojson`.
- GIS uses pure Python point-in-polygon (no SpatiaLite). GeoJSON coordinates are `[longitude, latitude]`.
- **Corporator dashboard shows wrong name:** `dashboard.py:76` queries `w.corporator_a_name` (static seed data from `wards` table) — must use `u.full_name` instead. Affects ALL corporators.
- **Admin ward dropdown sends internal `wards.id`:** `Admin.jsx:65` used `value={w.id}` (auto-increment) while displaying `#{w.ward_number}` — confusing mismatch. Fixed by sending `ward_number` and resolving to `wards.id` in `admin.py`.
- **PMC ward delimitation changed in 2025:** The original seed had 58 wards (older structure). Pune now has 41 wards per the 2025/2026 delimitation. Ward names in the DB may not match the new 2026 election area names exactly. The 164 corporator names are from the official 2026 results mapped by ward number.

### Frontend
- **No TypeScript** — plain JSX throughout. No NODE_ENV checks or route guards for auth state.
- **Design system:** `src/tokens.css` holds CSS custom properties (`--color-primary-*`, `--color-saffron-*`, `--status-*`, `--surface-*`, `--shadow-*`). `tailwind.config.js` extends Tailwind with these tokens so `bg-primary-600`, `text-saffron-500`, etc. all work.
- **UI atoms** in `src/components/ui/`: `KpiCard`, `StatusBadge`, `Sparkline`, `RepresentativeCard`, `PageHeader`, `NotificationDrawer`. Import from there — do NOT inline duplicate status badge logic in pages.
- **Login styling:** Split-layout — left 45% panel: `linear-gradient(160deg, #0d1b35 → #102a5c → #1a4a8a → #6b2206 → #c24a0a → #e8760e → #f5a31a)` with 0.18 overlay, Maharashtra bhagwa/saffron theme. Right 55% panel: white form with role selector, +91 mobile input, saffron OTP button, DEV MODE amber notice. `ShivajiIcon` SVG (three-tower fort) in government badge.
- **Layout (`src/components/Layout.jsx`):** Returns `<>{children}</>` when `user` is null (no navbar on login/register). Dark premium navbar: `linear-gradient(to right, #0f172a, #1e1b4b, #0f172a)`. Notification bell wired to `dashboardAPI.notifications()`. `EN | HI | MR` pill language toggle. Profile dropdown with avatar initials.
- Login flow: OTP screen (dev mode: any 6 digits) → checks `/auth/profile` → exists? redirects to dashboard. Doesn't exist? redirects to `/register`.
- `App.jsx` `handleLogin()` accepts either a token string or a full user object (for the redirect-after-register case).
- Register page extracts mobile from stored token (`token.replace("dev-user-", "")`).
- i18n JSON files in `src/i18n/` are copies from `backend/app/i18n/`. Add keys to both.
- **ComplaintTimeline** (`src/components/ComplaintTimeline.jsx`): Vertical timeline with emerald (done), indigo pulsing (current), gray (pending) nodes. Props: `status`, `statusLog`, `createdAt`. Filters out `assigned`/`escalated`/`closed` steps when not relevant.
- **CSS layer components** (in `src/index.css`): `.ds-card` (white card with shadow-card), `.page-content` (max-w-7xl mx-auto px-4 pt-6), `.kpi-indigo/saffron/emerald/gold/purple/rose` (gradient KPI cards), `.btn-primary`, `.btn-saffron`, `.btn-ghost`, `.btn-outline`, `.ds-input`, `.skeleton`, `.scrollbar-thin`.
- **chart.js / react-chartjs-2 removed** — Recharts is the only chart library. Do not re-add chart.js.

### Database
- Path: `backend/data/samvaad.db` (auto-created by config.py)
- Pre-seeded with 58 wards, 18 complaint categories, 211 sub-categories, 118 PIN→ward mappings, representative mappings.
- **After cleanup:** 41 administrative wards (Pune has exactly 41), 164 corporators (4 per ward: A/B/C/D labels), with names + party affiliations from the 2026 PMC election results.
- Ward seed originally had 58 entries — only wards 1–41 have `corporator_{a,b,c,d}_name` populated. Wards 42–58 are removed via `tools/cleanup_and_seed.py`.
- `tools/seed_all_corporators.py` populates all 4 slots from the official 2026 winner list (source: Free Press Journal, Jan 17 2026).
- `users.pin_code` is NOT NULL — admin user creation must include it.
- `config.py` `_cfg()` reads **real env vars first** (`os.environ`), then `.env` via `dotenv_values()`, then a default — so Railway dashboard vars like `DATABASE_PATH`/`UPLOAD_DIR` actually take effect (a plain `dotenv_values()`-only read silently ignored them). Default `DATABASE_PATH` is absolute (`BASE_DIR/data/samvaad.db`), so all three seed scripts + the backend resolve to the same file whether run from `tools/` or `backend/`.

### Shell Gotchas (PowerShell 5.1)
- **NEVER use `python -c "..."` for multi-line or quote-heavy code** — PowerShell's `\"` escaping inside `"` causes SyntaxErrors before Python even runs. Always use a temp file:
  ```powershell
  $tmp = "$env:TEMP\code.py"
  @"
  import requests
  r = requests.get('http://localhost:8000/path')
  print(r.json())
  "@ | Out-File $tmp -Encoding utf8
  python $tmp
  Remove-Item $tmp -Force
  ```
  (The here-string `@"..."@` must be on separate lines as shown — no inline content after `@`.)
- Use `python tools/verify_api.py [/path]` for quick API checks instead.

### Testing
- End-to-end API tests use `requests` from command line (no test framework configured).
- Verify with: health → register → create complaint (multipart) → list → get → update status → rate.
- GIS test: `POST /api/gis/locate {latitude:18.5073, longitude:73.8067}` → Ward 31 Kothrud.

### Python-dotenv
- `load_dotenv()` silently fails on Windows Python 3.14. `config.py` uses `dotenv_values()` from `python-dotenv` instead, with explicit `BASE_DIR` path.
- **MapMyIndia API key** in `.env` (`MAPMYINDIA_API_KEY`) is unused — OSM Nominatim replaced it since MapMyIndia requires OAuth2 client credentials.

### Address Autocomplete
- Uses OSM Nominatim (free, no key) via `backend/app/services/mapmyindia.py`. Proxy endpoint: `GET /api/gis/autocomplete?q=`. Returns `{suggestions: [{name, address, full, lat, lng}]}`.
