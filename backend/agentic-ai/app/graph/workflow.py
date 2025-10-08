from langgraph.graph import StateGraph, END
from app.graph.state import GraphState
from app.nodes.router import route_node
from app.nodes.risk_analyst import risk_analyst_node
from app.nodes.resource_optimizer import resource_optimizer_node
from app.nodes.cost_forecaster import cost_forecaster_node
from app.nodes.anomaly_detector import anomaly_detector_node
import logging

logger = logging.getLogger(__name__)

class WorkflowBuilder:
    """Builds and manages the agent workflow graph"""
    
    def __init__(self):
        self.graph = StateGraph(GraphState)
        self._build_graph()
    
    def _build_graph(self):
        """Build the workflow graph with nodes and edges"""
        
        # Add nodes
        self.graph.add_node("router", route_node)
        self.graph.add_node("agent_risk_analyst", risk_analyst_node)
        self.graph.add_node("agent_resource_optimizer", resource_optimizer_node)
        self.graph.add_node("agent_cost_forecaster", cost_forecaster_node)
        self.graph.add_node("agent_anomaly_detector", anomaly_detector_node)
        self.graph.add_node("generate_response", self._generate_response_node)
        self.graph.add_node("handle_error", self._handle_error_node)
        
        # Define entry point
        self.graph.set_entry_point("router")
        
        # Define routing logic
        self.graph.add_conditional_edges(
            "router",
            self._route_to_agent,
            {
                "agent_risk_analyst": "agent_risk_analyst",
                "agent_resource_optimizer": "agent_resource_optimizer", 
                "agent_cost_forecaster": "agent_cost_forecaster",
                "agent_anomaly_detector": "agent_anomaly_detector",
                "handle_error": "handle_error"
            }
        )
        
        # Connect agent nodes to response generation
        self.graph.add_edge("agent_risk_analyst", "generate_response")
        self.graph.add_edge("agent_resource_optimizer", "generate_response")
        self.graph.add_edge("agent_cost_forecaster", "generate_response")
        self.graph.add_edge("agent_anomaly_detector", "generate_response")
        
        # Final nodes
        self.graph.add_edge("generate_response", END)
        self.graph.add_edge("handle_error", END)
    
    def _route_to_agent(self, state: GraphState) -> str:
        """Route to appropriate agent based on current_agent"""
        current_agent = state.get("current_agent")
        
        if not current_agent:
            return "handle_error"
        
        agent_node = f"agent_{current_agent}"
        
        # Validate that the node exists
        if agent_node in ["agent_risk_analyst", "agent_resource_optimizer", 
                         "agent_cost_forecaster", "agent_anomaly_detector"]:
            return agent_node
        else:
            return "handle_error"
    
    async def _generate_response_node(self, state: GraphState) -> GraphState:
        """Generate final response"""
        try:
            # Extract the last agent response
            messages = state.get("messages", [])
            if messages:
                last_message = messages[-1]
                final_response = last_message.content
            else:
                final_response = "No response generated"
            
            return {
                **state,
                "analysis_results": {
                    **state.get("analysis_results", {}),
                    "final_response": final_response
                },
                "recommendations": self._extract_recommendations(final_response)
            }
            
        except Exception as e:
            logger.error(f"Response generation failed: {e}")
            return {
                **state,
                "error": f"Response generation failed: {str(e)}"
            }
    
    async def _handle_error_node(self, state: GraphState) -> GraphState:
        """Handle errors in the workflow"""
        error = state.get("error", "Unknown error occurred")
        logger.error(f"Workflow error: {error}")
        
        return {
            **state,
            "analysis_results": {
                "error": error,
                "final_response": f"I encountered an error: {error}. Please try again or rephrase your question."
            }
        }
    
    def _extract_recommendations(self, response: str) -> list:
        """Extract recommendations from agent response"""
        # Simple extraction - can be enhanced with more sophisticated NLP
        recommendations = []
        lines = response.split('\n')
        
        for line in lines:
            line = line.strip()
            if any(indicator in line.lower() for indicator in 
                  ['recommend', 'suggest', 'should', 'consider', 'advise']):
                recommendations.append(line)
        
        return recommendations[:5]  # Limit to top 5 recommendations
    
    def get_graph(self):
        """Get the compiled graph"""
        return self.graph.compile()

# Global graph instance
workflow_builder = WorkflowBuilder()
agentic_workflow = workflow_builder.get_graph()