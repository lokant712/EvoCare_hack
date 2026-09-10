#!/usr/bin/env bash
# ==============================================================================
# EvoCare — One-Click Demo Startup Script (Linux / macOS)
# ==============================================================================

set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
cd "$DIR"

echo "============================================================================"
echo "  Starting EvoCare Longitudinal Health Memory & Clinical Reasoning Demo"
echo "============================================================================"

echo "[1/3] Ensuring directories..."
mkdir -p EvoCare/backend/data

echo "[2/3] Seeding Security & 5 Rich Demo Patients..."
python3 EvoCare/backend/scripts/seed_security_demo.py || true
python3 EvoCare/backend/scripts/seed_5_demo_patients.py || true

echo "[3/3] Starting Backend & Frontend..."

# Start backend
cd EvoCare/backend
python3 -m uvicorn app.main:app --host 127.0.0.1 --port 8000 &
BACKEND_PID=$!
cd "$DIR"

# Wait for backend
sleep 2

# Start frontend
cd frontend
npm run dev -- --port 9000 &
FRONTEND_PID=$!
cd "$DIR"

trap "kill $BACKEND_PID $FRONTEND_PID" EXIT

echo ""
echo "============================================================================"
echo "  EvoCare Services Running:"
echo "  - Frontend: http://localhost:9000"
echo "  - Backend API: http://127.0.0.1:8000"
echo "  - API Documentation: http://127.0.0.1:8000/docs"
echo ""
echo "  Demo Login Accounts:"
echo "  - Doctor (P001):    doctor.demo    / DoctorPass123!"
echo "  - Caregiver (P001): caregiver.demo / CaregiverPass123!"
echo "  - Doctor (P002):    doctor.other   / DoctorPass123!"
echo "  - Administrator:    admin.demo     / AdminPass123!"
echo "============================================================================"
echo "Press Ctrl+C to stop both services."

wait
