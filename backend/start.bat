@echo off
REM Start Samvaad backend on IPv4 127.0.0.1 to match the frontend's
REM VITE_API_URL (http://127.0.0.1:8000/api). On Windows, binding to "::"
REM makes the socket IPv6-only (IPV6_V6ONLY defaults to true), so IPv4
REM clients hitting 127.0.0.1 time out ~2s — the cause of the intermittent
REM "Loading dashboard..." that only resolved after many refreshes.
cd /d %~dp0
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
