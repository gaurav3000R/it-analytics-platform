from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional, Dict, Any
import pandas as pd
from datetime import datetime, timedelta
import logging

from app.database import get_db
from app.models import Project, DailyLog, Sprint  # FIXED
from app.models.employee import Employee
from app.models.risk import RiskScore, Anomaly

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/analytics", tags=["analytics"])

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

@router.get("/trends")
async def get_trends_data(
    days_back: int = Query(default=30, ge=7, le=90),
    db: Session = Depends(get_db)
):
    """Get trend data for charts"""
    try:
        start_date = datetime.now() - timedelta(days=days_back)
        
        # Daily hours trend
        daily_hours = db.query(
            func.date(DailyLog.date).label('date'),
            func.sum(DailyLog.hours_logged).label('total_hours')
        ).filter(
            DailyLog.date >= start_date
        ).group_by(func.date(DailyLog.date)).all()
        
        # Daily completion rate trend
        daily_completion = db.query(
            func.date(DailyLog.date).label('date'),
            func.avg(DailyLog.completion_percentage).label('avg_completion')
        ).filter(
            DailyLog.date >= start_date
        ).group_by(func.date(DailyLog.date)).all()
        
        # Daily issues trend
        daily_issues = db.query(
            func.date(DailyLog.date).label('date'),
            func.sum(DailyLog.issues_reported).label('total_issues')
        ).filter(
            DailyLog.date >= start_date
        ).group_by(func.date(DailyLog.date)).all()
        
        return {
            "hours_trend": [
                {"date": str(row.date), "value": float(row.total_hours or 0)}
                for row in daily_hours
            ],
            "completion_trend": [
                {"date": str(row.date), "value": float(row.avg_completion or 0)}
                for row in daily_completion
            ],
            "issues_trend": [
                {"date": str(row.date), "value": int(row.total_issues or 0)}
                for row in daily_issues
            ]
        }
    
    except Exception as e:
        logger.error(f"Error getting trends data: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/team-performance")
async def get_team_performance(
    days_back: int = Query(default=30, ge=7, le=90),
    db: Session = Depends(get_db)
):
    """Get team performance analytics"""
    try:
        start_date = datetime.now() - timedelta(days=days_back)
        
        # Employee performance summary
        employee_stats = db.query(
            Employee.id,
            Employee.name,
            Employee.role,
            func.sum(DailyLog.hours_logged).label('total_hours'),
            func.avg(DailyLog.completion_percentage).label('avg_completion'),
            func.sum(DailyLog.issues_reported).label('total_issues'),
            func.count(func.distinct(func.date(DailyLog.date))).label('active_days')
        ).join(DailyLog).filter(
            DailyLog.date >= start_date
        ).group_by(Employee.id, Employee.name, Employee.role).all()
        
        team_performance = []
        for stat in employee_stats:
            productivity_score = (stat.avg_completion or 0) * (stat.total_hours or 0) / 100
            
            team_performance.append({
                "employee_id": stat.id,
                "name": stat.name,
                "role": stat.role,
                "total_hours": float(stat.total_hours or 0),
                "avg_completion": float(stat.avg_completion or 0),
                "total_issues": int(stat.total_issues or 0),
                "active_days": int(stat.active_days or 0),
                "productivity_score": float(productivity_score),
                "avg_hours_per_day": float((stat.total_hours or 0) / max(1, stat.active_days or 1))
            })
        
        # Sort by productivity score
        team_performance.sort(key=lambda x: x['productivity_score'], reverse=True)
        
        return {
            "team_performance": team_performance,
            "period_days": days_back,
            "total_team_members": len(team_performance)
        }
    
    except Exception as e:
        logger.error(f"Error getting team performance: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))# IT Analytics Platform - Complete Backend Structure