from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional, Dict, Any
import pandas as pd
from datetime import datetime, timedelta
import logging

from app.database import get_db
from app.models.project import Project
from app.models.daily_log import DailyLog
from app.models.sprint import Sprint
from app.models.employee import Employee
from app.models.risk import RiskScore, Anomaly

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/analytics", tags=["analytics"])

@router.get("/risk-dashboard")
async def get_risk_dashboard(
    days_back: int = Query(default=30, ge=7, le=90),
    db: Session = Depends(get_db)
):
    """Get comprehensive risk dashboard data"""
    try:
        # Get latest risk scores for all projects
        latest_scores = db.query(RiskScore).distinct(RiskScore.project_id)\
                        .order_by(RiskScore.project_id, RiskScore.date.desc()).all()
        
        # Calculate risk distribution
        risk_distribution = {
            "high_risk": len([s for s in latest_scores if s.overall_risk_score > 70]),
            "medium_risk": len([s for s in latest_scores if 30 <= s.overall_risk_score <= 70]),
            "low_risk": len([s for s in latest_scores if s.overall_risk_score < 30])
        }
        
        # Get recent anomalies
        recent_anomalies = db.query(Anomaly).filter(
            Anomaly.detected_at >= datetime.now() - timedelta(days=7)
        ).count()
        
        # Get resource utilization alerts
        utilization_alerts = await get_utilization_alerts(db, days_back)
        
        # Get cost overrun forecasts
        cost_alerts = await get_cost_alerts(db)
        
        dashboard_data = {
            "summary": {
                "total_projects": len(latest_scores),
                "high_risk_projects": risk_distribution["high_risk"],
                "recent_anomalies": recent_anomalies,
                "utilization_alerts": len(utilization_alerts),
                "cost_alerts": len(cost_alerts)
            },
            "risk_distribution": risk_distribution,
            "alerts": {
                "utilization": utilization_alerts[:5],
                "cost": cost_alerts[:5],
                "anomalies": await get_recent_anomalies(db, 5)
            },
            "trending_risks": await get_trending_risks(db, days_back)
        }
        
        return dashboard_data
    
    except Exception as e:
        logger.error(f"Error getting risk dashboard: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

async def get_utilization_alerts(db: Session, days_back: int) -> List[Dict[str, Any]]:
    """Get resource utilization alerts"""
    start_date = datetime.now() - timedelta(days=days_back)
    
    utilization_data = db.query(
        Employee.id,
        Employee.name,
        Employee.role,
        Employee.max_hours_per_day,
        func.avg(DailyLog.hours_logged).label('avg_daily_hours'),
        func.count(func.distinct(func.date(DailyLog.date))).label('active_days')
    ).join(DailyLog).filter(
        DailyLog.date >= start_date,
        Employee.is_active == True
    ).group_by(Employee.id).all()
    
    alerts = []
    
    for emp_data in utilization_data:
        expected_hours = emp_data.max_hours_per_day
        actual_hours = emp_data.avg_daily_hours or 0
        utilization_rate = actual_hours / expected_hours if expected_hours > 0 else 0
        
        if utilization_rate < 0.6:
            alerts.append({
                "type": "underutilization",
                "employee_id": emp_data.id,
                "employee_name": emp_data.name,
                "severity": "high" if utilization_rate < 0.4 else "medium",
                "utilization_rate": utilization_rate,
                "message": f"{emp_data.name} is underutilized ({utilization_rate:.1%})"
            })
        elif utilization_rate > 1.3:
            alerts.append({
                "type": "overutilization", 
                "employee_id": emp_data.id,
                "employee_name": emp_data.name,
                "severity": "high" if utilization_rate > 1.5 else "medium",
                "utilization_rate": utilization_rate,
                "message": f"{emp_data.name} is overworked ({utilization_rate:.1%})"
            })
    
    return alerts

async def get_cost_alerts(db: Session) -> List[Dict[str, Any]]:
    """Get cost overrun alerts"""
    from app.services.cost_forecasting import CostForecastingService
    
    cost_service = CostForecastingService()
    alerts = []
    
    projects = db.query(Project).all()
    for project in projects:
        try:
            forecast = cost_service.forecast_cost_overrun(db, project.id, 30)
            if forecast.get('overrun_probability', 0) > 0.6:
                alerts.append({
                    "project_id": project.id,
                    "project_name": project.name or f"Project {project.id}",
                    "overrun_probability": forecast['overrun_probability'],
                    "severity": "high" if forecast['overrun_probability'] > 0.8 else "medium",
                    "message": f"Potential cost overrun: {forecast['overrun_probability']:.1%}"
                })
        except:
            continue
    
    return alerts

async def get_recent_anomalies(db: Session, limit: int = 5) -> List[Dict[str, Any]]:
    """Get recent anomalies"""
    anomalies = db.query(Anomaly).filter(
        Anomaly.is_resolved == False
    ).order_by(Anomaly.detected_at.desc()).limit(limit).all()
    
    return [
        {
            "id": anomaly.id,
            "type": anomaly.anomaly_type,
            "severity": anomaly.severity,
            "description": anomaly.description,
            "detected_at": anomaly.detected_at.isoformat(),
            "project_id": anomaly.project_id
        }
        for anomaly in anomalies
    ]

async def get_trending_risks(db: Session, days_back: int) -> List[Dict[str, Any]]:
    """Get trending risk factors"""
    start_date = datetime.now() - timedelta(days=days_back)
    
    risk_trends = db.query(
        RiskScore.project_id,
        func.avg(RiskScore.overall_risk_score).label('avg_risk'),
        func.max(RiskScore.overall_risk_score).label('max_risk'),
        func.min(RiskScore.overall_risk_score).label('min_risk')
    ).filter(
        RiskScore.date >= start_date
    ).group_by(RiskScore.project_id).all()
    
    trending_risks = []
    
    for trend in risk_trends:
        if trend.avg_risk > 60:
            trending_risks.append({
                "project_id": trend.project_id,
                "avg_risk": trend.avg_risk,
                "risk_trend": "increasing" if trend.max_risk > trend.avg_risk else "stable",
                "severity": "high" if trend.avg_risk > 75 else "medium"
            })
    
    return sorted(trending_risks, key=lambda x: x['avg_risk'], reverse=True)[:5]

@router.get("/overview")
async def get_analytics_overview(db: Session = Depends(get_db)):
    """Get overall analytics overview"""
    try:
        # Basic counts
        total_projects = db.query(Project).count()
        total_employees = db.query(Employee).filter(Employee.is_active == True).count()
        
        # Recent activity (last 30 days)
        start_date = datetime.now() - timedelta(days=30)
        recent_logs = db.query(DailyLog).filter(DailyLog.date >= start_date).count()
        
        # Risk distribution
        latest_risks = db.query(RiskScore).distinct(RiskScore.project_id)\
                      .order_by(RiskScore.project_id, RiskScore.date.desc()).all()
        
        high_risk = len([r for r in latest_risks if r.overall_risk_score > 70])
        medium_risk = len([r for r in latest_risks if 30 <= r.overall_risk_score <= 70])
        low_risk = len([r for r in latest_risks if r.overall_risk_score < 30])
        
        # Recent anomalies (last 7 days)
        recent_anomalies = db.query(Anomaly).filter(
            Anomaly.detected_at >= datetime.now() - timedelta(days=7)
        ).count()
        
        return {
            "summary": {
                "total_projects": total_projects,
                "total_employees": total_employees,
                "recent_activity_logs": recent_logs,
                "recent_anomalies": recent_anomalies
            },
            "risk_distribution": {
                "high_risk": high_risk,
                "medium_risk": medium_risk,
                "low_risk": low_risk
            },
            "period": "Last 30 days"
        }
    
    except Exception as e:
        logger.error(f"Error getting analytics overview: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))