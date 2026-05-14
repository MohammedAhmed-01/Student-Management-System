from fastapi import FastAPI, Request, status, Response
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

from fastapi.responses import JSONResponse
import yaml
from sqlalchemy.exc import IntegrityError
from fastapi.encoders import jsonable_encoder

from app.core.config import settings
from app.middlewares.logging_middleware import LoggingMiddleware
from app.monitoring.dashboard import router as monitoring_router
from app.routes import auth, users, students

app = FastAPI(title=settings.app_name)

app.add_middleware(LoggingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.back_end_allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



@app.exception_handler(IntegrityError)
async def integrity_exception_handler(request: Request, exc: IntegrityError):
    """Handle database integrity errors (e.g. unique constraint violations)."""
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "detail": "Data integrity error. This might be due to a duplicate entry or constraint violation.",
            "error_type": "integrity_error"
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle Pydantic validation errors with a cleaner format."""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder({
            "detail": exc.errors(),
            "message": "Validation failed for one or more fields."
        }),
    )

app.include_router(auth.router, prefix="/auth", tags=["Auth"])
app.include_router(users.router, prefix="/users", tags=["Users"])
app.include_router(students.router, prefix="/students", tags=["Students"])
app.include_router(monitoring_router)


@app.get("/", tags=["Root"])
def read_root() -> dict[str, str]:
    return {"message": "Student Management API is running"}
