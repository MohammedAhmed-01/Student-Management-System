import json
from sqlalchemy import BigInteger, Column, Integer, String, Text, DateTime, ForeignKey, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from core.database import Base


class AuditLog(Base):
    """Append-only audit trail. Never update or delete rows from this table."""

    __tablename__  = "AuditLogs"
    __table_args__ = (
        Index("IX_AuditLogs_student",   "student_id"),
        Index("IX_AuditLogs_timestamp", "timestamp"),
        {"schema": "dbo"},
    )

    log_id     = Column(BigInteger, primary_key=True, autoincrement=True, index=True)  # BIGINT for high volume

    # SET NULL on delete → audit history survives even after student is removed
    student_id = Column(Integer, ForeignKey("dbo.Students.student_id", ondelete="SET NULL"), nullable=True)

    # NO ACTION → cannot delete a User who has audit records
    changed_by = Column(Integer, ForeignKey("dbo.Users.user_id", ondelete="NO ACTION"), nullable=False)

    action        = Column(String(10),  nullable=False)   # CREATE | UPDATE | DELETE
    endpoint      = Column(String(255), nullable=False)   # e.g. /students/3
    field_changed = Column(String(100), nullable=True)    # UPDATE only
    old_value     = Column(Text, nullable=True)           # JSON string
    new_value     = Column(Text, nullable=True)           # JSON string
    ip_address    = Column(String(45),  nullable=True)    # IPv4 or IPv6
    timestamp     = Column(DateTime, server_default=func.now(), nullable=False)

    student         = relationship("Student", back_populates="audit_logs")
    changed_by_user = relationship("User",    back_populates="audit_logs")

    def get_old_value(self) -> dict | None:
        return json.loads(self.old_value) if self.old_value else None

    def get_new_value(self) -> dict | None:
        return json.loads(self.new_value) if self.new_value else None

    def __repr__(self) -> str:
        return f"<AuditLog id={self.log_id} action={self.action!r} student_id={self.student_id} at={self.timestamp}>"