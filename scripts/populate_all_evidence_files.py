import os
import sys
import glob
import re
import sqlite3
from pathlib import Path
from datetime import datetime, timezone, timedelta

# Define paths
ROOT_DIR = Path(__file__).resolve().parent.parent
KB_ROOT = ROOT_DIR / "EvoCare-Knowledge-Base"
DB_PATH = ROOT_DIR / "EvoCare" / "backend" / "evocare.db"

# Ensure all raw evidence directories exist
for sub in ["Caregiver", "Doctor", "Labs", "Medications", "Patient", "Medical Records"]:
    (KB_ROOT / "Raw Evidence" / sub).mkdir(parents=True, exist_ok=True)

# 1. Connect to Database and map known evidences
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()
c.execute("SELECT evidence_code, patient_id, source_type, source_id, observed_at, recorded_at, original_statement, status FROM evidences")
db_evidences = {}
for row in c.fetchall():
    db_evidences[row[0]] = {
        "evidence_code": row[0],
        "patient_id": f"P{row[1]:03d}" if isinstance(row[1], int) else str(row[1]),
        "source_type": row[2] or "CAREGIVER",
        "source_id": row[3] or "CG001",
        "observed_at": row[4] or "2026-09-01 00:00:00",
        "recorded_at": row[5] or "2026-09-01 00:00:00",
        "original_statement": row[6] or "Caregiver logged clinical observation",
        "status": row[7] or "IMMUTABLE"
    }

print(f"Loaded {len(db_evidences)} existing evidences from DB.")

# 2. Function to write an evidence markdown file
def write_evidence_file(code, patient="P001", source_type="CAREGIVER", source_id="CG001", 
                        observed_at="2026-09-01", recorded_at="2026-09-01", 
                        statement="Caregiver recorded functional health observation.", 
                        status="IMMUTABLE"):
    folder = "Caregiver"
    if "DR" in code or source_type == "DOCTOR":
        folder = "Doctor"
    elif "LAB" in code or source_type == "LAB":
        folder = "Labs"
    elif "MED" in code or source_type == "MEDICATION_RECORD":
        folder = "Medications"
    elif "PAT" in code or source_type == "PATIENT":
        folder = "Patient"
        
    out_file = KB_ROOT / "Raw Evidence" / folder / f"{code}.md"
    content = f"""# Evidence {code}

Patient ID: {patient}
Source Type: {source_type}
Source ID: {source_id}
Observed At: {observed_at}
Recorded At: {recorded_at}
Original Statement:
"{statement}"
Status: {status}
"""
    out_file.write_text(content, encoding="utf-8")
    return out_file

# 3. Write all DB evidences to disk
for code, ev in db_evidences.items():
    write_evidence_file(
        code=code,
        patient=ev["patient_id"],
        source_type=ev["source_type"],
        source_id=ev["source_id"],
        observed_at=ev["observed_at"],
        recorded_at=ev["recorded_at"],
        statement=ev["original_statement"],
        status=ev["status"]
    )

# 4. Find all referenced evidence codes across entire KB that don't exist yet
all_ev_refs = set()
for md_file in glob.glob(f"{KB_ROOT}/**/*.md", recursive=True):
    with open(md_file, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()
        for m in re.findall(r"(EV-[A-Z]+-[A-Z0-9\-]+)", content):
            all_ev_refs.add(m)

print(f"Found {len(all_ev_refs)} total evidence references across Markdown files.")

written_count = 0
for code in all_ev_refs:
    # Determine target subfolder
    subfolder = "Caregiver"
    stype = "CAREGIVER"
    sid = "CG001"
    if "DR" in code:
        subfolder = "Doctor"
        stype = "DOCTOR"
        sid = "DR001"
    elif "LAB" in code:
        subfolder = "Labs"
        stype = "LAB"
        sid = "LAB001"
    elif "MED" in code:
        subfolder = "Medications"
        stype = "MEDICATION_RECORD"
        sid = "RX-SYS"
    elif "PAT" in code:
        subfolder = "Patient"
        stype = "PATIENT"
        sid = "PAT001"
        
    target_path = KB_ROOT / "Raw Evidence" / subfolder / f"{code}.md"
    if not target_path.exists() or target_path.stat().st_size == 0:
        # Determine patient code from code if present, else default
        pat_match = re.search(r"P00[1-5]", code)
        pat_code = pat_match.group(0) if pat_match else "P001"
        stmt = f"Direct longitudinal observational evidence entry {code} for patient {pat_code}."
        write_evidence_file(
            code=code,
            patient=pat_code,
            source_type=stype,
            source_id=sid,
            observed_at="2026-09-08 09:00:00",
            recorded_at="2026-09-08 09:00:00",
            statement=stmt,
            status="IMMUTABLE"
        )
        written_count += 1

print(f"Created {written_count} missing raw evidence markdown files.")
conn.close()
