from fastapi import APIRouter, Depends, HTTPException, Query
from supabase import Client

from app.database import get_db
from app.services.cost_forecasting import CostForecastingService

router = APIRouter(prefix="/cost-forecasting", tags=["cost-forecasting"])
cost_service = CostForecastingService()

@router.get("/forecast/{project_id}")
async def forecast_cost_overrun(
    project_id: int,
    forecast_days: int = Query(default=30, ge=7, le=180),
    db: Client = Depends(get_db)
):
    """Get cost overrun forecast for a project"""
    try:
        forecast = cost_service.forecast_cost_overrun(db, project_id, forecast_days)
        return forecast
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to forecast cost overrun: {str(e)}")

@router.get("/budget-alerts")
async def get_budget_alerts(db: Client = Depends(get_db)):
    """Get budget alerts for all projects"""
    try:
        projects = db.table("projects").select("id").execute().data
        alerts = []
        for project in projects:
            forecast = cost_service.forecast_cost_overrun(db, project["id"], 30)
            if forecast.get('overrun_probability', 0) > 0.5:
                alerts.append({
                    "project_id": project["id"],
                    "overrun_probability": forecast['overrun_probability']
                })
        return {"alerts": alerts}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate budget alerts: {str(e)}")