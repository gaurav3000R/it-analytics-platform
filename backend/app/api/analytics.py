# backend/app/api/analytics.py

from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional, Dict, Any
import pandas as pd
from datetime import datetime, timedelta
import logging
from supabase import Client

from app.database import get_db
from app.services.cost_forecasting import CostForecastingService
from app.services.risk_dashboard import RiskDashboardService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/analytics", tags=["analytics"])

# Initialize services
risk_dashboard_service = RiskDashboardService()

@router.get("/risk-dashboard")
async def get_risk_dashboard(
    days_back: int = Query(default=30, ge=7, le=90),
    max_projects: int = Query(default=500, le=1000),
    force_recalc: bool = Query(default=False),
    db: Client = Depends(get_db)
):
    """
    Get comprehensive risk dashboard data - OPTIMIZED VERSION
    
    This endpoint uses cached risk calculations for performance.
    Set force_recalc=true to recalculate all risks (slower).
    """
    try:
        logger.info(f"Fetching optimized risk dashboard (max_projects={max_projects})")
        
        # Get active projects
        projects_response = db.table("projects").select("id").eq(
            "status", "active"
        ).limit(max_projects).execute()
        
        project_ids = [p['id'] for p in projects_response.data]
        
        if not project_ids:
            return {
                "message": "No active projects found",
                "summary": {},
                "alerts": []
            }
        
        # Use optimized risk dashboard service
        dashboard = risk_dashboard_service.calculate_risk_dashboard_summary(
            db=db,
            project_ids=project_ids,
            force_recalculation=force_recalc
        )
        
        # Get alerts from other services
        utilization_alerts = await get_utilization_alerts_fast(db, days_back)
        cost_alerts = await get_cost_alerts_fast(db)
        anomaly_count = await get_anomaly_count_fast(db, days_back)
        
        # Build combined dashboard
        result = {
            "summary": {
                **dashboard['summary'],
                "utilization_alerts": len(utilization_alerts),
                "cost_alerts": len(cost_alerts),
                "recent_anomalies": anomaly_count
            },
            "risk_overview": {
                "risk_distribution": dashboard['summary']['risk_distribution'],
                "component_averages": dashboard['component_averages'],
                "flagged_projects": dashboard['flagged_projects']
            },
            "top_risk_projects": dashboard['top_risk_projects'][:10],
            "alerts": {
                "utilization": utilization_alerts[:5],
                "cost": cost_alerts[:5]
            },
            "generated_at": dashboard['generated_at']
        }
        
        return result

    except Exception as e:
        logger.error(f"Error getting risk dashboard: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


async def get_utilization_alerts_fast(db: Client, days_back: int) -> List[Dict[str, Any]]:
    """Fast utilization alerts retrieval"""
    try:
        start_date = (datetime.now() - timedelta(days=days_back)).isoformat()
        
        response = db.table("resource_utilization_alerts").select(
            "id, employee_id, alert_type, severity, utilization_rate, alert_message, "
            "employees(name)"
        ).gte("created_at", start_date).eq(
            "is_acknowledged", False
        ).order("severity").limit(10).execute()
        
        alerts = []
        for alert in response.data:
            emp_name = alert.get('employees', {}).get('name', 'Unknown') if alert.get('employees') else 'Unknown'
            alerts.append({
                "type": alert['alert_type'],
                "employee_name": emp_name,
                "severity": alert['severity'],
                "utilization_rate": alert.get('utilization_rate', 0),
                "message": alert['alert_message']
            })
        
        return alerts
    except Exception as e:
        logger.warning(f"Error fetching utilization alerts: {e}")
        return []


async def get_cost_alerts_fast(db: Client) -> List[Dict[str, Any]]:
    """Fast cost alerts retrieval"""
    try:
        # Get recent cost forecasts with high overrun probability
        response = db.table("cost_forecasts").select(
            "project_id, overrun_probability, overrun_amount, projects(name, project_id)"
        ).gte("overrun_probability", 0.6).order(
            "overrun_probability", desc=True
        ).limit(10).execute()
        
        alerts = []
        for forecast in response.data:
            proj_data = forecast.get('projects', {})
            alerts.append({
                "project_id": forecast['project_id'],
                "project_name": proj_data.get('name', 'Unknown') if proj_data else 'Unknown',
                "overrun_probability": forecast['overrun_probability'],
                "severity": "high" if forecast['overrun_probability'] > 0.8 else "medium",
                "message": f"High cost overrun risk: {forecast['overrun_probability']:.1%}"
            })
        
        return alerts
    except Exception as e:
        logger.warning(f"Error fetching cost alerts: {e}")
        return []


async def get_anomaly_count_fast(db: Client, days_back: int) -> int:
    """Fast anomaly count retrieval"""
    try:
        start_date = (datetime.now() - timedelta(days=7)).isoformat()
        
        response = db.table("anomalies").select(
            "id", count='exact'
        ).gte("detected_at", start_date).eq("is_resolved", False).execute()
        
        return response.count if response.count else 0
    except Exception as e:
        logger.warning(f"Error fetching anomaly count: {e}")
        return 0


@router.get("/overview")
async def get_analytics_overview(db: Client = Depends(get_db)):
    """Get overall analytics overview - OPTIMIZED"""
    try:
        # Parallel queries using batch approach
        total_projects_response = db.table("projects").select("id", count='exact').execute()
        total_projects = total_projects_response.count or 0

        total_employees_response = db.table("employees").select(
            "id", count='exact'
        ).eq("is_active", True).execute()
        total_employees = total_employees_response.count or 0

        # Recent activity (last 30 days)
        start_date = (datetime.now() - timedelta(days=30)).isoformat()
        recent_logs_response = db.table("daily_logs").select(
            "id", count='exact'
        ).gte("date", start_date).execute()
        recent_logs = recent_logs_response.count or 0

        # Risk distribution from cached summaries
        risk_summaries = db.table("risk_dashboard_summary").select(
            "risk_level"
        ).execute()
        
        risk_distribution = {
            'critical': 0,
            'high': 0,
            'medium': 0,
            'low': 0,
            'very_low': 0
        }
        
        for summary in risk_summaries.data:
            level = summary.get('risk_level', 'medium')
            risk_distribution[level] = risk_distribution.get(level, 0) + 1

        # Recent anomalies (last 7 days)
        anomaly_start_date = (datetime.now() - timedelta(days=7)).isoformat()
        recent_anomalies_response = db.table("anomalies").select(
            "id", count='exact'
        ).gte("detected_at", anomaly_start_date).execute()
        recent_anomalies = recent_anomalies_response.count or 0

        return {
            "summary": {
                "total_projects": total_projects,
                "total_employees": total_employees,
                "recent_activity_logs": recent_logs,
                "recent_anomalies": recent_anomalies
            },
            "risk_distribution": risk_distribution,
            "period": "Last 30 days",
            "generated_at": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Error getting analytics overview: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))