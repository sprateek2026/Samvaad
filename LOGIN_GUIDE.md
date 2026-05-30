# Samvaad — Login Guide

## Dev Mode

**No real SMS/Firebase auth required.** `DEV_MODE=true` is hardcoded — any Bearer token is accepted.

Token format: `dev-user-{mobile}` (e.g., `dev-user-9876543210`)

## Login Steps

1. Enter any 10-digit mobile number on the login screen
2. Enter **any 6 digits** as OTP (not validated)
3. The app calls `GET /api/auth/profile`:
   - **Profile exists** → redirects to role-appropriate dashboard
   - **Profile doesn't exist** → redirects to `/register` for new user signup

## Seeded Test Accounts

Run `python tools/seed_database.py` to create these accounts:

| Role | Mobile | Full Name | Redirect |
|------|--------|-----------|----------|
| Admin | `9999999998` | System Admin | `/admin` |
| Citizen | `9999999999` | E2E Test Citizen | `/` (citizen dashboard) |
| Citizen | `9876543210` | Test Citizen | `/` (citizen dashboard) |

> Corp: admin mobile `9888888881` (created via admin page)

## Role-Based Routing

Once logged in, `GET /api/auth/profile` returns a `role` field. The frontend dispatches at `/`:

- `role = "admin"` → Admin dashboard (`/admin`)
- `role = "corporator"` → Corporator dashboard (`/corporator`)
- `role = "citizen"` → Citizen dashboard (`/`)

Direct URL access also works: `/admin`, `/corporator`, `/raise`, etc.

## Creating a Corporator

Only an **admin** user can create corporators:

1. Login as admin (`9999999998` + any OTP)
2. Go to `/admin`
3. Fill in: full name, mobile, PIN code, select a ward from the dropdown
4. Submit — the new corporator user is created
5. The corporator can now login with their mobile + any OTP

> Note: The ward dropdown shows `Ward #{ward_number} — {ward_name}` but the backend stores it against the internal `wards.id` FK.

## MLA / MP

**No login or dashboard exists for MLA/MP roles.** The database schema only supports `citizen`, `corporator`, and `admin` roles. MLA/MP data is informational — stored as columns on `wards` and `representative_mapping` tables for display purposes only.
