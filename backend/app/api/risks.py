# backend/app/api/risks.py (FIXED)

from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
import logging
from datetime import datetime, timedelta

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
        # Get latest risk scores for all projects
        latest_scores = db.table("risk_scores").select(
            "project_id, overall_risk_score, schedule_risk, budget_risk, quality_risk, resource_risk, technical_risk, date"
        ).order("date", desc=True).execute().data
        
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

# ============= ANOMALY DETECTION ENDPOINTS =============

@router.post("/anomalies/detect")
async def detect_anomalies(
    days_back: int = Query(default=30, ge=1, le=90, description="Number of days to analyze"),
    project_id: Optional[int] = Query(default=None, description="Optional: Analyze specific project"),
    db: Client = Depends(get_db)
):
    """
    Comprehensive anomaly detection in daily logs
    Detects: missing logs, unusual hours, productivity issues, pattern changes
    """
    try:
        anomalies = anomaly_service.detect_daily_log_anomalies(db, days_back, project_id)
        
        # Group anomalies by type for summary
        by_type = {}
        by_severity = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0}
        
        for anomaly in anomalies:
            anom_type = anomaly['anomaly_type']
            severity = anomaly['severity']
            
            by_type[anom_type] = by_type.get(anom_type, 0) + 1
            by_severity[severity] = by_severity.get(severity, 0) + 1
        
        return {
            "message": f"Anomaly detection completed for last {days_back} days",
            "period_days": days_back,
            "total_anomalies": len(anomalies),
            "by_severity": by_severity,
            "by_type": by_type,
            "critical_count": by_severity['critical'],
            "high_count": by_severity['high'],
            "anomalies": anomalies[:50]  # Return top 50 for API response
        }
    
    except Exception as e:
        logger.error(f"Error detecting anomalies: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Anomaly detection failed: {str(e)}")

@router.get("/anomalies/project/{project_id}")
async def get_project_anomalies(
    project_id: int,
    days_back: int = Query(default=7, ge=1, le=30, description="Number of days to retrieve"),
    db: Client = Depends(get_db)
):
    """Get anomaly summary for a specific project"""
    try:
        summary = anomaly_service.get_project_anomaly_summary(db, project_id, days_back)
        return summary
    
    except Exception as e:
        logger.error(f"Error getting project anomalies: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.get("/anomalies/employee/{employee_id}")
async def get_employee_anomalies(
    employee_id: int,
    days_back: int = Query(default=30, ge=1, le=90, description="Number of days to retrieve"),
    db: Client = Depends(get_db)
):
    """Get anomaly summary for a specific employee"""
    try:
        summary = anomaly_service.get_employee_anomaly_summary(db, employee_id, days_back)
        return summary
    
    except Exception as e:
        logger.error(f"Error getting employee anomalies: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.get("/anomalies/dashboard")
async def get_anomalies_dashboard(
    days_back: int = Query(default=7, ge=1, le=30, description="Number of days for dashboard"),
    db: Client = Depends(get_db)
):
    """Get comprehensive anomaly dashboard data"""
    try:
        start_date = (datetime.now() - timedelta(days=days_back)).date().isoformat()
        
        # Get all anomalies
        anomalies_response = db.table("anomalies").select(
            "*, employees(name, role), projects(name)"
        ).gte("detected_at", start_date).execute()
        anomalies = anomalies_response.data
        
        # Group by various dimensions
        by_severity = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0}
        by_type = {}
        by_employee = {}
        by_project = {}
        
        for anomaly in anomalies:
            severity = anomaly['severity']
            anom_type = anomaly['anomaly_type']
            
            by_severity[severity] = by_severity.get(severity, 0) + 1
            by_type[anom_type] = by_type.get(anom_type, 0) + 1
            
            if anomaly.get('employee_id'):
                emp_name = anomaly.get('employees', {}).get('name', 'Unknown') if anomaly.get('employees') else 'Unknown'
                by_employee[emp_name] = by_employee.get(emp_name, 0) + 1
            
            if anomaly.get('project_id'):
                proj_name = anomaly.get('projects', {}).get('name', 'Unknown') if anomaly.get('projects') else 'Unknown'
                by_project[proj_name] = by_project.get(proj_name, 0) + 1
        
        # Get top issues
        top_employees = sorted(by_employee.items(), key=lambda x: x[1], reverse=True)[:10]
        top_projects = sorted(by_project.items(), key=lambda x: x[1], reverse=True)[:10]
        
        # Recent critical anomalies
        critical_anomalies = [a for a in anomalies if a['severity'] == 'critical']
        critical_anomalies.sort(key=lambda x: x['detected_at'], reverse=True)
        
        return {
            "period_days": days_back,
            "total_anomalies": len(anomalies),
            "summary": {
                "by_severity": by_severity,
                "by_type": by_type,
                "affected_employees": len(by_employee),
                "affected_projects": len(by_project)
            },
            "top_employees_with_anomalies": [
                {"employee": emp, "count": count} for emp, count in top_employees
            ],
            "top_projects_with_anomalies": [
                {"project": proj, "count": count} for proj, count in top_projects
            ],
            "recent_critical_anomalies": [
                {
                    "id": a['id'],
                    "type": a['anomaly_type'],
                    "description": a['description'],
                    "detected_at": a['detected_at'],
                    "employee": a.get('employees', {}).get('name') if a.get('employees') else None,
                    "project": a.get('projects', {}).get('name') if a.get('projects') else None
                }
                for a in critical_anomalies[:10]
            ]
        }
    
    except Exception as e:
        logger.error(f"Error getting anomaly dashboard: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@router.post("/detect-anomalies")
async def detect_anomalies_endpoint(
    days_back: int = Query(default=30, ge=1, le=90, description="Number of days to analyze"),
    project_id: Optional[int] = Query(default=None, description="Optional: Analyze specific project"),
    db: Client = Depends(get_db)
):
    """
    Detect anomalies in daily logs (matches expected URL structure)
    Detects: missing logs, unusual hours, productivity issues, pattern changes
    """
    try:
        anomalies = anomaly_service.detect_daily_log_anomalies(db, days_back, project_id)

        # Group anomalies by type for summary
        by_type = {}
        by_severity = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0}

        for anomaly in anomalies:
            anom_type = anomaly['anomaly_type']
            severity = anomaly['severity']

            by_type[anom_type] = by_type.get(anom_type, 0) + 1
            by_severity[severity] = by_severity.get(severity, 0) + 1

        return {
            "message": f"Anomaly detection completed for last {days_back} days",
            "period_days": days_back,
            "total_anomalies": len(anomalies),
            "by_severity": by_severity,
            "by_type": by_type,
            "critical_count": by_severity['critical'],
            "high_count": by_severity['high'],
            "anomalies": anomalies[:50]  # Return top 50 for API response
        }

    except Exception as e:
        logger.error(f"Error detecting anomalies: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Anomaly detection failed: {str(e)}")

@router.get("/anomalies/list")
async def list_anomalies(
    days_back: int = Query(default=7, ge=1, le=90, description="Number of days to retrieve"),
    severity: Optional[str] = Query(default=None, description="Filter by severity"),
    anomaly_type: Optional[str] = Query(default=None, description="Filter by type"),
    project_id: Optional[int] = Query(default=None, description="Filter by project"),
    employee_id: Optional[int] = Query(default=None, description="Filter by employee"),
    limit: int = Query(default=50, le=200, description="Maximum results"),
    db: Client = Depends(get_db)
):
    """List anomalies with optional filters"""
    try:
        start_date = (datetime.now() - timedelta(days=days_back)).date().isoformat()
        
        # Build query
        query = db.table("anomalies").select(
            "*, employees(name, role), projects(name)"
        ).gte("detected_at", start_date)
        
        if severity:
            query = query.eq("severity", severity)
        if anomaly_type:
            query = query.eq("anomaly_type", anomaly_type)
        if project_id:
            query = query.eq("project_id", project_id)
        if employee_id:
            query = query.eq("employee_id", employee_id)
        
        query = query.order("detected_at", desc=True).limit(limit)
        
        response = query.execute()
        anomalies = response.data
        
        return {
            "total": len(anomalies),
            "filters": {
                "days_back": days_back,
                "severity": severity,
                "anomaly_type": anomaly_type,
                "project_id": project_id,
                "employee_id": employee_id
            },
            "anomalies": [
                {
                    "id": a['id'],
                    "type": a['anomaly_type'],
                    "severity": a['severity'],
                    "description": a['description'],
                    "detected_at": a['detected_at'],
                    "employee": {
                        "id": a.get('employee_id'),
                        "name": a.get('employees', {}).get('name') if a.get('employees') else None
                    },
                    "project": {
                        "id": a.get('project_id'),
                        "name": a.get('projects', {}).get('name') if a.get('projects') else None
                    },
                    "is_resolved": a.get('is_resolved', False),
                    "metadata": a.get('metadata', {})
                }
                for a in anomalies
            ]
        }
    
    except Exception as e:
        logger.error(f"Error listing anomalies: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")