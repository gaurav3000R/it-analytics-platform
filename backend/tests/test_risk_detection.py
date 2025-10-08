import pytest
import pandas as pd
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import numpy as np

from app.database import Base
from app.models.project import Project, DailyLog
from app.models.employee import Employee
from app.services.risk_prediction import RiskPredictionService

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture
def db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def sample_data(db):
    # Create sample project
    project = Project(
        name="Test Project",
        client="Test Client",
        start_date=datetime.now() - timedelta(days=60),
        end_date=datetime.now() + timedelta(days=30),
        budget=100000.0,
        current_spend=60000.0,
        team_size=5,
        complexity_score=3.0
    )
    db.add(project)
    
    # Create sample employee
    employee = Employee(
        name="Test Employee",
        email="test@example.com",
        role="developer",
        skill_level="senior",
        hourly_rate=100.0
    )
    db.add(employee)
    db.commit()
    
    # Create sample daily logs
    for i in range(30):
        log_date = datetime.now() - timedelta(days=i)
        daily_log = DailyLog(
            project_id=project.id,
            employee_id=employee.id,
            date=log_date,
            hours_logged=np.random.uniform(6, 9),
            task_category="development",
            completion_percentage=np.random.uniform(70, 95),
            issues_reported=np.random.randint(0, 2)
        )
        db.add(daily_log)
    
    db.commit()
    return project, employee

def test_risk_prediction_service_initialization():
    """Test RiskPredictionService initialization"""
    service = RiskPredictionService()
    assert service.model is None
    assert service.scaler is not None
    assert service.feature_columns == []

def test_prepare_features(db, sample_data):
    """Test feature preparation"""
    service = RiskPredictionService()
    project, employee = sample_data
    
    df = service.prepare_features(db, project.id)
    
    assert not df.empty
    assert 'project_id' in df.columns
    assert 'total_hours_30d' in df.columns
    assert 'completion_rate' in df.columns
    assert 'budget_utilization' in df.columns

def test_model_training(db, sample_data):
    """Test model training"""
    service = RiskPredictionService()
    project, employee = sample_data
    
    # Train model
    metrics = service.train_model(db)
    
    assert service.model is not None
    assert 'train_r2' in metrics
    assert 'test_r2' in metrics
    assert len(service.feature_columns) > 0

def test_risk_prediction(db, sample_data):
    """Test risk prediction"""
    service = RiskPredictionService()
    project, employee = sample_data
    
    # Train model first
    service.train_model(db)
    
    # Make prediction
    prediction = service.predict_risk(db, project.id)
    
    assert 'project_id' in prediction
    assert 'overall_risk_score' in prediction
    assert 'component_risks' in prediction
    assert 0 <= prediction['overall_risk_score'] <= 100