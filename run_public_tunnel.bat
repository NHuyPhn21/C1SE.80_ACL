@echo off
title ACL - Cloudflare Public HTTPS Tunnel
echo ================================================================
echo   ACL - Public HTTPS Web Link (Cloudflare Quick Tunnel)
echo   Make sure run_production.bat is running on port 5000 first!
echo ================================================================

set "CF_EXE="
where cloudflared >nul 2>nul
if %errorlevel%==0 (
    set "CF_EXE=cloudflared"
) else if exist "%LOCALAPPDATA%\Microsoft\WinGet\Links\cloudflared.exe" (
    set "CF_EXE=%LOCALAPPDATA%\Microsoft\WinGet\Links\cloudflared.exe"
) else if exist "%ProgramFiles(x86)%\cloudflared\cloudflared.exe" (
    set "CF_EXE=%ProgramFiles(x86)%\cloudflared\cloudflared.exe"
) else if exist "%ProgramFiles%\cloudflared\cloudflared.exe" (
    set "CF_EXE=%ProgramFiles%\cloudflared\cloudflared.exe"
)

if "%CF_EXE%"=="" (
    echo [Init] cloudflared is not installed yet. Installing via winget...
    winget install --id Cloudflare.cloudflared -e --accept-package-agreements --accept-source-agreements
    if exist "%LOCALAPPDATA%\Microsoft\WinGet\Links\cloudflared.exe" (
        set "CF_EXE=%LOCALAPPDATA%\Microsoft\WinGet\Links\cloudflared.exe"
    ) else if exist "%ProgramFiles(x86)%\cloudflared\cloudflared.exe" (
        set "CF_EXE=%ProgramFiles(x86)%\cloudflared\cloudflared.exe"
    ) else if exist "%ProgramFiles%\cloudflared\cloudflared.exe" (
        set "CF_EXE=%ProgramFiles%\cloudflared\cloudflared.exe"
    ) else (
        set "CF_EXE=cloudflared"
    )
)

echo.
echo Starting HTTPS tunnel to http://127.0.0.1:5000 ...
echo Look for the box containing: https://xxxx-xxxx.trycloudflare.com
echo ================================================================
"%CF_EXE%" tunnel --url http://127.0.0.1:5000
pause
