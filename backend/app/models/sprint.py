from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Sprint(Base):
    __tablename__ = "sprints"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    sprint_number = Column(Integer)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    planned_points = Column(Float)
    completed_points = Column(Float)
    velocity = Column(Float)
    burndown_data = Column(JSON)  # Store burndown chart data
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    project = relationship("Project", back_populates="sprints")