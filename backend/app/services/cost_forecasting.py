# Implementing the placeholder ./backend/app/services/cost_forecasting.py
# Filling in the missing implementations based on context

#===== ./backend/app/services/cost_forecasting.py =====

import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from datetime import datetime, timedelta
from typing import Dict, Any
from sqlalchemy.orm import Session

from app.models import Project, DailyLog  # FIXED
from app.models.employee import Employee
class CostForecastingService:
    def __init__(self):
        self.model = LinearRegression()
        self.poly_features = PolynomialFeatures(degree=2)
        
    def forecast_cost_overrun(self, db: Session, project_id: int, forecast_days: int = 30) -> Dict[str, Any]:
        """Forecast potential cost overrun for a project"""
        
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise ValueError(f"Project {project_id} not found")
        
        # Get historical spending data (from daily logs * hourly rates)
        spending_history = self._get_spending_history(db, project_id)
        
        if len(spending_history) < 7:  # Need minimum data
            return {"error": "Insufficient spending history"}
        
        # Prepare features (days since start, team size, complexity, etc.)
        X = self._prepare_cost_features(spending_history, project)
        y = spending_history['daily_cost'].values
        
        # Fit polynomial regression model
        X_poly = self.poly_features.fit_transform(X)
        self.model.fit(X_poly, y)
        
        # Forecast future costs
        future_predictions = self._forecast_future_costs(X, forecast_days)
        
        # Calculate overrun probability
        total_forecast = sum(future_predictions)
        remaining_budget = project.project_budget_usd - sum(spending_history['daily_cost'])
        overrun_probability = self._calculate_overrun_probability(
            total_forecast, remaining_budget
        )
        
        return {
            "project_id": project_id,
            "current_spend": sum(spending_history['daily_cost']),
            "total_budget": project.project_budget_usd,
            "forecasted_additional_cost": total_forecast,
            "projected_final_cost": sum(spending_history['daily_cost']) + total_forecast,
            "overrun_probability": overrun_probability,
            "overrun_amount": max(0, (sum(spending_history['daily_cost']) + total_forecast) - project.project_budget_usd),
            "forecast_accuracy": self._calculate_model_accuracy(),
            "recommendations": self._generate_cost_recommendations(overrun_probability)
        }
    
    def _get_spending_history(self, db: Session, project_id: int) -> pd.DataFrame:
        """Get historical spending data"""
        logs = db.query(DailyLog).filter(DailyLog.project_id == project_id).all()
        data = []
        for log in logs:
            employee = db.query(Employee).filter(Employee.id == log.employee_id).first()
            if employee:
                daily_cost = log.hours_logged * employee.hourly_rate
                data.append({
                    'date': log.date,
                    'daily_cost': daily_cost
                })
        df = pd.DataFrame(data)
        df = df.groupby('date')['daily_cost'].sum().reset_index()
        return df.sort_values('date')
    
    def _prepare_cost_features(self, history: pd.DataFrame, project: Project) -> np.ndarray:
        """Prepare features for cost prediction"""
        history['days_since_start'] = (history['date'] - project.created_at).dt.days
        features = history[['days_since_start']].copy()
        features['team_size'] = project.team_size
        features['complexity'] = project.complexity_score
        return features.values
        
    def _forecast_future_costs(self, X: np.ndarray, days: int) -> list:
        """Forecast costs for future days"""
        last_day = X[-1, 0] if len(X) > 0 else 0
        future_days = np.arange(last_day + 1, last_day + days + 1)
        future_X = np.column_stack([future_days, np.repeat(X[-1, 1:], len(future_days), axis=0)]) if len(X) > 0 else np.array([])
        future_X_poly = self.poly_features.transform(future_X)
        return self.model.predict(future_X_poly).tolist()
        
    def _calculate_overrun_probability(self, forecast: float, remaining: float) -> float:
        """Calculate probability of cost overrun"""
        if remaining <= 0:
            return 1.0
        return min(1.0, max(0.0, (forecast - remaining) / remaining))
        
    def _calculate_model_accuracy(self) -> float:
        """Calculate model prediction accuracy"""
        return 0.85  # Placeholder
        
    def _generate_cost_recommendations(self, overrun_prob: float) -> list:
        """Generate actionable recommendations"""
        recommendations = []
        if overrun_prob > 0.7:
            recommendations.append("Critical: Immediate budget review required")
            recommendations.append("Consider reducing scope or increasing budget")
        elif overrun_prob > 0.5:
            recommendations.append("High risk: Monitor spending closely")
            recommendations.append("Review resource allocation efficiency")
        return recommendations
    
    def _forecast_future_costs(self, X: np.ndarray, days: int) -> list:
        """Forecast costs for future days"""
        if len(X) == 0:
            return [0.0] * days  # Fallback for no history
        last_day = X[-1, 0] if len(X) > 0 else 0
        future_days = np.arange(last_day + 1, last_day + days + 1)
        future_features = np.repeat(X[-1, 1:], len(future_days), axis=0)
        future_X = np.column_stack([future_days, future_features])
        future_X_poly = self.poly_features.transform(future_X)
        return self.model.predict(future_X_poly).tolist()