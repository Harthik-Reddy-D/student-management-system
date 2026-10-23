from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, Integer, String
from .database import Base
class Student(Base):
    __tablename__ = "students"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), nullable=False)
    email = Column(String(320), unique=True, index=True, nullable=False)
    phone = Column(String(30), nullable=False)
    department = Column(String(120), nullable=False)
    course = Column(String(120), nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
