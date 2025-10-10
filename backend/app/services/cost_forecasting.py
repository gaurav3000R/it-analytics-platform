#===== ./backend/app/services/cost_forecasting.py =====

import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from datetime import datetime, timedelta
from typing import Dict, Any
from supabase import Client

from app.database import connect_db

class CostForecastingService:
    def __init__(self):
        self.model = LinearRegression()
        self.poly_features = PolynomialFeatures(degree=2)

    def forecast_cost_overrun(self, db: Client, project_id: int, forecast_days: int = 30) -> Dict[str, Any]:
        """Forecast potential cost overrun for a project"""
        project_response = db.table("projects").select("id, project_budget_usd, created_at, team_size, complexity_score").eq("id", project_id).single().execute()
        if not project_response.data:
            raise ValueError(f"Project {project_id} not found")
        project = project_response.data

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
        remaining_budget = project['project_budget_usd'] - sum(spending_history['daily_cost'])
        overrun_probability = self._calculate_overrun_probability(
            total_forecast, remaining_budget
        )

        return {
            "project_id": project_id,
            "current_spend": sum(spending_history['daily_cost']),
            "total_budget": project['project_budget_usd'],
            "forecasted_additional_cost": total_forecast,
            "projected_final_cost": sum(spending_history['daily_cost']) + total_forecast,
            "overrun_probability": overrun_probability,
            "overrun_amount": max(0, (sum(spending_history['daily_cost']) + total_forecast) - project['project_budget_usd']),
            "forecast_accuracy": self._calculate_model_accuracy(),
            "recommendations": self._generate_cost_recommendations(overrun_probability)
        }

    def _get_spending_history(self, db: Client, project_id: int) -> pd.DataFrame:
        """Get historical spending data"""
        logs_response = db.table("daily_logs").select("date, hours_logged, employee_id").eq("project_id", project_id).execute()
        logs = logs_response.data
        data = []
        for log in logs:
            employee_response = db.table("employees").select("hourly_rate").eq("id", log["employee_id"]).single().execute()
            if employee_response.data:
                daily_cost = log["hours_logged"] * employee_response.data["hourly_rate"]
                data.append({
                    'date': pd.to_datetime(log['date']),
                    'daily_cost': daily_cost
                })
        df = pd.DataFrame(data)
        df = df.groupby('date')['daily_cost'].sum().reset_index()
        return df.sort_values('date')

    def _prepare_cost_features(self, history: pd.DataFrame, project: Dict) -> np.ndarray:
        """Prepare features for cost prediction"""
        history['days_since_start'] = (history['date'] - pd.to_datetime(project['created_at'])).dt.days
        features = history[['days_since_start']].copy()
        features['team_size'] = project['team_size']
        features['complexity'] = project['complexity_score']
        return features.values

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