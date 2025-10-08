from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
from app.graph.state import GraphState
from app.tools.api_tools import get_tool_by_name
from app.config import config
import logging
import asyncio
from typing import Dict, List, Any
import re

logger = logging.getLogger(__name__)

class AnomalyDetectorNode:
    """Node for anomaly detection and pattern analysis"""
    
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model=config.GEMINI_MODEL,
            google_api_key=config.GEMINI_API_KEY,
            temperature=0.1
        )
        
        # Anomaly detection specific tools
        self.tools = [
            get_tool_by_name("anomaly_detection"),
            get_tool_by_name("project_search"),
            get_tool_by_name("team_performance"),
            get_tool_by_name("risk_dashboard")
        ]
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an Anomaly Detection and Pattern Analysis Specialist for IT projects.

            Your expertise:
            - Detecting unusual patterns in project data
            - Identifying outliers and deviations from normal behavior
            - Analyzing trends for unexpected changes
            - Correlating anomalies across different data sources
            - Providing early warning signals for potential issues

            Key Anomaly Types to Detect:
            1. **Temporal Anomalies**: Unusual time-based patterns (sudden spikes/drops)
            2. **Behavioral Anomalies**: Deviations from typical team/work patterns
            3. **Performance Anomalies**: Unexpected changes in productivity metrics
            4. **Resource Anomalies**: Unusual resource utilization patterns
            5. **Financial Anomalies**: Unexpected cost or budget patterns
            6. **Quality Anomalies**: Sudden changes in bug rates or quality metrics

            Detection Methods:
            - Statistical outlier detection
            - Pattern recognition across time series
            - Correlation analysis between metrics
            - Baseline comparison and deviation analysis
            - Cluster analysis for grouping similar anomalies

            Always provide:
            - Clear anomaly severity assessment
            - Root cause analysis hypotheses
            - Impact assessment on project outcomes
            - Immediate action recommendations
            - Preventive measures for future
            """),
            MessagesPlaceholder(variable_name="messages"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])
        
        self.agent = create_tool_calling_agent(self.llm, self.tools, self.prompt)
        self.agent_executor = AgentExecutor(agent=self.agent, tools=self.tools, verbose=True)
    
    async def process(self, state: GraphState) -> GraphState:
        """Process anomaly detection queries"""
        try:
            user_query = state["user_query"]
            
            # Enhance query with anomaly detection context
            enhanced_query = await self._enhance_query_with_anomaly_context(user_query)
            
            result = await self.agent_executor.ainvoke({
                "input": enhanced_query,
                "messages": state.get("messages", [])
            })
            
            # Extract anomaly insights from the response
            anomaly_insights = await self._extract_anomaly_insights(result["output"])
            
            return {
                **state,
                "messages": state.get("messages", []) + [result["messages"][-1]],
                "analysis_results": {
                    "agent": "anomaly_detector",
                    "output": result["output"],
                    "anomaly_insights": anomaly_insights,
                    "tools_used": [tool.name for tool in self.tools],
                    "alert_level": self._determine_alert_level(anomaly_insights)
                },
                "recommendations": self._generate_anomaly_recommendations(anomaly_insights),
                "next_step": "generate_response"
            }
            
        except Exception as e:
            logger.error(f"Anomaly detector node failed: {e}")
            return {
                **state,
                "error": f"Anomaly detection failed: {str(e)}",
                "next_step": "handle_error"
            }
    
    async def _enhance_query_with_anomaly_context(self, query: str) -> str:
        """Enhance user query with anomaly detection context"""
        anomaly_context_prompt = f"""
        User Query: {query}
        
        As an anomaly detection expert, analyze this query with focus on:
        - Identifying unusual patterns or outliers
        - Detecting deviations from expected behavior
        - Correlating anomalies across different metrics
        - Assessing severity and potential impact
        - Providing early warning signals
        
        Look for patterns in:
        - Team performance metrics
        - Project timeline deviations
        - Resource utilization spikes/drops
        - Cost and budget anomalies
        - Quality metric fluctuations
        
        Provide specific anomaly detection insights and immediate actions.
        """
        
        return anomaly_context_prompt
    
    async def _extract_anomaly_insights(self, response: str) -> dict:
        """Extract structured anomaly insights from agent response"""
        try:
            # Use LLM to extract structured insights
            insight_prompt = f"""
            Extract anomaly detection insights from the following analysis:
            
            {response}
            
            Return a JSON structure with:
            - overall_anomaly_level: "none", "low", "medium", "high", "critical"
            - anomaly_count: estimated number of anomalies detected
            - primary_anomaly_types: list of main anomaly categories found
            - highest_risk_areas: areas with most significant anomalies
            - correlation_findings: any correlated anomalies across metrics
            - time_pattern: temporal pattern of anomalies (sporadic, clustered, trending)
            - impact_assessment: potential business impact of anomalies
            """
            
            messages = [
                SystemMessage(content="You are an anomaly data extractor. Return only valid JSON."),
                HumanMessage(content=insight_prompt)
            ]
            
            insight_response = await self.llm.ainvoke(messages)
            
            # Parse the JSON response
            import json
            
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', insight_response.content, re.DOTALL)
            if json_match:
                insights = json.loads(json_match.group())
                
                # Validate and set defaults for missing fields
                default_insights = {
                    "overall_anomaly_level": "none",
                    "anomaly_count": 0,
                    "primary_anomaly_types": [],
                    "highest_risk_areas": [],
                    "correlation_findings": [],
                    "time_pattern": "unknown",
                    "impact_assessment": "unknown"
                }
                
                return {**default_insights, **insights}
            else:
                return self._get_default_anomaly_insights()
                
        except Exception as e:
            logger.warning(f"Anomaly insight extraction failed: {e}")
            return self._get_default_anomaly_insights()
    
    def _get_default_anomaly_insights(self) -> dict:
        """Return default anomaly insights when extraction fails"""
        return {
            "overall_anomaly_level": "none",
            "anomaly_count": 0,
            "primary_anomaly_types": ["No specific anomalies detected"],
            "highest_risk_areas": ["Insufficient data for detailed analysis"],
            "correlation_findings": ["No correlations identified"],
            "time_pattern": "unknown",
            "impact_assessment": "minimal"
        }
    
    def _determine_alert_level(self, insights: dict) -> str:
        """Determine the overall alert level based on anomaly insights"""
        anomaly_level = insights.get('overall_anomaly_level', 'none')
        anomaly_count = insights.get('anomaly_count', 0)
        
        if anomaly_level == "critical" or anomaly_count > 10:
            return "red"  # Critical - immediate action required
        elif anomaly_level == "high" or anomaly_count > 5:
            return "orange"  # High - urgent attention needed
        elif anomaly_level == "medium" or anomaly_count > 2:
            return "yellow"  # Medium - monitor closely
        else:
            return "green"  # Low/Normal - routine monitoring
    
    def _generate_anomaly_recommendations(self, insights: dict) -> list:
        """Generate anomaly-specific recommendations"""
        recommendations = []
        alert_level = self._determine_alert_level(insights)
        anomaly_types = insights.get('primary_anomaly_types', [])
        risk_areas = insights.get('highest_risk_areas', [])
        
        # Alert level based recommendations
        if alert_level == "red":
            recommendations.extend([
                "🚨 CRITICAL: Immediate investigation required for detected anomalies",
                "🆘 Activate incident response team for high-risk areas",
                "📞 Escalate to senior management with detailed analysis",
                "🛑 Consider temporary work stoppage in affected areas"
            ])
        elif alert_level == "orange":
            recommendations.extend([
                "⚠️ HIGH: Urgent attention needed for multiple anomalies",
                "🔍 Conduct deep-dive analysis on correlated anomalies",
                "📊 Increase monitoring frequency to daily reviews",
                "👥 Assign dedicated resources for anomaly investigation"
            ])
        elif alert_level == "yellow":
            recommendations.extend([
                "📈 MEDIUM: Monitor anomalies closely for pattern development",
                "📋 Document all detected anomalies and their characteristics",
                "🔔 Set up automated alerts for similar anomaly patterns",
                "📝 Create anomaly response plan for future occurrences"
            ])
        
        # Anomaly type specific recommendations
        if "temporal" in str(anomaly_types).lower():
            recommendations.extend([
                "⏰ Analyze time-based patterns for root causes",
                "📅 Review seasonal or cyclical factors affecting metrics",
                "🔄 Check for external events correlating with anomalies"
            ])
        
        if "performance" in str(anomaly_types).lower():
            recommendations.extend([
                "📊 Conduct team performance deep-dive analysis",
                "🎯 Identify skill gaps or training needs",
                "🛠️ Review tools and processes affecting productivity"
            ])
        
        if "resource" in str(anomaly_types).lower():
            recommendations.extend([
                "👥 Analyze resource allocation and utilization patterns",
                "💰 Review budget and cost anomalies correlation",
                "📈 Assess capacity planning and workload distribution"
            ])
        
        # General anomaly management recommendations
        recommendations.extend([
            "🔍 Implement continuous anomaly monitoring system",
            "📈 Establish baseline metrics for normal behavior",
            "🎯 Create anomaly severity classification framework",
            "🤖 Develop automated anomaly detection rules",
            "📋 Maintain anomaly response playbook"
        ])
        
        return recommendations[:6]  # Return top 6 recommendations
    
    async def _correlate_anomalies(self, anomaly_data: List[Dict]) -> List[Dict]:
        """Correlate multiple anomalies to identify patterns"""
        if not anomaly_data:
            return []
        
        correlation_prompt = f"""
        Analyze these anomalies and identify correlations:
        
        {anomaly_data}
        
        Look for:
        - Temporal correlations (anomalies happening around same time)
        - Metric correlations (anomalies affecting related metrics)
        - Team/project correlations (anomalies in same teams/projects)
        - Causal relationships (one anomaly causing others)
        
        Return correlated anomaly groups.
        """
        
        try:
            messages = [
                SystemMessage(content="You are an anomaly correlation analyzer."),
                HumanMessage(content=correlation_prompt)
            ]
            
            response = await self.llm.ainvoke(messages)
            return self._parse_correlation_results(response.content)
        except Exception as e:
            logger.warning(f"Anomaly correlation failed: {e}")
            return []
    
    def _parse_correlation_results(self, correlation_text: str) -> List[Dict]:
        """Parse correlation analysis results"""
        # This is a simplified parser - in production, you'd want more sophisticated parsing
        correlations = []
        
        # Look for correlated groups in the text
        lines = correlation_text.split('\n')
        current_group = None
        
        for line in lines:
            line = line.strip()
            if line.startswith('**') and line.endswith('**'):
                # New correlation group
                if current_group:
                    correlations.append(current_group)
                current_group = {"group_name": line.strip('*').strip(), "anomalies": []}
            elif line.startswith('-') and current_group:
                # Anomaly in current group
                current_group["anomalies"].append(line.strip('- ').strip())
        
        if current_group:
            correlations.append(current_group)
        
        return correlations

# Node function
async def anomaly_detector_node(state: GraphState) -> GraphState:
    """Node function for anomaly detection"""
    node = AnomalyDetectorNode()
    return await node.process(state)