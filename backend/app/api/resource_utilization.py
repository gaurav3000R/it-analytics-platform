# backend/app/api/resource_utilization.py (UPDATED)

from fastapi import APIRouter, Depends, HTTPException, Query
from supabase import Client
from datetime import timedelta

from app.database import get_db
from app.services.resource_utilization import ResourceUtilizationService

router = APIRouter(prefix="/resource-utilization", tags=["resource-utilization"])
util_service = ResourceUtilizationService()

@router.get("/analyze")
async def analyze_utilization(
    days_back: int = Query(default=14, ge=7, le=90, description="Number of days to analyze"),
    db: Client = Depends(get_db)
):
    """
    Comprehensive team resource utilization analysis
    Returns: alerts, utilization metrics, rebalancing suggestions
    """
    try:
        analysis = util_service.analyze_team_utilization(db, days_back)
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to analyze team utilization: {str(e)}")

@router.get("/rebalancing-suggestions")
async def get_rebalancing_suggestions(db: Client = Depends(get_db)):
    """Get intelligent resource rebalancing suggestions"""
    try:
        suggestions = util_service.get_rebalancing_suggestions(db)
        return {
            "total_suggestions": len(suggestions),
            "suggestions": suggestions
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate rebalancing suggestions: {str(e)}")

@router.get("/employee/{employee_id}")
async def get_employee_utilization(
    employee_id: int,
    days_back: int = Query(default=30, ge=7, le=90, description="Number of days to analyze"),
    db: Client = Depends(get_db)
):
    """Get detailed utilization analysis for specific employee"""
    try:
        detail = util_service.get_employee_utilization_detail(db, employee_id, days_back)
        return detail
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get employee utilization: {str(e)}")

@router.get("/alerts")
async def get_utilization_alerts(
    days_back: int = Query(default=14, ge=7, le=90, description="Number of days to retrieve"),
    severity: str = Query(default=None, description="Filter by severity: critical, high, medium, low"),
    alert_type: str = Query(default=None, description="Filter by type: underutilization, overutilization, overbooked"),
    db: Client = Depends(get_db)
):
    """Get resource utilization alerts with filters"""
    try:
        from datetime import datetime, timedelta
        
        start_date = (datetime.now() - timedelta(days=days_back)).date().isoformat()
        
        # Build query
        query = db.table("resource_utilization_alerts").select(
            "*, employees(name, role, email)"
        ).gte("created_at", start_date)
        
        if severity:
            query = query.eq("severity", severity)
        if alert_type:
            query = query.eq("alert_type", alert_type)
        
        query = query.order("created_at", desc=True)
        
        alerts_response = query.execute()
        alerts = alerts_response.data
        
        # Format response
        formatted_alerts = []
        for alert in alerts:
            employee_data = alert.get('employees', {})
            formatted_alerts.append({
                "id": alert['id'],
                "employee_id": alert['employee_id'],
                "employee_name": employee_data.get('name', 'Unknown') if employee_data else 'Unknown',
                "employee_role": employee_data.get('role', 'Unknown') if employee_data else 'Unknown',
                "alert_type": alert['alert_type'],
                "severity": alert['severity'],
                "utilization_rate": alert.get('utilization_rate'),
                "avg_daily_hours": alert.get('avg_daily_hours'),
                "expected_hours": alert.get('expected_hours'),
                "alert_message": alert['alert_message'],
                "is_acknowledged": alert['is_acknowledged'],
                "acknowledged_at": alert.get('acknowledged_at'),
                "created_at": alert['created_at'],
                "period": {
                    "start_date": alert['period_start_date'],
                    "end_date": alert['period_end_date']
                }
            })
        
        return {
            "total_alerts": len(formatted_alerts),
            "period_days": days_back,
            "filters": {
                "severity": severity,
                "alert_type": alert_type
            },
            "alerts": formatted_alerts
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve alerts: {str(e)}")

@router.post("/alerts/{alert_id}/acknowledge")
async def acknowledge_alert(
    alert_id: int,
    acknowledged_by: str = Query(..., description="Name or ID of person acknowledging"),
    db: Client = Depends(get_db)
):
    """Acknowledge a utilization alert"""
    try:
        from datetime import datetime
        
        update_data = {
            "is_acknowledged": True,
            "acknowledged_at": datetime.now().isoformat(),
            "acknowledged_by": acknowledged_by
        }
        
        response = db.table("resource_utilization_alerts").update(
            update_data
        ).eq("id", alert_id).execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="Alert not found")
        
        return {
            "message": "Alert acknowledged successfully",
            "alert_id": alert_id,
            "acknowledged_by": acknowledged_by
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to acknowledge alert: {str(e)}")

@router.get("/dashboard")
async def get_utilization_dashboard(
    days_back: int = Query(default=14, ge=7, le=90),
    db: Client = Depends(get_db)
):
    """Get comprehensive utilization dashboard data"""
    try:
        # Get full analysis
        analysis = util_service.analyze_team_utilization(db, days_back)
        
        # Add historical trends
        from datetime import datetime, timedelta
        
        # Get alert history for trends
        alert_history_response = db.table("resource_utilization_alerts").select(
            "created_at, severity, alert_type"
        ).gte("created_at", (datetime.now() - timedelta(days=days_back)).isoformat()).execute()
        
        alert_history = alert_history_response.data
        
        # Group alerts by week
        import pandas as pd
        if alert_history:
            df = pd.DataFrame(alert_history)
            df['created_at'] = pd.to_datetime(df['created_at'])
            df['week'] = df['created_at'].dt.isocalendar().week
            
            weekly_alerts = df.groupby('week').size().to_dict()
        else:
            weekly_alerts = {}
        
        # Enhanced dashboard
        dashboard = {
            "period_days": days_back,
            "summary": {
                "total_employees": analysis['total_employees'],
                "total_alerts": len(analysis['alerts']),
                "critical_alerts": len([a for a in analysis['alerts'] if a['severity'] == 'critical']),
                "high_alerts": len([a for a in analysis['alerts'] if a['severity'] == 'high']),
                **analysis['summary_stats']
            },
            "utilization_distribution": {
                "underutilized": analysis['summary_stats'].get('underutilized_count', 0),
                "optimal": analysis['summary_stats'].get('optimal_count', 0),
                "overutilized": analysis['summary_stats'].get('overutilized_count', 0),
                "critically_underutilized": analysis['summary_stats'].get('critically_underutilized', 0),
                "critically_overutilized": analysis['summary_stats'].get('critically_overutilized', 0)
            },
            "top_alerts": analysis['alerts'][:10],
            "rebalancing_suggestions": analysis['rebalancing_suggestions'][:5],
            "trends": {
                "weekly_alert_counts": weekly_alerts,
                "avg_utilization": analysis['summary_stats'].get('avg_utilization', 0),
                "avg_health_score": analysis['summary_stats'].get('avg_health_score', 0)
            },
            "generated_at": analysis['generated_at']
        }
        
        return dashboard
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate dashboard: {str(e)}")

@router.get("/overbooking-report")
async def get_overbooking_report(db: Client = Depends(get_db)):
    """Get report of overbooked employees (>100% allocation)"""
    try:
        # Get all active assignments
        assignments_response = db.table("project_assignments").select(
            "*, employees(name, role, email), projects(name)"
        ).eq("is_active", True).execute()
        
        assignments = assignments_response.data
        
        # Group by employee
        from collections import defaultdict
        employee_allocations = defaultdict(lambda: {
            'total_allocation': 0,
            'projects': [],
            'employee_info': None
        })
        
        for assignment in assignments:
            emp_id = assignment['employee_id']
            employee_allocations[emp_id]['total_allocation'] += assignment['allocation_percentage']
            employee_allocations[emp_id]['projects'].append({
                'project_id': assignment['project_id'],
                'project_name': assignment.get('projects', {}).get('name', 'Unknown') if assignment.get('projects') else 'Unknown',
                'allocation': assignment['allocation_percentage'],
                'expected_hours': assignment.get('expected_hours_per_day', 0)
            })
            if not employee_allocations[emp_id]['employee_info']:
                emp_data = assignment.get('employees', {})
                employee_allocations[emp_id]['employee_info'] = {
                    'id': emp_id,
                    'name': emp_data.get('name', 'Unknown') if emp_data else 'Unknown',
                    'role': emp_data.get('role', 'Unknown') if emp_data else 'Unknown',
                    'email': emp_data.get('email', '') if emp_data else ''
                }
        
        # Filter overbooked employees
        overbooked = []
        for emp_id, data in employee_allocations.items():
            if data['total_allocation'] > 100:
                severity = 'critical' if data['total_allocation'] > 150 else 'high' if data['total_allocation'] > 120 else 'medium'
                
                overbooked.append({
                    'employee': data['employee_info'],
                    'total_allocation': data['total_allocation'],
                    'num_projects': len(data['projects']),
                    'projects': data['projects'],
                    'severity': severity,
                    'over_allocation': data['total_allocation'] - 100,
                    'recommendation': f"Reduce allocation by {data['total_allocation'] - 100}% or reassign projects"
                })
        
        # Sort by severity and allocation
        severity_order = {'critical': 0, 'high': 1, 'medium': 2}
        overbooked.sort(key=lambda x: (severity_order[x['severity']], -x['total_allocation']))
        
        return {
            "total_overbooked": len(overbooked),
            "critical_count": len([e for e in overbooked if e['severity'] == 'critical']),
            "high_count": len([e for e in overbooked if e['severity'] == 'high']),
            "overbooked_employees": overbooked
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate overbooking report: {str(e)}")