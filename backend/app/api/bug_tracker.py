# backend/app/api/bug_tracker.py (FIXED)

from fastapi import APIRouter, Depends, HTTPException, Query
from supabase import Client

from app.database import get_db
from app.services.bug_tracker import BugTrackerService

router = APIRouter(prefix="/bug-tracker", tags=["bug-tracker"])
bug_service = BugTrackerService()

@router.get("/analyze/{project_id}")
async def analyze_project_bugs(
    project_id: int,
    days_back: int = Query(default=30, ge=7, le=90),
    db: Client = Depends(get_db)
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
    db: Client = Depends(get_db)
):
    """Analyze bug patterns across all projects"""
    try:
        analysis = bug_service.analyze_bug_patterns(db, None, days_back)
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/dashboard")
async def get_bug_dashboard(
    days_back: int = Query(default=30, ge=7, le=90),
    db: Client = Depends(get_db)
):
    """Get comprehensive bug tracking dashboard"""
    try:
        from datetime import datetime, timedelta
        
        start_date = (datetime.now() - timedelta(days=days_back)).date().isoformat()
        
        # Get all bugs
        bugs_response = db.table("bugs").select(
            "*, projects(name)"
        ).gte("created_at", start_date).execute()
        bugs = bugs_response.data
        
        # Calculate statistics
        total_bugs = len(bugs)
        open_bugs = len([b for b in bugs if b['status'] in ['open', 'in_progress']])
        closed_bugs = len([b for b in bugs if b['status'] == 'closed'])
        
        by_severity = {}
        by_status = {}
        by_project = {}
        
        for bug in bugs:
            severity = bug.get('severity', 'medium')
            status = bug.get('status', 'open')
            project_name = bug.get('projects', {}).get('name', 'Unknown') if bug.get('projects') else 'Unknown'
            
            by_severity[severity] = by_severity.get(severity, 0) + 1
            by_status[status] = by_status.get(status, 0) + 1
            by_project[project_name] = by_project.get(project_name, 0) + 1
        
        return {
            "period_days": days_back,
            "summary": {
                "total_bugs": total_bugs,
                "open_bugs": open_bugs,
                "closed_bugs": closed_bugs,
                "resolution_rate": (closed_bugs / total_bugs * 100) if total_bugs > 0 else 0
            },
            "by_severity": by_severity,
            "by_status": by_status,
            "top_projects": sorted(by_project.items(), key=lambda x: x[1], reverse=True)[:10]
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))