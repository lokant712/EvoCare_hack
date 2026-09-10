import sys
import os
from pathlib import Path

backend_path = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_path))

from app.core.database import SessionLocal, engine, Base
from app.services.import_service import ImportService
import app.models

def run_import():
    print("Starting Knowledge Base Import...")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        results = ImportService.import_all(db)
        print("Knowledge Base Import Completed Successfully!")
        print("Import Results Summary:")
        for k, v in results.items():
            print(f"  - {k}: {v}")
    except Exception as e:
        print(f"Error during import: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    run_import()
