from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from routers import (
    auth_router,
    dashboard_router,
    transactions_router,
    accounts_router,
    budgets_router,
    reports_router,
    users_router,
    analytics_router
)

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="Finance Dashboard API",
    description="API untuk Dashboard Keuangan Perusahaan",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware - includes both dev and production origins
import os

# Get allowed origins from environment or use defaults
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "").split(",") if os.getenv("CORS_ORIGINS") else []
DEFAULT_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:3000",
    "http://127.0.0.1:5173",
    "https://finance.mitramutiara.co.id",
    "http://finance.mitramutiara.co.id",
]
ALLOWED_ORIGINS = list(set(DEFAULT_ORIGINS + [o.strip() for o in CORS_ORIGINS if o.strip()]))

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router, prefix="/api")
app.include_router(dashboard_router, prefix="/api")
app.include_router(transactions_router, prefix="/api")
app.include_router(accounts_router, prefix="/api")
app.include_router(budgets_router, prefix="/api")
app.include_router(reports_router, prefix="/api")
app.include_router(users_router, prefix="/api")
app.include_router(analytics_router, prefix="/api")


@app.get("/")
async def root():
    return {
        "message": "Finance Dashboard API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/api/health")
async def health_check():
    return {"status": "healthy"}


@app.get("/healthz")
async def healthz():
    """Health check endpoint for load balancers and monitoring"""
    return {"status": "ok"}


# Run seed on startup - respects SEED_MODE environment variable
@app.on_event("startup")
async def startup_event():
    seed_mode = os.getenv("SEED_MODE", "full").lower()
    
    if seed_mode == "users_only":
        # Production mode - only seed users, roles, and categories
        from utils.seed_users_only import seed_users_only
        seed_users_only()
    else:
        # Development mode - seed full demo data
        from utils.seed_data import seed_database
        seed_database()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
