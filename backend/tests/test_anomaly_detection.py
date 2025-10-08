import pytest
from datetime import datetime, timedelta
import numpy as np

from app.services.anomaly_detection import AnomalyDetectionService
from tests.test_risk_prediction import db, sample_data

def test_anomaly_detection_service_initialization():
    """Test AnomalyDetectionService initialization"""
    service = AnomalyDetectionService()
    assert service.isolation_forest is not None
    assert service.scaler is not None

def test_detect_daily_log_anomalies(db, sample_data):
    """Test anomaly detection in daily logs"""
    service = AnomalyDetectionService()
    project, employee = sample_data
    
    # Add some anomalous data
    from app.models.project import DailyLog
    anomalous_log = DailyLog(
        project_id=project.id,
        employee_id=employee.id,
        date=datetime.now(),
        hours_logged=15.0,  # Unusually high
        task_category="development",
        completion_percentage=10.0,  # Unusually low for high hours
        issues_reported=0
    )
    db.add(anomalous_log)
    db.commit()
    
    # Detect anomalies
    anomalies = service.detect_daily_log_anomalies(db, days_back=30)
    
    assert isinstance(anomalies, list)
    # Should detect the anomalous entry we added
    assert len(anomalies) > 0

def test_get_project_anomaly_summary(db, sample_data):
    """Test project anomaly summary"""
    service = AnomalyDetectionService()
    project, employee = sample_data
    
    # First detect some anomalies
    service.detect_daily_log_anomalies(db, days_back=30)
    
    # Get summary
    summary = service.get_project_anomaly_summary(db, project.id, days_back=7)
    
    assert 'total_anomalies' in summary
    assert 'by_severity' in summary
    assert 'by_type' in summary
    assert 'recent_anomalies' in summary