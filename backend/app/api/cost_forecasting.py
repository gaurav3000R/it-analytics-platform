# backend/app/api/cost_forecasting_optimized.py

from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from supabase import Client
from typing import Optional
import logging
from datetime import datetime, date

from app.database import get_db
from app.services.cost_forecasting import CostForecastingService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/cost-forecasting", tags=["cost-forecasting"])
cost_service = CostForecastingService()

@router.get("/forecast/{project_id}")
async def forecast_cost_overrun(
    project_id: int,
    forecast_days: int = Query(default=30, ge=7, le=180),
    db: Client = Depends(get_db)
):
    """Get cost forecast for specific project - uses cached data when available"""
    try:
        forecast = cost_service.forecast_cost_overrun(db, project_id, forecast_days)
        return forecast
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error forecasting cost for project {project_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to forecast: {str(e)}")


@router.get("/budget-alerts")
async def get_budget_alerts(
    min_probability: float = Query(default=0.5, ge=0.0, le=1.0),
    limit: int = Query(default=50, le=200),
    db: Client = Depends(get_db)
):
    """
    Get budget alerts - OPTIMIZED VERSION
    Returns cached forecasts with high overrun probability
    """
    try:
        # Use recent forecasts from database instead of recalculating
        today = date.today().isoformat()
        
        # Get forecasts from last 24 hours with high risk
        forecasts_response = db.table("cost_forecasts").select(
            "project_id, overrun_probability, overrun_amount, projected_final_cost, "
            "current_spend, total_budget, forecast_date, projects(project_id, name, status)"
        ).gte("forecast_date", today).gte(
            "overrun_probability", min_probability
        ).order("overrun_probability", desc=True).limit(limit).execute()
        
        forecasts = forecasts_response.data
        
        if not forecasts:
            # If no recent forecasts, return empty result
            return {
                "total_alerts": 0,
                "critical_alerts": 0,
                "high_alerts": 0,
                "alerts": [],
                "message": "No recent budget alerts. Run forecast analysis to generate alerts."
            }
        
        # Format alerts
        alerts = []
        for f in forecasts:
            proj_data = f.get('projects', {})
            
            # Only include active projects
            if proj_data and proj_data.get('status') != 'active':
                continue
            
            risk_level = (
                'critical' if f['overrun_probability'] > 0.8 else
                'high' if f['overrun_probability'] > 0.6 else
                'medium'
            )
            
            alerts.append({
                "project_id": f['project_id'],
                "project_identifier": proj_data.get('project_id', '') if proj_data else '',
                "project_name": proj_data.get('name', 'Unknown') if proj_data else 'Unknown',
                "overrun_probability": f['overrun_probability'],
                "expected_overrun_amount": f.get('overrun_amount', 0),
                "risk_level": risk_level,
                "budget_utilization": (f['current_spend'] / f['total_budget'] * 100) if f['total_budget'] > 0 else 0,
                "alert_severity": risk_level,
                "forecast_date": f['forecast_date']
            })
        
        return {
            "total_alerts": len(alerts),
            "critical_alerts": len([a for a in alerts if a['alert_severity'] == 'critical']),
            "high_alerts": len([a for a in alerts if a['alert_severity'] == 'high']),
            "alerts": alerts
        }
        
    except Exception as e:
        logger.error(f"Error generating budget alerts: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate alerts: {str(e)}")


@router.get("/portfolio-summary")
async def get_portfolio_cost_summary(
    use_cache: bool = Query(default=True, description="Use cached summary if available"),
    db: Client = Depends(get_db)
):
    """
    Get portfolio-wide cost forecast summary - HIGHLY OPTIMIZED
    Uses cached data to avoid recalculating all projects
    """
    try:
        if use_cache:
            # Try to get cached summary from today
            today = date.today().isoformat()
            cache_response = db.table("cost_summary_cache").select(
                "*"
            ).eq("summary_date", today).execute()
            
            if cache_response.data and len(cache_response.data) > 0:
                cached = cache_response.data[0]
                return {
                    "total_projects": cached['total_projects'],
                    "projects_at_risk": cached['projects_at_risk'],
                    "total_budget": cached['total_budget'],
                    "total_projected_overrun": cached['total_projected_overrun'],
                    "project_summaries": cached.get('high_risk_projects', []),
                    "cached": True,
                    "cache_date": cached['summary_date'],
                    "generated_at": cached['created_at']
                }
        
        # Generate new summary using optimized method
        summary = cost_service.get_portfolio_summary_optimized(db)
        
        # Cache the result
        try:
            cache_data = {
                'summary_date': date.today().isoformat(),
                'total_projects': summary['total_projects'],
                'projects_at_risk': summary['projects_at_risk'],
                'total_budget': summary['total_budget'],
                'total_projected_overrun': summary['total_projected_overrun'],
                'high_risk_projects': summary['project_summaries'][:50]  # Top 50 only
            }
            db.table("cost_summary_cache").upsert(cache_data).execute()
        except Exception as cache_error:
            logger.warning(f"Failed to cache summary: {cache_error}")
        
        summary['cached'] = False
        return summary
        
    except Exception as e:
        logger.error(f"Error generating portfolio summary: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate summary: {str(e)}")


@router.post("/refresh-forecasts")
async def refresh_forecasts(
    background_tasks: BackgroundTasks,
    project_limit: int = Query(default=100, le=500),
    db: Client = Depends(get_db)
):
    """
    Trigger background refresh of cost forecasts for active projects
    Returns immediately and processes in background
    """
    try:
        # Get projects needing forecast refresh (no forecast in last 24 hours)
        from datetime import timedelta
        cutoff = (datetime.now() - timedelta(hours=24)).date().isoformat()
        
        # Get active projects without recent forecasts
        projects_response = db.table("projects").select(
            "id"
        ).eq("status", "active").limit(project_limit).execute()
        
        project_ids = [p['id'] for p in projects_response.data]
        
        if not project_ids:
            return {
                "message": "No active projects found",
                "projects_queued": 0
            }
        
        # Filter out projects with recent forecasts
        forecasts_response = db.table("cost_forecasts").select(
            "project_id"
        ).in_("project_id", project_ids).gte("forecast_date", cutoff).execute()
        
        recent_forecast_ids = set(f['project_id'] for f in forecasts_response.data)
        projects_to_refresh = [pid for pid in project_ids if pid not in recent_forecast_ids]
        
        # Queue background job
        background_tasks.add_task(
            cost_service.batch_refresh_forecasts,
            db,
            projects_to_refresh[:100]  # Limit to 100 per batch
        )
        
        return {
            "message": "Forecast refresh queued",
            "projects_queued": len(projects_to_refresh[:100]),
            "total_active_projects": len(project_ids),
            "projects_with_recent_forecasts": len(recent_forecast_ids)
        }
        
    except Exception as e:
        logger.error(f"Error queuing forecast refresh: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/spending-trends/{project_id}")
async def get_spending_trends(
    project_id: int,
    days_back: int = Query(default=30, ge=7, le=90),
    db: Client = Depends(get_db)
):
    """Get spending trends - optimized with aggregated query"""
    try:
        from datetime import timedelta
        start_date = (datetime.now() - timedelta(days=days_back)).date().isoformat()
        
        # Get aggregated daily spending
        logs_response = db.table("daily_logs").select(
            "date, hours_logged, employee_id"
        ).eq("project_id", project_id).gte("date", start_date).order("date").execute()
        
        if not logs_response.data:
            raise HTTPException(status_code=404, detail="No spending data found")
        
        # Get employee rates in batch
        employee_ids = list(set(log['employee_id'] for log in logs_response.data))
        employees_response = db.table("employees").select(
            "id, hourly_rate"
        ).in_("id", employee_ids).execute()
        
        employee_rates = {
            emp['id']: emp.get('hourly_rate', 75.0) 
            for emp in employees_response.data
        }
        
        # Calculate daily costs
        import pandas as pd
        daily_costs = {}
        for log in logs_response.data:
            date_key = log['date']
            cost = log['hours_logged'] * employee_rates.get(log['employee_id'], 75.0)
            daily_costs[date_key] = daily_costs.get(date_key, 0) + cost
        
        # Create trends
        dates = sorted(daily_costs.keys())
        cumulative = 0
        trends = []
        
        for date_key in dates:
            cumulative += daily_costs[date_key]
            trends.append({
                'date': date_key,
                'daily_cost': round(daily_costs[date_key], 2),
                'cumulative_cost': round(cumulative, 2)
            })
        
        # Calculate statistics
        costs = list(daily_costs.values())
        
        return {
            "project_id": project_id,
            "period_days": days_back,
            "daily_trends": trends,
            "statistics": {
                "total_spend": round(cumulative, 2),
                "avg_daily_cost": round(sum(costs) / len(costs), 2) if costs else 0,
                "max_daily_cost": round(max(costs), 2) if costs else 0,
                "min_daily_cost": round(min(costs), 2) if costs else 0,
                "days_with_spending": len(trends)
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving spending trends: {e}")
        raise HTTPException(status_code=500, detail=str(e))