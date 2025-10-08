# Adding the missing ./backend/app/api/resource_utilization.py for ResourceUtilizationService (new router)

#===== ./backend/app/api/resource_utilization.py =====

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.resource_utilization import ResourceUtilizationService

router = APIRouter(prefix="/resource-utilization", tags=["resource-utilization"])
util_service = ResourceUtilizationService()

@router.get("/analyze")
async def analyze_utilization(
    days_back: int = Query(default=14, ge=7, le=90),
    db: Session = Depends(get_db)
):
    """Analyze team resource utilization"""
    try:
        analysis = util_service.analyze_team_utilization(db, days_back)
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/rebalancing-suggestions")
async def get_rebalancing_suggestions(db: Session = Depends(get_db)):
    """Get resource rebalancing suggestions"""
    try:
        suggestions = util_service.get_rebalancing_suggestions(db)
        return {"suggestions": suggestions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))