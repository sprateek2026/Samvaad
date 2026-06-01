@echo off
REM Start Samvaad backend — binds on both IPv4 and IPv6 (no 2-second localhost delay)
cd /d %~dp0
python -m uvicorn app.main:app --host "::" --port 8000 --reload
