"""
Root wrapper for EvoCare Phase 9 Final Verification Script.
Executes EvoCare/backend/scripts/verify_final.py.
"""
import sys
from pathlib import Path

# Add backend directory to sys.path
root_dir = Path(__file__).resolve().parent.parent
backend_script = root_dir / "EvoCare" / "backend" / "scripts" / "verify_final.py"

if not backend_script.exists():
    print(f"Error: Could not locate backend verification script at {backend_script}")
    sys.exit(1)

# Execute backend verification script
import runpy
runpy.run_path(str(backend_script), run_name="__main__")
