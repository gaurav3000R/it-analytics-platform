"""
FastAPI ML Prediction Endpoints
================================

REST API endpoints for model predictions.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from ml_predict import ProjectSuccessPredictor

router = APIRouter(prefix="/ml", tags=["Machine Learning"])

# Initialize predictor (singleton)
try:
    predictor = ProjectSuccessPredictor()
    MODEL_LOADED = True
except Exception as e:
    print(f"Warning: Could not load ML model: {e}")
    MODEL_LOADED = False
    predictor = None


# Request/Response Models
class ProjectFeatures(BaseModel):
    """Project features for prediction"""
    agile_effectiveness: int = Field(..., ge=1, le=5, description="Agile Effectiveness (1-5)")
    risk_mitigation: int = Field(..., ge=1, le=5, description="Risk Mitigation (1-5)")
    management_satisfaction: int = Field(..., ge=1, le=5, description="Management Satisfaction (1-5)")
    supply_chain_improvement: int = Field(..., ge=1, le=5, description="Supply Chain Improvement (1-5)")
    time_efficiency: int = Field(..., ge=1, le=5, description="Time Efficiency (1-5)")
    cost_savings_pct: int = Field(..., ge=0, le=100, description="Cost Savings Percentage (0-100)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "agile_effectiveness": 5,
                "risk_mitigation": 4,
                "management_satisfaction": 5,
                "supply_chain_improvement": 4,
                "time_efficiency": 4,
                "cost_savings_pct": 30
            }
        }


class PredictionResponse(BaseModel):
    """Prediction response"""
    prediction: int
    success: bool
    probability: Optional[float]
    confidence: Optional[float]
    model: str
    features: Optional[dict]
    message: str


class BatchPredictionRequest(BaseModel):
    """Batch prediction request"""
    projects: List[ProjectFeatures]


class ModelInfo(BaseModel):
    """Model information"""
    model_name: str
    accuracy: float
    f1_score: float
    precision: float
    recall: float
    training_date: str
    feature_names: List[str]


# API Endpoints
@router.get("/health", summary="Check ML service health")
async def health_check():
    """Check if ML model is loaded and ready"""
    return {
        "status": "healthy" if MODEL_LOADED else "unhealthy",
        "model_loaded": MODEL_LOADED,
        "model_name": predictor.metadata['model_name'] if MODEL_LOADED else None
    }


@router.get("/model/info", response_model=ModelInfo, summary="Get model information")
async def get_model_info():
    """Get information about the loaded model"""
    if not MODEL_LOADED:
        raise HTTPException(status_code=503, detail="ML model not loaded")
    
    return ModelInfo(
        model_name=predictor.metadata['model_name'],
        accuracy=predictor.metadata['metrics']['accuracy'],
        f1_score=predictor.metadata['metrics']['f1_score'],
        precision=predictor.metadata['metrics']['precision'],
        recall=predictor.metadata['metrics']['recall'],
        training_date=predictor.metadata['training_date'],
        feature_names=predictor.feature_names
    )


@router.post("/predict", response_model=PredictionResponse, summary="Predict project success")
async def predict_project_success(features: ProjectFeatures):
    """
    Predict whether a project will be successful based on its features.
    
    Returns:
        - prediction: 0 (failure) or 1 (success)
        - success: Boolean indicating success
        - probability: Probability of success (if available)
        - confidence: Confidence level
        - model: Name of the model used
    """
    if not MODEL_LOADED:
        raise HTTPException(status_code=503, detail="ML model not loaded")
    
    try:
        # Convert to dict with correct column names
        data = {
            'Agile Effectiveness': features.agile_effectiveness,
            'Risk Mitigation': features.risk_mitigation,
            'Management Satisfaction': features.management_satisfaction,
            'Supply Chain Improvement': features.supply_chain_improvement,
            'Time Efficiency': features.time_efficiency,
            'Cost Savings (%)': features.cost_savings_pct
        }
        
        # Make prediction
        result = predictor.predict(data)
        
        # Add message
        if result['success']:
            message = f"Project likely to succeed with {result['probability']:.1%} confidence" if result['probability'] else "Project likely to succeed"
        else:
            message = f"Project at risk of failure with {1-result['probability']:.1%} confidence" if result['probability'] else "Project at risk of failure"
        
        return PredictionResponse(**result, message=message)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")


@router.post("/predict/batch", summary="Batch predict project success")
async def predict_batch(request: BatchPredictionRequest):
    """
    Predict success for multiple projects at once.
    
    Returns a list of predictions.
    """
    if not MODEL_LOADED:
        raise HTTPException(status_code=503, detail="ML model not loaded")
    
    try:
        # Convert to list of dicts
        data_list = []
        for project in request.projects:
            data_list.append({
                'Agile Effectiveness': project.agile_effectiveness,
                'Risk Mitigation': project.risk_mitigation,
                'Management Satisfaction': project.management_satisfaction,
                'Supply Chain Improvement': project.supply_chain_improvement,
                'Time Efficiency': project.time_efficiency,
                'Cost Savings (%)': project.cost_savings_pct
            })
        
        # Make predictions
        results = predictor.predict_batch(data_list)
        
        # Format response
        predictions = []
        for i, (pred, prob) in enumerate(zip(results['prediction'], results['probability'])):
            predictions.append({
                'project_index': i,
                'prediction': int(pred),
                'success': bool(pred),
                'probability': float(prob) if prob is not None else None,
                'features': data_list[i]
            })
        
        return {
            'total': len(predictions),
            'successful': sum(1 for p in predictions if p['success']),
            'failed': sum(1 for p in predictions if not p['success']),
            'predictions': predictions
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch prediction error: {str(e)}")


@router.post("/analyze", summary="Analyze project and get recommendations")
async def analyze_project(features: ProjectFeatures):
    """
    Analyze project and provide detailed insights and recommendations.
    """
    if not MODEL_LOADED:
        raise HTTPException(status_code=503, detail="ML model not loaded")
    
    try:
        # Get prediction
        data = {
            'Agile Effectiveness': features.agile_effectiveness,
            'Risk Mitigation': features.risk_mitigation,
            'Management Satisfaction': features.management_satisfaction,
            'Supply Chain Improvement': features.supply_chain_improvement,
            'Time Efficiency': features.time_efficiency,
            'Cost Savings (%)': features.cost_savings_pct
        }
        
        result = predictor.predict(data)
        
        # Analyze features
        recommendations = []
        
        if features.agile_effectiveness < 3:
            recommendations.append("⚠️ Low agile effectiveness - consider agile training or methodology improvements")
        if features.risk_mitigation < 3:
            recommendations.append("⚠️ Weak risk mitigation - implement comprehensive risk management strategy")
        if features.management_satisfaction < 3:
            recommendations.append("⚠️ Low management satisfaction - improve communication and stakeholder engagement")
        if features.supply_chain_improvement < 3:
            recommendations.append("⚠️ Supply chain issues - review and optimize supply chain processes")
        if features.time_efficiency < 3:
            recommendations.append("⚠️ Low time efficiency - optimize workflows and remove bottlenecks")
        if features.cost_savings_pct < 20:
            recommendations.append("⚠️ Limited cost savings - explore cost optimization opportunities")
        
        # Strengths
        strengths = []
        if features.agile_effectiveness >= 4:
            strengths.append("✅ Strong agile implementation")
        if features.risk_mitigation >= 4:
            strengths.append("✅ Effective risk management")
        if features.management_satisfaction >= 4:
            strengths.append("✅ High management satisfaction")
        if features.cost_savings_pct >= 30:
            strengths.append("✅ Significant cost savings")
        
        return {
            'prediction': result,
            'analysis': {
                'overall_score': (
                    features.agile_effectiveness +
                    features.risk_mitigation +
                    features.management_satisfaction +
                    features.supply_chain_improvement +
                    features.time_efficiency
                ) / 5,
                'strengths': strengths if strengths else ["No significant strengths identified"],
                'recommendations': recommendations if recommendations else ["Project metrics are satisfactory"],
                'risk_level': 'Low' if result['success'] else 'High'
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis error: {str(e)}")
