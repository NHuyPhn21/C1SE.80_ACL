@echo off
title ACL - FastAPI Backend (Port 5000)
echo ========================================================
echo   ACL - Automated Comic Localization (FastAPI)
echo   Opening API on http://127.0.0.1:5000
echo   Swagger Docs: http://127.0.0.1:5000/docs
echo ========================================================

if exist "venv\Scripts\python.exe" (
    if not exist "acl.db" (
        echo [Init] Creating SQLite database acl.db...
        "venv\Scripts\python.exe" setup_db.py
    )
    "venv\Scripts\python.exe" -m uvicorn fastapi_app:app --reload --host 127.0.0.1 --port 5000
) else (
    if not exist "acl.db" (
        echo [Init] Creating SQLite database acl.db...
        python setup_db.py
    )
    python -m uvicorn fastapi_app:app --reload --host 127.0.0.1 --port 5000
)
pause
