@echo off
title ACL - FastAPI Backend
echo ========================================================
echo   ACL - Automated Comic Localization (FastAPI)
echo   Opening API on http://localhost:8000
echo ========================================================
python -m uvicorn fastapi_app:app --reload --host 127.0.0.1 --port 8000
pause
