# backend/app/api/bug_tracker.py

from fastapi import APIRouter, Depends, HTTPException, Query
from supabase import Client
from typing import Optional
from datetime import datetime, timedelta

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
        start_date = (datetime.now() - timedelta(days=days_back)).date().isoformat()
        
        # Get all bugs
        bugs_response = db.table("bugs").select(
            "*, projects(name), assigned_to_employee:employees!bugs_assigned_to_fkey(name, role)"
        ).gte("reported_at", start_date).execute()
        bugs = bugs_response.data
        
        if not bugs:
            return {
                "period_days": days_back,
                "message": "No bugs found in this period"
            }
        
        # Calculate statistics
        total_bugs = len(bugs)
        open_bugs = len([b for b in bugs if b['status'] in ['open', 'in_progress']])
        resolved_bugs = len([b for b in bugs if b['status'] in ['resolved', 'closed']])
        reopened_bugs = len([b for b in bugs if b.get('reopen_count', 0) > 0])
        
        by_severity = {}
        by_status = {}
        by_project = {}
        by_type = {}
        
        for bug in bugs:
            severity = bug.get('severity', 'medium')
            status = bug.get('status', 'open')
            bug_type = bug.get('bug_type', 'unknown')
            project_name = bug.get('projects', {}).get('name', 'Unknown') if bug.get('projects') else 'Unknown'
            
            by_severity[severity] = by_severity.get(severity, 0) + 1
            by_status[status] = by_status.get(status, 0) + 1
            by_type[bug_type] = by_type.get(bug_type, 0) + 1
            by_project[project_name] = by_project.get(project_name, 0) + 1
        
        # Calculate resolution metrics
        resolved_with_time = [b for b in bugs if b.get('resolution_time_hours') is not None]
        avg_resolution_time = sum(b['resolution_time_hours'] for b in resolved_with_time) / len(resolved_with_time) if resolved_with_time else 0
        
        # Top reopened bugs
        top_reopened = sorted(
            [b for b in bugs if b.get('reopen_count', 0) > 0],
            key=lambda x: x.get('reopen_count', 0),
            reverse=True
        )[:10]
        
        return {
            "period_days": days_back,
            "summary": {
                "total_bugs": total_bugs,
                "open_bugs": open_bugs,
                "resolved_bugs": resolved_bugs,
                "reopened_bugs": reopened_bugs,
                "resolution_rate": (resolved_bugs / total_bugs * 100) if total_bugs > 0 else 0,
                "reopen_rate": (reopened_bugs / total_bugs * 100) if total_bugs > 0 else 0,
                "avg_resolution_time_hours": avg_resolution_time
            },
            "by_severity": by_severity,
            "by_status": by_status,
            "by_type": by_type,
            "top_projects": sorted(by_project.items(), key=lambda x: x[1], reverse=True)[:10],
            "top_reopened_bugs": [
                {
                    "bug_id": b['bug_id'],
                    "title": b.get('title', ''),
                    "reopen_count": b.get('reopen_count', 0),
                    "severity": b['severity'],
                    "status": b['status'],
                    "project": b.get('projects', {}).get('name', 'Unknown') if b.get('projects') else 'Unknown'
                }
                for b in top_reopened
            ]
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/bug/{bug_id}")
async def get_bug_details(
    bug_id: str,
    db: Client = Depends(get_db)
):
    """Get detailed information about a specific bug"""
    try:
        details = bug_service.get_bug_details(db, bug_id)
        return details
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/list")
async def list_bugs(
    days_back: int = Query(default=30, ge=1, le=180),
    project_id: Optional[int] = Query(default=None),
    severity: Optional[str] = Query(default=None),
    status: Optional[str] = Query(default=None),
    bug_type: Optional[str] = Query(default=None),
    assigned_to: Optional[int] = Query(default=None),
    limit: int = Query(default=100, le=500),
    db: Client = Depends(get_db)
):
    """List bugs with optional filters"""
    try:
        start_date = (datetime.now() - timedelta(days=days_back)).date().isoformat()
        
        # Build query
        query = db.table("bugs").select(
            "*, projects(name), assigned_to_employee:employees!bugs_assigned_to_fkey(name, role), "
            "reported_by_employee:employees!bugs_reported_by_fkey(name)"
        ).gte("reported_at", start_date)
        
        if project_id:
            query = query.eq("project_id", project_id)
        if severity:
            query = query.eq("severity", severity)
        if status:
            query = query.eq("status", status)
        if bug_type:
            query = query.eq("bug_type", bug_type)
        if assigned_to:
            query = query.eq("assigned_to", assigned_to)
        
        query = query.order("reported_at", desc=True).limit(limit)
        
        response = query.execute()
        bugs = response.data
        
        return {
            "total": len(bugs),
            "filters": {
                "days_back": days_back,
                "project_id": project_id,
                "severity": severity,
                "status": status,
                "bug_type": bug_type,
                "assigned_to": assigned_to
            },
            "bugs": [
                {
                    "id": b['id'],
                    "bug_id": b['bug_id'],
                    "title": b.get('title', ''),
                    "description": b.get('description', ''),
                    "severity": b['severity'],
                    "priority": b.get('priority', ''),
                    "status": b['status'],
                    "bug_type": b.get('bug_type', ''),
                    "environment": b.get('environment', ''),
                    "reopen_count": b.get('reopen_count', 0),
                    "resolution_time_hours": b.get('resolution_time_hours'),
                    "project": {
                        "id": b.get('project_id'),
                        "name": b.get('projects', {}).get('name') if b.get('projects') else 'Unknown'
                    },
                    "assigned_to": {
                        "id": b.get('assigned_to'),
                        "name": b.get('assigned_to_employee', {}).get('name') if b.get('assigned_to_employee') else None
                    },
                    "reported_by": {
                        "id": b.get('reported_by'),
                        "name": b.get('reported_by_employee', {}).get('name') if b.get('reported_by_employee') else None
                    },
                    "reported_at": b.get('reported_at'),
                    "resolved_at": b.get('resolved_at')
                }
                for b in bugs
            ]
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/quality-risks")
async def get_quality_risks(
    days_back: int = Query(default=30, ge=7, le=90),
    min_severity: str = Query(default="medium", description="Minimum severity: low, medium, high"),
    db: Client = Depends(get_db)
):
    """Get quality risks identified from bug patterns"""
    try:
        analysis = bug_service.analyze_bug_patterns(db, None, days_back)
        
        # Filter by severity if specified
        severity_order = {"low": 1, "medium": 2, "high": 3, "critical": 4}
        min_level = severity_order.get(min_severity, 2)
        
        filtered_risks = [
            risk for risk in analysis.get('quality_risks', [])
            if severity_order.get(risk.get('severity', 'medium'), 2) >= min_level
        ]
        
        return {
            "period_days": days_back,
            "total_risks": len(filtered_risks),
            "risks": filtered_risks,
            "recommendations": analysis.get('recommendations', [])
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/metrics/resolution")
async def get_resolution_metrics(
    days_back: int = Query(default=30, ge=7, le=90),
    project_id: Optional[int] = Query(default=None),
    db: Client = Depends(get_db)
):
    """Get detailed bug resolution metrics"""
    try:
        start_date = (datetime.now() - timedelta(days=days_back)).date().isoformat()
        
        query = db.table("bugs").select("*").gte("reported_at", start_date)
        if project_id:
            query = query.eq("project_id", project_id)
        
        bugs_response = query.execute()
        bugs = bugs_response.data
        
        if not bugs:
            return {"message": "No bugs found"}
        
        # Calculate metrics
        resolved = [b for b in bugs if b['status'] in ['resolved', 'closed']]
        open_bugs = [b for b in bugs if b['status'] in ['open', 'in_progress']]
        
        # Resolution time by severity
        resolution_by_severity = {}
        for severity in ['critical', 'high', 'medium', 'low']:
            sev_bugs = [b for b in resolved if b['severity'] == severity and b.get('resolution_time_hours')]
            if sev_bugs:
                resolution_by_severity[severity] = {
                    "count": len(sev_bugs),
                    "avg_hours": sum(b['resolution_time_hours'] for b in sev_bugs) / len(sev_bugs),
                    "median_hours": sorted([b['resolution_time_hours'] for b in sev_bugs])[len(sev_bugs)//2]
                }
        
        # First response time
        bugs_with_response = [b for b in bugs if b.get('first_response_time_hours')]
        avg_first_response = sum(b['first_response_time_hours'] for b in bugs_with_response) / len(bugs_with_response) if bugs_with_response else 0
        
        # Aging analysis for open bugs
        aging_buckets = {
            "0-24h": 0,
            "24-72h": 0,
            "72h-1w": 0,
            "1w+": 0
        }
        
        for bug in open_bugs:
            age_hours = (datetime.now() - datetime.fromisoformat(bug['reported_at'].replace('Z', '+00:00'))).total_seconds() / 3600
            if age_hours < 24:
                aging_buckets["0-24h"] += 1
            elif age_hours < 72:
                aging_buckets["24-72h"] += 1
            elif age_hours < 168:
                aging_buckets["72h-1w"] += 1
            else:
                aging_buckets["1w+"] += 1
        
        return {
            "period_days": days_back,
            "total_bugs": len(bugs),
            "resolved_count": len(resolved),
            "open_count": len(open_bugs),
            "resolution_rate": (len(resolved) / len(bugs) * 100) if bugs else 0,
            "resolution_by_severity": resolution_by_severity,
            "avg_first_response_hours": avg_first_response,
            "open_bugs_aging": aging_buckets
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/trends")
async def get_bug_trends(
    days_back: int = Query(default=60, ge=14, le=180),
    project_id: Optional[int] = Query(default=None),
    db: Client = Depends(get_db)
):
    """Get bug trends over time"""
    try:
        start_date = (datetime.now() - timedelta(days=days_back)).date().isoformat()
        
        query = db.table("bugs").select("*").gte("reported_at", start_date)
        if project_id:
            query = query.eq("project_id", project_id)
        
        bugs_response = query.execute()
        bugs = bugs_response.data
        
        if not bugs:
            return {"message": "No bugs found"}
        
        # Group by week
        import pandas as pd
        df = pd.DataFrame(bugs)
        df['reported_at'] = pd.to_datetime(df['reported_at'])
        df['week'] = df['reported_at'].dt.isocalendar().week
        df['year'] = df['reported_at'].dt.year
        
        # Weekly statistics
        weekly_stats = []
        for (year, week), group in df.groupby(['year', 'week']):
            weekly_stats.append({
                "year": int(year),
                "week": int(week),
                "total_bugs": len(group),
                "critical_count": len(group[group['severity'] == 'critical']),
                "high_count": len(group[group['severity'] == 'high']),
                "resolved_count": len(group[group['status'].isin(['resolved', 'closed'])]),
                "reopened_count": len(group[group['reopen_count'] > 0])
            })
        
        # Calculate trend
        if len(weekly_stats) >= 2:
            recent_avg = sum(w['total_bugs'] for w in weekly_stats[-4:]) / min(4, len(weekly_stats[-4:]))
            historical_avg = sum(w['total_bugs'] for w in weekly_stats[:-4]) / max(1, len(weekly_stats[:-4]))
            trend = "increasing" if recent_avg > historical_avg * 1.1 else "decreasing" if recent_avg < historical_avg * 0.9 else "stable"
        else:
            trend = "insufficient_data"
            recent_avg = 0
            historical_avg = 0
        
        return {
            "period_days": days_back,
            "weekly_stats": weekly_stats,
            "trend": trend,
            "recent_avg_weekly": recent_avg,
            "historical_avg_weekly": historical_avg
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))