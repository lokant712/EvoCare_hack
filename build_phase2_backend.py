import os
import shutil

ROOT_DIR = r"c:\Users\lokan\Downloads\journey\sve\EvoCare"
BACKEND_DIR = os.path.join(ROOT_DIR, "backend")

def write_code(rel_path, content):
    full_path = os.path.join(BACKEND_DIR, rel_path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")
    print(f"Created: backend/{rel_path}")

print("Creating EvoCare Phase 2 Backend Structure...")

# requirements.txt
write_code("requirements.txt", """fastapi>=0.110.0
uvicorn>=0.28.0
sqlalchemy>=2.0.28
pydantic>=2.6.0
pytest>=8.0.0
httpx>=0.27.0
python-dotenv>=1.0.0
""")

# .env.example
write_code(".env.example", """DATABASE_URL=sqlite:///./evocare.db
APP_ENV=development
API_PREFIX=/api
DEBUG=True
""")

# app/__init__.py
write_code("app/__init__.py", """# EvoCare Backend Package
__version__ = "1.0.0"
""")

# app/core/config.py
write_code("app/core/config.py", """import os
from pydantic_settings import BaseSettings if hasattr(__import__('pydantic'), 'BaseSettings') else object

class Settings:
    PROJECT_NAME: str = "EvoCare Longitudinal Patient Memory System"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./evocare.db")
    DEBUG: bool = os.getenv("DEBUG", "True").lower() in ("true", "1")
    KNOWLEDGE_BASE_DIR: str = os.getenv(
        "KNOWLEDGE_BASE_DIR", 
        os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "knowledge-base"))
    )

settings = Settings()
""")

# app/core/database.py
write_code("app/core/database.py", """import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import settings

# In-memory or file-based SQLite engine configuration
connect_args = {"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    echo=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
""")

print("Core files written.")
