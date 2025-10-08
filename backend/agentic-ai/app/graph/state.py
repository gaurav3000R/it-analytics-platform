from typing import TypedDict, List, Dict, Any, Optional, Annotated
from langchain_core.messages import BaseMessage
import operator

class GraphState(TypedDict):
    """
    Represents the state of our graph.
    
    Attributes:
        messages: Messages in the conversation
        user_query: Original user query
        current_agent: Currently active agent
        available_agents: List of available agents
        selected_tools: Tools selected for current task
        api_data: Data fetched from APIs
        analysis_results: Results from data analysis
        recommendations: Generated recommendations
        next_step: Next step in workflow
        error: Any error that occurred
    """
    messages: Annotated[List[BaseMessage], operator.add]
    user_query: str
    current_agent: Optional[str]
    available_agents: List[str]
    selected_tools: List[str]
    api_data: Dict[str, Any]
    analysis_results: Dict[str, Any]
    recommendations: List[str]
    next_step: str
    error: Optional[str]