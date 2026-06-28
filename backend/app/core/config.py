from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "TwinRank AI"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Caching
    CACHE_MAX_SIZE: int = 1000
    CACHE_TTL_SECONDS: int = 3600
    
    # ML Constraints
    MAX_CANDIDATES_PER_REQUEST: int = 1000
    
    class Config:
        case_sensitive = True

settings = Settings()
