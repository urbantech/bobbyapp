"""
Error handling middleware for the FastAPI application.
Provides consistent error responses and logging.
"""

import traceback
import logging
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("app.errors")

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Handle validation errors from FastAPI's request validation.
    Returns a more user-friendly error format.
    """
    errors = []
    for error in exc.errors():
        error_msg = {
            "loc": error.get("loc", []),
            "msg": error.get("msg", "Validation error"),
            "type": error.get("type", "")
        }
        errors.append(error_msg)
    
    logger.warning(f"Validation error: {errors}")
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": "Invalid request data",
            "errors": errors
        }
    )

async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """
    Handle HTTP exceptions with a consistent response format.
    """
    logger.warning(f"HTTP error {exc.status_code}: {exc.detail}")
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "status_code": exc.status_code
        },
    )

async def pydantic_validation_exception_handler(request: Request, exc: ValidationError):
    """
    Handle Pydantic validation errors.
    """
    errors = exc.errors()
    logger.warning(f"Pydantic validation error: {errors}")
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": "Data validation error",
            "errors": errors
        }
    )

async def general_exception_handler(request: Request, exc: Exception):
    """
    Handle any unhandled exceptions to prevent exposing sensitive information.
    """
    # Log the full exception for debugging
    error_details = traceback.format_exc()
    logger.error(f"Unhandled exception: {str(exc)}\n{error_details}")
    
    # Return a generic error to the client
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "An unexpected error occurred. Please try again later.",
            "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR
        }
    )

def register_exception_handlers(app):
    """
    Register all exception handlers with the FastAPI app.
    """
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(ValidationError, pydantic_validation_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)
