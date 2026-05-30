# Samvaad — User Manual

**Samvaad** is the Government of Maharashtra's smart governance portal for Pune. It lets citizens report civic problems, track them to resolution, and connect with their elected representatives. This manual explains how to use the website for each type of user.

- **Live site:** https://samvaad-81g6pch15-sprateek2026-2855s-projects.vercel.app
- **Languages:** English (EN), Hindi (HI), Marathi (MR) — switch anytime using the language toggle in the top navigation bar.

---

## Table of Contents
1. [Who Uses Samvaad](#1-who-uses-samvaad)
2. [Logging In](#2-logging-in)
3. [Citizen Guide](#3-citizen-guide)
4. [Corporator Guide](#4-corporator-guide)
5. [Admin Guide](#5-admin-guide)
6. [Complaint Status Meanings](#6-complaint-status-meanings)
7. [Tips & Troubleshooting](#7-tips--troubleshooting)

---

## 1. Who Uses Samvaad

| Role | What they do |
|------|--------------|
| **Citizen** | Report civic complaints, submit suggestions, track progress, rate resolutions |
| **Corporator** | View and resolve complaints for their ward, monitor performance |
| **Admin** | Oversee all wards, manage representatives, view city-wide analytics |

---

## 2. Logging In

1. Open the site. You'll land on the **login page**.
2. **Choose your role** — Citizen, Corporator, or Admin (tap the matching button).
3. Enter your **10-digit mobile number** (the +91 prefix is shown for you).
4. Tap **Send OTP**.
5. On the next screen, enter the **6-digit OTP**.
   - The site currently runs in **DEV MODE** — no real SMS is sent. Enter **any 6 digits** (e.g. `123456`) to continue.
6. Tap **Sign In**.

**What happens next:**
- **Existing users** go straight to their dashboard.
- **New citizens** are taken to the **registration page** to set up their profile (see below).
- **Admin accounts** are created by the system authority — admins cannot self-register.

> Your session stays logged in even if you refresh the page. Use the **profile menu → Logout** (top right) to sign out.

---

## 3. Citizen Guide

### 3.1 First-Time Registration

After your first OTP login, complete your profile so complaints can be routed to the right ward:

1. **Full Name** — enter your name.
2. **PIN Code** — enter your 6-digit area PIN (e.g. `411038`).
   - A **locality dropdown** appears. Pick your locality to auto-fill your ward.
3. **Address** — start typing; pick from the **autocomplete suggestions**, or:
   - **Click on the map** to drop a pin at your exact location, **or**
   - Tap **📍 Detect My Location** to use GPS.
4. A green box confirms **Your Area** — your ward number, name, and your elected corporators / MLA / MP.
5. Tap **Confirm** to finish. You're taken to your dashboard.

### 3.2 The Citizen Dashboard

Your home screen shows:
- **KPI cards** — total complaints, pending, resolved, and your average rating.
- **Charts** — complaints by category, by status, and a 7-day trend.
- **Your representatives** — corporators, MLA, and MP for your ward.

### 3.3 Raising a Complaint

Tap **Raise Issue** in the top navigation. You'll choose between two options:

#### Option A — Report a Complaint
A guided **4-step wizard**:

1. **Category** — pick the type of issue (water, roads, electricity, waste, etc.). Use the **search box** to find it fast, or tap **Other**.
2. **Sub-issue** — choose the specific problem, or tap **Other — write my own**.
3. **Details:**
   - **Title** — a short summary (e.g. "Pothole near bus stop").
   - **Description** — up to 500 characters. Tap the **🎤 microphone** to dictate instead of typing (works in EN/HI/MR).
   - **Photos** — upload up to **5 images** as evidence.
   - **Location** — your GPS location is attached automatically; tap **Locate again** to refresh.
   - An **expected resolution time** (SLA) is shown.
4. **Done** — you get a **Complaint ID** (tap to copy it), an **AI classification** showing how the system categorized your issue with a confidence score, and your **resolution deadline**.

#### Option B — Submit a Suggestion
For ideas rather than problems (e.g. "Install more dustbins"). Just enter a **title** and **description** and submit. You'll receive a suggestion ID.

### 3.4 Tracking Your Complaints

- Tap **My Complaints** (top nav or profile menu) to see all your submissions.
- Click any complaint to open its **detail page**, which shows:
  - Category, priority, submission date, and SLA deadline.
  - A **progress timeline** (Submitted → Under Review → In Progress → Resolved).
  - Your description, photos, and the AI classification.

### 3.5 Rating a Resolution

Once a complaint is marked **Resolved**, open it and give a **1–5 star rating** on how well it was handled. Your feedback feeds into your corporator's satisfaction score.

---

## 4. Corporator Guide

When you log in as a **Corporator**, you land on your **ward dashboard**.

### 4.1 Your Dashboard
- **Header** shows your ward name and your name.
- **KPI cards:** total complaints, pending, resolved, satisfaction score, SLA compliance, and suggestions received.
- **Overdue alert:** a red banner warns you if any complaints have passed their SLA deadline.
- **Charts:** complaints by category, pending vs resolved, and a 30-day trend.
- **Heatmap:** a live map of your ward with colored dots marking complaint locations (color = status).
- **Recent complaints table:** click any title to open it.
- **Recent suggestions** from citizens in your ward.

### 4.2 Resolving a Complaint
1. Click a complaint from the recent list (or open it by ID).
2. Review the description, photos, location, and AI classification.
3. In the **Update Status** section, optionally add **remarks/notes**.
4. Tap a status button:
   - **Mark as Under Review** — you've seen it and are assessing it.
   - **Mark as In Progress** — work has started.
   - **Mark as Resolved** — the issue is fixed.
5. The citizen is notified and the timeline updates automatically.

---

## 5. Admin Guide

When you log in as an **Admin**, you get a city-wide view with two tabs.

### 5.1 Dashboard Tab
- **Filter by Ward** — view the whole city or drill into a single ward.
- **KPI cards:** total, pending, resolved, overdue, average resolution time, and SLA compliance.
- **Charts:** complaints by ward (or by category when filtered), pending vs resolved, and a 30-day trend.
- **Heatmap** of all complaint locations.
- **Insight cards:** total wards, active representatives, average satisfaction, resolution rate.
- **Recent complaints** table across all wards.

### 5.2 Representatives Tab
Manage the elected representatives for each ward.

1. **Select a ward** from the dropdown. Optionally **search by name/party** or **filter by party**.
2. Each ward has **4 corporator slots (A, B, C, D)** plus an **MLA** and an **MP**.
3. For each slot you can:
   - **➕ Add** — fill in name, party, (for corporators) the slot label, an optional **mobile number** (which creates a login for that corporator), and an optional **photo**.
   - **✏️ Edit** — update their details.
   - **🗑️ Delete** — remove the representative (asks for confirmation).
   - **ℹ️ Know Your Corporator (KYC)** — view a profile card with contact, term, constituency, bio, and achievements.
4. A **green dot** next to a name means they have a login account; a **yellow dot** means they don't yet.

---

## 6. Complaint Status Meanings

| Status | Meaning |
|--------|---------|
| **Submitted** | Received, awaiting review |
| **Under Review** | A corporator is assessing it |
| **In Progress** | Work is underway |
| **Resolved** | The issue has been fixed (citizen can now rate it) |
| **Escalated** | Past its deadline / raised to a higher level |
| **Closed** | Finalized |

The **SLA deadline** is the expected resolution date. Complaints past their deadline are flagged in red.

---

## 7. Tips & Troubleshooting

- **Change language anytime** — use the **EN / HI / MR** toggle in the top bar. The whole interface, including categories, updates instantly.
- **Stay logged in** — refreshing the page keeps you signed in. To switch users, log out from the profile menu first.
- **Page looks blank for a moment?** The site shows a brief loading spinner while it verifies your session — this is normal.
- **Can't find a complaint?** Use **My Complaints** (citizens) or the recent-complaints tables (corporator/admin). Each complaint has a unique ID you can copy and share.
- **Voice input not showing?** The microphone button only appears in browsers that support speech recognition (e.g. Chrome).
- **OTP not arriving?** The site is in DEV MODE — no SMS is sent. Enter **any 6 digits** to log in.

---

*For technical issues with the deployment, contact the system administrator.*
