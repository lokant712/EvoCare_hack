import os
from pathlib import Path
try:
    from dotenv import load_dotenv
    # Load backend .env or root .env
    backend_env = Path(__file__).resolve().parent.parent.parent / ".env"
    root_env = Path(__file__).resolve().parent.parent.parent.parent / ".env"
    if backend_env.exists():
        load_dotenv(backend_env)
    elif root_env.exists():
        load_dotenv(root_env)
    else:
        load_dotenv()
except Exception:
    pass

class Settings:
    PROJECT_NAME: str = "EvoCare Longitudinal Patient Memory System"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"
    DB_FILE_PATH: Path = Path(__file__).resolve().parent.parent.parent / "evocare.db"
    DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite:///{DB_FILE_PATH}")
    DEBUG: bool = os.getenv("DEBUG", "True").lower() in ("true", "1")
    KNOWLEDGE_BASE_DIR: str = os.getenv(
        "KNOWLEDGE_BASE_DIR",
        str(Path(__file__).resolve().parent.parent.parent.parent / "knowledge-base")
    )

    # Multi-Tier AI Provider Settings (Gemini Flash + Groq + Deterministic Fallback)
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", os.getenv("GOOGLE_API_KEY", "")).strip()
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash").strip()
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "").strip()
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile").strip()

    # Legacy compatibility
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "").strip()
    ANTHROPIC_MODEL: str = os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022").strip()
    CLINICAL_REASONING_MODEL: str = GEMINI_MODEL

    LLM_ENABLED: bool = os.getenv("LLM_ENABLED", "true").lower() in ("true", "1")

    # Phase 8 Security & Authentication Settings
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "evocare-dev-jwt-secret-key-32bytes-long-2026!!")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("JWT_REFRESH_TOKEN_EXPIRE_DAYS", "7"))
    CORS_ORIGINS: list = os.getenv("CORS_ORIGINS", "http://localhost:9000,http://127.0.0.1:9000,http://localhost:5173,http://127.0.0.1:5173").split(",")
    AUTH_ENABLED: bool = os.getenv("AUTH_ENABLED", "true").lower() in ("true", "1")
    DEMO_MODE: bool = os.getenv("DEMO_MODE", "true").lower() in ("true", "1")

settings = Settings()
