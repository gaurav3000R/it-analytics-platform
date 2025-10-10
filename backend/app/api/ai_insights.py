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
        project = db.table("projects").select("project_id, ai_risk_analysis, ai_recommendations, ai_insights_updated_at").eq("project_id", project_id).single().execute().data
        
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