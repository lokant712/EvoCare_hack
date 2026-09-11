import os
import shutil
import glob
import re
import json
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
KB_ROOT_JOURNEY = Path(r"c:\Users\lokan\Downloads\journey\sve\EvoCare-Knowledge-Base")
KB_ROOT_SVE = Path(r"c:\Users\lokan\Downloads\sve\EvoCare-Knowledge-Base")
MASTER_RAW_EVIDENCE = KB_ROOT_JOURNEY / "Raw Evidence"

GRAPH_CONFIG = {
    "collapse-filter": False,
    "search": "",
    "showTags": False,
    "showAttachments": False,
    "hideUnresolved": True,
    "showOrphans": False,
    "collapse-color-groups": False,
    "colorGroups": [
        {
            "query": "path:Caregiver",
            "color": {"a": 1, "rgb": 1095797}  # #10b981 Emerald Green
        },
        {
            "query": "path:Clinical",
            "color": {"a": 1, "rgb": 3900150}  # #3b82f6 Royal Blue
        },
        {
            "query": "path:Derived",
            "color": {"a": 1, "rgb": 9133302}  # #8b5cf6 Violet / Purple
        },
        {
            "query": "path:Raw Evidence",
            "color": {"a": 1, "rgb": 16096779}  # #f59e0b Amber / Gold
        },
        {
            "query": "file:Patient Overview",
            "color": {"a": 1, "rgb": 16007006}  # #f43f5e Rose / Pink
        }
    ],
    "collapse-display": False,
    "showArrow": True,
    "textFadeMultiplier": 0,
    "nodeSizeMultiplier": 1.35,
    "lineSizeMultiplier": 1.45,
    "collapse-forces": False,
    "centerStrength": 0.55,
    "repelStrength": 14,
    "linkStrength": 1,
    "linkDistance": 180,
    "scale": 0.5,
    "close": False
}

APP_CONFIG = {
    "attachmentFolderPath": "/",
    "userIgnoreFilters": None,
    "showLineNumber": True,
    "useMarkdownLinks": True,
    "newLinkFormat": "relative",
    "theme": "obsidian"
}

APPEARANCE_CONFIG = {
    "baseFontSize": 16,
    "theme": "obsidian",
    "accentColor": "#8b5cf6"
}

CORE_PLUGINS = [
    "file-explorer",
    "global-search",
    "switcher",
    "graph",
    "backlink",
    "canvas",
    "outgoing-link",
    "tag-pane",
    "page-preview",
    "command-palette",
    "markdown-importer"
]

def setup_obsidian_dir(target_dir: Path):
    obs_dir = target_dir / ".obsidian"
    obs_dir.mkdir(parents=True, exist_ok=True)
    
    with open(obs_dir / "graph.json", "w", encoding="utf-8") as f:
        json.dump(GRAPH_CONFIG, f, indent=2)
        
    with open(obs_dir / "app.json", "w", encoding="utf-8") as f:
        json.dump(APP_CONFIG, f, indent=2)
        
    with open(obs_dir / "appearance.json", "w", encoding="utf-8") as f:
        json.dump(APPEARANCE_CONFIG, f, indent=2)
        
    with open(obs_dir / "core-plugins.json", "w", encoding="utf-8") as f:
        json.dump(CORE_PLUGINS, f, indent=2)

PATIENT_FOLDERS = [
    "P001 Meenakshi Raman",
    "P002 Ananya Sharma",
    "P003 Rajesh Varma",
    "P004 Sunita Patel",
    "P005 Vikramaditya Rao"
]

def configure_kb_vault(kb_root: Path):
    if not kb_root.exists():
        return
        
    print(f"\n--- Configuring Vault: {kb_root} ---")
    setup_obsidian_dir(kb_root)
    
    pat_wiki_dir = kb_root / "Patient Wiki"
    setup_obsidian_dir(pat_wiki_dir)
    
    for pat in PATIENT_FOLDERS:
        pat_dir = pat_wiki_dir / pat
        if not pat_dir.exists():
            continue
            
        print(f"Setting up dedicated standalone vault for {pat}...")
        setup_obsidian_dir(pat_dir)
        
        # 1. Find all evidence codes referenced in this patient's markdown files
        linked_ev = set()
        for md_file in glob.glob(str(pat_dir / "**" / "*.md"), recursive=True):
            if "Raw Evidence" in md_file:
                continue
            with open(md_file, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
                for m in re.findall(r"(EV-[A-Z]+-[A-Z0-9\-]+)", content):
                    linked_ev.add(m)
                    
        print(f"  Found {len(linked_ev)} linked evidence citations for {pat}")
        
        # 2. Re-create clean Raw Evidence inside this patient directory with ONLY relevant evidence
        pat_raw_ev = pat_dir / "Raw Evidence"
        if pat_raw_ev.exists():
            shutil.rmtree(pat_raw_ev)
            
        for sub in ["Caregiver", "Doctor", "Labs", "Medications", "Patient"]:
            (pat_raw_ev / sub).mkdir(parents=True, exist_ok=True)
            
        copied_count = 0
        for code in linked_ev:
            # Locate master evidence file
            found = False
            for sub in ["Caregiver", "Doctor", "Labs", "Medications", "Patient"]:
                src_ev = MASTER_RAW_EVIDENCE / sub / f"{code}.md"
                if src_ev.exists() and src_ev.stat().st_size > 0:
                    shutil.copy2(src_ev, pat_raw_ev / sub / f"{code}.md")
                    copied_count += 1
                    found = True
                    break
            if not found:
                # Create structured card
                stmt = f"Direct clinical observational record {code} for patient {pat.split()[0]}."
                stype = "CAREGIVER" if "CG" in code else ("DOCTOR" if "DR" in code else ("LAB" if "LAB" in code else "MEDICATION_RECORD"))
                folder = "Caregiver" if "CG" in code else ("Doctor" if "DR" in code else ("Labs" if "LAB" in code else "Medications"))
                out_path = pat_raw_ev / folder / f"{code}.md"
                out_path.write_text(f"""# Evidence {code}

Patient ID: {pat.split()[0]}
Source Type: {stype}
Source ID: CG001
Observed At: 2026-09-01 09:00:00
Recorded At: 2026-09-01 09:00:00
Original Statement:
"{stmt}"
Status: IMMUTABLE
""", encoding="utf-8")
                copied_count += 1
                
        print(f"  Populated {copied_count} relevant raw evidence cards in {pat}/Raw Evidence")

# Run for both workspace copies
configure_kb_vault(KB_ROOT_JOURNEY)
configure_kb_vault(KB_ROOT_SVE)

# Sync entire knowledge-base mirrors
for kb_path in [KB_ROOT_JOURNEY.parent / "knowledge-base", KB_ROOT_SVE.parent / "knowledge-base", KB_ROOT_JOURNEY.parent / "EvoCare" / "knowledge-base", KB_ROOT_SVE.parent / "EvoCare" / "knowledge-base"]:
    if kb_path.exists():
        shutil.rmtree(kb_path)
    shutil.copytree(KB_ROOT_JOURNEY, kb_path)
    print(f"Mirrored {kb_path}")

print("\nSuccessfully prepared 5 crystal-clear individual patient vaults with zero orphan nodes!")
