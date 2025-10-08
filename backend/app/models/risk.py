from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class RiskScore(Base):
    __tablename__ = "risk_scores"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    date = Column(DateTime, default=func.now())
    overall_risk_score = Column(Float)  # 0-100 scale
    delay_risk = Column(Float)
    budget_risk = Column(Float)
    quality_risk = Column(Float)
    resource_risk = Column(Float)
    risk_factors = Column(JSON)  # Store detailed risk breakdown
    predictions = Column(JSON)  # Store model predictions

    # Relationships
    project = relationship("Project", back_populates="risk_scores")


class Anomaly(Base):
    __tablename__ = "anomalies"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=True)
    anomaly_type = Column(String)  # hours_drop, missing_logs, unusual_pattern
    severity = Column(String)  # low, medium, high, critical
    description = Column(String)
    detected_at = Column(DateTime, default=func.now())
    is_resolved = Column(Boolean, default=False)
    anomaly_data = Column(JSON)  # Store raw anomaly detection data
