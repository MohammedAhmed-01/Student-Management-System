import os
import pyodbc
from urllib.parse import quote_plus
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base

load_dotenv()

SERVER   = os.getenv("DB_SERVER",   "MOHAMMED_SALAH")
DATABASE = os.getenv("DB_NAME",     "student_mgmt")
USERNAME = os.getenv("DB_USER",     "app_user")
PASSWORD = os.getenv("DB_PASSWORD", "AppStr0ngP@ss!")


def _get_odbc_driver() -> str:
    """Auto-detect the best installed SQL Server ODBC driver (18 → 17 → 13)."""
    preferred = [
        "ODBC Driver 18 for SQL Server",
        "ODBC Driver 17 for SQL Server",
        "ODBC Driver 13 for SQL Server",
    ]
    installed = pyodbc.drivers()
    for driver in preferred:
        if driver in installed:
            return driver
    raise RuntimeError(
        f"No SQL Server ODBC driver found. Installed drivers: {installed}\n"
        "Download: https://learn.microsoft.com/sql/connect/odbc/download-odbc-driver-for-sql-server"
    )


DRIVER = _get_odbc_driver()

# quote_plus encodes special chars in password (e.g. '@' → '%40')
# to prevent the URL parser from misreading the connection string
CONN_STR = (
    f"mssql+pyodbc://{USERNAME}:{quote_plus(PASSWORD)}@{SERVER}/{DATABASE}"
    f"?driver={DRIVER.replace(' ', '+')}"
    "&TrustServerCertificate=yes"
    "&Encrypt=yes"
)

engine = create_engine(
    CONN_STR,
    pool_size=10,       # persistent connections kept open
    max_overflow=20,    # extra connections allowed under peak load
    pool_pre_ping=True, # drop stale connections before use
    echo=False,         # set True to log all SQL statements
)

# One session per request; commit/rollback explicitly
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Shared base — all ORM models must inherit from this
Base = declarative_base()


def get_db():
    """FastAPI dependency: yields a DB session and closes it on exit."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


if __name__ == "__main__":
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT @@VERSION"))
            print(" Connected to MSSQL:")
            print(result.fetchone()[0])
    except Exception as exc:
        print(f"  Connection failed: {exc}")