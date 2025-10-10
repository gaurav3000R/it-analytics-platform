#backend/app/api/analytics.py

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional, Dict, Any
import pandas as pd
from datetime import datetime, timedelta
import logging
from supabase import Client

from app.database import connect_db
from app.services.cost_forecasting import CostForecastingService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/analytics", tags=["analytics"])

@router.get("/risk-dashboard")
async def get_risk_dashboard(
    days_back: int = Query(default=30, ge=7, le=90),
):
    """Get comprehensive risk dashboard data"""
    try:
        db: Client = connect_db()
        if not db:
            raise HTTPException(status_code=500, detail="Failed to connect to database")

        # Get latest risk scores for all projects
        latest_scores_response = db.table("risk_scores").select("*").order("date", desc=True).execute()
        latest_scores = latest_scores_response.data
        unique_scores = {}
        for score in latest_scores:
            if score["project_id"] not in unique_scores:
                unique_scores[score["project_id"]] = score
        latest_scores = list(unique_scores.values())

        # Calculate risk distribution
        risk_distribution = {
            "high_risk": len([s for s in latest_scores if s["overall_risk_score"] > 70]),
            "medium_risk": len([s for s in latest_scores if 30 <= s["overall_risk_score"] <= 70]),
            "low_risk": len([s for s in latest_scores if s["overall_risk_score"] < 30])
        }

        # Get recent anomalies
        start_date = (datetime.now() - timedelta(days=7)).isoformat()
        recent_anomalies_response = db.table("anomalies").select("id").gte("detected_at", start_date).execute()
        recent_anomalies = len(recent_anomalies_response.data)

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

async def get_utilization_alerts(db: Client, days_back: int) -> List[Dict[str, Any]]:
    """Get resource utilization alerts"""
    start_date = (datetime.now() - timedelta(days=days_back)).isoformat()

    # Fetch employees and daily logs
    employees_response = db.table("employees").select("id, name, role, max_hours_per_day").eq("is_active", True).execute()
    daily_logs_response = db.table("daily_logs").select("employee_id, hours_logged, date").gte("date", start_date).execute()

    employees = {emp["id"]: emp for emp in employees_response.data}
    daily_logs = daily_logs_response.data

    # Aggregate utilization data
    utilization_data = []
    for emp_id in employees:
        emp_logs = [log for log in daily_logs if log["employee_id"] == emp_id]
        if not emp_logs:
            continue
        avg_daily_hours = sum(log["hours_logged"] for log in emp_logs) / len(set(log["date"] for log in emp_logs))
        active_days = len(set(log["date"] for log in emp_logs))
        utilization_data.append({
            "id": emp_id,
            "name": employees[emp_id]["name"],
            "role": employees[emp_id]["role"],
            "max_hours_per_day": employees[emp_id]["max_hours_per_day"],
            "avg_daily_hours": avg_daily_hours,
            "active_days": active_days
        })

    alerts = []
    for emp_data in utilization_data:
        expected_hours = emp_data["max_hours_per_day"]
        actual_hours = emp_data["avg_daily_hours"] or 0
        utilization_rate = actual_hours / expected_hours if expected_hours > 0 else 0

        if utilization_rate < 0.6:
            alerts.append({
                "type": "underutilization",
                "employee_id": emp_data["id"],
                "employee_name": emp_data["name"],
                "severity": "high" if utilization_rate < 0.4 else "medium",
                "utilization_rate": utilization_rate,
                "message": f"{emp_data['name']} is underutilized ({utilization_rate:.1%})"
            })
        elif utilization_rate > 1.3:
            alerts.append({
                "type": "overutilization",
                "employee_id": emp_data["id"],
                "employee_name": emp_data["name"],
                "severity": "high" if utilization_rate > 1.5 else "medium",
                "utilization_rate": utilization_rate,
                "message": f"{emp_data['name']} is overworked ({utilization_rate:.1%})"
            })

    return alerts

async def get_cost_alerts(db: Client) -> List[Dict[str, Any]]:
    """Get cost overrun alerts"""
    cost_service = CostForecastingService()
    alerts = []

    projects_response = db.table("projects").select("id, name, project_budget_usd").execute()
    projects = projects_response.data

    for project in projects:
        try:
            forecast = cost_service.forecast_cost_overrun(db, project["id"], 30)
            if forecast.get("overrun_probability", 0) > 0.6:
                alerts.append({
                    "project_id": project["id"],
                    "project_name": project["name"] or f"Project {project['id']}",
                    "overrun_probability": forecast["overrun_probability"],
                    "severity": "high" if forecast["overrun_probability"] > 0.8 else "medium",
                    "message": f"Potential cost overrun: {forecast['overrun_probability']:.1%}"
                })
        except:
            continue

    return alerts

async def get_recent_anomalies(db: Client, limit: int = 5) -> List[Dict[str, Any]]:
    """Get recent anomalies"""
    anomalies_response = db.table("anomalies").select("*").eq("is_resolved", False).order("detected_at", desc=True).limit(limit).execute()
    anomalies = anomalies_response.data

    return [
        {
            "id": anomaly["id"],
            "type": anomaly["anomaly_type"],
            "severity": anomaly["severity"],
            "description": anomaly["description"],
            "detected_at": anomaly["detected_at"],
            "project_id": anomaly["project_id"]
        }
        for anomaly in anomalies
    ]

async def get_trending_risks(db: Client, days_back: int) -> List[Dict[str, Any]]:
    """Get trending risk factors"""
    start_date = (datetime.now() - timedelta(days=days_back)).isoformat()

    # Aggregate risk scores
    risk_trends_response = db.table("risk_scores").select("project_id, overall_risk_score").gte("date", start_date).execute()
    risk_trends = risk_trends_response.data

    # Group by project_id
    project_risks = {}
    for trend in risk_trends:
        pid = trend["project_id"]
        if pid not in project_risks:
            project_risks[pid] = []
        project_risks[pid].append(trend["overall_risk_score"])

    trending_risks = []
    for project_id, scores in project_risks.items():
        avg_risk = sum(scores) / len(scores)
        max_risk = max(scores)
        min_risk = min(scores)
        if avg_risk > 60:
            trending_risks.append({
                "project_id": project_id,
                "avg_risk": avg_risk,
                "risk_trend": "increasing" if max_risk > avg_risk else "stable",
                "severity": "high" if avg_risk > 75 else "medium"
            })

    return sorted(trending_risks, key=lambda x: x["avg_risk"], reverse=True)[:5]

@router.get("/overview")
async def get_analytics_overview():
    """Get overall analytics overview"""
    try:
        db: Client = connect_db()
        if not db:
            raise HTTPException(status_code=500, detail="Failed to connect to database")

        # Basic counts
        total_projects_response = db.table("projects").select("id").execute()
        total_projects = len(total_projects_response.data)

        total_employees_response = db.table("employees").select("id").eq("is_active", True).execute()
        total_employees = len(total_employees_response.data)

        # Recent activity (last 30 days)
        start_date = (datetime.now() - timedelta(days=30)).isoformat()
        recent_logs_response = db.table("daily_logs").select("id").gte("date", start_date).execute()
        recent_logs = len(recent_logs_response.data)

        # Risk distribution
        latest_risks_response = db.table("risk_scores").select("*").order("date", desc=True).execute()
        latest_risks = latest_risks_response.data
        unique_risks = {}
        for risk in latest_risks:
            if risk["project_id"] not in unique_risks:
                unique_risks[risk["project_id"]] = risk
        latest_risks = list(unique_risks.values())

        high_risk = len([r for r in latest_risks if r["overall_risk_score"] > 70])
        medium_risk = len([r for r in latest_risks if 30 <= r["overall_risk_score"] <= 70])
        low_risk = len([r for r in latest_risks if r["overall_risk_score"] < 30])

        # Recent anomalies (last 7 days)
        anomaly_start_date = (datetime.now() - timedelta(days=7)).isoformat()
        recent_anomalies_response = db.table("anomalies").select("id").gte("detected_at", anomaly_start_date).execute()
        recent_anomalies = len(recent_anomalies_response.data)

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