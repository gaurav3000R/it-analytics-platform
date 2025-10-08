#===== ./app/models/project.py =====

from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Project(Base):
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Core project fields for dashboard compatibility
    name = Column(String, index=True)
    client = Column(String)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    current_spend = Column(Float, default=0.0)
    status = Column(String, default="active")
    budget = Column(Float)  # For dashboard compatibility
    
    # CSV Dataset Fields
    project_id = Column(String, unique=True, index=True)
    project_type = Column(String, index=True)
    team_size = Column(Integer)
    project_budget_usd = Column(Float)
    estimated_timeline_months = Column(Float)
    complexity_score = Column(Float)
    stakeholder_count = Column(Integer)
    methodology_used = Column(String)
    team_experience_level = Column(String)
    past_similar_projects = Column(Integer)
    
    # Operational Metrics (from CSV)
    external_dependencies_count = Column(Integer)
    change_request_frequency = Column(String)
    project_phase = Column(String)
    requirement_stability = Column(String)
    team_turnover_rate = Column(String)
    vendor_reliability_score = Column(Float)
    historical_risk_incidents = Column(Integer)
    communication_frequency = Column(String)
    budget_utilization_rate = Column(Float)
    resource_availability = Column(String)
    current_phase_duration_months = Column(Float)
    
    # Human Factors
    project_manager_experience = Column(String)
    stakeholder_engagement_level = Column(String)
    key_stakeholder_availability = Column(String)
    team_colocation = Column(String)
    
    # Organizational Context
    regulatory_compliance_level = Column(String)
    executive_sponsorship = Column(String)
    funding_source = Column(String)
    organizational_change_frequency = Column(String)
    org_process_maturity = Column(String)
    risk_management_maturity = Column(String)
    change_control_maturity = Column(String)
    
    # Technical Aspects
    technology_familiarity = Column(String)
    integration_complexity = Column(String)
    technical_debt_level = Column(String)
    tech_environment_stability = Column(String)
    data_security_requirements = Column(String)
    
    # External Influences
    market_volatility = Column(String)
    industry_volatility = Column(String)
    geographical_distribution = Column(String)
    client_experience_level = Column(String)
    contract_type = Column(String)
    resource_contention_level = Column(String)
    
    # Additional Fields
    schedule_pressure = Column(String)
    priority_level = Column(String)
    cross_functional_dependencies = Column(Integer)
    previous_delivery_success_rate = Column(Float)
    documentation_quality = Column(String)
    project_start_month = Column(String)
    seasonal_risk_factor = Column(Float)
    
    # Target Variable
    risk_level = Column(String, index=True)
    
    # System fields
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # AI-generated insights
    ai_risk_analysis = Column(Text)
    ai_recommendations = Column(Text)
    ai_insights_updated_at = Column(DateTime)
    
    # Relationships
    daily_logs = relationship("DailyLog", back_populates="project")
    risk_scores = relationship("RiskScore", back_populates="project")
    sprints = relationship("Sprint", back_populates="project")