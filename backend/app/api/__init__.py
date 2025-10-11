from .ai_insights import router as ai_insights_router
from .analytics import router as analytics_router
from .bug_tracker import router as bug_tracker_router
from .cost_forecasting import router as cost_forecasting_router
from .projects import router as projects_router
from .resource_utilization import router as resource_utilization_router
from .risks import router as risks_router
from .risk_dashboard import router as risk_dashboard_router

__all__ = [
    "ai_insights_router",
    "analytics_router",
    "bug_tracker_router",
    "cost_forecasting_router",
    "projects_router",
    "resource_utilization_router",
    "risks_router",
    "risk_dashboard_router"
]