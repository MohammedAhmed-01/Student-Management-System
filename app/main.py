# app/main.py
import sys, os
sys.path.insert(0, os.path.dirname(__file__))  # ensures 'core' and 'models' are found

from fastapi import FastAPI

from core.database import Base, engine
from models.user import User
from models.student import Student
from models.audit_log import AuditLog

# Creates all tables in MSSQL if they don't exist yet
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Student Management System")

# ── Routers ───────────────────────────────────────────────────────────────────
from routers.auth import router as auth_router
app.include_router(auth_router)
