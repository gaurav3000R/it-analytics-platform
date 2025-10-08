# Completing the truncated ./backend/app/services/gemini_service.py
# Based on context, adding logical completion for portfolio analysis and helper methods

#===== ./backend/app/services/gemini_service.py =====

import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session

from app.utils.gemini_client import get_gemini_client
from app.models.project import Project
from app.models.risk import RiskScore, Anomaly

logger = logging.getLogger(__name__)

class GeminiAnalyticsService:
    def __init__(self):
        self.gemini_client = get_gemini_client()
        
    async def generate_project_risk_analysis(self, db: Session, project_id: str) -> Dict[str, Any]:
        """Generate AI-powered risk analysis for a specific project"""
        
        project = db.query(Project).filter(Project.project_id == project_id).first()
        if not project:
            raise ValueError(f"Project {project_id} not found")
        
        # Prepare project data for analysis
        project_data = self._prepare_project_data(project)
        
        # Create prompt for risk analysis
        prompt = self._create_risk_analysis_prompt(project_data)
        
        try:
            # Generate analysis using Gemini
            analysis = await self.gemini_client.generate_content_with_retry(
                prompt=prompt,
                text_only=True,
                max_retries=3
            )
            
            # Parse and structure the response
            structured_analysis = self._parse_risk_analysis(analysis)
            
            # Update project with AI insights
            project.ai_risk_analysis = analysis
            project.ai_insights_updated_at = datetime.now()
            db.commit()
            
            return {
                "project_id": project_id,
                "analysis": structured_analysis,
                "raw_analysis": analysis,
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to generate risk analysis for project {project_id}: {e}")
            raise
    
    async def generate_recommendations(self, db: Session, project_id: str) -> Dict[str, Any]:
        """Generate AI-powered recommendations for project improvement"""
        
        project = db.query(Project).filter(Project.project_id == project_id).first()
        if not project:
            raise ValueError(f"Project {project_id} not found")
        
        # Get recent risk scores and anomalies
        recent_risks = db.query(RiskScore).filter(
            RiskScore.project_id == project.id
        ).order_by(RiskScore.date.desc()).limit(3).all()
        
        recent_anomalies = db.query(Anomaly).filter(
            Anomaly.project_id == project.id
        ).order_by(Anomaly.detected_at.desc()).limit(5).all()
        
        # Prepare data for recommendations
        context_data = {
            "project": self._prepare_project_data(project),
            "recent_risks": [self._risk_score_to_dict(risk) for risk in recent_risks],
            "recent_anomalies": [self._anomaly_to_dict(anomaly) for anomaly in recent_anomalies]
        }
        
        prompt = self._create_recommendations_prompt(context_data)
        
        try:
            recommendations = await self.gemini_client.generate_content_with_retry(
                prompt=prompt,
                text_only=True,
                max_retries=3
            )
            
            # Structure the recommendations
            structured_recommendations = self._parse_recommendations(recommendations)
            
            # Update project with recommendations
            project.ai_recommendations = recommendations
            project.ai_insights_updated_at = datetime.now()
            db.commit()
            
            return {
                "project_id": project_id,
                "recommendations": structured_recommendations,
                "raw_recommendations": recommendations,
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to generate recommendations for project {project_id}: {e}")
            raise
    
    async def analyze_portfolio_trends(self, db: Session) -> Dict[str, Any]:
        """Analyze trends across all projects in the portfolio"""
        
        projects = db.query(Project).filter(Project.risk_level.isnot(None)).all()
        
        if not projects:
            return {"error": "No projects found for analysis"}
        
        # Prepare portfolio data
        portfolio_data = {
            "total_projects": len(projects),
            "risk_distribution": self._calculate_risk_distribution(projects),
            "common_risk_factors": self._identify_common_risk_factors(projects),
            "project_types": self._calculate_project_types(projects),
            "team_experience_distribution": self._calculate_team_experience_distribution(projects)
        }
        
        prompt = self._create_portfolio_trends_prompt(portfolio_data)
        
        try:
            analysis = await self.gemini_client.generate_content_with_retry(
                prompt=prompt,
                text_only=True,
                max_retries=3
            )
            
            structured_analysis = self._parse_portfolio_trends(analysis)
            
            return {
                "analysis": structured_analysis,
                "raw_analysis": analysis,
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to generate portfolio trends: {e}")
            raise
    
    async def generate_executive_summary(self, db: Session) -> Dict[str, Any]:
        """Generate executive summary of overall project health"""
        
        projects = db.query(Project).all()
        
        # Aggregate key metrics
        aggregate_data = {
            "total_projects": len(projects),
            "average_risk_level": self._calculate_average_risk(projects),
            "budget_summary": self._calculate_budget_summary(projects),
            "timeline_summary": self._calculate_timeline_summary(projects)
        }
        
        prompt = self._create_executive_summary_prompt(aggregate_data)
        
        try:
            summary = await self.gemini_client.generate_content_with_retry(
                prompt=prompt,
                text_only=True,
                max_retries=3
            )
            
            structured_summary = self._parse_executive_summary(summary)
            
            return {
                "summary": structured_summary,
                "raw_summary": summary,
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to generate executive summary: {e}")
            raise
    
    def _prepare_project_data(self, project: Project) -> Dict[str, Any]:
        """Prepare project data for AI analysis"""
        return {
            "project_id": project.project_id,
            "type": project.project_type,
            "team_size": project.team_size,
            "budget_usd": project.project_budget_usd,
            "complexity_score": project.complexity_score,
            "risk_level": project.risk_level,
            # Add more fields as needed
        }
    
    def _create_risk_analysis_prompt(self, project_data: Dict) -> str:
        """Create prompt for risk analysis"""
        return f"Analyze the following project data and provide a detailed risk analysis: {json.dumps(project_data)}"
    
    def _parse_risk_analysis(self, analysis: str) -> Dict[str, Any]:
        """Parse AI-generated risk analysis"""
        # Implement parsing logic, e.g., extract sections
        return {"full_text": analysis}  # Placeholder
    
    def _create_recommendations_prompt(self, context_data: Dict) -> str:
        """Create prompt for recommendations"""
        return f"Generate actionable recommendations based on this project context: {json.dumps(context_data)}"
    
    def _parse_recommendations(self, recommendations: str) -> List[str]:
        """Parse AI-generated recommendations"""
        return recommendations.split("\n")  # Simple split as placeholder
    
    def _calculate_risk_distribution(self, projects: List[Project]) -> Dict[str, int]:
        """Calculate risk level distribution"""
        distribution = {"Low": 0, "Medium": 0, "High": 0}
        for p in projects:
            if p.risk_level:
                distribution[p.risk_level] += 1
        return distribution
    
    def _identify_common_risk_factors(self, projects: List[Project]) -> List[str]:
        """Identify common risk factors across projects"""
        # Placeholder logic
        return ["High complexity", "Low team experience"]
    
    def _calculate_project_types(self, projects: List[Project]) -> Dict[str, int]:
        """Calculate distribution of project types"""
        types = {}
        for p in projects:
            if p.project_type:
                types[p.project_type] = types.get(p.project_type, 0) + 1
        return types
    
    def _calculate_team_experience_distribution(self, projects: List[Project]) -> Dict[str, int]:
        """Calculate team experience distribution"""
        experience = {}
        for p in projects:
            if p.team_experience_level:
                experience[p.team_experience_level] = experience.get(p.team_experience_level, 0) + 1
        return experience
    
    def _create_portfolio_trends_prompt(self, portfolio_data: Dict) -> str:
        """Create prompt for portfolio trends analysis"""
        return f"Analyze trends in this project portfolio: {json.dumps(portfolio_data)}"
    
    def _parse_portfolio_trends(self, analysis: str) -> Dict[str, Any]:
        """Parse AI-generated portfolio trends"""
        return {"full_text": analysis}  # Placeholder
    
    def _calculate_average_risk(self, projects: List[Project]) -> str:
        """Calculate average risk level"""
        risks = [p.risk_level for p in projects if p.risk_level]
        if not risks:
            return "Unknown"
        # Simple mode calculation
        return max(set(risks), key=risks.count)
    
    def _calculate_budget_summary(self, projects: List[Project]) -> Dict[str, float]:
        """Calculate budget summary"""
        total_budget = sum(p.project_budget_usd or 0 for p in projects)
        return {"total_budget": total_budget}
    
    def _calculate_timeline_summary(self, projects: List[Project]) -> Dict[str, float]:
        """Calculate timeline summary"""
        total_months = sum(p.estimated_timeline_months or 0 for p in projects)
        return {"total_months": total_months}
    
    def _create_executive_summary_prompt(self, aggregate_data: Dict) -> str:
        """Create prompt for executive summary"""
        return f"Generate an executive summary based on this aggregate data: {json.dumps(aggregate_data)}"
    
    def _parse_executive_summary(self, summary: str) -> Dict[str, Any]:
        """Parse AI-generated executive summary"""
        return {"full_text": summary}  # Placeholder
    
    def _risk_score_to_dict(self, risk: RiskScore) -> Dict[str, Any]:
        """Convert RiskScore to dict"""
        return {
            "overall_risk_score": risk.overall_risk_score,
            "date": risk.date.isoformat()
        }
    
    def _anomaly_to_dict(self, anomaly: Anomaly) -> Dict[str, Any]:
        """Convert Anomaly to dict"""
        return {
            "anomaly_type": anomaly.anomaly_type,
            "severity": anomaly.severity,
            "description": anomaly.description
        }