#backend/app/api/cost_forecasting.py

from fastapi import APIRouter, Depends, HTTPException, Query
from supabase import Client
from typing import Optional
import logging

from app.database import get_db
from app.services.cost_forecasting import CostForecastingService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/cost-forecasting", tags=["cost-forecasting"])
cost_service = CostForecastingService()

@router.get("/forecast/{project_id}")
async def forecast_cost_overrun(
    project_id: int,
    forecast_days: int = Query(default=30, ge=7, le=180, description="Number of days to forecast ahead"),
    db: Client = Depends(get_db)
):
    """
    Get comprehensive cost overrun forecast for a specific project
    
    Returns detailed analysis including:
    - Current spending status
    - Burn rate trends
    - Future cost predictions
    - Overrun probability analysis
    - Risk factors
    - Actionable recommendations
    """
    try:
        forecast = cost_service.forecast_cost_overrun(db, project_id, forecast_days)
        return forecast
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error forecasting cost for project {project_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to forecast cost overrun: {str(e)}")

@router.get("/budget-alerts")
async def get_budget_alerts(
    min_probability: float = Query(default=0.5, ge=0.0, le=1.0, description="Minimum overrun probability to include"),
    db: Client = Depends(get_db)
):
    """
    Get budget alerts for all projects with overrun risk above threshold
    
    Returns projects sorted by overrun probability
    """
    try:
        projects_response = db.table("projects").select("id, project_id, name").eq("status", "active").execute()
        projects = projects_response.data
        
        alerts = []
        
        for project in projects:
            try:
                forecast = cost_service.forecast_cost_overrun(db, project["id"], 30)
                
                if forecast.get('overrun_analysis', {}).get('overrun_probability', 0) >= min_probability:
                    alerts.append({
                        "project_id": project["id"],
                        "project_identifier": project["project_id"],
                        "project_name": forecast.get('project_name', project.get('name')),
                        "overrun_probability": forecast['overrun_analysis']['overrun_probability'],
                        "expected_overrun_amount": forecast['overrun_analysis']['expected_overrun_amount'],
                        "risk_level": forecast['overrun_analysis']['risk_level'],
                        "budget_utilization": forecast['current_status']['budget_utilization_percentage'],
                        "alert_severity": "critical" if forecast['overrun_analysis']['risk_level'] == 'critical' else
                                        "high" if forecast['overrun_analysis']['risk_level'] == 'high' else "medium"
                    })
            except Exception as e:
                logger.warning(f"Could not forecast project {project['id']}: {e}")
                continue
        
        # Sort by overrun probability (highest first)
        alerts.sort(key=lambda x: x['overrun_probability'], reverse=True)
        
        return {
            "total_alerts": len(alerts),
            "critical_alerts": len([a for a in alerts if a['alert_severity'] == 'critical']),
            "high_alerts": len([a for a in alerts if a['alert_severity'] == 'high']),
            "alerts": alerts
        }
        
    except Exception as e:
        logger.error(f"Error generating budget alerts: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate budget alerts: {str(e)}")

@router.get("/portfolio-summary")
async def get_portfolio_cost_summary(db: Client = Depends(get_db)):
    """
    Get portfolio-wide cost forecast summary
    
    Returns aggregated metrics across all active projects
    """
    try:
        summary = cost_service.get_all_projects_forecast_summary(db)
        return summary
    except Exception as e:
        logger.error(f"Error generating portfolio summary: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate portfolio summary: {str(e)}")

@router.get("/forecast-history/{project_id}")
async def get_forecast_history(
    project_id: int,
    days_back: int = Query(default=30, ge=7, le=90, description="Number of days of history to retrieve"),
    db: Client = Depends(get_db)
):
    """
    Get historical forecast data for a project
    
    Shows how predictions have evolved over time
    """
    try:
        from datetime import datetime, timedelta
        
        start_date = (datetime.now() - timedelta(days=days_back)).date().isoformat()
        
        history_response = db.table("cost_forecasts").select(
            "forecast_date, overrun_probability, projected_final_cost, "
            "current_spend, forecast_accuracy_score"
        ).eq("project_id", project_id).gte("forecast_date", start_date).order("forecast_date").execute()
        
        history = history_response.data
        
        if not history:
            raise HTTPException(status_code=404, detail="No forecast history found for this project")
        
        return {
            "project_id": project_id,
            "history_period_days": days_back,
            "forecasts": history,
            "trend_analysis": {
                "probability_trend": "increasing" if len(history) > 1 and 
                    history[-1]['overrun_probability'] > history[0]['overrun_probability'] else "stable",
                "accuracy_avg": sum(f['forecast_accuracy_score'] for f in history) / len(history)
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving forecast history: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve forecast history: {str(e)}")

@router.get("/spending-trends/{project_id}")
async def get_spending_trends(
    project_id: int,
    days_back: int = Query(default=30, ge=7, le=90, description="Number of days of trends to analyze"),
    db: Client = Depends(get_db)
):
    """
    Get detailed spending trends for a project
    
    Returns daily spending patterns and analysis
    """
    try:
        from datetime import datetime, timedelta
        
        start_date = (datetime.now() - timedelta(days=days_back)).date().isoformat()
        
        # Get daily logs
        logs_response = db.table("daily_logs").select(
            "date, hours_logged, employee_id"
        ).eq("project_id", project_id).gte("date", start_date).order("date").execute()
        
        if not logs_response.data:
            raise HTTPException(status_code=404, detail="No spending data found for this project")
        
        # Get employee rates
        employee_ids = list(set(log['employee_id'] for log in logs_response.data))
        employees_response = db.table("employees").select("id, hourly_rate").in_("id", employee_ids).execute()
        employee_rates = {emp['id']: emp.get('hourly_rate', 75.0) for emp in employees_response.data}
        
        # Calculate daily costs
        import pandas as pd
        daily_costs = {}
        for log in logs_response.data:
            date = log['date']
            cost = log['hours_logged'] * employee_rates.get(log['employee_id'], 75.0)
            daily_costs[date] = daily_costs.get(date, 0) + cost
        
        # Create trends
        dates = sorted(daily_costs.keys())
        cumulative_cost = 0
        trends = []
        
        for date in dates:
            cumulative_cost += daily_costs[date]
            trends.append({
                'date': date,
                'daily_cost': daily_costs[date],
                'cumulative_cost': cumulative_cost
            })
        
        # Calculate statistics
        costs = [daily_costs[d] for d in dates]
        avg_cost = sum(costs) / len(costs) if costs else 0
        
        return {
            "project_id": project_id,
            "period_days": days_back,
            "daily_trends": trends,
            "statistics": {
                "total_spend": cumulative_cost,
                "avg_daily_cost": avg_cost,
                "max_daily_cost": max(costs) if costs else 0,
                "min_daily_cost": min(costs) if costs else 0,
                "days_with_spending": len(trends)
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving spending trends: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve spending trends: {str(e)}")