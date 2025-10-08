from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Employee(Base):
    __tablename__ = "employees"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    role = Column(String)  # developer, tester, designer, manager
    skill_level = Column(String)  # junior, mid, senior
    hourly_rate = Column(Float)
    max_hours_per_day = Column(Float, default=8.0)
    is_active = Column(Boolean, default=True)
    hire_date = Column(DateTime)
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    daily_logs = relationship("DailyLog", back_populates="employee")