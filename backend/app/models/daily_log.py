from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class DailyLog(Base):
    __tablename__ = "daily_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    employee_id = Column(Integer, ForeignKey("employees.id"))
    date = Column(DateTime)
    hours_logged = Column(Float)
    task_description = Column(String)
    task_category = Column(String)
    completion_percentage = Column(Float)
    issues_reported = Column(Integer, default=0)
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    project = relationship("Project", back_populates="daily_logs")
    employee = relationship("Employee", back_populates="daily_logs")