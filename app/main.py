# app/main.py
import sys, os
sys.path.insert(0, os.path.dirname(__file__))  # ensures 'core' and 'models' are found

<<<<<<< HEAD
from fastapi import FastAPI

=======
>>>>>>> 25b99af975ba39173ba359d4cd357fbff23a8d79
from core.database import Base, engine
from models.user import User
from models.student import Student
from models.audit_log import AuditLog

# Creates all tables in MSSQL if they don't exist yet
Base.metadata.create_all(bind=engine)
<<<<<<< HEAD

app = FastAPI(title="Student Management System")

# ── Routers ───────────────────────────────────────────────────────────────────
from routers.auth import router as auth_router
app.include_router(auth_router)
=======
print(" All tables created successfully")
>>>>>>> 25b99af975ba39173ba359d4cd357fbff23a8d79
