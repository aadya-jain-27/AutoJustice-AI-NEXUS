#!/bin/bash
# ─────────────────────────────────────────────────────────────────
# AutoJustice AI NEXUS v2.0 — One-Click Setup & Run (Mac/Linux)
# Just run:  bash start.sh
# ─────────────────────────────────────────────────────────────────

set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "============================================================"
echo "  AutoJustice AI NEXUS v2.0"
echo "  AI-Driven Digital Forensics & Threat Triage Platform"
echo "============================================================"
echo ""

# ── Step 1: Find Python 3.11 / 3.12 / 3.13 ──────────────────────
PYTHON=""
for candidate in python3.12 python3.13 python3.11 python3; do
    if command -v "$candidate" &>/dev/null; then
        VERSION=$("$candidate" -c "import sys; print(sys.version_info.minor)" 2>/dev/null)
        MAJOR=$("$candidate" -c "import sys; print(sys.version_info.major)" 2>/dev/null)
        if [ "$MAJOR" = "3" ] && [ "$VERSION" -ge 11 ] && [ "$VERSION" -le 13 ]; then
            PYTHON="$candidate"
            break
        fi
    fi
done

# Fallback to whatever python3 is available
if [ -z "$PYTHON" ]; then
    if command -v python3 &>/dev/null; then
        PYTHON="python3"
        echo "  WARNING: Could not find Python 3.11-3.13."
        echo "  Using $(python3 --version) — may have compatibility issues."
        echo ""
    else
        echo "  ERROR: Python 3 not found."
        echo "  Install from: https://www.python.org/downloads/"
        exit 1
    fi
fi

echo "  Using: $PYTHON ($(${PYTHON} --version))"

# ── Step 2: Create virtual environment ───────────────────────────
VENV_DIR="$SCRIPT_DIR/.venv"
if [ ! -d "$VENV_DIR" ]; then
    echo "  Creating virtual environment..."
    "$PYTHON" -m venv "$VENV_DIR"
    echo "  Virtual environment created."
else
    echo "  Virtual environment already exists — skipping."
fi

# ── Step 3: Activate venv ─────────────────────────────────────────
source "$VENV_DIR/bin/activate"
VENV_PYTHON="$VENV_DIR/bin/python"

# ── Step 4: Install / upgrade dependencies ───────────────────────
echo ""
echo "  Checking dependencies..."
INSTALLED=$("$VENV_PYTHON" -c "import sqlalchemy; import fastapi; import passlib; import jose; import reportlab; print('ok')" 2>/dev/null || echo "missing")

if [ "$INSTALLED" != "ok" ]; then
    echo "  Installing packages from requirements.txt..."
    "$VENV_DIR/bin/pip" install --quiet --upgrade pip
    "$VENV_DIR/bin/pip" install --quiet -r requirements.txt
    # Ensure bcrypt 3.x — bcrypt 4.x breaks passlib 1.7.4 at startup
    "$VENV_DIR/bin/pip" install --quiet "bcrypt==3.2.2"
    echo "  All packages installed."
else
    # Check bcrypt version even if packages are already installed
    BCRYPT_VER=$("$VENV_PYTHON" -c "import bcrypt; print(bcrypt.__version__)" 2>/dev/null || echo "0")
    BCRYPT_MAJOR=$(echo "$BCRYPT_VER" | cut -d. -f1)
    if [ "$BCRYPT_MAJOR" -ge 4 ] 2>/dev/null; then
        echo "  Fixing bcrypt version (downgrading from $BCRYPT_VER to 3.2.2)..."
        "$VENV_DIR/bin/pip" install --quiet "bcrypt==3.2.2"
    fi
    echo "  All packages already installed."
fi

# ── Step 5: Check .env ───────────────────────────────────────────
if [ ! -f "$SCRIPT_DIR/backend/.env" ]; then
    echo ""
    echo "  WARNING: backend/.env not found — copying from .env.example"
    cp "$SCRIPT_DIR/.env.example" "$SCRIPT_DIR/backend/.env"
    echo "  Edit backend/.env and add your GEMINI_API_KEY for full AI features."
fi

# ── Step 6: Start the server ─────────────────────────────────────
echo ""
echo "  Starting server..."
echo ""
echo "  ┌────────────────────────────────────────────────────┐"
echo "  │  Citizen Portal    →  http://localhost:8000        │"
echo "  │  Track Case        →  http://localhost:8000/track  │"
echo "  │  Officer Login     →  http://localhost:8000/login  │"
echo "  │  Dashboard         →  http://localhost:8000/dashboard │"
echo "  │  API Docs          →  http://localhost:8000/api/docs │"
echo "  │                                                    │"
echo "  │  Login: admin / AutoJustice@2024!                  │"
echo "  └────────────────────────────────────────────────────┘"
echo ""
echo "  Press Ctrl+C to stop."
echo ""

cd "$SCRIPT_DIR/backend"
"$VENV_PYTHON" -m uvicorn main:app \
    --reload \
    --host 0.0.0.0 \
    --port 8000 \
    --log-level info
