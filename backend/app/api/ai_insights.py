# backend/app/api/ai_insights_fixed.py

from fastapi import APIRouter, Depends, HTTPException, Query
from supabase import Client
from typing import Optional
import logging

from app.database import get_db

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/ai-insights", tags=["ai-insights"])

# Check if Gemini service is available
try:
    from app.services.gemini_service import GeminiAnalyticsService
    gemini_service = GeminiAnalyticsService()
    GEMINI_ENABLED = gemini_service.is_enabled
except Exception as e:
    logger.warning(f"Gemini service not available: {e}")
    GEMINI_ENABLED = False
    gemini_service = None


@router.get("/portfolio-trends")
async def analyze_portfolio_trends(db: Client = Depends(get_db)):
    """
    Analyze portfolio trends - FIXED with proper error handling
    Returns statistical analysis without requiring AI if not available
    """
    try:
        # Get projects with proper error handling
        try:
            projects_response = db.table("projects").select(
                "id, project_id, name, risk_level, project_type, team_experience_level, "
                "complexity_score, team_size, project_budget_usd, status"
            ).limit(1000).execute()
            
            projects = projects_response.data
        except Exception as db_error:
            logger.error(f"Database error: {db_error}")
            raise HTTPException(status_code=500, detail=f"Database error: {str(db_error)}")
        
        if not projects:
            return {
                "error": "No projects found for analysis",
                "total_projects": 0
            }
        
        # Calculate statistical trends
        trends = _calculate_portfolio_statistics(projects)
        
        # If Gemini is enabled, try to get AI insights
        if GEMINI_ENABLED and gemini_service:
            try:
                ai_analysis = await gemini_service.analyze_portfolio_trends(db)
                trends['ai_insights'] = ai_analysis.get('analysis', {})
                trends['ai_generated'] = True
            except Exception as ai_error:
                logger.warning(f"AI analysis failed, using statistical analysis only: {ai_error}")
                trends['ai_generated'] = False
                trends['ai_error'] = str(ai_error)
        else:
            trends['ai_generated'] = False
            trends['ai_note'] = "AI insights not available. Set GOOGLE_API_KEY to enable AI analysis."
        
        return trends
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing portfolio trends: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to analyze portfolio: {str(e)}")


def _calculate_portfolio_statistics(projects: list) -> dict:
    """Calculate statistical portfolio analysis"""
    
    # Risk level distribution
    risk_distribution = {}
    for project in projects:
        risk_level = project.get('risk_level', 'Unknown')
        # Handle case variations
        if risk_level:
            risk_level = risk_level.strip().title()
        else:
            risk_level = 'Unknown'
        risk_distribution[risk_level] = risk_distribution.get(risk_level, 0) + 1
    
    # Project type distribution
    type_distribution = {}
    for project in projects:
        proj_type = project.get('project_type', 'Unknown')
        if proj_type:
            proj_type = proj_type.strip()
        else:
            proj_type = 'Unknown'
        type_distribution[proj_type] = type_distribution.get(proj_type, 0) + 1
    
    # Team experience distribution
    experience_distribution = {}
    for project in projects:
        exp_level = project.get('team_experience_level', 'Unknown')
        if exp_level:
            exp_level = exp_level.strip()
        else:
            exp_level = 'Unknown'
        experience_distribution[exp_level] = experience_distribution.get(exp_level, 0) + 1
    
    # Calculate averages
    import statistics
    
    complexity_scores = [p.get('complexity_score', 0) for p in projects if p.get('complexity_score')]
    team_sizes = [p.get('team_size', 0) for p in projects if p.get('team_size')]
    budgets = [p.get('project_budget_usd', 0) for p in projects if p.get('project_budget_usd')]
    
    # Status distribution
    status_distribution = {}
    for project in projects:
        status = project.get('status', 'unknown')
        status_distribution[status] = status_distribution.get(status, 0) + 1
    
    # Identify trends
    high_risk_percentage = (risk_distribution.get('High', 0) + risk_distribution.get('Very High', 0)) / len(projects) * 100 if projects else 0
    
    trends = {
        "total_projects": len(projects),
        "risk_distribution": risk_distribution,
        "project_type_distribution": type_distribution,
        "team_experience_distribution": experience_distribution,
        "status_distribution": status_distribution,
        "averages": {
            "complexity": round(statistics.mean(complexity_scores), 2) if complexity_scores else 0,
            "team_size": round(statistics.mean(team_sizes), 2) if team_sizes else 0,
            "budget": round(statistics.mean(budgets), 2) if budgets else 0
        },
        "insights": {
            "high_risk_percentage": round(high_risk_percentage, 2),
            "total_budget": sum(budgets),
            "most_common_type": max(type_distribution.items(), key=lambda x: x[1])[0] if type_distribution else "Unknown",
            "most_common_experience": max(experience_distribution.items(), key=lambda x: x[1])[0] if experience_distribution else "Unknown"
        },
        "recommendations": _generate_statistical_recommendations(
            risk_distribution, 
            high_risk_percentage,
            experience_distribution
        ),
        "analysis_method": "statistical"
    }
    
    return trends


def _generate_statistical_recommendations(
    risk_distribution: dict,
    high_risk_percentage: float,
    experience_distribution: dict
) -> list:
    """Generate recommendations based on statistical analysis"""
    recommendations = []
    
    if high_risk_percentage > 40:
        recommendations.append({
            "priority": "high",
            "category": "risk_management",
            "finding": f"{high_risk_percentage:.1f}% of projects are high risk",
            "recommendation": "Implement enhanced risk mitigation strategies and increase monitoring frequency for high-risk projects"
        })
    
    junior_projects = experience_distribution.get('Junior', 0)
    total = sum(experience_distribution.values())
    if total > 0 and (junior_projects / total) > 0.3:
        recommendations.append({
            "priority": "medium",
            "category": "team_development",
            "finding": "High proportion of projects with junior teams",
            "recommendation": "Consider mentorship programs and knowledge transfer initiatives to improve team capabilities"
        })
    
    if len(recommendations) == 0:
        recommendations.append({
            "priority": "low",
            "category": "general",
            "finding": "Portfolio appears balanced",
            "recommendation": "Continue current project management practices and maintain regular monitoring"
        })
    
    return recommendations


@router.get("/executive-summary")
async def generate_executive_summary(db: Client = Depends(get_db)):
    """Generate executive summary - works without AI"""
    try:
        # Get portfolio statistics
        projects_response = db.table("projects").select(
            "id, status, risk_level, project_budget_usd, current_spend"
        ).execute()
        
        projects = projects_response.data
        
        if not projects:
            return {"error": "No projects found"}
        
        # Calculate metrics
        total_projects = len(projects)
        active_projects = len([p for p in projects if p.get('status') == 'active'])
        
        total_budget = sum(p.get('project_budget_usd', 0) for p in projects if p.get('project_budget_usd'))
        total_spend = sum(p.get('current_spend', 0) for p in projects if p.get('current_spend'))
        
        high_risk = len([p for p in projects if p.get('risk_level') in ['High', 'Very High']])
        
        summary = {
            "overview": {
                "total_projects": total_projects,
                "active_projects": active_projects,
                "completed_projects": len([p for p in projects if p.get('status') == 'completed']),
                "high_risk_count": high_risk,
                "high_risk_percentage": round(high_risk / total_projects * 100, 2) if total_projects > 0 else 0
            },
            "financial": {
                "total_budget": round(total_budget, 2),
                "total_spend": round(total_spend, 2),
                "budget_utilization": round(total_spend / total_budget * 100, 2) if total_budget > 0 else 0,
                "remaining_budget": round(total_budget - total_spend, 2)
            },
            "key_findings": [
                f"Portfolio consists of {total_projects} projects with {active_projects} currently active",
                f"Total budget allocation: ${total_budget:,.0f}",
                f"{high_risk} projects ({high_risk / total_projects * 100:.1f}%) are classified as high risk" if total_projects > 0 else "No risk data available"
            ],
            "generated_at": str(__import__('datetime').datetime.now()),
            "analysis_method": "statistical"
        }
        
        # Try AI enhancement if available
        if GEMINI_ENABLED and gemini_service:
            try:
                ai_summary = await gemini_service.generate_executive_summary(db)
                summary['ai_insights'] = ai_summary.get('summary', {})
            except:
                pass
        
        return summary
        
    except Exception as e:
        logger.error(f"Error generating executive summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/risk-analysis/{project_id}")
async def generate_risk_analysis(
    project_id: str,
    db: Client = Depends(get_db)
):
    """Generate risk analysis - requires AI"""
    if not GEMINI_ENABLED or not gemini_service:
        raise HTTPException(
            status_code=503,
            detail="AI service not available. Set GOOGLE_API_KEY environment variable to enable AI features."
        )
    
    try:
        analysis = await gemini_service.generate_project_risk_analysis(db, project_id)
        return analysis
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error generating risk analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/service-status")
async def get_service_status():
    """Check AI service availability"""
    return {
        "ai_enabled": GEMINI_ENABLED,
        "service_available": gemini_service is not None,
        "features": {
            "portfolio_trends": "available",
            "executive_summary": "available",
            "risk_analysis": "available" if GEMINI_ENABLED else "requires_ai",
            "recommendations": "available" if GEMINI_ENABLED else "requires_ai"
        },
        "note": "Set GOOGLE_API_KEY environment variable to enable full AI features" if not GEMINI_ENABLED else "AI features enabled"
    }