from langchain.tools import BaseTool
from langchain.pydantic_v1 import BaseModel, Field
from typing import Type, Optional, Dict, Any, List
import httpx
import logging
from app.config import config

logger = logging.getLogger(__name__)

# Input Schemas
class ProjectSearchInput(BaseModel):
    risk_level: Optional[str] = Field(default=None, description="Filter by risk level")
    project_type: Optional[str] = Field(default=None, description="Filter by project type")
    limit: int = Field(default=50, description="Number of projects to return")

class RiskPredictionInput(BaseModel):
    project_id: int = Field(description="ID of the project to analyze")

class AnalyticsInput(BaseModel):
    days_back: int = Field(default=30, description="Number of days to look back")

class TeamPerformanceInput(BaseModel):
    days_back: int = Field(default=30, description="Number of days to analyze")

class CostAnalysisInput(BaseModel):
    project_id: Optional[int] = Field(default=None, description="Specific project ID to analyze")
    detailed: bool = Field(default=False, description="Whether to get detailed analysis")

class AnomalyDetectionInput(BaseModel):
    detection_type: Optional[str] = Field(default=None, description="Type of anomalies to detect")
    severity_filter: Optional[str] = Field(default=None, description="Filter by severity level")

class BaseAPITool(BaseTool):
    """Base class for API tools with common functionality"""
    
    base_url: str = config.IT_ANALYTICS_BASE_URL
    api_prefix: str = config.API_V1_PREFIX
    timeout: float = 30.0
    
    async def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make HTTP request to API"""
        url = f"{self.base_url}{self.api_prefix}{endpoint}"
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                logger.info(f"Making {method} request to {url}")
                response = await client.request(method, url, **kwargs)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            logger.error(f"API request failed: {e}")
            return {"error": f"API request failed: {str(e)}"}
        except Exception as e:
            logger.error(f"Unexpected error in API request: {e}")
            return {"error": f"Unexpected error: {str(e)}"}

class ProjectSearchTool(BaseAPITool):
    name: str = "project_search"
    description: str = "Search and filter projects by risk level, type, or other criteria"
    args_schema: Type[BaseModel] = ProjectSearchInput
    
    def _run(self, risk_level: Optional[str] = None, 
             project_type: Optional[str] = None, limit: int = 50) -> str:
        """Synchronous version - not implemented"""
        raise NotImplementedError("This tool only supports async execution")
    
    async def _arun(self, risk_level: Optional[str] = None,
                   project_type: Optional[str] = None, limit: int = 50) -> str:
        """Search projects with filters"""
        params = {"limit": limit}
        if risk_level:
            params["risk_level"] = risk_level
        if project_type:
            params["project_type"] = project_type
            
        data = await self._make_request("GET", "/projects/", params=params)
        
        if "error" in data:
            return f"Error searching projects: {data['error']}"
        
        return f"Found {len(data)} projects matching criteria. " + \
               f"Risk levels: {', '.join(set(p.get('risk_level', 'Unknown') for p in data))}"

class RiskPredictionTool(BaseAPITool):
    name: str = "risk_prediction"
    description: str = "Predict risk score for a specific project"
    args_schema: Type[BaseModel] = RiskPredictionInput
    
    def _run(self, project_id: int) -> str:
        raise NotImplementedError("This tool only supports async execution")
    
    async def _arun(self, project_id: int) -> str:
        """Predict risk for a specific project"""
        data = await self._make_request("GET", f"/risks/predict/{project_id}")
        
        if "error" in data:
            return f"Error predicting risk: {data['error']}"
        
        risk_score = data.get('overall_risk_score', 0)
        risk_level = data.get('risk_level', 'Unknown')
        components = data.get('component_risks', {})
        
        component_info = ", ".join([f"{k}: {v}" for k, v in components.items()])
        return f"Project {project_id} risk: {risk_score} ({risk_level}). Components: {component_info}"

class RiskDashboardTool(BaseAPITool):
    name: str = "risk_dashboard"
    description: str = "Get comprehensive risk dashboard data"
    args_schema: Type[BaseModel] = AnalyticsInput
    
    def _run(self, days_back: int = 30) -> str:
        raise NotImplementedError("This tool only supports async execution")
    
    async def _arun(self, days_back: int = 30) -> str:
        """Get risk dashboard data"""
        data = await self._make_request("GET", "/analytics/risk-dashboard", 
                                       params={"days_back": days_back})
        
        if "error" in data:
            return f"Error getting risk dashboard: {data['error']}"
        
        summary = data.get('summary', {})
        risk_dist = data.get('risk_distribution', {})
        
        return (f"Risk Dashboard (last {days_back} days): "
               f"{summary.get('total_projects', 0)} projects, "
               f"{risk_dist.get('high_risk', 0)} high risk, "
               f"{risk_dist.get('medium_risk', 0)} medium risk, "
               f"{summary.get('recent_anomalies', 0)} anomalies")

class TeamPerformanceTool(BaseAPITool):
    name: str = "team_performance"
    description: str = "Analyze team performance and utilization metrics"
    args_schema: Type[BaseModel] = TeamPerformanceInput
    
    def _run(self, days_back: int = 30) -> str:
        raise NotImplementedError("This tool only supports async execution")
    
    async def _arun(self, days_back: int = 30) -> str:
        """Get team performance data"""
        data = await self._make_request("GET", "/analytics/team-performance", 
                                       params={"days_back": days_back})
        
        if "error" in data:
            return f"Error getting team performance: {data['error']}"
        
        performance = data.get('team_performance', [])
        total_members = len(performance)
        
        if total_members == 0:
            return "No team performance data available"
        
        # Calculate average utilization
        utilizations = [p.get('utilization_rate', 0) for p in performance]
        avg_utilization = sum(utilizations) / len(utilizations) if utilizations else 0
        
        return f"Team performance: {total_members} members, average utilization: {avg_utilization:.1%}"

class UtilizationAnalysisTool(BaseAPITool):
    name: str = "utilization_analysis"
    description: str = "Analyze resource utilization and identify optimization opportunities"
    args_schema: Type[BaseModel] = AnalyticsInput
    
    def _run(self, days_back: int = 14) -> str:
        raise NotImplementedError("This tool only supports async execution")
    
    async def _arun(self, days_back: int = 14) -> str:
        """Analyze resource utilization"""
        data = await self._make_request("GET", "/resource-utilization/analyze", 
                                       params={"days_back": days_back})
        
        if "error" in data:
            return f"Error analyzing utilization: {data['error']}"
        
        alerts = data.get('alerts', [])
        utilization_data = data.get('utilization_summary', [])
        
        high_alerts = len([a for a in alerts if a.get('severity') == 'high'])
        
        return f"Utilization analysis: {len(alerts)} total alerts, {high_alerts} high severity"

class CostForecastTool(BaseAPITool):
    name: str = "cost_forecast"
    description: str = "Forecast cost overruns and analyze budget risks"
    
    def _run(self, project_id: int) -> str:
        raise NotImplementedError("This tool only supports async execution")
    
    async def _arun(self, project_id: int) -> str:
        """Forecast cost overrun for a project"""
        data = await self._make_request("GET", f"/cost-forecasting/forecast/{project_id}")
        
        if "error" in data:
            return f"Error forecasting cost: {data['error']}"
        
        probability = data.get('overrun_probability', 0)
        amount = data.get('overrun_amount', 0)
        
        return f"Cost forecast for project {project_id}: {probability:.1%} overrun probability, ${amount:,.2f} potential overrun"

class AnomalyDetectionTool(BaseAPITool):
    name: str = "anomaly_detection"
    description: str = "Detect anomalies in project data and daily logs"
    args_schema: Type[BaseModel] = AnalyticsInput
    
    def _run(self, days_back: int = 30) -> str:
        raise NotImplementedError("This tool only supports async execution")
    
    async def _arun(self, days_back: int = 30) -> str:
        """Detect anomalies"""
        data = await self._make_request("POST", "/risks/detect-anomalies", 
                                       params={"days_back": days_back})
        
        if "error" in data:
            return f"Error detecting anomalies: {data['error']}"
        
        anomalies = data.get('anomalies_detected', 0)
        anomaly_list = data.get('anomalies', [])
        
        if anomalies == 0:
            return f"No anomalies detected in the last {days_back} days"
        
        # Count by severity
        severities = {}
        for anomaly in anomaly_list:
            severity = anomaly.get('severity', 'unknown')
            severities[severity] = severities.get(severity, 0) + 1
        
        severity_info = ", ".join([f"{count} {sev}" for sev, count in severities.items()])
        return f"Detected {anomalies} anomalies in last {days_back} days: {severity_info}"

class CostAnalysisTool(BaseAPITool):
    name: str = "cost_analysis"
    description: str = "Comprehensive cost analysis across projects"
    args_schema: Type[BaseModel] = CostAnalysisInput
    
    def _run(self, project_id: Optional[int] = None, detailed: bool = False) -> str:
        raise NotImplementedError("This tool only supports async execution")
    
    async def _arun(self, project_id: Optional[int] = None, detailed: bool = False) -> str:
        """Analyze costs across projects"""
        if project_id:
            # Get specific project cost forecast
            data = await self._make_request("GET", f"/cost-forecasting/forecast/{project_id}")
            if "error" in data:
                return f"Error analyzing project costs: {data['error']}"
            
            probability = data.get('overrun_probability', 0)
            return f"Project {project_id} cost analysis: {probability:.1%} overrun risk"
        else:
            # Get portfolio cost analysis
            data = await self._make_request("GET", "/cost-forecasting/budget-alerts")
            if "error" in data:
                return f"Error analyzing portfolio costs: {data['error']}"
            
            alerts = data.get('alerts', [])
            high_risk = len([a for a in alerts if a.get('severity') == 'high'])
            return f"Portfolio cost analysis: {len(alerts)} budget alerts, {high_risk} high risk"

class DetailedAnomalyTool(BaseAPITool):
    name: str = "detailed_anomaly_analysis"
    description: str = "Get detailed anomaly analysis with filtering options"
    args_schema: Type[BaseModel] = AnomalyDetectionInput
    
    def _run(self, detection_type: Optional[str] = None, severity_filter: Optional[str] = None) -> str:
        raise NotImplementedError("This tool only supports async execution")
    
    async def _arun(self, detection_type: Optional[str] = None, severity_filter: Optional[str] = None) -> str:
        """Get detailed anomaly analysis"""
        data = await self._make_request("POST", "/risks/detect-anomalies", params={"days_back": 30})
        
        if "error" in data:
            return f"Error getting detailed anomalies: {data['error']}"
        
        anomalies = data.get('anomalies', [])
        
        # Apply filters
        if severity_filter:
            filtered = [a for a in anomalies if a.get('severity') == severity_filter]
            return f"Found {len(filtered)} {severity_filter} severity anomalies"
        
        if detection_type:
            filtered = [a for a in anomalies if detection_type in a.get('anomaly_type', '')]
            return f"Found {len(filtered)} {detection_type} type anomalies"
        
        return f"Detailed anomaly analysis: {len(anomalies)} total anomalies"

# Tool registry
def get_all_tools() -> List[BaseAPITool]:
    """Get all available tools"""
    return [
        ProjectSearchTool(),
        RiskPredictionTool(),
        RiskDashboardTool(),
        TeamPerformanceTool(),
        UtilizationAnalysisTool(),
        CostForecastTool(),
        AnomalyDetectionTool(),
        CostAnalysisTool(),
        DetailedAnomalyTool()
    ]

def get_tool_by_name(name: str) -> Optional[BaseAPITool]:
    """Get specific tool by name"""
    tools = {tool.name: tool for tool in get_all_tools()}
    return tools.get(name)