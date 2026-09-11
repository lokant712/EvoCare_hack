import sqlite3
import os
import glob
import re

db_path = 'EvoCare/backend/evocare.db'
conn = sqlite3.connect(db_path)
c = conn.cursor()

c.execute("SELECT COUNT(*) FROM evidences")
print("Total evidences in DB:", c.fetchone()[0])

c.execute("SELECT evidence_code, patient_id, source_type, observed_at, original_statement FROM evidences")
all_db_evidences = c.fetchall()

print(f"Sample evidences in DB (first 5):")
for row in all_db_evidences[:5]:
    print(" ", row)

print(f"Sample evidences with 222 or high numbers:")
for row in all_db_evidences:
    if "222" in str(row[0]) or "22" in str(row[0]):
        print(" ", row)

# Check all references in Patient Wiki markdown files
kb_root = 'EvoCare-Knowledge-Base'
wikilinks = set()
for md_file in glob.glob(f'{kb_root}/**/*.md', recursive=True):
    with open(md_file, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
        links = re.findall(r'\[\[(.*?)\]\]', content)
        for link in links:
            # e.g. [[Raw Evidence/Caregiver/EV-CG-222|EV-CG-222]] -> target is Raw Evidence/Caregiver/EV-CG-222
            target = link.split('|')[0].strip()
            wikilinks.add((md_file, target))

print(f"\nTotal unique wikilinks across KB: {len(wikilinks)}")

# Check which targets exist on disk
missing_files = []
for source_file, target in wikilinks:
    # Check if target ends with .md or not
    candidate1 = os.path.join(kb_root, target + '.md')
    candidate2 = os.path.join(kb_root, target)
    # Check relative to source_file's directory
    candidate3 = os.path.join(os.path.dirname(source_file), target + '.md')
    candidate4 = os.path.join(os.path.dirname(source_file), target)
    
    if not (os.path.exists(candidate1) or os.path.exists(candidate2) or os.path.exists(candidate3) or os.path.exists(candidate4)):
        missing_files.append((source_file, target))

print(f"Missing referenced wikilink files: {len(missing_files)}")
print("Sample missing wikilinks (first 20):")
for src, tgt in missing_files[:20]:
    print(f"  From {os.path.basename(src)} -> {tgt}")
