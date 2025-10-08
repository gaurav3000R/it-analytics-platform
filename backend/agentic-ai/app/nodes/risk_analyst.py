from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_google_genai import ChatGoogleGenerativeAI
from app.graph.state import GraphState
from app.tools.api_tools import get_tool_by_name
from app.config import config
import logging

logger = logging.getLogger(__name__)

class RiskAnalystNode:
    """Node for risk analysis and prediction"""
    
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model=config.GEMINI_MODEL,
            google_api_key=config.GEMINI_API_KEY,
            temperature=0.1
        )
        
        # Risk analysis specific tools
        self.tools = [
            get_tool_by_name("project_search"),
            get_tool_by_name("risk_prediction"), 
            get_tool_by_name("risk_dashboard"),
            get_tool_by_name("anomaly_detection")
        ]
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a Risk Analysis Specialist for IT projects.
            
            Your capabilities:
            - Analyze project risk levels and distributions
            - Predict risk scores for specific projects
            - Identify high-risk projects needing attention
            - Detect anomalies and unusual patterns
            - Provide risk mitigation recommendations
            
            Use the available tools to gather data and provide comprehensive risk analysis.
            Be proactive in identifying potential issues and suggesting solutions.
            
            Always provide:
            1. Clear risk assessment
            2. Data-driven insights  
            3. Actionable recommendations
            4. Priority areas for attention
            """),
            MessagesPlaceholder(variable_name="messages"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])
        
        self.agent = create_tool_calling_agent(self.llm, self.tools, self.prompt)
        self.agent_executor = AgentExecutor(agent=self.agent, tools=self.tools, verbose=True)
    
    async def process(self, state: GraphState) -> GraphState:
        """Process risk analysis queries"""
        try:
            user_query = state["user_query"]
            
            result = await self.agent_executor.ainvoke({
                "input": user_query,
                "messages": state.get("messages", [])
            })
            
            return {
                **state,
                "messages": state.get("messages", []) + [result["messages"][-1]],
                "analysis_results": {
                    "agent": "risk_analyst",
                    "output": result["output"],
                    "tools_used": [tool.name for tool in self.tools]
                },
                "next_step": "generate_response"
            }
            
        except Exception as e:
            logger.error(f"Risk analyst node failed: {e}")
            return {
                **state,
                "error": f"Risk analysis failed: {str(e)}",
                "next_step": "handle_error"
            }

# Node function
async def risk_analyst_node(state: GraphState) -> GraphState:
    """Node function for risk analysis"""
    node = RiskAnalystNode()
    return await node.process(state)