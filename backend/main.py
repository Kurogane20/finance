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

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173"],
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


# Run seed on startup (optional - can be run separately)
@app.on_event("startup")
async def startup_event():
    from utils.seed_data import seed_database
    seed_database()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
