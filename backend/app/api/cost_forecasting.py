# Adding the missing ./backend/app/api/cost_forecasting.py (already partial, completing)

#===== ./backend/app/api/cost_forecasting.py =====

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.cost_forecasting import CostForecastingService
from app.models import Project  # NEW

router = APIRouter(prefix="/cost-forecasting", tags=["cost-forecasting"])
cost_service = CostForecastingService()

@router.get("/forecast/{project_id}")
async def forecast_cost_overrun(
    project_id: int,
    forecast_days: int = Query(default=30, ge=7, le=180),
    db: Session = Depends(get_db)
):
    """Get cost overrun forecast for a project"""
    try:
        forecast = cost_service.forecast_cost_overrun(db, project_id, forecast_days)
        return forecast
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/budget-alerts")
async def get_budget_alerts(db: Session = Depends(get_db)):
    """Get budget alerts for all projects"""
    try:
        # Implementation to get alerts for all projects
        projects = db.query(Project).all()
        alerts = []
        for project in projects:
            forecast = cost_service.forecast_cost_overrun(db, project.id, 30)
            if forecast.get('overrun_probability', 0) > 0.5:
                alerts.append({
                    "project_id": project.id,
                    "overrun_probability": forecast['overrun_probability']
                })
        return {"alerts": alerts}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))