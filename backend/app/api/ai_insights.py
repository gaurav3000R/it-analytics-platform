# backend/app/api/ai_insights.py (FIXED)

from fastapi import APIRouter, Depends, HTTPException, Query
from supabase import Client
from typing import Optional

from app.database import get_db
from app.services.gemini_service import GeminiAnalyticsService

router = APIRouter(prefix="/ai-insights", tags=["ai-insights"])
gemini_service = GeminiAnalyticsService()

@router.post("/risk-analysis/{project_id}")
async def generate_risk_analysis(
    project_id: str,
    db: Client = Depends(get_db)
):
    """Generate AI-powered risk analysis for a specific project"""
    try:
        analysis = await gemini_service.generate_project_risk_analysis(db, project_id)
        return analysis
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate risk analysis: {str(e)}")

@router.post("/recommendations/{project_id}")
async def generate_recommendations(
    project_id: str,
    db: Client = Depends(get_db)
):
    """Generate AI-powered recommendations for a specific project"""
    try:
        recommendations = await gemini_service.generate_recommendations(db, project_id)
        return recommendations
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate recommendations: {str(e)}")

@router.get("/portfolio-trends")
async def analyze_portfolio_trends(db: Client = Depends(get_db)):
    """Analyze trends across the entire project portfolio"""
    try:
        analysis = await gemini_service.analyze_portfolio_trends(db)
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to analyze portfolio: {str(e)}")

@router.get("/executive-summary")
async def generate_executive_summary(db: Client = Depends(get_db)):
    """Generate executive summary of overall project health"""
    try:
        summary = await gemini_service.generate_executive_summary(db)
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate executive summary: {str(e)}")

@router.get("/project/{project_id}/insights")
async def get_project_insights(
    project_id: str,
    db: Client = Depends(get_db)
):
    """Get existing AI insights for a project"""
    try:
        project = db.table("projects").select(
            "project_id, ai_risk_analysis, ai_recommendations, ai_insights_updated_at"
        ).eq("project_id", project_id).single().execute().data
        
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        return {
            "project_id": project_id,
            "ai_risk_analysis": project.get("ai_risk_analysis"),
            "ai_recommendations": project.get("ai_recommendations"),
            "last_updated": project.get("ai_insights_updated_at")
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch project insights: {str(e)}")

@router.get("/dashboard")
async def get_ai_insights_dashboard(db: Client = Depends(get_db)):
    """Get dashboard showing AI insights coverage across projects"""
    try:
        # Get all projects with AI insights
        projects_response = db.table("projects").select(
            "project_id, name, ai_risk_analysis, ai_recommendations, ai_insights_updated_at"
        ).execute()
        projects = projects_response.data
        
        with_insights = [p for p in projects if p.get('ai_risk_analysis') or p.get('ai_recommendations')]
        without_insights = [p for p in projects if not (p.get('ai_risk_analysis') or p.get('ai_recommendations'))]
        
        return {
            "total_projects": len(projects),
            "projects_with_insights": len(with_insights),
            "projects_without_insights": len(without_insights),
            "coverage_percentage": (len(with_insights) / len(projects) * 100) if projects else 0,
            "recent_insights": [
                {
                    "project_id": p['project_id'],
                    "project_name": p.get('name', 'Unknown'),
                    "has_risk_analysis": bool(p.get('ai_risk_analysis')),
                    "has_recommendations": bool(p.get('ai_recommendations')),
                    "last_updated": p.get('ai_insights_updated_at')
                }
                for p in sorted(with_insights, key=lambda x: x.get('ai_insights_updated_at', ''), reverse=True)[:10]
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate dashboard: {str(e)}")