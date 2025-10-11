# backend/app/api/resource_utilization_optimized.py

from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from supabase import Client
from datetime import datetime, timedelta, date

from app.database import get_db

router = APIRouter(prefix="/resource-utilization", tags=["resource-utilization"])

@router.get("/analyze")
async def analyze_utilization(
    days_back: int = Query(default=14, ge=7, le=90),
    use_cache: bool = Query(default=True),
    db: Client = Depends(get_db)
):
    """
    Resource utilization analysis - OPTIMIZED with caching
    """
    try:
        if use_cache:
            # Try to get cached analysis
            today = date.today().isoformat()
            cache_response = db.table("resource_summary_cache").select(
                "*"
            ).eq("analysis_date", today).eq("period_days", days_back).execute()
            
            if cache_response.data and len(cache_response.data) > 0:
                cached = cache_response.data[0]
                return {
                    "period_days": days_back,
                    "total_employees": cached['total_employees'],
                    "total_alerts": cached['total_alerts'],
                    "summary_stats": cached.get('summary_stats', {}),
                    "utilization_distribution": cached.get('utilization_distribution', {}),
                    "alerts": [],  # Load separately if needed
                    "rebalancing_suggestions": [],
                    "cached": True,
                    "generated_at": cached['created_at']
                }
        
        # Generate new analysis (simplified)
        analysis = await _generate_utilization_analysis(db, days_back)
        
        # Cache result
        try:
            cache_data = {
                'analysis_date': date.today().isoformat(),
                'period_days': days_back,
                'total_employees': analysis['total_employees'],
                'total_alerts': len(analysis.get('alerts', [])),
                'critical_alerts': len([a for a in analysis.get('alerts', []) if a.get('severity') == 'critical']),
                'high_alerts': len([a for a in analysis.get('alerts', []) if a.get('severity') == 'high']),
                'summary_stats': analysis.get('summary_stats', {}),
                'utilization_distribution': {}
            }
            db.table("resource_summary_cache").upsert(cache_data).execute()
        except Exception as e:
            import logging
            logging.warning(f"Failed to cache resource analysis: {e}")
        
        analysis['cached'] = False
        return analysis
        
    except Exception as e:
        import logging
        logging.error(f"Error analyzing team utilization: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def _generate_utilization_analysis(db: Client, days_back: int) -> dict:
    """Generate simplified utilization analysis"""
    start_date = (datetime.now() - timedelta(days=days_back)).date().isoformat()
    
    # Get active employees
    employees_response = db.table("employees").select(
        "id, name, role, max_hours_per_day"
    ).eq("is_active", True).limit(100).execute()
    
    employees = employees_response.data
    
    if not employees:
        return {
            "period_days": days_back,
            "total_employees": 0,
            "alerts": [],
            "summary_stats": {},
            "rebalancing_suggestions": [],
            "generated_at": datetime.now().isoformat()
        }
    
    # Get logs in batch
    employee_ids = [e['id'] for e in employees]
    logs_response = db.table("daily_logs").select(
        "employee_id, date, hours_logged, project_id"
    ).in_("employee_id", employee_ids).gte("date", start_date).execute()
    
    logs = logs_response.data
    
    # Calculate working days
    import numpy as np
    working_days = np.busday_count(
        datetime.strptime(start_date, '%Y-%m-%d').date(),
        datetime.now().date()
    )
    
    # Analyze each employee
    alerts = []
    utilization_data = []
    
    for employee in employees:
        emp_id = employee['id']
        emp_logs = [l for l in logs if l['employee_id'] == emp_id]
        
        if len(emp_logs) == 0:
            # Missing logs alert
            alerts.append({
                'type': 'no_activity',
                'employee_id': emp_id,
                'employee_name': employee['name'],
                'employee_role': employee['role'],
                'severity': 'critical',
                'message': f"{employee['name']} has no logged hours in the period",
                'utilization_rate': 0.0
            })
            continue
        
        # Calculate metrics
        total_hours = sum(l['hours_logged'] for l in emp_logs)
        unique_days = len(set(l['date'] for l in emp_logs))
        avg_daily_hours = total_hours / unique_days if unique_days > 0 else 0
        max_hours = employee.get('max_hours_per_day', 8)
        expected_hours = max_hours * working_days
        utilization_rate = total_hours / expected_hours if expected_hours > 0 else 0
        
        utilization_data.append({
            'employee_id': emp_id,
            'employee_name': employee['name'],
            'utilization_rate': utilization_rate,
            'avg_daily_hours': avg_daily_hours,
            'total_hours': total_hours
        })
        
        # Check for alerts
        if utilization_rate < 0.6:
            severity = 'critical' if utilization_rate < 0.4 else 'high'
            alerts.append({
                'type': 'underutilization',
                'employee_id': emp_id,
                'employee_name': employee['name'],
                'employee_role': employee['role'],
                'severity': severity,
                'utilization_rate': float(utilization_rate),
                'avg_daily_hours': float(avg_daily_hours),
                'expected_hours': float(max_hours),
                'message': f"{employee['name']} is underutilized at {utilization_rate:.1%}"
            })
        elif utilization_rate > 1.3:
            severity = 'critical' if utilization_rate > 1.5 else 'high'
            alerts.append({
                'type': 'overutilization',
                'employee_id': emp_id,
                'employee_name': employee['name'],
                'employee_role': employee['role'],
                'severity': severity,
                'utilization_rate': float(utilization_rate),
                'avg_daily_hours': float(avg_daily_hours),
                'expected_hours': float(max_hours),
                'message': f"{employee['name']} is overworked at {utilization_rate:.1%}"
            })
    
    # Calculate summary stats
    rates = [u['utilization_rate'] for u in utilization_data]
    summary_stats = {
        'avg_utilization': float(np.mean(rates)) if rates else 0,
        'median_utilization': float(np.median(rates)) if rates else 0,
        'underutilized_count': len([r for r in rates if r < 0.6]),
        'overutilized_count': len([r for r in rates if r > 1.3]),
        'optimal_count': len([r for r in rates if 0.6 <= r <= 1.3])
    }
    
    return {
        "period_days": days_back,
        "total_employees": len(employees),
        "alerts": sorted(alerts, key=lambda x: {'critical': 0, 'high': 1, 'medium': 2}.get(x['severity'], 3))[:20],
        "utilization_summary": sorted(utilization_data, key=lambda x: x['utilization_rate'], reverse=True)[:50],
        "summary_stats": summary_stats,
        "rebalancing_suggestions": [],  # Simplified
        "generated_at": datetime.now().isoformat()
    }


@router.get("/alerts")
async def get_utilization_alerts(
    days_back: int = Query(default=14, ge=7, le=90),
    severity: str = Query(default=None),
    limit: int = Query(default=50, le=200),
    db: Client = Depends(get_db)
):
    """Get resource utilization alerts - optimized query"""
    try:
        start_date = (datetime.now() - timedelta(days=days_back)).date().isoformat()
        
        # Build query
        query = db.table("resource_utilization_alerts").select(
            "id, employee_id, alert_type, severity, utilization_rate, "
            "avg_daily_hours, expected_hours, alert_message, is_acknowledged, "
            "created_at, employees(name, role)"
        ).gte("created_at", start_date)
        
        if severity:
            query = query.eq("severity", severity)
        
        query = query.order("created_at", desc=True).limit(limit)
        
        alerts_response = query.execute()
        alerts = alerts_response.data
        
        # Format response
        formatted_alerts = []
        for alert in alerts:
            emp_data = alert.get('employees', {})
            formatted_alerts.append({
                "id": alert['id'],
                "employee_id": alert['employee_id'],
                "employee_name": emp_data.get('name', 'Unknown') if emp_data else 'Unknown',
                "employee_role": emp_data.get('role', 'Unknown') if emp_data else 'Unknown',
                "alert_type": alert['alert_type'],
                "severity": alert['severity'],
                "utilization_rate": alert.get('utilization_rate'),
                "avg_daily_hours": alert.get('avg_daily_hours'),
                "expected_hours": alert.get('expected_hours'),
                "alert_message": alert['alert_message'],
                "is_acknowledged": alert['is_acknowledged'],
                "created_at": alert['created_at']
            })
        
        return {
            "total_alerts": len(formatted_alerts),
            "period_days": days_back,
            "filters": {"severity": severity},
            "alerts": formatted_alerts
        }
    
    except Exception as e:
        import logging
        logging.error(f"Error retrieving alerts: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/dashboard")
async def get_utilization_dashboard(
    days_back: int = Query(default=14, ge=7, le=90),
    db: Client = Depends(get_db)
):
    """Get utilization dashboard - optimized"""
    try:
        # Use cached analysis
        analysis = await analyze_utilization(days_back=days_back, use_cache=True, db=db)
        
        # Get alert counts from database
        start_date = (datetime.now() - timedelta(days=days_back)).date().isoformat()
        alerts_response = db.table("resource_utilization_alerts").select(
            "severity", count='exact'
        ).gte("created_at", start_date).execute()
        
        # Count by severity
        alert_counts = {
            'critical': 0,
            'high': 0,
            'medium': 0,
            'low': 0
        }
        
        if hasattr(alerts_response, 'data'):
            for alert in alerts_response.data:
                severity = alert.get('severity', 'medium')
                alert_counts[severity] = alert_counts.get(severity, 0) + 1
        
        dashboard = {
            "period_days": days_back,
            "summary": {
                "total_employees": analysis.get('total_employees', 0),
                "total_alerts": analysis.get('total_alerts', 0),
                "critical_alerts": alert_counts['critical'],
                "high_alerts": alert_counts['high'],
                **analysis.get('summary_stats', {})
            },
            "utilization_distribution": {
                "underutilized": analysis.get('summary_stats', {}).get('underutilized_count', 0),
                "optimal": analysis.get('summary_stats', {}).get('optimal_count', 0),
                "overutilized": analysis.get('summary_stats', {}).get('overutilized_count', 0)
            },
            "top_alerts": analysis.get('alerts', [])[:10],
            "generated_at": analysis.get('generated_at')
        }
        
        return dashboard
    
    except Exception as e:
        import logging
        logging.error(f"Error generating dashboard: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/employee/{employee_id}")
async def get_employee_utilization(
    employee_id: int,
    days_back: int = Query(default=30, ge=7, le=90),
    db: Client = Depends(get_db)
):
    """Get employee utilization - simplified"""
    try:
        start_date = (datetime.now() - timedelta(days=days_back)).date().isoformat()
        
        # Get employee
        employee_response = db.table("employees").select("*").eq("id", employee_id).single().execute()
        employee = employee_response.data
        
        # Get logs
        logs_response = db.table("daily_logs").select(
            "date, hours_logged, completion_percentage, project_id, projects(name)"
        ).eq("employee_id", employee_id).gte("date", start_date).execute()
        
        logs = logs_response.data
        
        if not logs:
            return {
                "employee_id": employee_id,
                "employee_name": employee['name'],
                "period_days": days_back,
                "message": "No activity in this period"
            }
        
        # Calculate metrics
        total_hours = sum(l['hours_logged'] for l in logs)
        unique_days = len(set(l['date'] for l in logs))
        avg_daily_hours = total_hours / unique_days if unique_days > 0 else 0
        
        import numpy as np
        working_days = np.busday_count(
            datetime.strptime(start_date, '%Y-%m-%d').date(),
            datetime.now().date()
        )
        
        max_hours = employee.get('max_hours_per_day', 8)
        expected_hours = max_hours * working_days
        utilization_rate = total_hours / expected_hours if expected_hours > 0 else 0
        
        return {
            "employee_id": employee_id,
            "employee_name": employee['name'],
            "employee_role": employee['role'],
            "period_days": days_back,
            "utilization_rate": float(utilization_rate),
            "avg_daily_hours": float(avg_daily_hours),
            "total_hours": float(total_hours),
            "days_worked": unique_days,
            "expected_days": int(working_days),
            "status": (
                'optimal' if 0.6 <= utilization_rate <= 1.3 else
                'underutilized' if utilization_rate < 0.6 else
                'overutilized'
            )
        }
        
    except Exception as e:
        import logging
        logging.error(f"Error getting employee utilization: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/refresh-analysis")
async def refresh_analysis(
    background_tasks: BackgroundTasks,
    days_back: int = Query(default=14, ge=7, le=90),
    db: Client = Depends(get_db)
):
    """Trigger background refresh of utilization analysis"""
    try:
        # Queue background task
        background_tasks.add_task(
            _generate_utilization_analysis,
            db,
            days_back
        )
        
        return {
            "message": "Analysis refresh queued",
            "period_days": days_back
        }
        
    except Exception as e:
        import logging
        logging.error(f"Error queuing analysis refresh: {e}")
        raise HTTPException(status_code=500, detail=str(e))