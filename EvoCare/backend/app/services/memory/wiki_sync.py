import os
import re
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

from app.core.config import settings

logger = logging.getLogger(__name__)

PAGE_FILE_MAPPING = {
    "Mobility": "Caregiver/Mobility.md",
    "Falls": "Caregiver/Falls.md",
    "Dizziness": "Caregiver/Dizziness.md",
    "Cognition": "Caregiver/Cognition.md",
    "Nutrition": "Caregiver/Nutrition.md",
    "Sleep": "Caregiver/Sleep.md",
    "Pain": "Caregiver/Pain.md",
    "Behavior": "Caregiver/Behavior.md",
    "Medication Adherence": "Caregiver/Medication Adherence.md",
    "Patient Overview": "Patient Overview.md"
}

class WikiSynchronizer:
    @classmethod
    def get_wiki_root_dirs(cls) -> List[Path]:
        """
        Finds all active Knowledge Base Wiki directories.
        """
        candidates = [
            Path(settings.KNOWLEDGE_BASE_DIR),
            Path(__file__).resolve().parents[5] / "EvoCare-Knowledge-Base",
            Path(__file__).resolve().parents[4] / "knowledge-base",
            Path(__file__).resolve().parent.parent.parent / "knowledge-base"
        ]
        valid = []
        for p in candidates:
            if p.exists() and p.is_dir() and p not in valid:
                valid.append(p)
        return valid

    @classmethod
    def get_patient_wiki_path(cls, patient_code: str, memory_page: str) -> Optional[Path]:
        rel_subpath = PAGE_FILE_MAPPING.get(memory_page, f"Caregiver/{memory_page}.md")
        patient_folder_name = f"{patient_code} Meenakshi Raman" if patient_code == "P001" else patient_code

        for root in cls.get_wiki_root_dirs():
            wiki_target = root / "Patient Wiki" / patient_folder_name / rel_subpath
            if wiki_target.exists():
                return wiki_target
            # Check without Patient Wiki prefix
            direct_target = root / patient_folder_name / rel_subpath
            if direct_target.exists():
                return direct_target

        # Fallback to creating in primary root
        roots = cls.get_wiki_root_dirs()
        if roots:
            return roots[0] / "Patient Wiki" / patient_folder_name / rel_subpath
        return None

    @classmethod
    def read_page(cls, patient_code: str, memory_page: str) -> str:
        target_path = cls.get_patient_wiki_path(patient_code, memory_page)
        if not target_path or not target_path.exists():
            return f"# {memory_page}\n\n## Baseline\nHistorically normal.\n\n## Longitudinal Memory\nNo longitudinal entries yet.\n"
        with open(target_path, "r", encoding="utf-8") as f:
            return f.read()

    @classmethod
    def sync_memory_update(
        cls,
        patient_code: str,
        memory_page: str,
        version_number: int,
        previous_version: Optional[int],
        statement: str,
        evidence_ids: List[str],
        update_type: str,
        change_summary: str
    ) -> str:
        """
        Synchronizes a validated memory update into the Patient Wiki markdown file.
        Preserves all existing content, appends longitudinal memory claim, updates version banner and evidence list.
        """
        target_path = cls.get_patient_wiki_path(patient_code, memory_page)
        if not target_path:
            raise IOError(f"Could not locate Knowledge Base directory for patient {patient_code}")

        # Ensure parent directory exists
        target_path.parent.mkdir(parents=True, exist_ok=True)

        if target_path.exists():
            with open(target_path, "r", encoding="utf-8") as f:
                content = f.read()
        else:
            content = f"# Caregiver Observation Log: {memory_page}\n\n## Baseline\nHistorically normal.\n\n## Longitudinal Memory\n\n## Evidence\n"

        # 1. Update or Insert Longitudinal Memory Section
        evidence_links_inline = ", ".join([f"[[Raw Evidence/Caregiver/{ev}|{ev}]]" for ev in evidence_ids])
        new_memory_entry = f"- **Version {version_number}** ({datetime.now(timezone.utc).strftime('%Y-%m-%d')}): {statement} *(Evidence: {evidence_links_inline})*"

        if "## Longitudinal Memory" in content:
            content = re.sub(
                r"(## Longitudinal Memory\n)",
                rf"\1{new_memory_entry}\n",
                content,
                count=1
            )
        else:
            content += f"\n\n## Longitudinal Memory\n{new_memory_entry}\n"

        # 2. Append new Evidence IDs to Evidence section if not present
        for ev in evidence_ids:
            ev_link = f"- [[Raw Evidence/Caregiver/{ev}|{ev}]]"
            if ev not in content:
                if "## Evidence" in content:
                    content = re.sub(
                        r"(## Evidence\n)",
                        rf"\1{ev_link}\n",
                        content,
                        count=1
                    )
                else:
                    content += f"\n\n## Evidence\n{ev_link}\n"

        # 3. Update Memory Version Header / Footer
        version_banner = (
            f"\n---\n\n## Memory Version History\n"
            f"- **Current Memory Version**: {version_number}\n"
            f"- **Previous Version**: {previous_version if previous_version is not None else 1}\n"
            f"- **Last Synchronized**: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}\n"
            f"- **Update Type**: {update_type}\n"
            f"- **Change Summary**: {change_summary}\n"
        )

        if "## Memory Version History" in content:
            # Replace existing banner with updated one
            content = re.sub(r"\n---\n\n## Memory Version History[\s\S]*$", version_banner, content)
        else:
            content += version_banner

        # Write safely
        try:
            with open(target_path, "w", encoding="utf-8") as f:
                f.write(content)
            logger.info(f"Wiki successfully updated at {target_path} (Version {version_number})")
        except Exception as e:
            logger.error(f"Failed to write to Wiki file {target_path}: {e}")
            raise IOError(f"Wiki write failure: {str(e)}")

        return str(target_path)

    CATEGORY_TO_PAGE = {
        "mobility": "Mobility",
        "movement": "Mobility",
        "walking": "Mobility",
        "ambulation": "Mobility",
        "fall": "Falls",
        "falls": "Falls",
        "near_fall": "Falls",
        "dizziness": "Dizziness",
        "dizzy": "Dizziness",
        "vertigo": "Dizziness",
        "lightheaded": "Dizziness",
        "cognition": "Cognition",
        "confusion": "Cognition",
        "memory": "Cognition",
        "nutrition": "Nutrition",
        "appetite": "Nutrition",
        "meal": "Nutrition",
        "eating": "Nutrition",
        "sleep": "Sleep",
        "insomnia": "Sleep",
        "pain": "Pain",
        "knee": "Pain",
        "behavior": "Behavior",
        "mood": "Behavior",
        "medication": "Medication Adherence",
        "medication_adherence": "Medication Adherence"
    }

    @classmethod
    def append_caregiver_observation_row(
        cls,
        patient_code: str,
        category: str,
        observed_date_str: str,
        observer: str,
        raw_statement: str,
        functional_interpretation: str,
        evidence_code: str,
        extra_attributes: Optional[Dict[str, Any]] = None
    ) -> List[str]:
        """
        Appends an observation row into the existing Caregiver markdown file
        in all active wiki directories without creating new files.
        """
        cat_key = (category or "").lower().replace(" ", "_").strip()
        page_name = cls.CATEGORY_TO_PAGE.get(cat_key, "Mobility")
        rel_subpath = PAGE_FILE_MAPPING.get(page_name, f"Caregiver/{page_name}.md")
        patient_folder_name = f"{patient_code} Meenakshi Raman" if patient_code == "P001" else patient_code

        clean_stmt = raw_statement.replace("\n", " ").replace("|", "/").strip()
        clean_interp = functional_interpretation.replace("\n", " ").replace("|", "/").strip() if functional_interpretation else "Caregiver recorded home observation"
        evidence_link = f"- [[Raw Evidence/Caregiver/{evidence_code}|{evidence_code}]]"

        updated_paths = []
        for root in cls.get_wiki_root_dirs():
            candidates = [
                root / "Patient Wiki" / patient_folder_name / rel_subpath,
                root / patient_folder_name / rel_subpath
            ]
            for target_path in candidates:
                if target_path.exists() and target_path.is_file():
                    try:
                        content = target_path.read_text(encoding="utf-8")

                        # Inspect table header columns
                        header_match = re.search(r"(\|\s*Date\s*\|[^\n]+\|)", content)
                        col_count = 5
                        if header_match:
                            header_line = header_match.group(1)
                            # count pipes minus 1
                            col_count = len([c for c in header_line.split("|") if c.strip()])

                        if col_count >= 6:
                            # e.g. Dizziness: Date | Observer | Statement | Context | Details | Evidence ID
                            attrs = extra_attributes or {}
                            sev = attrs.get("severity", "Noted")
                            dur = attrs.get("duration", "Transient")
                            detail_str = f"Severity: {sev}<br>Duration: {dur}"
                            new_row = f"| **{observed_date_str}** | {observer} | *\"{clean_stmt}\"* | {clean_interp} | {detail_str} | [[Raw Evidence/Caregiver/{evidence_code}|{evidence_code}]] |"
                        else:
                            # 5 columns: Date | Observer | Statement | Interpretation | Evidence ID
                            new_row = f"| **{observed_date_str}** | {observer} | *\"{clean_stmt}\"* | {clean_interp} | [[Raw Evidence/Caregiver/{evidence_code}|{evidence_code}]] |"

                        # 1. Insert row into existing table
                        table_match = re.search(r"(\|\s*:?---.*?\n)((?:\|[^\n]+\n)+)", content)
                        if table_match:
                            full_table_rows = table_match.group(0)
                            if evidence_code not in full_table_rows:
                                updated_table = full_table_rows.rstrip("\n") + f"\n{new_row}\n"
                                content = content.replace(full_table_rows, updated_table, 1)
                        elif "## Chronological" in content:
                            content = re.sub(
                                r"(## Chronological[^\n]+\n)",
                                rf"\1\n{new_row}\n",
                                content,
                                count=1
                            )

                        # 2. Append to Evidence section if not already present
                        if evidence_code not in content:
                            if "## Evidence" in content:
                                content = re.sub(
                                    r"(## Evidence\n)",
                                    rf"\1{evidence_link}\n",
                                    content,
                                    count=1
                                )
                            else:
                                content += f"\n\n## Evidence\n{evidence_link}\n"

                        target_path.write_text(content, encoding="utf-8")
                        updated_paths.append(str(target_path))
                        logger.info(f"Appended observation row to existing Wiki file: {target_path}")

                        # Also ensure Raw Evidence markdown file exists on disk
                        ev_dir = root / "Raw Evidence" / "Caregiver"
                        ev_dir.mkdir(parents=True, exist_ok=True)
                        ev_file = ev_dir / f"{evidence_code}.md"
                        if not ev_file.exists() or ev_file.stat().st_size == 0:
                            ev_content = f"""# Evidence {evidence_code}

Patient ID: {patient_code}
Source Type: CAREGIVER
Source ID: {observer}
Observed At: {observed_date_str}
Recorded At: {observed_date_str}
Original Statement:
"{clean_stmt}"
Status: IMMUTABLE
"""
                            ev_file.write_text(ev_content, encoding="utf-8")
                    except Exception as e:
                        logger.error(f"Failed to append to Wiki file {target_path}: {e}")

        return updated_paths

