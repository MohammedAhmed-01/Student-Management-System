from sqlalchemy import Column, Integer, SmallInteger, String, Date, DateTime, ForeignKey, Numeric, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class Student(Base):
    __tablename__  = "Students"
    __table_args__ = (
        Index("IX_Students_department", "department"),
        Index("IX_Students_gpa",        "gpa"),
        Index("IX_Students_status",     "status"),
        {"schema": "dbo"},
    )

    student_id      = Column(Integer, primary_key=True, autoincrement=True, index=True)
    user_id         = Column(Integer, ForeignKey("dbo.Users.user_id", ondelete="CASCADE"), unique=True, nullable=False)

    first_name      = Column(String(100), nullable=False)
    last_name       = Column(String(100), nullable=False)
    email           = Column(String(255), unique=True, nullable=False)  # may differ from login email
    phone           = Column(String(20),  nullable=True)
    date_of_birth   = Column(Date,        nullable=True)
    gender          = Column(String(10),  nullable=True)

    department      = Column(String(100), nullable=False)  # indexed for filter queries
    major           = Column(String(100), nullable=False)
    enrollment_year = Column(SmallInteger, nullable=False)
    year_of_study   = Column(SmallInteger, nullable=False)  # 1–6; CHECK in DDL
    gpa             = Column(Numeric(3, 2), nullable=True)  # Numeric avoids float rounding
    status          = Column(String(20), default="active", nullable=False)  # active|inactive|graduated
    address         = Column(String(500), nullable=True)

    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, onupdate=func.now(), nullable=True)

    user       = relationship("User",     back_populates="student")
    audit_logs = relationship("AuditLog", back_populates="student", lazy="dynamic")

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    def __repr__(self) -> str:
        return f"<Student id={self.student_id} name={self.full_name!r} status={self.status!r}>"