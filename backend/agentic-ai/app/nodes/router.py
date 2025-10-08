from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from app.graph.state import GraphState
from app.config import config
import logging

logger = logging.getLogger(__name__)

class AgentRouter:
    """Routes queries to appropriate specialized agents"""
    
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model=config.GEMINI_MODEL,
            google_api_key=config.GEMINI_API_KEY,
            temperature=0
        )
        
        self.available_agents = {
            "risk_analyst": "Risk analysis, prediction, and mitigation",
            "resource_optimizer": "Team utilization and resource optimization", 
            "cost_forecaster": "Budget analysis and cost forecasting",
            "anomaly_detector": "Anomaly detection and pattern analysis",
            "general_analyst": "General project analytics and overview"
        }
    
    async def route_query(self, state: GraphState) -> GraphState:
        """Route user query to appropriate agent"""
        user_query = state["user_query"]
        
        # System prompt for routing
        system_prompt = f"""
        You are an intelligent router for an IT Analytics platform. 
        Analyze the user query and determine which specialized agent should handle it.
        
        Available Agents:
        {self._format_agents_list()}
        
        Respond with ONLY the agent name from the available list above.
        """
        
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_query)
        ]
        
        try:
            response = await self.llm.ainvoke(messages)
            selected_agent = response.content.strip().lower()
            
            # Validate agent selection
            if selected_agent not in self.available_agents:
                selected_agent = "general_analyst"
                
            logger.info(f"Router selected agent: {selected_agent} for query: {user_query}")
            
            return {
                **state,
                "current_agent": selected_agent,
                "next_step": f"agent_{selected_agent}",
                "available_agents": list(self.available_agents.keys())
            }
            
        except Exception as e:
            logger.error(f"Routing failed: {e}")
            return {
                **state,
                "current_agent": "general_analyst",
                "next_step": "agent_general_analyst", 
                "error": f"Routing error: {str(e)}"
            }
    
    def _format_agents_list(self) -> str:
        """Format available agents for prompt"""
        return "\n".join([
            f"- {name}: {description}" 
            for name, description in self.available_agents.items()
        ])

# Router node function
async def route_node(state: GraphState) -> GraphState:
    """Node function for routing"""
    router = AgentRouter()
    return await router.route_query(state)