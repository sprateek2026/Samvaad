# Samvaad — User Guide

**Samvaad** ("conversation/dialogue") is the citizen grievance portal for Pune, Government of Maharashtra. Citizens raise civic complaints and suggestions; the system classifies them and routes them to the right ward corporator, and everyone can track progress to resolution.

- **Live app:** https://samvaad-pune.vercel.app
- **Languages:** English, हिंदी (Hindi), मराठी (Marathi) — switch any time using the **EN | HI | MR** toggle in the top bar.

---

## 1. Who uses Samvaad

| Role | What they do |
|------|--------------|
| **Citizen** | Register complaints & suggestions, track status, rate resolutions, see their ward representatives. |
| **Corporator** | See complaints for their ward, update status, view citizen suggestions, monitor a ward heatmap. |
| **Admin** | Oversee all complaints city-wide, manage representatives, review all suggestions, view the city heatmap. |

---

## 2. Logging in

1. Open the app and you'll land on the **Login** page.
2. **Select your role** — Citizen, Corporator, or Admin (required).
3. Enter your **10-digit mobile number** (the `+91` prefix is fixed).
4. Click **Send OTP**.
5. Enter the **6-digit OTP** and click **Sign In**.
   - **Demo / DEV mode:** the app currently accepts **any 6 digits** as a valid OTP (shown by the amber notice on the login screen).
6. After sign-in:
   - If your profile already exists → you go to your dashboard.
   - If it's your first time (citizen) → you're taken to **Register** to complete your details.

**Logging out:** click your avatar (top-right) → **Logout**.

---

## 3. Citizen guide

### 3.1 Registering (first-time citizens)
After your first OTP sign-in, fill in:
- Full name
- PIN code (used to find your ward) — and confirm your **ward**
- Any other requested profile details

Your ward determines which corporator your complaints are routed to.

### 3.2 Your dashboard
The citizen dashboard shows:
- A greeting and your current **ward** (with a **Change** option).
- **KPI cards:** Total, Pending, Resolved, and your average satisfaction rating. Click a card to filter your complaints.
- **Your representatives:** corporators, MLA, and MP for your ward.
- **Charts:** status breakdown, 7-day activity trend, complaints by category.
- **Recent Complaints** list.
- **My Suggestions** list (the ideas you've submitted).

### 3.3 Raising a complaint
Click **Raise Complaint** (top bar or dashboard). A 4-step wizard guides you:

1. **Category** — pick the issue type (e.g. Water, Roads, Garbage), or search, or choose **Other**.
2. **Sub-issue** — pick the specific sub-category (or "Other — write your own").
3. **Details** — add a **title** and **description**, attach **photos** (optional), and set the **location**:
   - Tap **Detect location** to use GPS, or enter/adjust the address.
4. **Done** — review and submit. You'll receive a **Complaint ID** (e.g. `PMC-20260609-0001`) — note it to track your complaint.

### 3.4 Tracking & rating
- Go to **My Complaints** (top bar) or **View all** on the dashboard.
- Open any complaint to see its **timeline** and current **status**.
- When a complaint is marked **Resolved**, you can **rate** the resolution (this feeds your satisfaction score).

### 3.5 Submitting a suggestion
Suggestions are ideas for civic improvement (not problems to fix).
1. Click **Raise Complaint**, then choose **Submit a Suggestion**.
2. Enter a **title** and **description**, then submit.
3. Your suggestion appears under **My Suggestions** on your dashboard, and is visible to your corporator and the admin.

### 3.6 Changing your ward
If your ward is wrong, click **Change** next to your ward on the dashboard → enter your PIN code → **Find wards** → select the correct ward → **Save**.

---

## 4. Corporator guide

After logging in as **Corporator**, your dashboard shows complaints **for your ward**:
- **KPIs and charts** summarising your ward's complaints by status and category.
- A **heatmap** of complaint locations across your ward.
- The **complaint list** for your ward — open any complaint to:
  - View full details, photos, and the citizen's location.
  - **Update the status** as you work the issue (see status meanings in §6).
- **Suggestions** submitted by citizens in your ward.

---

## 5. Admin guide

After logging in as **Admin**, you get a city-wide view:
- **Dashboard:** overall complaint statistics and a **city heatmap** (every complaint is placed on the map; complaints without GPS are shown at their ward centre).
- **Representatives:** manage corporators / MLAs / MPs (including profile photos).
- **Suggestions:** review **all** citizen suggestions across Pune.

> Tip: if the dashboard ever looks empty right after a deploy, the backend re-seeds reference data automatically on startup — give it a moment and refresh.

---

## 6. Complaint status meanings

| Status | Meaning |
|--------|---------|
| **Submitted** | Received, awaiting review. |
| **Under review** | Being assessed by the ward team. |
| **Assigned** | Allocated to a corporator/department. |
| **In progress** | Work is underway. |
| **Escalated** | Raised to a higher authority (e.g. overdue). |
| **Resolved** | Fixed — you can now rate it. |
| **Closed** | Completed and closed out. |
| **Reopened** | Re-opened after being resolved/closed. |

---

## 7. Tips & FAQ

- **Switch language any time** with the EN | HI | MR toggle — it applies across the whole app.
- **Keep your Complaint ID** to look up status quickly.
- **Add photos** to complaints — they help corporators understand and prioritise the issue.
- **Wrong representatives showing?** Check your ward is correct (dashboard → **Change**).
- **Map not loading?** It will fall back to a basic map automatically; complaint pins still appear.
- **"Could not get location" on first try?** Allow location permission and retry — GPS sometimes needs a second attempt.

---

*Government of Maharashtra · Pune Municipal Corporation · Samvaad — Smart Governance Portal*
