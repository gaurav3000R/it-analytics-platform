"""
API Routes for Risk Early Warning System
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks
from sqlmodel import Session, select
from typing import List, Optional, Dict, Any
import pandas as pd
from datetime import datetime
import json

from app.db.database import get_session
from app.db.models import (
    Project, Task, User, RiskPrediction, AnomalyDetection,
    ProjectMetrics, ResourceUtilization, RiskLevel
)
from app.ml.risk_models import MLPipeline
from app.services.data_processing import DataPipeline
from app.services.visualization import DataVisualizer, EDAAnalyzer
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1", tags=["risk-analytics"])


# Pydantic models for request/response
class ProjectRiskResponse(BaseModel):
    project_id: int
    project_name: str
    risk_score: float
    risk_level: str
    delay_prediction: Dict[str, float]
    cost_prediction: Dict[str, float]
    resource_bottlenecks: Dict[str, Any]
    timestamp: str


class TrainModelRequest(BaseModel):
    project_ids: Optional[List[int]] = None
    model_types: List[str] = ["delay", "cost", "resource"]


class AnalysisRequest(BaseModel):
    project_id: int
    analysis_type: str = "comprehensive"  # comprehensive, velocity, bugs, resources


class DataUploadResponse(BaseModel):
    status: str
    records_processed: int
    message: str


# Initialize ML Pipeline
ml_pipeline = MLPipeline()
data_pipeline = DataPipeline()
visualizer = DataVisualizer()
eda_analyzer = EDAAnalyzer()


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "IT Analytics - Risk Early Warning System"
    }


@router.get("/projects", response_model=List[Dict[str, Any]])
async def get_projects(
    status: Optional[str] = None,
    risk_level: Optional[str] = None,
    session: Session = Depends(get_session)
):
    """Get all projects with optional filters"""
    query = select(Project)
    
    if status:
        query = query.where(Project.status == status)
    if risk_level:
        query = query.where(Project.risk_level == risk_level)
    
    projects = session.exec(query).all()
    
    return [
        {
            "id": p.id,
            "name": p.name,
            "status": p.status,
            "risk_score": p.risk_score,
            "risk_level": p.risk_level,
            "manager_id": p.manager_id,
            "start_date": p.start_date.isoformat() if p.start_date else None,
            "planned_end_date": p.planned_end_date.isoformat() if p.planned_end_date else None
        }
        for p in projects
    ]


@router.get("/projects/{project_id}/risk", response_model=ProjectRiskResponse)
async def get_project_risk(
    project_id: int,
    session: Session = Depends(get_session)
):
    """Get risk analysis for a specific project"""
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Get latest risk prediction
    latest_prediction = session.exec(
        select(RiskPrediction)
        .where(RiskPrediction.project_id == project_id)
        .order_by(RiskPrediction.prediction_date.desc())
    ).first()
    
    if not latest_prediction:
        raise HTTPException(status_code=404, detail="No risk predictions available for this project")
    
    return ProjectRiskResponse(
        project_id=project.id,
        project_name=project.name,
        risk_score=latest_prediction.overall_risk_score,
        risk_level=latest_prediction.risk_level,
        delay_prediction={
            "predicted_days": latest_prediction.predicted_delay_days or 0,
            "confidence": latest_prediction.delay_confidence
        },
        cost_prediction={
            "predicted_overrun_percent": latest_prediction.predicted_cost_overrun_percent or 0,
            "confidence": latest_prediction.cost_confidence
        },
        resource_bottlenecks={
            "risk_score": latest_prediction.resource_bottleneck_risk,
            "predicted_resources": json.loads(latest_prediction.predicted_bottleneck_resources) if latest_prediction.predicted_bottleneck_resources else []
        },
        timestamp=latest_prediction.prediction_date.isoformat()
    )


@router.post("/predict")
async def predict_risks(
    project_id: int,
    background_tasks: BackgroundTasks,
    session: Session = Depends(get_session)
):
    """Generate risk predictions for a project"""
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    try:
        # Get project metrics
        metrics = session.exec(
            select(ProjectMetrics)
            .where(ProjectMetrics.project_id == project_id)
            .order_by(ProjectMetrics.metric_date.desc())
            .limit(30)
        ).all()
        
        if not metrics:
            raise HTTPException(status_code=400, detail="Insufficient data for prediction")
        
        # Get resource data
        resources = session.exec(
            select(ResourceUtilization)
            .where(ResourceUtilization.project_id == project_id)
        ).all()
        
        # Convert to DataFrames
        metrics_df = pd.DataFrame([{
            'sprint_velocity': m.sprint_velocity,
            'completion_rate': m.completion_rate,
            'bug_reopen_rate': m.bug_reopen_rate,
            'team_size': m.team_size,
            'avg_utilization_rate': m.avg_utilization_rate,
            'blocked_tasks': m.blocked_tasks,
            'days_behind_schedule': m.days_behind_schedule,
            'budget_variance_percent': m.budget_variance_percent,
            'total_tasks': m.total_tasks,
            'completed_tasks': m.completed_tasks
        } for m in metrics])
        
        resource_df = pd.DataFrame([{
            'utilization_rate': r.utilization_rate,
            'tasks_assigned': r.tasks_assigned,
            'tasks_completed': r.tasks_completed,
            'avg_task_completion_time': r.avg_task_completion_time,
            'bugs_created': r.bugs_created
        } for r in resources]) if resources else pd.DataFrame()
        
        # Generate predictions
        try:
            ml_pipeline.load_all_models()
        except:
            raise HTTPException(status_code=400, detail="ML models not trained yet. Please train models first.")
        
        predictions = ml_pipeline.predict_project_risks(metrics_df.tail(1), resource_df)
        
        # Save predictions to database
        risk_prediction = RiskPrediction(
            project_id=project_id,
            delay_risk_score=predictions['delay_prediction']['predicted_days'],
            predicted_delay_days=int(predictions['delay_prediction']['predicted_days']),
            delay_confidence=predictions['delay_prediction']['confidence'],
            cost_overrun_risk_score=predictions['cost_prediction']['predicted_overrun_percent'],
            predicted_cost_overrun_percent=predictions['cost_prediction']['predicted_overrun_percent'],
            cost_confidence=0.8,
            resource_bottleneck_risk=predictions['resource_bottlenecks']['avg_anomaly_score'],
            predicted_bottleneck_resources=json.dumps([]),
            overall_risk_score=predictions['risk_report']['overall_score'],
            risk_level=RiskLevel(predictions['risk_report']['risk_level']),
            model_version="1.0",
            model_type="ensemble"
        )
        
        session.add(risk_prediction)
        
        # Update project risk score
        project.risk_score = predictions['risk_report']['overall_score']
        project.risk_level = RiskLevel(predictions['risk_report']['risk_level'])
        project.delay_probability = predictions['delay_prediction']['predicted_days'] / 30.0  # Normalize to 0-1
        
        session.commit()
        
        return {
            "status": "success",
            "project_id": project_id,
            "predictions": predictions,
            "message": "Risk predictions generated successfully"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating predictions: {str(e)}")


@router.post("/train")
async def train_models(
    request: TrainModelRequest,
    background_tasks: BackgroundTasks,
    session: Session = Depends(get_session)
):
    """Train ML models on historical data"""
    try:
        # Get training data
        query = select(ProjectMetrics)
        if request.project_ids:
            query = query.where(ProjectMetrics.project_id.in_(request.project_ids))
        
        metrics = session.exec(query).all()
        
        if len(metrics) < 30:
            raise HTTPException(status_code=400, detail="Insufficient training data. Need at least 30 records.")
        
        # Prepare training data
        project_df = pd.DataFrame([{
            'sprint_velocity': m.sprint_velocity,
            'completion_rate': m.completion_rate,
            'bug_reopen_rate': m.bug_reopen_rate,
            'team_size': m.team_size,
            'avg_utilization_rate': m.avg_utilization_rate,
            'blocked_tasks': m.blocked_tasks,
            'days_behind_schedule': m.days_behind_schedule,
            'budget_variance_percent': m.budget_variance_percent,
            'total_tasks': m.total_tasks,
            'completed_tasks': m.completed_tasks,
            'delay_days': m.days_behind_schedule,  # Target variable
            'cost_overrun_percent': m.budget_variance_percent  # Target variable
        } for m in metrics])
        
        # Get resource data
        resources = session.exec(select(ResourceUtilization)).all()
        resource_df = pd.DataFrame([{
            'utilization_rate': r.utilization_rate,
            'tasks_assigned': r.tasks_assigned,
            'tasks_completed': r.tasks_completed,
            'avg_task_completion_time': r.avg_task_completion_time,
            'bugs_created': r.bugs_created
        } for r in resources]) if resources else pd.DataFrame()
        
        # Train models
        training_results = ml_pipeline.train_all_models(project_df, resource_df)
        
        return {
            "status": "success",
            "training_results": training_results,
            "records_trained": len(project_df),
            "message": "Models trained successfully"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error training models: {str(e)}")


@router.get("/analyze/{project_id}")
async def analyze_project(
    project_id: int,
    analysis_type: str = "comprehensive",
    session: Session = Depends(get_session)
):
    """Perform EDA and generate insights for a project"""
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    try:
        # Get project metrics
        metrics = session.exec(
            select(ProjectMetrics)
            .where(ProjectMetrics.project_id == project_id)
            .order_by(ProjectMetrics.metric_date)
        ).all()
        
        if not metrics:
            raise HTTPException(status_code=404, detail="No metrics data available")
        
        metrics_df = pd.DataFrame([{
            'metric_date': m.metric_date,
            'sprint_velocity': m.sprint_velocity,
            'completion_rate': m.completion_rate,
            'bug_reopen_rate': m.bug_reopen_rate,
            'total_tasks': m.total_tasks,
            'completed_tasks': m.completed_tasks,
            'blocked_tasks': m.blocked_tasks,
            'team_size': m.team_size,
            'avg_utilization_rate': m.avg_utilization_rate
        } for m in metrics])
        
        # Generate analysis
        summary_stats = eda_analyzer.generate_summary_statistics(metrics_df)
        risk_trends = eda_analyzer.analyze_risk_trends(metrics_df)
        insights = eda_analyzer.generate_insights(metrics_df, 'project_metrics')
        
        # Generate visualizations
        velocity_chart = visualizer.create_velocity_trend_chart(metrics_df, 'metric_date')
        
        return {
            "project_id": project_id,
            "project_name": project.name,
            "summary_statistics": summary_stats,
            "risk_trends": risk_trends,
            "insights": insights,
            "visualizations": {
                "velocity_trend": velocity_chart
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing project: {str(e)}")


@router.get("/visualizations/dashboard")
async def get_dashboard_visualizations(
    project_id: Optional[int] = None,
    session: Session = Depends(get_session)
):
    """Get visualizations for dashboard"""
    try:
        query = select(ProjectMetrics)
        if project_id:
            query = query.where(ProjectMetrics.project_id == project_id)
        
        metrics = session.exec(query).all()
        
        if not metrics:
            return {"visualizations": {}, "message": "No data available"}
        
        metrics_df = pd.DataFrame([{
            'metric_date': m.metric_date,
            'sprint_velocity': m.sprint_velocity,
            'completion_rate': m.completion_rate,
            'bug_reopen_rate': m.bug_reopen_rate,
            'total_bugs': m.total_bugs,
            'project_id': m.project_id
        } for m in metrics])
        
        # Get resource data
        resource_query = select(ResourceUtilization)
        if project_id:
            resource_query = resource_query.where(ResourceUtilization.project_id == project_id)
        
        resources = session.exec(resource_query).all()
        resource_df = pd.DataFrame([{
            'user_id': r.user_id,
            'week_start_date': r.week_start_date,
            'utilization_rate': r.utilization_rate
        } for r in resources]) if resources else pd.DataFrame()
        
        # Generate visualizations
        visualizations = {
            "velocity_trend": visualizer.create_velocity_trend_chart(metrics_df, 'metric_date'),
            "bug_analysis": visualizer.create_bug_analysis_chart(metrics_df)
        }
        
        if not resource_df.empty:
            visualizations["resource_heatmap"] = visualizer.create_resource_utilization_heatmap(resource_df)
        
        return {
            "visualizations": visualizations,
            "generated_at": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating visualizations: {str(e)}")


@router.get("/anomalies")
async def get_anomalies(
    project_id: Optional[int] = None,
    severity: Optional[str] = None,
    limit: int = 50,
    session: Session = Depends(get_session)
):
    """Get detected anomalies"""
    query = select(AnomalyDetection).where(AnomalyDetection.is_resolved == False)
    
    if project_id:
        query = query.where(AnomalyDetection.project_id == project_id)
    if severity:
        query = query.where(AnomalyDetection.severity == severity)
    
    query = query.order_by(AnomalyDetection.detection_date.desc()).limit(limit)
    
    anomalies = session.exec(query).all()
    
    return [
        {
            "id": a.id,
            "project_id": a.project_id,
            "user_id": a.user_id,
            "anomaly_type": a.anomaly_type,
            "severity": a.severity,
            "anomaly_score": a.anomaly_score,
            "description": a.description,
            "metric_name": a.metric_name,
            "expected_value": a.expected_value,
            "actual_value": a.actual_value,
            "deviation_percent": a.deviation_percent,
            "recommended_action": a.recommended_action,
            "detection_date": a.detection_date.isoformat()
        }
        for a in anomalies
    ]


@router.post("/upload/kaizen")
async def upload_kaizen_logs(
    file: UploadFile = File(...),
    session: Session = Depends(get_session)
):
    """Upload and process Kaizen logs"""
    try:
        # Save file temporarily
        content = await file.read()
        file_path = f"/tmp/kaizen_{datetime.utcnow().timestamp()}.csv"
        
        with open(file_path, "wb") as f:
            f.write(content)
        
        # Extract and process data
        extractor = data_pipeline.extractor
        df = extractor.extract_kaizen_logs(file_path)
        
        # Clean data
        df_clean = data_pipeline.cleaner.handle_missing_values(df)
        df_clean = data_pipeline.cleaner.remove_duplicates(df_clean)
        
        return DataUploadResponse(
            status="success",
            records_processed=len(df_clean),
            message=f"Successfully processed {len(df_clean)} Kaizen log records"
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")


@router.post("/upload/jira-sync")
async def sync_jira_data(
    project_key: str,
    session: Session = Depends(get_session)
):
    """Sync data from Jira API"""
    try:
        # This would integrate with actual Jira API
        # For now, return a placeholder response
        return {
            "status": "success",
            "project_key": project_key,
            "records_synced": 0,
            "message": "Jira sync endpoint ready. Configure Jira credentials to enable sync."
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error syncing Jira data: {str(e)}")


@router.get("/reports/risk-summary")
async def get_risk_summary(session: Session = Depends(get_session)):
    """Get overall risk summary across all projects"""
    projects = session.exec(select(Project)).all()
    
    if not projects:
        return {"message": "No projects found"}
    
    # Calculate summary statistics
    total_projects = len(projects)
    at_risk_projects = len([p for p in projects if p.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]])
    avg_risk_score = sum(p.risk_score or 0 for p in projects) / total_projects
    
    risk_distribution = {
        "low": len([p for p in projects if p.risk_level == RiskLevel.LOW]),
        "medium": len([p for p in projects if p.risk_level == RiskLevel.MEDIUM]),
        "high": len([p for p in projects if p.risk_level == RiskLevel.HIGH]),
        "critical": len([p for p in projects if p.risk_level == RiskLevel.CRITICAL])
    }
    
    return {
        "total_projects": total_projects,
        "at_risk_projects": at_risk_projects,
        "avg_risk_score": round(avg_risk_score, 2),
        "risk_distribution": risk_distribution,
        "generated_at": datetime.utcnow().isoformat()
    }
