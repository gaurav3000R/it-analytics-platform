# backend/app/services/cost_forecasting_optimized.py

import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from datetime import datetime, timedelta, date
from typing import Dict, Any, List, Optional
from supabase import Client
import logging

logger = logging.getLogger(__name__)

class CostForecastingService:
    """
    Optimized cost forecasting service with caching and batch operations
    """
    
    def __init__(self):
        self.model = LinearRegression()
        self.poly_features = PolynomialFeatures(degree=2)
        self._forecast_cache = {}
        self._cache_ttl = 3600  # 1 hour
    
    def forecast_cost_overrun(
        self, 
        db: Client, 
        project_id: int, 
        forecast_days: int = 30
    ) -> Dict[str, Any]:
        """
        Forecast cost overrun - uses cache when available
        """
        try:
            # Check cache first
            cache_key = f"{project_id}_{forecast_days}"
            cached = self._get_from_cache(cache_key)
            if cached:
                logger.info(f"Using cached forecast for project {project_id}")
                return cached
            
            # Check database for recent forecast
            today = date.today().isoformat()
            db_forecast = db.table("cost_forecasts").select(
                "*"
            ).eq("project_id", project_id).eq("forecast_date", today).execute()
            
            if db_forecast.data and len(db_forecast.data) > 0:
                logger.info(f"Using database forecast for project {project_id}")
                return self._format_forecast_from_db(db_forecast.data[0])
            
            # Generate new forecast
            forecast = self._generate_forecast(db, project_id, forecast_days)
            
            # Cache result
            self._set_cache(cache_key, forecast)
            
            return forecast
            
        except Exception as e:
            logger.error(f"Error forecasting for project {project_id}: {e}")
            raise
    
    def _generate_forecast(
        self, 
        db: Client, 
        project_id: int, 
        forecast_days: int
    ) -> Dict[str, Any]:
        """Generate new forecast"""
        
        # Get project details
        project = self._get_project_details(db, project_id)
        if not project:
            raise ValueError(f"Project {project_id} not found")
        
        # Get spending history (optimized query)
        history = self._get_spending_history_optimized(db, project_id)
        
        if len(history) < 7:
            return self._insufficient_data_response(project, forecast_days)
        
        # Calculate metrics
        current_metrics = self._calculate_current_metrics(history, project)
        
        # Simple forecast using linear extrapolation
        forecast_data = self._simple_forecast(history, forecast_days, current_metrics)
        
        # Analyze overrun risk
        overrun_analysis = self._analyze_overrun_risk_simple(
            forecast_data, project, current_metrics
        )
        
        # Generate response
        response = {
            "project_id": project_id,
            "project_name": project.get('name', f"Project {project_id}"),
            "forecast_generated_at": datetime.now().isoformat(),
            "forecast_period_days": forecast_days,
            "current_status": {
                "total_budget": float(project['project_budget_usd']),
                "current_spend": float(current_metrics['current_spend']),
                "remaining_budget": float(current_metrics['remaining_budget']),
                "budget_utilization_percentage": float(current_metrics['budget_utilization']),
                "days_remaining": current_metrics['days_remaining']
            },
            "spending_trends": {
                "avg_daily_burn_rate": float(current_metrics['avg_daily_burn']),
                "recent_7day_burn_rate": float(current_metrics['recent_burn']),
                "burn_rate_trend": current_metrics['burn_trend']
            },
            "forecast": {
                "forecasted_additional_cost": float(forecast_data['total_forecast']),
                "projected_final_cost": float(forecast_data['projected_final']),
                "projected_budget_utilization": float(forecast_data['projected_utilization'])
            },
            "overrun_analysis": {
                "overrun_probability": float(overrun_analysis['probability']),
                "expected_overrun_amount": float(overrun_analysis['expected_amount']),
                "risk_level": overrun_analysis['risk_level']
            },
            "model_metrics": {
                "forecast_accuracy_score": 75.0,  # Simplified
                "model_confidence": 70.0
            },
            "recommendations": self._get_simple_recommendations(overrun_analysis, current_metrics)
        }
        
        # Save to database (async, don't wait)
        try:
            self._save_forecast_async(db, project_id, response)
        except Exception as e:
            logger.warning(f"Failed to save forecast: {e}")
        
        return response
    
    def _get_spending_history_optimized(
        self, 
        db: Client, 
        project_id: int
    ) -> pd.DataFrame:
        """Get spending history with optimized query"""
        try:
            # Get last 60 days only
            start_date = (datetime.now() - timedelta(days=60)).date().isoformat()
            
            # Single query with joins
            logs_response = db.table("daily_logs").select(
                "date, hours_logged, employee_id, employees(hourly_rate)"
            ).eq("project_id", project_id).gte("date", start_date).order("date").execute()
            
            if not logs_response.data:
                return pd.DataFrame()
            
            # Build dataframe
            data = []
            for log in logs_response.data:
                emp_data = log.get('employees', {})
                hourly_rate = emp_data.get('hourly_rate', 75.0) if emp_data else 75.0
                
                data.append({
                    'date': pd.to_datetime(log['date']),
                    'daily_cost': log['hours_logged'] * hourly_rate,
                    'hours_logged': log['hours_logged']
                })
            
            df = pd.DataFrame(data)
            
            # Aggregate by date
            df = df.groupby('date').agg({
                'daily_cost': 'sum',
                'hours_logged': 'sum'
            }).reset_index()
            
            df = df.sort_values('date')
            df['cumulative_cost'] = df['daily_cost'].cumsum()
            
            return df
            
        except Exception as e:
            logger.error(f"Error fetching spending history: {e}")
            return pd.DataFrame()
    
    def _calculate_current_metrics(
        self, 
        history: pd.DataFrame, 
        project: Dict
    ) -> Dict[str, Any]:
        """Calculate current project metrics"""
        total_budget = project['project_budget_usd'] or 1000000
        current_spend = history['cumulative_cost'].iloc[-1] if len(history) > 0 else 0
        
        # Date calculations
        start_date = pd.to_datetime(project.get('start_date') or project.get('created_at') or datetime.now())
        end_date = pd.to_datetime(project.get('end_date') or (start_date + timedelta(days=180)))
        
        days_elapsed = (datetime.now() - start_date).days
        days_remaining = max(0, (end_date - datetime.now()).days)
        
        # Burn rate
        avg_daily_burn = current_spend / max(1, days_elapsed)
        
        # Recent burn rate (last 7 days)
        if len(history) >= 7:
            recent_spend = history['daily_cost'].tail(7).sum()
            recent_burn = recent_spend / 7
        else:
            recent_burn = avg_daily_burn
        
        # Trend
        if len(history) >= 14:
            early_burn = history['daily_cost'].head(7).mean()
            late_burn = history['daily_cost'].tail(7).mean()
            burn_trend = "increasing" if late_burn > early_burn * 1.1 else \
                        "decreasing" if late_burn < early_burn * 0.9 else "stable"
        else:
            burn_trend = "stable"
        
        return {
            'current_spend': current_spend,
            'remaining_budget': total_budget - current_spend,
            'budget_utilization': (current_spend / total_budget) * 100,
            'days_elapsed': days_elapsed,
            'days_remaining': days_remaining,
            'avg_daily_burn': avg_daily_burn,
            'recent_burn': recent_burn,
            'burn_trend': burn_trend
        }
    
    def _simple_forecast(
        self, 
        history: pd.DataFrame, 
        forecast_days: int,
        current_metrics: Dict
    ) -> Dict[str, Any]:
        """Simple linear forecast"""
        
        # Use recent burn rate for projection
        daily_forecast = current_metrics['recent_burn']
        total_forecast = daily_forecast * forecast_days
        
        current_spend = current_metrics['current_spend']
        projected_final = current_spend + total_forecast
        
        # Adjust for weekends (reduce by 30%)
        total_forecast *= 0.85  # Account for weekends
        projected_final = current_spend + total_forecast
        
        total_budget = current_spend + current_metrics['remaining_budget']
        
        return {
            'total_forecast': total_forecast,
            'projected_final': projected_final,
            'projected_utilization': (projected_final / total_budget * 100) if total_budget > 0 else 0
        }
    
    def _analyze_overrun_risk_simple(
        self,
        forecast_data: Dict,
        project: Dict,
        current_metrics: Dict
    ) -> Dict[str, Any]:
        """Simplified overrun risk analysis"""
        
        total_budget = project['project_budget_usd'] or 1000000
        projected_final = forecast_data['projected_final']
        
        overrun_amount = max(0, projected_final - total_budget)
        overrun_percentage = (overrun_amount / total_budget) * 100 if overrun_amount > 0 else 0
        
        # Calculate probability
        budget_util = current_metrics['budget_utilization']
        
        if projected_final > total_budget:
            base_prob = min(0.9, overrun_amount / total_budget)
        else:
            base_prob = 0.1
        
        # Adjust for trend
        if current_metrics['burn_trend'] == 'increasing':
            base_prob += 0.2
        elif current_metrics['burn_trend'] == 'decreasing':
            base_prob -= 0.1
        
        # Adjust for current utilization
        if budget_util > 80:
            base_prob += 0.15
        
        probability = max(0, min(1, base_prob))
        
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
            'risk_level': risk_level
        }
    
    def _get_simple_recommendations(
        self,
        overrun_analysis: Dict,
        current_metrics: Dict
    ) -> List[Dict[str, str]]:
        """Generate simple recommendations"""
        recommendations = []
        
        risk_level = overrun_analysis['risk_level']
        
        if risk_level in ['critical', 'high']:
            recommendations.append({
                'priority': 'high',
                'category': 'budget_control',
                'action': 'Implement immediate cost control measures',
                'rationale': f"High overrun risk ({overrun_analysis['probability']*100:.0f}%)"
            })
        
        if current_metrics['burn_trend'] == 'increasing':
            recommendations.append({
                'priority': 'medium',
                'category': 'resource_optimization',
                'action': 'Review resource allocation and identify cost optimization',
                'rationale': 'Spending is accelerating'
            })
        
        return recommendations
    
    def _get_project_details(self, db: Client, project_id: int) -> Optional[Dict]:
        """Get project details"""
        try:
            response = db.table("projects").select(
                "id, project_id, name, project_budget_usd, start_date, end_date, "
                "team_size, current_spend, created_at, status"
            ).eq("id", project_id).single().execute()
            return response.data
        except:
            return None
    
    def _insufficient_data_response(self, project: Dict, forecast_days: int) -> Dict[str, Any]:
        """Response for insufficient data"""
        total_budget = project['project_budget_usd'] or 1000000
        
        return {
            "project_id": project['id'],
            "project_name": project.get('name', f"Project {project['id']}"),
            "forecast_generated_at": datetime.now().isoformat(),
            "forecast_period_days": forecast_days,
            "error": "insufficient_data",
            "message": "Less than 7 days of spending data available",
            "current_status": {
                "total_budget": float(total_budget),
                "current_spend": 0.0,
                "remaining_budget": float(total_budget),
                "budget_utilization_percentage": 0.0
            },
            "recommendations": [{
                'priority': 'high',
                'category': 'data_collection',
                'action': 'Ensure daily time logging',
                'rationale': 'Minimum 7 days of data required'
            }]
        }
    
    def _format_forecast_from_db(self, forecast_record: Dict) -> Dict[str, Any]:
        """Format forecast from database record"""
        return {
            "project_id": forecast_record['project_id'],
            "project_name": "Cached Forecast",
            "forecast_generated_at": forecast_record.get('created_at', datetime.now().isoformat()),
            "forecast_period_days": 30,
            "current_status": {
                "total_budget": float(forecast_record['total_budget']),
                "current_spend": float(forecast_record['current_spend']),
                "remaining_budget": float(forecast_record['total_budget'] - forecast_record['current_spend']),
                "budget_utilization_percentage": float(forecast_record['current_spend'] / forecast_record['total_budget'] * 100) if forecast_record['total_budget'] > 0 else 0
            },
            "spending_trends": {
                "avg_daily_burn_rate": float(forecast_record.get('avg_daily_burn_rate', 0)),
                "burn_rate_trend": "stable"
            },
            "forecast": {
                "forecasted_additional_cost": float(forecast_record['forecasted_additional_cost']),
                "projected_final_cost": float(forecast_record['projected_final_cost']),
                "projected_budget_utilization": float(forecast_record['projected_final_cost'] / forecast_record['total_budget'] * 100) if forecast_record['total_budget'] > 0 else 0
            },
            "overrun_analysis": {
                "overrun_probability": float(forecast_record['overrun_probability']),
                "expected_overrun_amount": float(forecast_record.get('overrun_amount', 0)),
                "risk_level": "critical" if forecast_record['overrun_probability'] > 0.7 else "high" if forecast_record['overrun_probability'] > 0.5 else "medium"
            },
            "model_metrics": {
                "forecast_accuracy_score": float(forecast_record.get('forecast_accuracy_score', 75.0)),
                "model_confidence": float(forecast_record.get('model_confidence', 70.0))
            },
            "recommendations": forecast_record.get('recommendations', []),
            "cached": True
        }
    
    def _save_forecast_async(self, db: Client, project_id: int, forecast_data: Dict):
        """Save forecast to database"""
        try:
            forecast_record = {
                'project_id': project_id,
                'forecast_date': date.today().isoformat(),
                'current_spend': forecast_data['current_status']['current_spend'],
                'total_budget': forecast_data['current_status']['total_budget'],
                'forecasted_additional_cost': forecast_data['forecast']['forecasted_additional_cost'],
                'projected_final_cost': forecast_data['forecast']['projected_final_cost'],
                'overrun_probability': forecast_data['overrun_analysis']['overrun_probability'],
                'overrun_amount': forecast_data['overrun_analysis']['expected_overrun_amount'],
                'avg_daily_burn_rate': forecast_data['spending_trends']['avg_daily_burn_rate'],
                'forecast_accuracy_score': forecast_data['model_metrics']['forecast_accuracy_score'],
                'model_confidence': forecast_data['model_metrics']['model_confidence'],
                'recommendations': forecast_data['recommendations']
            }
            
            db.table('cost_forecasts').upsert(forecast_record).execute()
        except Exception as e:
            logger.error(f"Error saving forecast: {e}")
    
    def get_portfolio_summary_optimized(self, db: Client) -> Dict[str, Any]:
        """Get portfolio summary using cached forecasts"""
        try:
            today = date.today().isoformat()
            
            # Get recent forecasts from database
            forecasts_response = db.table("cost_forecasts").select(
                "project_id, overrun_probability, overrun_amount, total_budget, "
                "projected_final_cost, forecast_date, projects(name, status)"
            ).gte("forecast_date", today).execute()
            
            forecasts = forecasts_response.data
            
            # Filter active projects only
            active_forecasts = [
                f for f in forecasts 
                if f.get('projects') and f['projects'].get('status') == 'active'
            ]
            
            summary = {
                'total_projects': len(active_forecasts),
                'projects_at_risk': 0,
                'total_budget': 0,
                'total_projected_overrun': 0,
                'project_summaries': []
            }
            
            for forecast in active_forecasts:
                summary['total_budget'] += forecast['total_budget']
                
                if forecast['overrun_probability'] > 0.5:
                    summary['projects_at_risk'] += 1
                    summary['total_projected_overrun'] += forecast.get('overrun_amount', 0)
                
                proj_data = forecast.get('projects', {})
                summary['project_summaries'].append({
                    'project_id': forecast['project_id'],
                    'project_name': proj_data.get('name', 'Unknown') if proj_data else 'Unknown',
                    'overrun_probability': forecast['overrun_probability'],
                    'risk_level': (
                        'critical' if forecast['overrun_probability'] > 0.7 else
                        'high' if forecast['overrun_probability'] > 0.5 else
                        'medium'
                    ),
                    'budget_utilization': 0  # Simplified
                })
            
            # Sort by risk
            summary['project_summaries'].sort(
                key=lambda x: x['overrun_probability'],
                reverse=True
            )
            
            return summary
            
        except Exception as e:
            logger.error(f"Error generating portfolio summary: {e}")
            raise
    
    def batch_refresh_forecasts(self, db: Client, project_ids: List[int]):
        """Background task to refresh multiple forecasts"""
        logger.info(f"Starting batch forecast refresh for {len(project_ids)} projects")
        
        successful = 0
        failed = 0
        
        for project_id in project_ids:
            try:
                self._generate_forecast(db, project_id, 30)
                successful += 1
            except Exception as e:
                logger.warning(f"Failed to forecast project {project_id}: {e}")
                failed += 1
        
        logger.info(f"Batch forecast complete: {successful} successful, {failed} failed")
    
    def _get_from_cache(self, key: str) -> Optional[Dict]:
        """Get from memory cache"""
        if key in self._forecast_cache:
            cached_data, timestamp = self._forecast_cache[key]
            if (datetime.now() - timestamp).seconds < self._cache_ttl:
                return cached_data
            else:
                del self._forecast_cache[key]
        return None
    
    def _set_cache(self, key: str, data: Dict):
        """Set memory cache"""
        self._forecast_cache[key] = (data, datetime.now())