from fastapi import Request
from fastapi.responses import JSONResponse
from app.utils.logger import logger

class RankingException(Exception):
    def __init__(self, message: str, code: str = "RANKING_ERROR"):
        self.message = message
        self.code = code
        super().__init__(self.message)

class InvalidInputException(RankingException):
    def __init__(self, message: str):
        super().__init__(message, code="INVALID_INPUT")

async def ranking_exception_handler(request: Request, exc: RankingException):
    logger.error(f"RankingException: {exc.message} (Code: {exc.code})")
    return JSONResponse(
        status_code=400,
        content={"error": exc.code, "message": exc.message},
    )

async def global_exception_handler(request: Request, exc: Exception):
    logger.exception(f"Unhandled server error: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"error": "INTERNAL_SERVER_ERROR", "message": "An unexpected error occurred"},
    )
