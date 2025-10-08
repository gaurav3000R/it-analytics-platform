from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
import logging

from app.database import get_db
from app.services.data_processor import DataProcessorService
from app.services.csv_loader import CSVLoaderService  # NEW
from app.models.project import Project

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/projects", tags=["projects"])

data_processor = DataProcessorService()
csv_loader = CSVLoaderService()  # NEW

@router.post("/upload-csv")
async def upload_csv_file(
    file: UploadFile = File(...),
    clear_existing: bool = Query(default=False),
    db: Session = Depends(get_db)
):
    """Upload and process CSV file with project risk data"""
    
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File must be a CSV")
    
    try:
        # Save uploaded file temporarily
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_file_path = tmp_file.name
        
        # Process CSV
        result = csv_loader.csv_to_database(db, tmp_file_path, clear_existing)
        
        # Clean up temporary file
        os.unlink(tmp_file_path)
        
        return {
            "message": "CSV file processed successfully",
            "filename": file.filename,
            "result": result
        }
        
    except Exception as e:
        logger.error(f"Error processing CSV: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process CSV: {str(e)}")

@router.post("/load-default-csv")
async def load_default_csv(
    clear_existing: bool = Query(default=False),
    db: Session = Depends(get_db)
):
    """Load the default project risk dataset CSV"""
    try:
        result = csv_loader.csv_to_database(db, clear_existing=clear_existing)
        return {
            "message": "Default CSV loaded successfully", 
            "result": result
        }
    except Exception as e:
        logger.error(f"Error loading default CSV: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to load CSV: {str(e)}")

@router.get("/csv-summary")
async def get_csv_summary():
    """Get summary of the CSV data structure"""
    try:
        df = csv_loader.load_csv_data()
        summary = csv_loader.get_data_summary(df)
        return summary
    except Exception as e:
        logger.error(f"Error getting CSV summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Keep all existing endpoints...
@router.post("/generate-sample-data")
async def generate_sample_data(
    num_projects: int = Query(default=10, ge=1, le=50),
    num_employees: int = Query(default=20, ge=5, le=100),
    db: Session = Depends(get_db)
):
    """Generate sample data for demonstration (legacy - use CSV instead)"""
    try:
        data_processor.generate_sample_data(db, num_projects, num_employees)
        return {
            "message": f"Generated sample data: {num_projects} projects, {num_employees} employees",
            "status": "success",
            "note": "Consider using CSV upload for real project data"
        }
    except Exception as e:
        logger.error(f"Error generating sample data: {e}")
        raise HTTPException(status_code=500, detail=f"Data generation failed: {str(e)}")

@router.get("/")
async def get_all_projects(
    risk_level: Optional[str] = Query(None),
    project_type: Optional[str] = Query(None),
    limit: int = Query(default=100, le=500),
    db: Session = Depends(get_db)
):
    """Get all projects with optional filtering"""
    try:
        query = db.query(Project)
        
        if risk_level:
            query = query.filter(Project.risk_level == risk_level)
        if project_type:
            query = query.filter(Project.project_type == project_type)
            
        projects = query.limit(limit).all()
        
        return [
            {
                "id": p.id,
                "project_id": p.project_id,
                "project_type": p.project_type,
                "budget_usd": p.project_budget_usd,
                "team_size": p.team_size,
                "complexity_score": p.complexity_score,
                "risk_level": p.risk_level,
                "team_experience": p.team_experience_level,
                "has_ai_insights": bool(p.ai_risk_analysis or p.ai_recommendations)
            }
            for p in projects
        ]
    except Exception as e:
        logger.error(f"Error getting projects: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{project_id}")
async def get_project(project_id: str, db: Session = Depends(get_db)):
    """Get specific project details by project_id"""
    try:
        project = db.query(Project).filter(Project.project_id == project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        return {
            "id": project.id,
            "project_id": project.project_id,
            "project_type": project.project_type,
            "team_size": project.team_size,
            "budget_usd": project.project_budget_usd,
            "timeline_months": project.estimated_timeline_months,
            "complexity_score": project.complexity_score,
            "risk_level": project.risk_level,
            "team_experience": project.team_experience_level,
            "methodology": project.methodology_used,
            "stakeholder_count": project.stakeholder_count,
            "change_frequency": project.change_request_frequency,
            "budget_utilization": project.budget_utilization_rate,
            "technical_debt": project.technical_debt_level,
            "market_volatility": project.market_volatility,
            "ai_insights": {
                "risk_analysis": project.ai_risk_analysis,
                "recommendations": project.ai_recommendations,
                "last_updated": project.ai_insights_updated_at.isoformat() if project.ai_insights_updated_at else None
            },
            "created_at": project.created_at.isoformat(),
            "updated_at": project.updated_at.isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting project: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))