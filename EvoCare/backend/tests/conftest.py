import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.database import SessionLocal, engine, Base
from app.services.import_service import ImportService
from app.main import app
from app.core.config import settings

@pytest.fixture(scope="session", autouse=True)
def test_environment_isolation():
    """Ensure automated tests don't consume user's free-tier rate limits"""
    prev_llm = settings.LLM_ENABLED
    settings.LLM_ENABLED = False
    yield
    settings.LLM_ENABLED = prev_llm

@pytest.fixture(scope="session")
def db_session():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    # Ensure KB is imported
    ImportService.import_all(db)
    from app.models.security import User
    if not db.query(User).filter(User.username == "doctor.demo").first():
        try:
            from scripts.seed_security_demo import seed_security_and_p002
            seed_security_and_p002()
        except Exception:
            pass
    try:
        yield db
    finally:
        db.close()

@pytest.fixture(scope="session")
def client(db_session):
    c = TestClient(app)
    from app.core.security import create_access_token
    from app.models.security import User
    db = SessionLocal()
    user = db.query(User).filter(User.username == "doctor.demo").first()
    if user:
        token = create_access_token(data={"sub": str(user.id), "username": user.username, "role": "DOCTOR"})
        c.headers.update({"Authorization": f"Bearer {token}"})
    db.close()
    return c

