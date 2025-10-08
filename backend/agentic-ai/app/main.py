from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
import uvicorn
import logging

from app.graph.workflow import agentic_workflow
from app.graph.state import GraphState
from app.config import config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="IT Analytics Agentic AI",
    description="Intelligent AI agents for IT project analytics and insights",
    version="1.0.0"
)

class QueryRequest(BaseModel):
    query: str
    context: Optional[Dict[str, Any]] = None

class QueryResponse(BaseModel):
    success: bool
    response: str
    agent: Optional[str] = None
    recommendations: list = []
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

@app.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """Process user query through agentic workflow"""
    try:
        logger.info(f"Processing query: {request.query}")
        
        # Initialize state
        initial_state: GraphState = {
            "messages": [],
            "user_query": request.query,
            "current_agent": None,
            "available_agents": [],
            "selected_tools": [],
            "api_data": {},
            "analysis_results": {},
            "recommendations": [],
            "next_step": "router",
            "error": None
        }
        
        # Execute workflow
        final_state = await agentic_workflow.ainvoke(initial_state)
        
        # Extract response
        analysis_results = final_state.get("analysis_results", {})
        final_response = analysis_results.get("final_response", "No response generated")
        
        return QueryResponse(
            success=True,
            response=final_response,
            agent=final_state.get("current_agent"),
            recommendations=final_state.get("recommendations", []),
            data=analysis_results,
            error=final_state.get("error")
        )
        
    except Exception as e:
        logger.error(f"Query processing failed: {e}")
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "IT Analytics Agentic AI",
        "version": "1.0.0"
    }

@app.get("/agents")
async def list_agents():
    """List available agents"""
    return {
        "agents": {
            "risk_analyst": "Risk analysis and prediction",
            "resource_optimizer": "Team resource optimization", 
            "cost_forecaster": "Budget and cost analysis",
            "anomaly_detector": "Pattern and anomaly detection"
        }
    }

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8001,
        reload=True
    )