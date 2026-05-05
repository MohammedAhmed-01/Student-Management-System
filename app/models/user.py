from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class User(Base):
    __tablename__  = "Users"
    __table_args__ = {"schema": "dbo"}

    user_id         = Column(Integer, primary_key=True, autoincrement=True, index=True)
    username        = Column(String(50),  unique=True, nullable=False)
    email           = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)  # bcrypt hash — never plain text
    role            = Column(String(20),  nullable=False, default="student")  # 'admin' | 'student'
    is_active       = Column(Boolean, default=True, nullable=False)  # False = soft-deleted

    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, onupdate=func.now(), nullable=True)

    # One-to-one: uselist=False returns a single Student, not a list
    student = relationship(
        "Student",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )

    # One-to-many: via AuditLog.changed_by
    audit_logs = relationship(
        "AuditLog",
        back_populates="changed_by_user",
        lazy="dynamic",
    )

    def __repr__(self) -> str:
        return f"<User id={self.user_id} username={self.username!r} role={self.role!r}>"