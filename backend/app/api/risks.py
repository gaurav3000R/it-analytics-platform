from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
import logging

from app.database import get_db
from app.services.risk_prediction import RiskPredictionService
from app.services.anomaly_detection import AnomalyDetectionService
from app.models.risk import RiskScore

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/risks", tags=["risks"])

# Initialize services
risk_service = RiskPredictionService()
anomaly_service = AnomalyDetectionService()

@router.post("/train-model")
async def train_risk_model(db: Session = Depends(get_db)):
    """Train the risk prediction model"""
    try:
        metrics = risk_service.train_model(db)
        return {
            "message": "Model training completed successfully",
            "metrics": metrics
        }
    except Exception as e:
        logger.error(f"Error training model: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Training failed: {str(e)}")

@router.get("/predict/{project_id}")
async def predict_project_risk(project_id: int, db: Session = Depends(get_db)):
    """Predict risk for a specific project"""
    try:
        prediction = risk_service.predict_risk(db, project_id)
        
        # Save prediction to database
        risk_score = RiskScore(
            project_id=project_id,
            overall_risk_score=prediction['overall_risk_score'],
            delay_risk=prediction['component_risks']['delay_risk'],
            budget_risk=prediction['component_risks']['budget_risk'],
            quality_risk=prediction['component_risks']['quality_risk'],
            resource_risk=prediction['component_risks']['resource_risk'],
            risk_factors=prediction['feature_importance'],
            predictions=prediction
        )
        db.add(risk_score)
        db.commit()
        
        return prediction
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error predicting risk: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

@router.get("/dashboard")
async def get_risk_dashboard(db: Session = Depends(get_db)):
    """Get risk dashboard data for all projects"""
    try:
        # Get latest risk scores for all projects
        latest_scores = db.query(RiskScore).distinct(RiskScore.project_id)\
                        .order_by(RiskScore.project_id, RiskScore.date.desc()).all()
        
        dashboard_data = {
            "total_projects": len(latest_scores),
            "high_risk_projects": len([s for s in latest_scores if s.overall_risk_score > 70]),
            "medium_risk_projects": len([s for s in latest_scores if 30 <= s.overall_risk_score <= 70]),
            "low_risk_projects": len([s for s in latest_scores if s.overall_risk_score < 30]),
            "projects": [
                {
                    "project_id": score.project_id,
                    "overall_risk": score.overall_risk_score,
                    "delay_risk": score.delay_risk,
                    "budget_risk": score.budget_risk,
                    "quality_risk": score.quality_risk,
                    "resource_risk": score.resource_risk,
                    "last_updated": score.date.isoformat()
                }
                for score in latest_scores
            ]
        }
        
        return dashboard_data
    
    except Exception as e:
        logger.error(f"Error getting dashboard data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Dashboard error: {str(e)}")

@router.post("/detect-anomalies")
async def detect_anomalies(
    days_back: int = Query(default=30, ge=1, le=90),
    db: Session = Depends(get_db)
):
    """Detect anomalies in daily logs"""
    try:
        anomalies = anomaly_service.detect_daily_log_anomalies(db, days_back)
        
        return {
            "message": f"Anomaly detection completed for last {days_back} days",
            "anomalies_detected": len(anomalies),
            "anomalies": anomalies
        }
    
    except Exception as e:
        logger.error(f"Error detecting anomalies: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Anomaly detection failed: {str(e)}")

@router.get("/anomalies/{project_id}")
async def get_project_anomalies(
    project_id: int,
    days_back: int = Query(default=7, ge=1, le=30),
    db: Session = Depends(get_db)
):
    """Get anomaly summary for a specific project"""
    try:
        summary = anomaly_service.get_project_anomaly_summary(db, project_id, days_back)
        return summary
    
    except Exception as e:
        logger.error(f"Error getting project anomalies: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
