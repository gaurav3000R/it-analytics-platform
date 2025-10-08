from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_google_genai import ChatGoogleGenerativeAI
from app.graph.state import GraphState
from app.tools.api_tools import get_tool_by_name
from app.config import config
import logging

logger = logging.getLogger(__name__)

class ResourceOptimizerNode:
    """Node for resource utilization and optimization"""
    
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model=config.GEMINI_MODEL,
            google_api_key=config.GEMINI_API_KEY,
            temperature=0.1
        )
        
        # Resource optimization tools
        self.tools = [
            get_tool_by_name("team_performance"),
            get_tool_by_name("utilization_analysis"),
            get_tool_by_name("project_search")
        ]
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a Resource Optimization Specialist for IT teams.
            
            Your capabilities:
            - Analyze team utilization rates and productivity
            - Identify underutilized or overworked team members
            - Suggest resource rebalancing and workload distribution
            - Optimize team composition for project needs
            - Provide capacity planning insights
            
            Focus on:
            - Balancing workload across teams
            - Identifying skill gaps and training needs
            - Optimizing resource allocation
            - Improving team productivity metrics
            
            Provide practical, actionable recommendations for resource management.
            """),
            MessagesPlaceholder(variable_name="messages"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])
        
        self.agent = create_tool_calling_agent(self.llm, self.tools, self.prompt)
        self.agent_executor = AgentExecutor(agent=self.agent, tools=self.tools, verbose=True)
    
    async def process(self, state: GraphState) -> GraphState:
        """Process resource optimization queries"""
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
                    "agent": "resource_optimizer", 
                    "output": result["output"],
                    "tools_used": [tool.name for tool in self.tools]
                },
                "next_step": "generate_response"
            }
            
        except Exception as e:
            logger.error(f"Resource optimizer node failed: {e}")
            return {
                **state,
                "error": f"Resource optimization failed: {str(e)}",
                "next_step": "handle_error"
            }

# Node function
async def resource_optimizer_node(state: GraphState) -> GraphState:
    """Node function for resource optimization"""
    node = ResourceOptimizerNode()
    return await node.process(state)