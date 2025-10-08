# Adding the missing ./backend/app/api/bug_tracker.py for BugTrackerService integration (new router)

#===== ./backend/app/api/bug_tracker.py =====

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.bug_tracker import BugTrackerService

router = APIRouter(prefix="/bug-tracker", tags=["bug-tracker"])
bug_service = BugTrackerService()

@router.get("/analyze/{project_id}")
async def analyze_project_bugs(
    project_id: int,
    days_back: int = Query(default=30, ge=7, le=90),
    db: Session = Depends(get_db)
):
    """Analyze bug patterns for a specific project"""
    try:
        analysis = bug_service.analyze_bug_patterns(db, project_id, days_back)
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/portfolio-analysis")
async def analyze_portfolio_bugs(
    days_back: int = Query(default=30, ge=7, le=90),
    db: Session = Depends(get_db)
):
    """Analyze bug patterns across all projects"""
    try:
        analysis = bug_service.analyze_bug_patterns(db, None, days_back)
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))