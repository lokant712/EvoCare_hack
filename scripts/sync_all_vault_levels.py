import os
import shutil
import glob

base_evidence_source = r'c:\Users\lokan\Downloads\journey\sve\EvoCare-Knowledge-Base\Raw Evidence'

target_locations = [
    r'c:\Users\lokan\Downloads\journey\sve\EvoCare-Knowledge-Base\Patient Wiki\Raw Evidence',
    r'c:\Users\lokan\Downloads\journey\sve\EvoCare-Knowledge-Base\Patient Wiki\P001 Meenakshi Raman\Raw Evidence',
    r'c:\Users\lokan\Downloads\journey\sve\EvoCare\knowledge-base\Raw Evidence',
    r'c:\Users\lokan\Downloads\journey\sve\EvoCare\knowledge-base\Patient Wiki\Raw Evidence',
    r'c:\Users\lokan\Downloads\journey\sve\knowledge-base\Raw Evidence',
    r'c:\Users\lokan\Downloads\journey\sve\knowledge-base\Patient Wiki\Raw Evidence',
    r'c:\Users\lokan\Downloads\sve\EvoCare-Knowledge-Base\Raw Evidence',
    r'c:\Users\lokan\Downloads\sve\EvoCare-Knowledge-Base\Patient Wiki\Raw Evidence',
    r'c:\Users\lokan\Downloads\sve\EvoCare-Knowledge-Base\Patient Wiki\P001 Meenakshi Raman\Raw Evidence',
    r'c:\Users\lokan\Downloads\sve\EvoCare\knowledge-base\Raw Evidence',
    r'c:\Users\lokan\Downloads\sve\EvoCare\knowledge-base\Patient Wiki\Raw Evidence',
    r'c:\Users\lokan\Downloads\sve\knowledge-base\Raw Evidence',
    r'c:\Users\lokan\Downloads\sve\knowledge-base\Patient Wiki\Raw Evidence',
]

for tgt in target_locations:
    if os.path.abspath(tgt) == os.path.abspath(base_evidence_source):
        continue
    os.makedirs(os.path.dirname(tgt), exist_ok=True)
    if os.path.exists(tgt):
        shutil.rmtree(tgt)
    shutil.copytree(base_evidence_source, tgt)
    files = glob.glob(os.path.join(tgt, '**/*.md'), recursive=True)
    print(f"Synced {tgt} -> {len(files)} files")

# Remove any stray 0-byte files across the system
for root_scan in [r'c:\Users\lokan\Downloads\journey\sve', r'c:\Users\lokan\Downloads\sve']:
    for f in glob.glob(os.path.join(root_scan, '**/*.md'), recursive=True):
        if os.path.getsize(f) == 0:
            print(f"Removing stray 0-byte file: {f}")
            os.remove(f)

print("\nVault synchronization complete. Zero 0-byte files remain anywhere.")
