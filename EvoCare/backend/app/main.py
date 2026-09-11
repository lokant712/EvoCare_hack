from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from contextlib import asynccontextmanager
from app.core.config import settings
from app.core.database import engine, Base, SessionLocal
import app.models  # Load all models for metadata

# Initialize database schema
Base.metadata.create_all(bind=engine)

def auto_seed_database_if_empty():
    """Automatically seeds default demo accounts, 5 patients, and knowledge base if database is empty."""
    db = SessionLocal()
    try:
        from app.models.security import User
        user_count = db.query(User).count()
        if user_count == 0:
            print("[EvoCare Startup] New database detected. Seeding Knowledge Base & Demo Accounts...")
            from app.services.import_service import ImportService
            ImportService.import_all(db)

            try:
                from scripts.seed_security_demo import seed_security_and_p002
                seed_security_and_p002()
            except Exception as e:
                print(f"[EvoCare Startup] Security seeding notice: {e}")

            try:
                from scripts.seed_5_demo_patients import seed_patients
                seed_patients()
            except Exception as e:
                print(f"[EvoCare Startup] 5 Patients seeding notice: {e}")
            print("[EvoCare Startup] Seeding complete! Demo users (doctor.demo, caregiver.demo, patient.demo, admin.demo) are active.")
    except Exception as e:
        print(f"[EvoCare Startup] Seeding check notice: {e}")
    finally:
        db.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    auto_seed_database_if_empty()
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Longitudinal Memory System & Clinical Intelligence API for Elderly Healthcare",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Security Headers Middleware
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        return response

app.add_middleware(SecurityHeadersMiddleware)

# Universal CORS middleware (supports local, Vercel, Render, Cloudflare, mobile)
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"^https?://.*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check
@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok", "project": settings.PROJECT_NAME, "version": settings.VERSION}

# Include routers
from app.routers import (
    auth,
    admin,
    patients,
    evidence,
    caregiver,
    clinical,
    medications,
    labs,
    memory,
    timeline,
    observations,
    clarification,
    dashboard,
    clinical_reasoning,
    patient_companion,
    caregiver_connections
)

app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(admin.router, prefix=settings.API_V1_STR)
app.include_router(patients.router, prefix=settings.API_V1_STR)
app.include_router(caregiver_connections.router, prefix=settings.API_V1_STR)
app.include_router(evidence.router, prefix=settings.API_V1_STR)
app.include_router(caregiver.router, prefix=settings.API_V1_STR)
app.include_router(clinical.router, prefix=settings.API_V1_STR)
app.include_router(medications.router, prefix=settings.API_V1_STR)
app.include_router(labs.router, prefix=settings.API_V1_STR)
app.include_router(memory.router, prefix=settings.API_V1_STR)
app.include_router(timeline.router, prefix=settings.API_V1_STR)
app.include_router(observations.router, prefix=settings.API_V1_STR)
app.include_router(clarification.router, prefix=settings.API_V1_STR)
app.include_router(dashboard.router, prefix=settings.API_V1_STR)
app.include_router(clinical_reasoning.router, prefix=settings.API_V1_STR)
app.include_router(patient_companion.router, prefix=settings.API_V1_STR)

# Serve built frontend static files if present (All-in-One Deployment)
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path

frontend_dist = Path(__file__).resolve().parent.parent.parent.parent / "frontend" / "dist"
if not frontend_dist.exists():
    frontend_dist = Path("/app/frontend_dist")
if not frontend_dist.exists():
    frontend_dist = Path(__file__).resolve().parent.parent.parent / "frontend_dist"

if frontend_dist.exists():
    assets_dir = frontend_dist / "assets"
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_spa_frontend(full_path: str):
        # Don't intercept API routes or docs
        if full_path.startswith("api") or full_path in ("docs", "redoc", "openapi.json", "health"):
            return None
        target = frontend_dist / full_path
        if target.is_file():
            return FileResponse(str(target))
        return FileResponse(str(frontend_dist / "index.html"))


