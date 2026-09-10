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
            Path(__file__).resolve().parent.parent.parent.parent.parent / "EvoCare-Knowledge-Base",
            Path(__file__).resolve().parent.parent.parent.parent / "knowledge-base",
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
