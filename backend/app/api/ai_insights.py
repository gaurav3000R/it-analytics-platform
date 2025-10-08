from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.services.gemini_service import GeminiAnalyticsService

router = APIRouter(prefix="/ai-insights", tags=["ai-insights"])
gemini_service = GeminiAnalyticsService()

@router.post("/risk-analysis/{project_id}")
async def generate_risk_analysis(
    project_id: str,
    db: Session = Depends(get_db)
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
    db: Session = Depends(get_db)
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
async def analyze_portfolio_trends(db: Session = Depends(get_db)):
    """Analyze trends across the entire project portfolio"""
    try:
        analysis = await gemini_service.analyze_portfolio_trends(db)
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to analyze portfolio: {str(e)}")

@router.get("/executive-summary")
async def generate_executive_summary(db: Session = Depends(get_db)):
    """Generate executive summary of overall project health"""
    try:
        summary = await gemini_service.generate_executive_summary(db)
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate executive summary: {str(e)}")

@router.get("/project/{project_id}/insights")
async def get_project_insights(
    project_id: str,
    db: Session = Depends(get_db)
):
    """Get existing AI insights for a project"""
    try:
        from app.models.project import Project
        project = db.query(Project).filter(Project.project_id == project_id).first()
        
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        return {
            "project_id": project_id,
            "ai_risk_analysis": project.ai_risk_analysis,
            "ai_recommendations": project.ai_recommendations,
            "last_updated": project.ai_insights_updated_at.isoformat() if project.ai_insights_updated_at else None
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))