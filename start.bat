@echo off
:: ─────────────────────────────────────────────────────────────────
:: AutoJustice AI NEXUS v2.0 — One-Click Setup & Run (Windows)
:: Double-click this file OR run:  start.bat
:: ─────────────────────────────────────────────────────────────────

echo ============================================================
echo   AutoJustice AI NEXUS v2.0
echo   AI-Driven Digital Forensics ^& Threat Triage Platform
echo ============================================================
echo.

cd /d "%~dp0"

:: ── Find Python ──────────────────────────────────────────────────
set PYTHON=
for %%v in (python3.12 python3.13 python3.11 python3 python) do (
    if not defined PYTHON (
        where %%v >nul 2>&1 && set PYTHON=%%v
    )
)

if not defined PYTHON (
    echo   ERROR: Python not found.
    echo   Download from: https://www.python.org/downloads/
    echo   Make sure to check "Add Python to PATH" during install.
    pause
    exit /b 1
)

echo   Using: %PYTHON%

:: ── Create virtual environment ───────────────────────────────────
if not exist ".venv" (
    echo   Creating virtual environment...
    %PYTHON% -m venv .venv
    echo   Done.
) else (
    echo   Virtual environment already exists.
)

:: ── Install dependencies ─────────────────────────────────────────
echo   Checking dependencies...
.venv\Scripts\python -c "import sqlalchemy, fastapi, passlib, jose, reportlab" >nul 2>&1
if errorlevel 1 (
    echo   Installing packages from requirements.txt...
    .venv\Scripts\pip install --quiet --upgrade pip
    .venv\Scripts\pip install --quiet -r requirements.txt
    echo   All packages installed.
) else (
    echo   All packages already installed.
)

:: ── Check .env ───────────────────────────────────────────────────
if not exist "backend\.env" (
    echo   Copying .env.example to backend\.env ...
    copy ".env.example" "backend\.env" >nul
    echo   Edit backend\.env and add your GEMINI_API_KEY for full AI.
)

:: ── Start server ─────────────────────────────────────────────────
echo.
echo   Starting server...
echo.
echo   Citizen Portal    -^>  http://localhost:8000
echo   Track Case        -^>  http://localhost:8000/track
echo   Officer Login     -^>  http://localhost:8000/login
echo   Dashboard         -^>  http://localhost:8000/dashboard
echo   API Docs          -^>  http://localhost:8000/api/docs
echo.
echo   Login: admin / AutoJustice@2024!
echo.
echo   Press Ctrl+C to stop.
echo.

cd backend
..\venv\Scripts\python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000 --log-level info
pause
