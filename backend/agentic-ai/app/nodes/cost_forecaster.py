from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
from app.graph.state import GraphState
from app.tools.api_tools import get_tool_by_name
from app.config import config
import logging
import asyncio

logger = logging.getLogger(__name__)

class CostForecasterNode:
    """Node for cost forecasting and budget analysis"""
    
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model=config.GEMINI_MODEL,
            google_api_key=config.GEMINI_API_KEY,
            temperature=0.1
        )
        
        # Cost forecasting specific tools
        self.tools = [
            get_tool_by_name("cost_forecast"),
            get_tool_by_name("project_search"),
            get_tool_by_name("risk_dashboard")
        ]
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a Cost Forecasting and Budget Analysis Specialist for IT projects.

            Your expertise:
            - Predicting cost overruns and budget risks
            - Analyzing spending patterns and trends
            - Identifying financial risks and opportunities
            - Providing budget optimization recommendations
            - Financial planning and forecasting

            Key Focus Areas:
            1. **Cost Prediction**: Forecast potential overruns using historical data
            2. **Budget Analysis**: Analyze current spending vs allocated budgets
            3. **Risk Assessment**: Identify projects with high financial risk
            4. **Optimization**: Suggest cost-saving measures and efficiency improvements
            5. **Trend Analysis**: Identify spending patterns across projects

            Always provide:
            - Clear financial risk assessment
            - Data-driven cost predictions
            - Actionable budget recommendations
            - Priority financial alerts
            - Cost optimization strategies

            Use financial metrics like:
            - ROAS (Return on Advertising Spend) equivalent for projects
            - Budget utilization rates
            - Cost variance analysis
            - Burn rate calculations
            """),
            MessagesPlaceholder(variable_name="messages"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])
        
        self.agent = create_tool_calling_agent(self.llm, self.tools, self.prompt)
        self.agent_executor = AgentExecutor(agent=self.agent, tools=self.tools, verbose=True)
    
    async def process(self, state: GraphState) -> GraphState:
        """Process cost forecasting queries"""
        try:
            user_query = state["user_query"]
            
            # Enhance query with cost-specific context
            enhanced_query = await self._enhance_query_with_financial_context(user_query)
            
            result = await self.agent_executor.ainvoke({
                "input": enhanced_query,
                "messages": state.get("messages", [])
            })
            
            # Extract financial insights from the response
            financial_insights = await self._extract_financial_insights(result["output"])
            
            return {
                **state,
                "messages": state.get("messages", []) + [result["messages"][-1]],
                "analysis_results": {
                    "agent": "cost_forecaster",
                    "output": result["output"],
                    "financial_insights": financial_insights,
                    "tools_used": [tool.name for tool in self.tools],
                    "risk_level": self._assess_financial_risk(financial_insights)
                },
                "recommendations": self._generate_financial_recommendations(financial_insights),
                "next_step": "generate_response"
            }
            
        except Exception as e:
            logger.error(f"Cost forecaster node failed: {e}")
            return {
                **state,
                "error": f"Cost forecasting failed: {str(e)}",
                "next_step": "handle_error"
            }
    
    async def _enhance_query_with_financial_context(self, query: str) -> str:
        """Enhance user query with financial context"""
        financial_context_prompt = f"""
        User Query: {query}
        
        As a cost forecasting expert, analyze this query and provide comprehensive financial insights.
        Focus on:
        - Budget risks and opportunities
        - Cost prediction accuracy
        - Financial optimization strategies
        - Return on investment analysis
        
        Provide specific, actionable financial recommendations.
        """
        
        return financial_context_prompt
    
    async def _extract_financial_insights(self, response: str) -> dict:
        """Extract structured financial insights from agent response"""
        try:
            # Use LLM to extract structured insights
            insight_prompt = f"""
            Extract financial insights from the following analysis:
            
            {response}
            
            Return a JSON structure with:
            - overall_risk_level: "low", "medium", "high", "critical"
            - budget_utilization: percentage estimate
            - cost_trend: "increasing", "decreasing", "stable"
            - key_risk_factors: list of main risk factors
            - potential_savings: estimated savings opportunities
            - timeline_impact: how costs affect project timeline
            """
            
            messages = [
                SystemMessage(content="You are a financial data extractor. Return only valid JSON."),
                HumanMessage(content=insight_prompt)
            ]
            
            insight_response = await self.llm.ainvoke(messages)
            
            # Parse the JSON response
            import json
            import re
            
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', insight_response.content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                return {
                    "overall_risk_level": "medium",
                    "budget_utilization": 65,
                    "cost_trend": "stable",
                    "key_risk_factors": ["Insufficient data for detailed analysis"],
                    "potential_savings": 0,
                    "timeline_impact": "minimal"
                }
                
        except Exception as e:
            logger.warning(f"Financial insight extraction failed: {e}")
            return {
                "overall_risk_level": "unknown",
                "budget_utilization": 0,
                "cost_trend": "unknown",
                "key_risk_factors": ["Analysis incomplete"],
                "potential_savings": 0,
                "timeline_impact": "unknown"
            }
    
    def _assess_financial_risk(self, insights: dict) -> str:
        """Assess overall financial risk level"""
        risk_level = insights.get('overall_risk_level', 'medium')
        budget_utilization = insights.get('budget_utilization', 0)
        
        if risk_level == "critical" or budget_utilization > 90:
            return "high"
        elif risk_level == "high" or budget_utilization > 75:
            return "medium"
        else:
            return "low"
    
    def _generate_financial_recommendations(self, insights: dict) -> list:
        """Generate financial recommendations based on insights"""
        recommendations = []
        risk_level = insights.get('overall_risk_level', 'medium')
        budget_utilization = insights.get('budget_utilization', 0)
        cost_trend = insights.get('cost_trend', 'stable')
        
        # Risk-based recommendations
        if risk_level in ["high", "critical"]:
            recommendations.extend([
                "🚨 Immediate budget review required for high-risk projects",
                "💰 Implement strict cost controls and approval processes",
                "📊 Increase monitoring frequency to weekly reviews"
            ])
        
        # Budget utilization recommendations
        if budget_utilization > 80:
            recommendations.extend([
                "⚠️ High budget utilization detected - consider scope reduction",
                "📉 Identify non-essential expenses for potential cuts",
                "🔄 Reallocate budget from lower priority initiatives"
            ])
        elif budget_utilization < 40:
            recommendations.extend([
                "📈 Underutilized budget - consider accelerating deliverables",
                "🎯 Allocate additional resources to critical path items",
                "💡 Invest in quality improvements or additional features"
            ])
        
        # Cost trend recommendations
        if cost_trend == "increasing":
            recommendations.extend([
                "📈 Rising costs detected - analyze cost drivers",
                "🔍 Review vendor contracts and procurement processes",
                "⚡ Implement cost optimization initiatives"
            ])
        
        # General financial best practices
        recommendations.extend([
            "📋 Maintain detailed cost tracking and reporting",
            "🔮 Regular forecasting updates based on actual spending",
            "🤝 Stakeholder alignment on budget expectations"
        ])
        
        return recommendations[:5]  # Return top 5 recommendations

# Node function
async def cost_forecaster_node(state: GraphState) -> GraphState:
    """Node function for cost forecasting"""
    node = CostForecasterNode()
    return await node.process(state)