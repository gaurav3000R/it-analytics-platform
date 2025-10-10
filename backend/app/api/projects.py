from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from typing import List, Optional
import logging
from datetime import datetime

from app.database import get_db
from app.services.data_processor import DataProcessorService
from app.services.csv_loader import CSVLoaderService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/projects", tags=["projects"])

data_processor = DataProcessorService()
csv_loader = CSVLoaderService()

@router.post("/upload-csv")
async def upload_csv_file(
    file: UploadFile = File(...),
    clear_existing: bool = Query(default=False),
    db = Depends(get_db)
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
    db = Depends(get_db)
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

@router.post("/generate-sample-data")
async def generate_sample_data(
    num_projects: int = Query(default=10, ge=1, le=50),
    num_employees: int = Query(default=20, ge=5, le=100),
    db = Depends(get_db)
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
    db = Depends(get_db)
):
    """Get all projects with optional filtering"""
    try:
        # Build Supabase query
        query = db.table('projects').select('*')
        
        if risk_level:
            query = query.eq('risk_level', risk_level)
        if project_type:
            query = query.eq('project_type', project_type)
            
        query = query.limit(limit)
        
        response = query.execute()
        projects = response.data
        
        return [
            {
                "id": p['id'],
                "project_id": p['project_id'],
                "project_type": p.get('project_type'),
                "budget_usd": p.get('project_budget_usd'),
                "team_size": p.get('team_size'),
                "complexity_score": p.get('complexity_score'),
                "risk_level": p.get('risk_level'),
                "team_experience": p.get('team_experience_level'),
                "has_ai_insights": bool(p.get('ai_risk_analysis') or p.get('ai_recommendations'))
            }
            for p in projects
        ]
    except Exception as e:
        logger.error(f"Error getting projects: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{project_id}")
async def get_project(project_id: str, db = Depends(get_db)):
    """Get specific project details by project_id"""
    try:
        response = db.table('projects').select('*').eq('project_id', project_id).execute()
        
        if not response.data or len(response.data) == 0:
            raise HTTPException(status_code=404, detail="Project not found")
        
        project = response.data[0]
        
        return {
            "id": project['id'],
            "project_id": project['project_id'],
            "project_type": project.get('project_type'),
            "team_size": project.get('team_size'),
            "budget_usd": project.get('project_budget_usd'),
            "timeline_months": project.get('estimated_timeline_months'),
            "complexity_score": project.get('complexity_score'),
            "risk_level": project.get('risk_level'),
            "team_experience": project.get('team_experience_level'),
            "methodology": project.get('methodology_used'),
            "stakeholder_count": project.get('stakeholder_count'),
            "change_frequency": project.get('change_request_frequency'),
            "budget_utilization": project.get('budget_utilization_rate'),
            "technical_debt": project.get('technical_debt_level'),
            "market_volatility": project.get('market_volatility'),
            "ai_insights": {
                "risk_analysis": project.get('ai_risk_analysis'),
                "recommendations": project.get('ai_recommendations'),
                "last_updated": project.get('ai_insights_updated_at')
            },
            "created_at": project.get('created_at'),
            "updated_at": project.get('updated_at')
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting project: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))