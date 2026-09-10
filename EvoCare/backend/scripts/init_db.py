import sys
import os
from pathlib import Path

# Add app to path
backend_path = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_path))

from app.core.database import engine, Base
import app.models

def init_db():
    print("Initializing EvoCare Database Schema...")
    Base.metadata.create_all(bind=engine)
    print(f"Database schema initialized successfully at: {engine.url}")

if __name__ == "__main__":
    init_db()
