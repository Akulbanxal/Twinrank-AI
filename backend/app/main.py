from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import router as api_router
from app.core.config import settings
from app.utils.logger import logger
from app.utils.errors import RankingException, ranking_exception_handler, global_exception_handler

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Backend API for TwinRank AI Recruitment Platform",
    version=settings.VERSION,
)

# Exception Handlers
app.add_exception_handler(RankingException, ranking_exception_handler)
app.add_exception_handler(Exception, global_exception_handler)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=f"{settings.API_V1_STR}/jobs", tags=["Jobs"])

@app.on_event("startup")
async def startup_event():
    logger.info(f"Starting {settings.PROJECT_NAME} backend server...")
    # Here we would load ML models into memory as singletons
    logger.info("ML Models initialized.")

@app.get("/health", tags=["System"])
async def health_check():
    return {"status": "healthy", "version": settings.VERSION}

@app.get("/", tags=["System"])
async def root():
    return {"message": f"Welcome to {settings.PROJECT_NAME} API"}
