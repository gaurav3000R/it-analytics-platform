#===== ./backend/app/services/cost_forecasting.py =====

import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.metrics import mean_absolute_error, r2_score
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from supabase import Client
import logging

logger = logging.getLogger(__name__)

class CostForecastingService:
    def __init__(self):
        self.model = LinearRegression()
        self.poly_features = PolynomialFeatures(degree=2)
        
    def forecast_cost_overrun(self, db: Client, project_id: int, forecast_days: int = 30) -> Dict[str, Any]:
        """
        Comprehensive cost overrun forecast with detailed metrics
        
        Args:
            db: Supabase client
            project_id: Project ID to forecast
            forecast_days: Number of days to forecast ahead
            
        Returns:
            Detailed forecast dictionary with predictions and recommendations
        """
        try:
            # Get project details
            project = self._get_project_details(db, project_id)
            if not project:
                raise ValueError(f"Project {project_id} not found")
            
            # Get historical spending data
            spending_history = self._get_spending_history(db, project_id)
            
            if len(spending_history) < 7:
                return self._generate_insufficient_data_response(project, forecast_days)
            
            # Calculate current metrics
            current_metrics = self._calculate_current_metrics(spending_history, project)
            
            # Prepare features and train model
            X, y = self._prepare_features_and_targets(spending_history, project)
            
            # Train forecasting model
            model_metrics = self._train_forecasting_model(X, y)
            
            # Generate forecasts
            forecast_data = self._generate_forecast(X, forecast_days, project)
            
            # Calculate overrun probability
            overrun_analysis = self._analyze_overrun_risk(
                spending_history, 
                forecast_data, 
                project,
                current_metrics
            )
            
            # Generate recommendations
            recommendations = self._generate_recommendations(
                overrun_analysis, 
                current_metrics,
                project
            )
            
            # Identify risk factors
            risk_factors = self._identify_risk_factors(
                spending_history,
                current_metrics,
                project
            )
            
            # Prepare comprehensive response
            response = {
                "project_id": project_id,
                "project_name": project.get('name', f"Project {project_id}"),
                "forecast_generated_at": datetime.now().isoformat(),
                "forecast_period_days": forecast_days,
                
                # Current status
                "current_status": {
                    "total_budget": float(project['project_budget_usd']),
                    "current_spend": float(current_metrics['current_spend']),
                    "remaining_budget": float(current_metrics['remaining_budget']),
                    "budget_utilization_percentage": float(current_metrics['budget_utilization']),
                    "days_elapsed": current_metrics['days_elapsed'],
                    "days_remaining": current_metrics['days_remaining'],
                    "project_completion_percentage": float(current_metrics['completion_percentage'])
                },
                
                # Spending trends
                "spending_trends": {
                    "avg_daily_burn_rate": float(current_metrics['avg_daily_burn']),
                    "recent_7day_burn_rate": float(current_metrics['recent_burn']),
                    "burn_rate_trend": current_metrics['burn_trend'],
                    "spending_acceleration": float(current_metrics['spending_acceleration']),
                    "total_days_with_spending": len(spending_history)
                },
                
                # Forecast predictions
                "forecast": {
                    "forecasted_additional_cost": float(forecast_data['total_forecast']),
                    "projected_final_cost": float(forecast_data['projected_final']),
                    "projected_budget_utilization": float(forecast_data['projected_utilization']),
                    "daily_forecast_breakdown": forecast_data['daily_forecasts'][:7],  # First week
                    "weekly_forecast_summary": forecast_data['weekly_summary']
                },
                
                # Overrun analysis
                "overrun_analysis": {
                    "overrun_probability": float(overrun_analysis['probability']),
                    "expected_overrun_amount": float(overrun_analysis['expected_amount']),
                    "overrun_percentage": float(overrun_analysis['overrun_percentage']),
                    "risk_level": overrun_analysis['risk_level'],
                    "confidence_interval": {
                        "lower_bound": float(overrun_analysis['lower_bound']),
                        "upper_bound": float(overrun_analysis['upper_bound'])
                    }
                },
                
                # Model performance
                "model_metrics": {
                    "forecast_accuracy_score": float(model_metrics['accuracy']),
                    "model_r2_score": float(model_metrics['r2']),
                    "mean_absolute_error": float(model_metrics['mae']),
                    "model_confidence": float(model_metrics['confidence'])
                },
                
                # Risk factors
                "risk_factors": risk_factors,
                
                # Recommendations
                "recommendations": recommendations,
                
                # Alert flags
                "alerts": self._generate_alerts(overrun_analysis, current_metrics)
            }
            
            # Save forecast to database
            self._save_forecast_to_db(db, project_id, response)
            
            return response
            
        except Exception as e:
            logger.error(f"Error forecasting cost for project {project_id}: {e}")
            raise
    
    def _get_project_details(self, db: Client, project_id: int) -> Optional[Dict]:
        """Get project details from database"""
        try:
            response = db.table("projects").select(
                "id, project_id, name, project_budget_usd, start_date, end_date, "
                "team_size, complexity_score, current_spend, created_at"
            ).eq("id", project_id).single().execute()
            return response.data
        except Exception as e:
            logger.error(f"Error fetching project details: {e}")
            return None
    
    def _get_spending_history(self, db: Client, project_id: int) -> pd.DataFrame:
        """Get historical spending data from daily logs"""
        try:
            # Get daily logs with employee hourly rates
            logs_response = db.table("daily_logs").select(
                "date, hours_logged, employee_id"
            ).eq("project_id", project_id).order("date").execute()
            
            if not logs_response.data:
                return pd.DataFrame()
            
            # Get all unique employee IDs
            employee_ids = list(set(log['employee_id'] for log in logs_response.data))
            
            # Fetch employee hourly rates in batch
            employees_response = db.table("employees").select(
                "id, hourly_rate"
            ).in_("id", employee_ids).execute()
            
            # Create employee rate mapping
            employee_rates = {
                emp['id']: emp.get('hourly_rate', 75.0) 
                for emp in employees_response.data
            }
            
            # Calculate daily costs
            data = []
            for log in logs_response.data:
                hourly_rate = employee_rates.get(log['employee_id'], 75.0)
                daily_cost = log['hours_logged'] * hourly_rate
                data.append({
                    'date': pd.to_datetime(log['date']),
                    'daily_cost': daily_cost,
                    'hours_logged': log['hours_logged']
                })
            
            df = pd.DataFrame(data)
            
            # Aggregate by date (in case multiple entries per day)
            df = df.groupby('date').agg({
                'daily_cost': 'sum',
                'hours_logged': 'sum'
            }).reset_index()
            
            # Calculate cumulative costs
            df = df.sort_values('date')
            df['cumulative_cost'] = df['daily_cost'].cumsum()
            
            return df
            
        except Exception as e:
            logger.error(f"Error fetching spending history: {e}")
            return pd.DataFrame()
    
    def _calculate_current_metrics(self, history: pd.DataFrame, project: Dict) -> Dict[str, Any]:
        """Calculate current project metrics"""
        total_budget = project['project_budget_usd'] or 1000000
        current_spend = history['cumulative_cost'].iloc[-1] if len(history) > 0 else 0
        
        # Date calculations
        start_date = pd.to_datetime(project.get('start_date') or project.get('created_at') or datetime.now())
        end_date = pd.to_datetime(project.get('end_date') or (start_date + timedelta(days=180)))
        
        days_elapsed = (datetime.now() - start_date).days
        days_remaining = max(0, (end_date - datetime.now()).days)
        total_project_days = (end_date - start_date).days
        
        # Burn rate calculations
        avg_daily_burn = current_spend / max(1, days_elapsed)
        
        # Recent burn rate (last 7 days)
        if len(history) >= 7:
            recent_spend = history['daily_cost'].tail(7).sum()
            recent_burn = recent_spend / 7
        else:
            recent_burn = avg_daily_burn
        
        # Burn rate trend
        if len(history) >= 14:
            early_burn = history['daily_cost'].head(7).mean()
            late_burn = history['daily_cost'].tail(7).mean()
            burn_trend = "increasing" if late_burn > early_burn * 1.1 else \
                        "decreasing" if late_burn < early_burn * 0.9 else "stable"
            spending_acceleration = ((late_burn - early_burn) / early_burn) * 100 if early_burn > 0 else 0
        else:
            burn_trend = "insufficient_data"
            spending_acceleration = 0
        
        return {
            'current_spend': current_spend,
            'remaining_budget': total_budget - current_spend,
            'budget_utilization': (current_spend / total_budget) * 100,
            'days_elapsed': days_elapsed,
            'days_remaining': days_remaining,
            'completion_percentage': (days_elapsed / max(1, total_project_days)) * 100,
            'avg_daily_burn': avg_daily_burn,
            'recent_burn': recent_burn,
            'burn_trend': burn_trend,
            'spending_acceleration': spending_acceleration
        }
    
    def _prepare_features_and_targets(self, history: pd.DataFrame, project: Dict) -> tuple:
        """Prepare features for forecasting model"""
        start_date = pd.to_datetime(project.get('start_date') or project.get('created_at'))
        
        history = history.copy()
        history['days_since_start'] = (history['date'] - start_date).dt.days
        history['day_of_week'] = history['date'].dt.dayofweek
        history['is_weekend'] = history['day_of_week'].isin([5, 6]).astype(int)
        
        # Rolling averages for trend capture
        history['rolling_avg_7d'] = history['daily_cost'].rolling(window=7, min_periods=1).mean()
        history['rolling_avg_14d'] = history['daily_cost'].rolling(window=14, min_periods=1).mean()
        
        # Features
        feature_cols = [
            'days_since_start', 
            'day_of_week', 
            'is_weekend',
            'rolling_avg_7d',
            'rolling_avg_14d'
        ]
        
        X = history[feature_cols].values
        y = history['daily_cost'].values
        
        return X, y
    
    def _train_forecasting_model(self, X: np.ndarray, y: np.ndarray) -> Dict[str, float]:
        """Train the forecasting model and return metrics"""
        # Transform features with polynomial
        X_poly = self.poly_features.fit_transform(X)
        
        # Train model
        self.model.fit(X_poly, y)
        
        # Calculate metrics
        y_pred = self.model.predict(X_poly)
        mae = mean_absolute_error(y, y_pred)
        r2 = r2_score(y, y_pred)
        
        # Calculate accuracy score (0-100)
        mape = np.mean(np.abs((y - y_pred) / np.maximum(y, 1))) * 100
        accuracy = max(0, 100 - mape)
        
        # Confidence based on R² and sample size
        confidence = min(95, (r2 * 100) * (min(len(y) / 30, 1)))
        
        return {
            'accuracy': accuracy,
            'r2': r2,
            'mae': mae,
            'confidence': confidence
        }
    
    def _generate_forecast(self, X: np.ndarray, forecast_days: int, project: Dict) -> Dict[str, Any]:
        """Generate future cost forecasts"""
        if len(X) == 0:
            return {
                'total_forecast': 0,
                'projected_final': 0,
                'projected_utilization': 0,
                'daily_forecasts': [],
                'weekly_summary': []
            }
        
        # Generate future days features
        last_day = X[-1, 0]
        future_days = np.arange(last_day + 1, last_day + forecast_days + 1)
        
        daily_forecasts = []
        total_forecast = 0
        
        for day in future_days:
            day_of_week = int((day - 1) % 7)
            is_weekend = 1 if day_of_week in [5, 6] else 0
            
            # Use recent averages for rolling features
            recent_avg_7d = X[-7:, 3].mean() if len(X) >= 7 else X[:, 3].mean()
            recent_avg_14d = X[-14:, 4].mean() if len(X) >= 14 else X[:, 4].mean()
            
            future_features = np.array([[
                day,
                day_of_week,
                is_weekend,
                recent_avg_7d,
                recent_avg_14d
            ]])
            
            future_X_poly = self.poly_features.transform(future_features)
            predicted_cost = max(0, self.model.predict(future_X_poly)[0])
            
            # Reduce prediction for weekends
            if is_weekend:
                predicted_cost *= 0.3
            
            daily_forecasts.append({
                'day': int(day),
                'date': (datetime.now() + timedelta(days=int(day - last_day))).strftime('%Y-%m-%d'),
                'predicted_cost': float(predicted_cost)
            })
            
            total_forecast += predicted_cost
        
        # Calculate weekly summary
        weekly_summary = []
        for i in range(0, len(daily_forecasts), 7):
            week_data = daily_forecasts[i:i+7]
            weekly_summary.append({
                'week': (i // 7) + 1,
                'total_cost': sum(d['predicted_cost'] for d in week_data),
                'avg_daily_cost': np.mean([d['predicted_cost'] for d in week_data])
            })
        
        total_budget = project['project_budget_usd'] or 1000000
        current_spend = X[:, 0].sum() if len(X) > 0 else 0  # Simplified
        projected_final = current_spend + total_forecast
        
        return {
            'total_forecast': total_forecast,
            'projected_final': projected_final,
            'projected_utilization': (projected_final / total_budget) * 100,
            'daily_forecasts': daily_forecasts,
            'weekly_summary': weekly_summary
        }
    
    def _analyze_overrun_risk(
        self, 
        history: pd.DataFrame, 
        forecast_data: Dict, 
        project: Dict,
        current_metrics: Dict
    ) -> Dict[str, Any]:
        """Analyze probability and severity of cost overrun"""
        total_budget = project['project_budget_usd'] or 1000000
        projected_final = forecast_data['projected_final']
        
        overrun_amount = max(0, projected_final - total_budget)
        overrun_percentage = (overrun_amount / total_budget) * 100 if overrun_amount > 0 else 0
        
        # Calculate probability based on multiple factors
        factors = []
        
        # Factor 1: Current trajectory
        if projected_final > total_budget:
            trajectory_prob = min(0.9, overrun_amount / total_budget)
            factors.append(trajectory_prob)
        else:
            factors.append(0.1)
        
        # Factor 2: Burn rate trend
        if current_metrics['burn_trend'] == 'increasing':
            factors.append(0.7)
        elif current_metrics['burn_trend'] == 'stable':
            factors.append(0.4)
        else:
            factors.append(0.2)
        
        # Factor 3: Budget utilization vs timeline
        budget_util = current_metrics['budget_utilization']
        time_util = current_metrics['completion_percentage']
        
        if budget_util > time_util + 15:
            factors.append(0.8)
        elif budget_util > time_util + 5:
            factors.append(0.6)
        else:
            factors.append(0.3)
        
        # Factor 4: Spending acceleration
        if abs(current_metrics['spending_acceleration']) > 20:
            factors.append(0.7)
        elif abs(current_metrics['spending_acceleration']) > 10:
            factors.append(0.5)
        else:
            factors.append(0.3)
        
        # Combined probability (weighted average)
        probability = np.average(factors, weights=[0.4, 0.2, 0.25, 0.15])
        
        # Calculate confidence intervals
        std_dev = history['daily_cost'].std() if len(history) > 1 else 0
        margin = std_dev * 1.96 * np.sqrt(forecast_data.get('total_forecast', 0) / max(1, len(history)))
        
        # Determine risk level
        if probability > 0.7:
            risk_level = "critical"
        elif probability > 0.5:
            risk_level = "high"
        elif probability > 0.3:
            risk_level = "medium"
        else:
            risk_level = "low"
        
        return {
            'probability': probability,
            'expected_amount': overrun_amount,
            'overrun_percentage': overrun_percentage,
            'risk_level': risk_level,
            'lower_bound': projected_final - margin,
            'upper_bound': projected_final + margin
        }
    
    def _identify_risk_factors(
        self, 
        history: pd.DataFrame, 
        current_metrics: Dict,
        project: Dict
    ) -> List[Dict[str, Any]]:
        """Identify specific risk factors contributing to cost overrun"""
        risk_factors = []
        
        # High burn rate
        if current_metrics['recent_burn'] > current_metrics['avg_daily_burn'] * 1.2:
            risk_factors.append({
                'factor': 'accelerating_burn_rate',
                'severity': 'high',
                'description': f"Recent burn rate ({current_metrics['recent_burn']:.0f}/day) is 20% higher than average",
                'impact': 'high'
            })
        
        # Budget utilization ahead of schedule
        budget_util = current_metrics['budget_utilization']
        time_util = current_metrics['completion_percentage']
        
        if budget_util > time_util + 15:
            risk_factors.append({
                'factor': 'budget_ahead_of_schedule',
                'severity': 'critical',
                'description': f"Budget {budget_util:.1f}% utilized but project only {time_util:.1f}% complete",
                'impact': 'critical'
            })
        
        # Increasing trend
        if current_metrics['burn_trend'] == 'increasing':
            risk_factors.append({
                'factor': 'increasing_spending_trend',
                'severity': 'high',
                'description': f"Spending acceleration of {current_metrics['spending_acceleration']:.1f}%",
                'impact': 'high'
            })
        
        # Low remaining budget
        if current_metrics['remaining_budget'] < 0:
            risk_factors.append({
                'factor': 'budget_exhausted',
                'severity': 'critical',
                'description': "Project budget already exhausted",
                'impact': 'critical'
            })
        elif current_metrics['budget_utilization'] > 80:
            days_remaining = current_metrics['days_remaining']
            remaining_budget = current_metrics['remaining_budget']
            required_daily_budget = remaining_budget / max(1, days_remaining)
            
            if required_daily_budget < current_metrics['recent_burn']:
                risk_factors.append({
                    'factor': 'insufficient_remaining_budget',
                    'severity': 'high',
                    'description': f"Remaining budget insufficient for current burn rate",
                    'impact': 'high'
                })
        
        # High complexity
        complexity = project.get('complexity_score', 0)
        if complexity > 7:
            risk_factors.append({
                'factor': 'high_project_complexity',
                'severity': 'medium',
                'description': f"High complexity score ({complexity}) increases cost risk",
                'impact': 'medium'
            })
        
        return risk_factors
    
    def _generate_recommendations(
        self, 
        overrun_analysis: Dict, 
        current_metrics: Dict,
        project: Dict
    ) -> List[Dict[str, str]]:
        """Generate actionable recommendations"""
        recommendations = []
        
        probability = overrun_analysis['probability']
        risk_level = overrun_analysis['risk_level']
        
        if risk_level == 'critical':
            recommendations.append({
                'priority': 'immediate',
                'category': 'budget_control',
                'action': 'Immediate budget review and project scope reassessment required',
                'rationale': f"{probability*100:.0f}% probability of significant cost overrun"
            })
            
            recommendations.append({
                'priority': 'immediate',
                'category': 'stakeholder_communication',
                'action': 'Notify stakeholders and prepare contingency budget request',
                'rationale': f"Expected overrun: ${overrun_analysis['expected_amount']:,.2f}"
            })
        
        elif risk_level == 'high':
            recommendations.append({
                'priority': 'high',
                'category': 'cost_control',
                'action': 'Implement strict cost control measures and daily spending monitoring',
                'rationale': f"High overrun risk ({probability*100:.0f}%)"
            })
        
        # Burn rate specific recommendations
        if current_metrics['burn_trend'] == 'increasing':
            recommendations.append({
                'priority': 'high',
                'category': 'resource_optimization',
                'action': 'Review resource allocation and identify cost optimization opportunities',
                'rationale': f"Spending accelerating by {current_metrics['spending_acceleration']:.1f}%"
            })
        
        # Budget utilization recommendations
        budget_util = current_metrics['budget_utilization']
        time_util = current_metrics['completion_percentage']
        
        if budget_util > time_util + 10:
            recommendations.append({
                'priority': 'high',
                'category': 'schedule_alignment',
                'action': 'Accelerate project timeline or reduce scope to align with budget consumption',
                'rationale': f"Budget {budget_util:.1f}% used but project {time_util:.1f}% complete"
            })
        
        # General recommendations
        if risk_level in ['high', 'critical']:
            recommendations.append({
                'priority': 'medium',
                'category': 'process_improvement',
                'action': 'Conduct cost-benefit analysis for remaining deliverables',
                'rationale': 'Prioritize high-value features to maximize ROI'
            })
            
            recommendations.append({
                'priority': 'medium',
                'category': 'vendor_management',
                'action': 'Renegotiate vendor contracts if applicable',
                'rationale': 'Reduce external costs where possible'
            })
        
        return recommendations
    
    def _generate_alerts(self, overrun_analysis: Dict, current_metrics: Dict) -> List[Dict[str, str]]:
        """Generate alert flags for UI"""
        alerts = []
        
        if overrun_analysis['risk_level'] == 'critical':
            alerts.append({
                'level': 'critical',
                'message': f"CRITICAL: {overrun_analysis['probability']*100:.0f}% probability of cost overrun",
                'icon': '🚨'
            })
        
        if current_metrics['remaining_budget'] < 0:
            alerts.append({
                'level': 'critical',
                'message': 'Budget exhausted - project over budget',
                'icon': '💸'
            })
        
        if current_metrics['burn_trend'] == 'increasing':
            alerts.append({
                'level': 'warning',
                'message': f"Spending accelerating by {current_metrics['spending_acceleration']:.1f}%",
                'icon': '📈'
            })
        
        budget_util = current_metrics['budget_utilization']
        time_util = current_metrics['completion_percentage']
        
        if budget_util > time_util + 15:
            alerts.append({
                'level': 'warning',
                'message': f"Budget {budget_util:.1f}% used, project {time_util:.1f}% complete",
                'icon': '⚠️'
            })
        
        if current_metrics['recent_burn'] > current_metrics['avg_daily_burn'] * 1.5:
            alerts.append({
                'level': 'info',
                'message': 'Recent spending significantly above average',
                'icon': '📊'
            })
        
        return alerts
    
    def _generate_insufficient_data_response(self, project: Dict, forecast_days: int) -> Dict[str, Any]:
        """Generate response when insufficient data is available"""
        total_budget = project['project_budget_usd'] or 1000000
        
        return {
            "project_id": project['id'],
            "project_name": project.get('name', f"Project {project['id']}"),
            "forecast_generated_at": datetime.now().isoformat(),
            "forecast_period_days": forecast_days,
            "error": "insufficient_data",
            "message": "Less than 7 days of spending data available. Forecast not reliable.",
            "current_status": {
                "total_budget": float(total_budget),
                "current_spend": 0.0,
                "remaining_budget": float(total_budget),
                "budget_utilization_percentage": 0.0
            },
            "recommendations": [
                {
                    'priority': 'high',
                    'category': 'data_collection',
                    'action': 'Ensure daily time logging for accurate cost tracking',
                    'rationale': 'Minimum 7 days of data required for forecasting'
                }
            ]
        }
    
    def _save_forecast_to_db(self, db: Client, project_id: int, forecast_data: Dict):
        """Save forecast results to database"""
        try:
            forecast_record = {
                'project_id': project_id,
                'forecast_date': datetime.now().date().isoformat(),
                'current_spend': forecast_data['current_status']['current_spend'],
                'total_budget': forecast_data['current_status']['total_budget'],
                'forecasted_additional_cost': forecast_data['forecast']['forecasted_additional_cost'],
                'projected_final_cost': forecast_data['forecast']['projected_final_cost'],
                'overrun_probability': forecast_data['overrun_analysis']['overrun_probability'],
                'overrun_amount': forecast_data['overrun_analysis']['expected_overrun_amount'],
                'days_remaining': forecast_data['current_status']['days_remaining'],
                'avg_daily_burn_rate': forecast_data['spending_trends']['avg_daily_burn_rate'],
                'forecast_accuracy_score': forecast_data['model_metrics']['forecast_accuracy_score'],
                'model_confidence': forecast_data['model_metrics']['model_confidence'],
                'risk_factors': forecast_data['risk_factors'],
                'recommendations': forecast_data['recommendations']
            }
            
            # Upsert (insert or update if exists)
            db.table('cost_forecasts').upsert(forecast_record).execute()
            logger.info(f"Forecast saved for project {project_id}")
            
        except Exception as e:
            logger.error(f"Error saving forecast to database: {e}")
    
    def get_all_projects_forecast_summary(self, db: Client) -> Dict[str, Any]:
        """Get cost forecast summary for all projects"""
        try:
            # Get all active projects
            projects_response = db.table("projects").select(
                "id, project_id, name, project_budget_usd"
            ).eq("status", "active").execute()
            
            projects = projects_response.data
            
            summary_data = {
                'total_projects': len(projects),
                'projects_at_risk': 0,
                'total_budget': 0,
                'total_projected_overrun': 0,
                'project_summaries': []
            }
            
            for project in projects:
                try:
                    forecast = self.forecast_cost_overrun(db, project['id'], 30)
                    
                    summary_data['total_budget'] += forecast['current_status']['total_budget']
                    
                    if forecast['overrun_analysis']['overrun_probability'] > 0.5:
                        summary_data['projects_at_risk'] += 1
                        summary_data['total_projected_overrun'] += forecast['overrun_analysis']['expected_overrun_amount']
                    
                    summary_data['project_summaries'].append({
                        'project_id': project['id'],
                        'project_name': forecast['project_name'],
                        'overrun_probability': forecast['overrun_analysis']['overrun_probability'],
                        'risk_level': forecast['overrun_analysis']['risk_level'],
                        'budget_utilization': forecast['current_status']['budget_utilization_percentage']
                    })
                    
                except Exception as e:
                    logger.warning(f"Could not forecast for project {project['id']}: {e}")
                    continue
            
            # Sort by risk
            summary_data['project_summaries'].sort(
                key=lambda x: x['overrun_probability'], 
                reverse=True
            )
            
            return summary_data
            
        except Exception as e:
            logger.error(f"Error generating portfolio forecast summary: {e}")
            raise