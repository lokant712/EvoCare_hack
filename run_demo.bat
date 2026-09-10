@echo off
REM ============================================================================
REM EvoCare — One-Click Demo Startup Script (Windows)
REM Starts:
REM   1. EvoCare FastAPI Backend on port 8000
REM   2. EvoCare React / Vite Frontend on port 9000
REM ============================================================================

echo ============================================================================
echo   Starting EvoCare Longitudinal Health Memory and Clinical Reasoning Demo
echo ============================================================================

cd /d "%~dp0"

echo [1/3] Checking environment and directories...
if not exist "EvoCare\backend\data" mkdir "EvoCare\backend\data"

echo [2/3] Seeding Security and 5 Rich Demo Patients...
python EvoCare\backend\scripts\seed_security_demo.py
python EvoCare\backend\scripts\seed_5_demo_patients.py
if %ERRORLEVEL% NEQ 0 (
    echo [WARNING] Seed script exited with non-zero code. Continuing startup...
)

echo [3/3] Launching Backend and Frontend services...

REM Start backend in a new command window
start "EvoCare Backend API (Port 8000)" cmd /k "cd /d %~dp0EvoCare\backend && python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload"

REM Wait 2 seconds for backend to initialize
timeout /t 2 /nobreak >nul

REM Start frontend in a new command window
start "EvoCare Doctor Dashboard (Port 9000)" cmd /k "cd /d %~dp0frontend && npm run dev -- --port 9000"

echo.
echo ============================================================================
echo   EvoCare Services Running:
echo   - Frontend: http://localhost:9000
echo   - Backend API: http://127.0.0.1:8000
echo   - API Documentation: http://127.0.0.1:8000/docs
echo.
echo   Demo Login Accounts:
echo   - Doctor (P001):    doctor.demo    / DoctorPass123!
echo   - Caregiver (P001): caregiver.demo / CaregiverPass123!
echo   - Doctor (P002):    doctor.other   / DoctorPass123!
echo   - Administrator:    admin.demo     / AdminPass123!
echo ============================================================================
