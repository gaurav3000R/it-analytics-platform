from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import pandas as pd
import numpy as np
import json

def calculate_business_days(start_date: datetime, end_date: datetime) -> int:
    """Calculate number of business days between two dates"""
    business_days = np.busday_count(
        start_date.date(),
        end_date.date(),
        weekmask='1111100'  # Mon-Fri
    )
    return int(business_days)

def get_date_range(days_back: int) -> tuple:
    """Get date range for analysis"""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days_back)
    return start_date, end_date

def calculate_percentage_change(old_value: float, new_value: float) -> float:
    """Calculate percentage change between two values"""
    if old_value == 0:
        return 0.0 if new_value == 0 else 100.0
    return ((new_value - old_value) / old_value) * 100

def normalize_score(value: float, min_val: float, max_val: float) -> float:
    """Normalize a value to 0-100 scale"""
    if max_val == min_val:
        return 50.0  # Default middle value
    return max(0, min(100, ((value - min_val) / (max_val - min_val)) * 100))

def calculate_trend(values: List[float], periods: int = 3) -> str:
    """Calculate trend direction from a list of values"""
    if len(values) < periods:
        return "insufficient_data"
    
    recent_values = values[-periods:]
    if len(recent_values) < 2:
        return "stable"
    
    # Simple linear regression slope
    x = np.arange(len(recent_values))
    slope = np.polyfit(x, recent_values, 1)[0]
    
    if slope > 0.1:
        return "increasing"
    elif slope < -0.1:
        return "decreasing"
    else:
        return "stable"

def format_currency(amount: float) -> str:
    """Format amount as currency string"""
    return f"${amount:,.2f}"

def format_hours(hours: float) -> str:
    """Format hours with proper suffix"""
    if hours == 1:
        return "1 hour"
    return f"{hours:.1f} hours"

def calculate_working_days_in_month(year: int, month: int) -> int:
    """Calculate number of working days in a given month"""
    start_date = datetime(year, month, 1)
    if month == 12:
        end_date = datetime(year + 1, 1, 1) - timedelta(days=1)
    else:
        end_date = datetime(year, month + 1, 1) - timedelta(days=1)
    
    return calculate_business_days(start_date, end_date)

def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """Safely divide two numbers, returning default if denominator is zero"""
    return numerator / denominator if denominator != 0 else default

def get_severity_color(severity: str) -> str:
    """Get color code for severity level"""
    colors = {
        'low': '#28a745',      # Green
        'medium': '#ffc107',   # Yellow
        'high': '#fd7e14',     # Orange
        'critical': '#dc3545'  # Red
    }
    return colors.get(severity.lower(), '#6c757d')  # Default gray

def calculate_project_health_score(metrics: Dict[str, float]) -> Dict[str, Any]:
    """Calculate overall project health score from various metrics"""
    
    # Weights for different metrics
    weights = {
        'completion_rate': 0.25,
        'budget_utilization': 0.20,
        'team_productivity': 0.20,
        'velocity_trend': 0.15,
        'issue_rate': 0.10,
        'timeline_adherence': 0.10
    }
    
    # Normalize metrics to 0-100 scale (higher is better)
    normalized_metrics = {}
    
    # Completion rate (higher is better)
    normalized_metrics['completion_rate'] = metrics.get('completion_rate', 50)
    
    # Budget utilization (80% is optimal, higher or lower is worse)
    budget_util = metrics.get('budget_utilization', 50)
    if budget_util <= 80:
        normalized_metrics['budget_utilization'] = budget_util * 1.25  # Scale up to 100
    else:
        normalized_metrics['budget_utilization'] = max(0, 100 - (budget_util - 80) * 2)
    
    # Team productivity (hours per completion point)
    normalized_metrics['team_productivity'] = min(100, metrics.get('team_productivity', 50))
    
    # Velocity trend (positive trend is better)
    velocity = metrics.get('velocity_trend', 0)
    normalized_metrics['velocity_trend'] = min(100, max(0, 50 + velocity * 10))
    
    # Issue rate (lower is better)
    issue_rate = metrics.get('issue_rate', 0)
    normalized_metrics['issue_rate'] = max(0, 100 - issue_rate * 10)
    
    # Timeline adherence (higher is better)
    normalized_metrics['timeline_adherence'] = metrics.get('timeline_adherence', 50)
    
    # Calculate weighted health score
    health_score = sum(
        normalized_metrics.get(metric, 50) * weight
        for metric, weight in weights.items()
    )
    
    # Determine health status
    if health_score >= 80:
        status = "excellent"
        color = "#28a745"
    elif health_score >= 60:
        status = "good"
        color = "#28a745"
    elif health_score >= 40:
        status = "fair"
        color = "#ffc107"
    elif health_score >= 20:
        status = "poor"
        color = "#fd7e14"
    else:
        status = "critical"
        color = "#dc3545"
    
    return {
        'score': round(health_score, 1),
        'status': status,
        'color': color,
        'components': normalized_metrics,
        'weights': weights
    }

class DataValidator:
    """Utility class for data validation"""
    
    @staticmethod
    def validate_date_range(start_date: str, end_date: str) -> bool:
        """Validate date range"""
        try:
            start = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            end = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            return start < end
        except:
            return False
    
    @staticmethod
    def validate_project_id(project_id: Any) -> bool:
        """Validate project ID"""
        try:
            return isinstance(project_id, int) and project_id > 0
        except:
            return False
    
    @staticmethod
    def validate_risk_score(score: Any) -> bool:
        """Validate risk score"""
        try:
            return isinstance(score, (int, float)) and 0 <= score <= 100
        except:
            return False

def generate_project_summary(project_data: Dict[str, Any]) -> str:
    """Generate a human-readable project summary"""
    
    name = project_data.get('name', 'Unknown Project')
    status = project_data.get('status', 'unknown').title()
    
    # Budget information
    budget = project_data.get('budget', 0)
    spent = project_data.get('current_spend', 0)
    budget_util = (spent / budget * 100) if budget > 0 else 0
    
    # Timeline information
    start_date = project_data.get('start_date')
    end_date = project_data.get('end_date')
    
    summary_parts = [f"Project {name} ({status})"]
    
    if budget > 0:
        summary_parts.append(f"Budget: {format_currency(spent)} of {format_currency(budget)} ({budget_util:.1f}%)")
    
    if start_date and end_date:
        try:
            start = datetime.fromisoformat(start_date)
            end = datetime.fromisoformat(end_date)
            duration = (end - start).days
            elapsed = (datetime.now() - start).days
            progress = (elapsed / duration * 100) if duration > 0 else 0
            
            summary_parts.append(f"Timeline: {elapsed} of {duration} days ({progress:.1f}%)")
        except:
            pass
    
    team_size = project_data.get('team_size', 0)
    if team_size:
        summary_parts.append(f"Team: {team_size} members")
    
    return " | ".join(summary_parts)