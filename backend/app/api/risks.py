from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
import logging
from datetime import datetime

from app.database import get_db
from app.services.risk_prediction import RiskPredictionService
from app.services.anomaly_detection import AnomalyDetectionService

from supabase import Client


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/risks", tags=["risks"])

# Initialize services
risk_service = RiskPredictionService()
anomaly_service = AnomalyDetectionService()

@router.post("/train-model")
async def train_risk_model(db: Client = Depends(get_db)):
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
async def predict_project_risk(project_id: int, db: Client = Depends(get_db)):
    """Predict risk for a specific project"""
    try:
        prediction = risk_service.predict_risk(db, project_id)
        
        # Save prediction to Supabase
        risk_data = {
            'project_id': project_id,
            'date': datetime.now().date().isoformat(),
            'overall_risk_score': prediction['overall_risk_score'],
            'schedule_risk': prediction['component_risks']['schedule_risk'],
            'budget_risk': prediction['component_risks']['budget_risk'],
            'quality_risk': prediction['component_risks']['quality_risk'],
            'resource_risk': prediction['component_risks']['resource_risk'],
            'technical_risk': prediction['component_risks']['technical_risk'],
            'risk_factors': prediction.get('feature_importance', {}),
            'predictions': prediction
        }
        
        db.table('risk_scores').insert(risk_data).execute()
        
        return prediction
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error predicting risk: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

@router.get("/dashboard")
async def get_risk_dashboard(db: Client = Depends(get_db)):
    """Get risk dashboard data for all projects"""
    try:
        # Get latest risk scores for all projects using Supabase query
        latest_scores = db.table("risk_scores").select(
            "project_id, overall_risk_score, schedule_risk, budget_risk, quality_risk, resource_risk, technical_risk, date"
        ).order("date.desc").execute().data
        
        # Group by project_id and get the latest record for each
        latest_scores_dict = {}
        for score in latest_scores:
            project_id = score['project_id']
            if project_id not in latest_scores_dict or score['date'] > latest_scores_dict[project_id]['date']:
                latest_scores_dict[project_id] = score
        
        latest_scores = list(latest_scores_dict.values())
        
        high_risk = sum(1 for s in latest_scores if s['overall_risk_score'] > 70)
        medium_risk = sum(1 for s in latest_scores if 30 <= s['overall_risk_score'] <= 70)
        low_risk = sum(1 for s in latest_scores if s['overall_risk_score'] < 30)
        
        dashboard_data = {
            "total_projects": len(latest_scores),
            "high_risk_projects": high_risk,
            "medium_risk_projects": medium_risk,
            "low_risk_projects": low_risk,
            "projects": [
                {
                    "project_id": score['project_id'],
                    "overall_risk": float(score['overall_risk_score']) if score['overall_risk_score'] else 0,
                    "schedule_risk": float(score['schedule_risk']) if score['schedule_risk'] else 0,
                    "budget_risk": float(score['budget_risk']) if score['budget_risk'] else 0,
                    "quality_risk": float(score['quality_risk']) if score['quality_risk'] else 0,
                    "resource_risk": float(score['resource_risk']) if score['resource_risk'] else 0,
                    "technical_risk": float(score['technical_risk']) if score['technical_risk'] else 0,
                    "last_updated": score['date'] if score['date'] else None
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
    db: Client = Depends(get_db)
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
    db: Client = Depends(get_db)
):
    """Get anomaly summary for a specific project"""
    try:
        summary = anomaly_service.get_project_anomaly_summary(db, project_id, days_back)
        return summary
    
    except Exception as e:
        logger.error(f"Error getting project anomalies: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")