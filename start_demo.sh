#!/bin/bash
# ─────────────────────────────────────────────────────────────────
# AutoJustice AI NEXUS v2.0 — Demo Mode (pre-loaded with sample cases)
# Just run:  bash start_demo.sh
# ─────────────────────────────────────────────────────────────────

set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "============================================================"
echo "  AutoJustice AI NEXUS v2.0 — DEMO MODE"
echo "  Loading sample cases for demonstration..."
echo "============================================================"
echo ""

# ── Find Python (same logic as start.sh) ─────────────────────────
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

if [ -z "$PYTHON" ]; then
    if command -v python3 &>/dev/null; then
        PYTHON="python3"
    else
        echo "  ERROR: Python 3 not found."
        exit 1
    fi
fi

echo "  Using: $PYTHON ($(${PYTHON} --version))"

# ── Create & activate venv ────────────────────────────────────────
VENV_DIR="$SCRIPT_DIR/.venv"
if [ ! -d "$VENV_DIR" ]; then
    echo "  Creating virtual environment..."
    "$PYTHON" -m venv "$VENV_DIR"
fi

source "$VENV_DIR/bin/activate"
VENV_PYTHON="$VENV_DIR/bin/python"

# ── Install dependencies ──────────────────────────────────────────
INSTALLED=$("$VENV_PYTHON" -c "import sqlalchemy; import fastapi; import passlib; import jose; import reportlab; print('ok')" 2>/dev/null || echo "missing")
if [ "$INSTALLED" != "ok" ]; then
    echo "  Installing packages..."
    "$VENV_DIR/bin/pip" install --quiet --upgrade pip
    "$VENV_DIR/bin/pip" install --quiet -r requirements.txt
    # Ensure bcrypt 3.x — bcrypt 4.x breaks passlib 1.7.4 at startup
    "$VENV_DIR/bin/pip" install --quiet "bcrypt==3.2.2"
    echo "  Done."
else
    BCRYPT_VER=$("$VENV_PYTHON" -c "import bcrypt; print(bcrypt.__version__)" 2>/dev/null || echo "0")
    BCRYPT_MAJOR=$(echo "$BCRYPT_VER" | cut -d. -f1)
    if [ "$BCRYPT_MAJOR" -ge 4 ] 2>/dev/null; then
        echo "  Fixing bcrypt version (downgrading from $BCRYPT_VER to 3.2.2)..."
        "$VENV_DIR/bin/pip" install --quiet "bcrypt==3.2.2"
    fi
fi

# ── Train ML models if not already trained ────────────────────────
ML_MODELS_DIR="$SCRIPT_DIR/backend/ml/models"
if [ ! -f "$ML_MODELS_DIR/fake_detector.pkl" ]; then
    echo "  Training ML models (first run only, takes ~30 seconds)..."
    cd "$SCRIPT_DIR/backend/ml"
    "$VENV_PYTHON" train.py
    cd "$SCRIPT_DIR"
    echo "  ML models trained and saved."
else
    echo "  ML models: already trained."
fi

# ── Check .env ────────────────────────────────────────────────────
if [ ! -f "$SCRIPT_DIR/backend/.env" ]; then
    cp "$SCRIPT_DIR/.env.example" "$SCRIPT_DIR/backend/.env"
fi

# ── Delete old DB so demo seeds fresh ────────────────────────────
if [ -f "$SCRIPT_DIR/backend/autojustice.db" ]; then
    echo "  Removing old database for fresh demo..."
    rm "$SCRIPT_DIR/backend/autojustice.db"
fi

# ── Seed demo data ────────────────────────────────────────────────
echo "  Seeding demo cases..."
cd "$SCRIPT_DIR/backend"
"$VENV_PYTHON" "../demo_seed.py" 2>&1 | tail -5
cd "$SCRIPT_DIR"

echo ""
echo "  Demo data loaded!"
echo ""
echo "  Starting server..."
echo ""
echo "  ┌────────────────────────────────────────────────────────┐"
echo "  │  Citizen Portal    →  http://localhost:8000            │"
echo "  │  Track Case        →  http://localhost:8000/track      │"
echo "  │  Officer Login     →  http://localhost:8000/login      │"
echo "  │  Dashboard         →  http://localhost:8000/dashboard  │"
echo "  │  API Docs          →  http://localhost:8000/api/docs   │"
echo "  │                                                        │"
echo "  │  Login: admin / AutoJustice@2024!                      │"
echo "  │  Demo has 15 pre-loaded cases across all risk levels   │"
echo "  └────────────────────────────────────────────────────────┘"
echo ""
echo "  Press Ctrl+C to stop."
echo ""

cd "$SCRIPT_DIR/backend"
"$VENV_PYTHON" -m uvicorn main:app \
    --reload \
    --host 0.0.0.0 \
    --port 8000 \
    --log-level info
