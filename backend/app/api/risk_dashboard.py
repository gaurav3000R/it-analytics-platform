# backend/app/api/risk_dashboard.py

from fastapi import APIRouter, Depends, HTTPException, Query
from supabase import Client
from typing import Optional
import logging

from app.database import get_db
from app.services.risk_dashboard import RiskDashboardService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/risk-dashboard", tags=["risk-dashboard"])

risk_dashboard_service = RiskDashboardService()

@router.get("/overview")
async def get_risk_dashboard_overview(
    force_recalculation: bool = Query(default=False, description="Force recalculation of all risks"),
    max_projects: int = Query(default=1000, le=1000, description="Maximum projects to analyze"),
    db: Client = Depends(get_db)
):
    """
    Get comprehensive risk dashboard overview
    
    Returns:
    - Summary statistics
    - Risk distribution
    - Top risk projects
    - Flagged projects by risk factor
    
    Performance: Optimized with batch processing and parallel computation
    """
    try:
        logger.info(f"Fetching risk dashboard overview (force_recalc={force_recalculation})")
        
        # Get active projects (limit to prevent timeout)
        projects_response = db.table("projects").select("id").eq(
            "status", "active"
        ).limit(max_projects).execute()
        
        project_ids = [p['id'] for p in projects_response.data]
        
        if not project_ids:
            return {
                "message": "No active projects found",
                "summary": {
                    "total_projects": 0,
                    "avg_risk_score": 0,
                    "risk_distribution": {
                        "critical": 0,
                        "high": 0,
                        "medium": 0,
                        "low": 0,
                        "very_low": 0
                    }
                }
            }
        
        # Calculate dashboard
        dashboard = risk_dashboard_service.calculate_risk_dashboard_summary(
            db,
            project_ids=project_ids,
            force_recalculation=force_recalculation
        )
        
        return dashboard
        
    except Exception as e:
        logger.error(f"Error getting risk dashboard: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate dashboard: {str(e)}")


@router.get("/projects")
async def get_project_risks_paginated(
    page: int = Query(default=1, ge=1, description="Page number"),
    page_size: int = Query(default=50, ge=10, le=100, description="Items per page"),
    risk_level: Optional[str] = Query(default=None, description="Filter by risk level"),
    sort_by: str = Query(default="overall_risk_score", description="Sort field"),
    order: str = Query(default="desc", description="Sort order: asc or desc"),
    db: Client = Depends(get_db)
):
    """
    Get paginated list of project risks with filtering and sorting
    
    Filters:
    - risk_level: critical, high, medium, low, very_low
    
    Sorting:
    - overall_risk_score (default)
    - schedule_risk
    - budget_risk
    - quality_risk
    - resource_risk
    - technical_risk
    """
    try:
        result = risk_dashboard_service.get_paginated_project_risks(
            db=db,
            page=page,
            page_size=page_size,
            risk_level=risk_level,
            sort_by=sort_by,
            order=order
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Error getting paginated projects: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/project/{project_id}")
async def get_project_risk_detail(
    project_id: int,
    force_recalculation: bool = Query(default=False, description="Force recalculation"),
    db: Client = Depends(get_db)
):
    """
    Get detailed risk assessment for a specific project
    
    Returns:
    - Comprehensive risk scores
    - Component risk breakdown
    - Key metrics
    - Risk flags
    """
    try:
        detail = risk_dashboard_service.get_project_risk_detail(
            db=db,
            project_id=project_id,
            force_recalculation=force_recalculation
        )
        
        return detail
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting project detail: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/recalculate")
async def recalculate_all_risks(
    project_ids: Optional[list[int]] = None,
    db: Client = Depends(get_db)
):
    """
    Trigger recalculation of risk scores
    
    Use this endpoint to refresh risk calculations for all or specific projects
    """
    try:
        if project_ids and len(project_ids) > 100:
            raise HTTPException(
                status_code=400,
                detail="Cannot recalculate more than 100 projects at once"
            )
        
        dashboard = risk_dashboard_service.calculate_risk_dashboard_summary(
            db=db,
            project_ids=project_ids,
            force_recalculation=True
        )
        
        return {
            "message": "Risk recalculation completed",
            "projects_updated": dashboard['summary']['total_projects'],
            "summary": dashboard['summary']
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error recalculating risks: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/flagged-projects")
async def get_flagged_projects(
    flag_type: str = Query(..., description="Flag type: irregular_velocity, inconsistent_logging, overbudget, high_bug_rate"),
    limit: int = Query(default=50, le=100, description="Maximum results"),
    db: Client = Depends(get_db)
):
    """
    Get projects flagged for specific risk factors
    """
    try:
        # Validate flag type
        valid_flags = ['irregular_velocity', 'inconsistent_logging', 'overbudget', 'high_bug_rate']
        if flag_type not in valid_flags:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid flag_type. Must be one of: {', '.join(valid_flags)}"
            )
        
        # Query flagged projects
        flag_column = f"{flag_type}_flag"
        
        response = db.table("risk_dashboard_summary").select(
            "*, projects(id, project_id, name, status)"
        ).eq(flag_column, True).order(
            "overall_risk_score", desc=True
        ).limit(limit).execute()
        
        projects = []
        for summary in response.data:
            proj_data = summary.get('projects', {})
            projects.append({
                'project_id': summary['project_id'],
                'project_name': proj_data.get('name', 'Unknown'),
                'project_identifier': proj_data.get('project_id', ''),
                'overall_risk_score': summary['overall_risk_score'],
                'risk_level': summary['risk_level'],
                'flag_details': {
                    'flag_type': flag_type,
                    'metric_value': summary.get(self._get_metric_for_flag(flag_type), 0)
                },
                'last_updated': summary['last_calculated_at']
            })
        
        return {
            'flag_type': flag_type,
            'total_flagged': len(projects),
            'projects': projects
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting flagged projects: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def _get_metric_for_flag(flag_type: str) -> str:
    """Map flag type to metric column"""
    mapping = {
        'irregular_velocity': 'sprint_velocity_deviation',
        'inconsistent_logging': 'logging_consistency_score',
        'overbudget': 'budget_utilization',
        'high_bug_rate': 'bug_density'
    }
    return mapping.get(flag_type, 'overall_risk_score')


@router.get("/trends")
async def get_risk_trends(
    days_back: int = Query(default=30, ge=7, le=90, description="Days to analyze"),
    project_id: Optional[int] = Query(default=None, description="Specific project or all"),
    db: Client = Depends(get_db)
):
    """
    Get risk score trends over time
    
    Shows how risk scores have changed over the specified period
    """
    try:
        from datetime import datetime, timedelta
        
        start_date = (datetime.now() - timedelta(days=days_back)).date().isoformat()
        
        # Query historical risk scores
        query = db.table("risk_scores").select(
            "project_id, date, overall_risk_score, schedule_risk, budget_risk, "
            "quality_risk, resource_risk, technical_risk"
        ).gte("date", start_date)
        
        if project_id:
            query = query.eq("project_id", project_id)
        
        query = query.order("date")
        
        response = query.execute()
        scores = response.data
        
        if not scores:
            return {
                "message": "No historical risk data found",
                "period_days": days_back
            }
        
        # Group by project
        import pandas as pd
        df = pd.DataFrame(scores)
        
        if project_id:
            # Single project trend
            trend_data = df.sort_values('date').to_dict('records')
            
            return {
                'project_id': project_id,
                'period_days': days_back,
                'data_points': len(trend_data),
                'trend': trend_data,
                'statistics': {
                    'avg_risk': float(df['overall_risk_score'].mean()),
                    'max_risk': float(df['overall_risk_score'].max()),
                    'min_risk': float(df['overall_risk_score'].min()),
                    'current_risk': float(trend_data[-1]['overall_risk_score']) if trend_data else 0
                }
            }
        else:
            # Portfolio trend
            daily_avg = df.groupby('date').agg({
                'overall_risk_score': 'mean',
                'schedule_risk': 'mean',
                'budget_risk': 'mean',
                'quality_risk': 'mean',
                'resource_risk': 'mean',
                'technical_risk': 'mean'
            }).reset_index()
            
            trend_data = daily_avg.to_dict('records')
            
            return {
                'portfolio_trend': True,
                'period_days': days_back,
                'data_points': len(trend_data),
                'trend': trend_data,
                'statistics': {
                    'avg_risk': float(daily_avg['overall_risk_score'].mean()),
                    'max_risk': float(daily_avg['overall_risk_score'].max()),
                    'min_risk': float(daily_avg['overall_risk_score'].min())
                }
            }
        
    except Exception as e:
        logger.error(f"Error getting risk trends: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/statistics")
async def get_risk_statistics(
    db: Client = Depends(get_db)
):
    """
    Get aggregated risk statistics across the portfolio
    
    Returns high-level metrics for executive dashboards
    """
    try:
        # Get all cached summaries
        response = db.table("risk_dashboard_summary").select("*").execute()
        summaries = response.data
        
        if not summaries:
            return {
                "message": "No risk data available",
                "statistics": {}
            }
        
        import pandas as pd
        df = pd.DataFrame(summaries)
        
        # Calculate statistics
        stats = {
            'total_projects': len(df),
            'risk_distribution': df['risk_level'].value_counts().to_dict(),
            'average_scores': {
                'overall': float(df['overall_risk_score'].mean()),
                'schedule': float(df['schedule_risk'].mean()),
                'budget': float(df['budget_risk'].mean()),
                'quality': float(df['quality_risk'].mean()),
                'resource': float(df['resource_risk'].mean()),
                'technical': float(df['technical_risk'].mean())
            },
            'score_ranges': {
                'overall': {
                    'min': float(df['overall_risk_score'].min()),
                    'max': float(df['overall_risk_score'].max()),
                    'median': float(df['overall_risk_score'].median()),
                    'std': float(df['overall_risk_score'].std())
                }
            },
            'flag_counts': {
                'irregular_velocity': int(df['irregular_velocity_flag'].sum()),
                'inconsistent_logging': int(df['inconsistent_logging_flag'].sum()),
                'overbudget': int(df['overbudget_flag'].sum()),
                'high_bug_rate': int(df['high_bug_rate_flag'].sum())
            },
            'metric_averages': {
                'velocity_deviation': float(df['sprint_velocity_deviation'].mean()),
                'logging_consistency': float(df['logging_consistency_score'].mean()),
                'budget_utilization': float(df['budget_utilization'].mean()),
                'team_utilization': float(df['team_utilization_avg'].mean()),
                'bug_density': float(df['bug_density'].mean())
            }
        }
        
        return {
            'statistics': stats,
            'generated_at': datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))