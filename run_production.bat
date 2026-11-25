@echo off
title ACL - Production Web Server (Port 5000)
echo ================================================================
echo   ACL - Automated Comic Localization (Single-Port Web Mode)
echo   Building React Frontend + Starting FastAPI on Port 5000...
echo ================================================================

echo [1/3] Building Frontend (frontend/dist)...
call npm --prefix frontend run build
if errorlevel 1 (
    echo [ERROR] Frontend build failed! Please check Node.js / npm.
    pause
    exit /b 1
)

if exist "venv\Scripts\python.exe" (
    set "PY_CMD=venv\Scripts\python.exe"
) else (
    set "PY_CMD=python"
)

if not exist "acl.db" (
    echo [2/3] Initializing SQLite database acl.db...
    "%PY_CMD%" setup_db.py
)

echo.
echo [3/3] Starting ACL Web Server at: http://127.0.0.1:5000
echo       (Keep this window open while using the app or tunnel)
echo ================================================================
"%PY_CMD%" -m uvicorn fastapi_app:app --host 127.0.0.1 --port 5000
pause
