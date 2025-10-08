import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
from typing import Dict, List, Any, Optional
import joblib
import logging
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.models import Project, DailyLog, Sprint
from app.models.employee import Employee
from app.models.risk import RiskScore

logger = logging.getLogger(__name__)

class RiskPredictionService:
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.feature_columns = []
        
    def prepare_features(self, db: Session, project_id: Optional[int] = None) -> pd.DataFrame:
        """Prepare feature matrix for risk prediction - Handles CSV-only (no logs)"""
        
        # Query project data
        query = db.query(Project)
        if project_id:
            query = query.filter(Project.id == project_id)
        projects = query.all()
        
        if not projects:
            raise ValueError("No projects available for training")
        
        features_list = []
        
        for project in projects:
            # Get recent daily logs (last 30 days) - FALLBACK if none
            recent_logs = db.query(DailyLog).filter(
                DailyLog.project_id == project.id,
                DailyLog.date >= datetime.now() - timedelta(days=30)
            ).all()
            
            if recent_logs:
                # Dynamic features from logs
                total_hours = sum([log.hours_logged for log in recent_logs])
                num_log_days = len(set([log.date.date() for log in recent_logs]))
                avg_daily_hours = total_hours / num_log_days if num_log_days > 0 else 0
                completion_rate = np.mean([log.completion_percentage for log in recent_logs])
                unique_employees = len(set([log.employee_id for log in recent_logs]))
                hours_per_employee = total_hours / unique_employees if unique_employees > 0 else 0
                issues_reported = sum([log.issues_reported for log in recent_logs])
            else:
                # FALLBACK: Static features from CSV/project metadata
                total_hours = 0
                avg_daily_hours = 0
                completion_rate = 50.0  # Neutral
                unique_employees = project.team_size or 5
                hours_per_employee = 0
                issues_reported = project.historical_risk_incidents or 0  # Use CSV incidents as proxy
            
            # Time-based (estimate from metadata)
            days_since_start = (datetime.now() - (project.created_at or datetime.now())).days
            days_to_end = max(0, (project.estimated_timeline_months or 6) * 30 - days_since_start)  # From CSV timeline
            
            # Sprint velocity (fallback)
            recent_sprints = db.query(Sprint).filter(Sprint.project_id == project.id).order_by(Sprint.start_date.desc()).limit(3).all()
            avg_velocity = np.mean([s.velocity for s in recent_sprints if s.velocity]) if recent_sprints else 30.0
            velocity_trend = self._calculate_velocity_trend(recent_sprints)
            
            features = {
                'project_id': project.id,
                'total_hours_30d': total_hours,
                'avg_daily_hours': avg_daily_hours,
                'completion_rate': completion_rate,
                'budget_utilization': (project.current_spend or 0) / max(1, project.project_budget_usd or 1),  # From CSV budget
                'team_size': unique_employees,
                'hours_per_employee': hours_per_employee,
                'days_since_start': days_since_start,
                'days_to_end': days_to_end,
                'project_complexity': project.complexity_score or 3.0,  # From CSV
                'avg_velocity': avg_velocity,
                'velocity_trend': velocity_trend,
                'issues_reported': issues_reported
            }
            
            features_list.append(features)
        
        df = pd.DataFrame(features_list)
        return df
    
    def _calculate_velocity_trend(self, sprints: List[Sprint]) -> float:
        """Calculate velocity trend (positive = improving, negative = declining)"""
        if len(sprints) < 2:
            return 0.0
        
        velocities = [s.velocity for s in reversed(sprints) if s.velocity is not None]
        if len(velocities) < 2:
            return 0.0
        
        # Simple linear trend
        x = np.arange(len(velocities))
        trend = np.polyfit(x, velocities, 1)[0]
        return trend
    
    def train_model(self, db: Session) -> Dict[str, float]:
        """Train the risk prediction model"""
        logger.info("Starting risk prediction model training...")
        
        # Prepare features
        df = self.prepare_features(db)
        
        if df.empty:
            raise ValueError("No data available for training")
        
        # For demonstration, create synthetic risk scores based on features
        # In real scenario, you would use historical risk scores
        df = self._create_synthetic_risk_scores(db, df)  # FIXED: Pass db 
       
        # Prepare feature matrix
        feature_cols = [col for col in df.columns if col not in ['project_id', 'risk_score']]
        self.feature_columns = feature_cols
        
        X = df[feature_cols].fillna(0)
        y = df['risk_score']
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train model
        self.model = GradientBoostingRegressor(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=6,
            random_state=42
        )
        
        self.model.fit(X_train_scaled, y_train)
        
        # Evaluate
        train_pred = self.model.predict(X_train_scaled)
        test_pred = self.model.predict(X_test_scaled)
        
        metrics = {
            'train_r2': r2_score(y_train, train_pred),
            'test_r2': r2_score(y_test, test_pred),
            'train_rmse': np.sqrt(mean_squared_error(y_train, train_pred)),
            'test_rmse': np.sqrt(mean_squared_error(y_test, test_pred))
        }
        
        logger.info(f"Model training completed. Test R2: {metrics['test_r2']:.3f}")
        return metrics
    
    def _create_synthetic_risk_scores(self, db: Session, df: pd.DataFrame) -> pd.DataFrame:  # FIXED: Add db: Session
        """Use real Risk_Level from CSV/projects as targets (better than synthetic)"""
        
        risk_scores = []
        for _, row in df.iterrows():
            # Map CSV Risk_Level to numeric (use project.risk_level if available)
            project = db.query(Project).filter(Project.id == row['project_id']).first()  # Now db is available
            risk_level = project.risk_level if project else 'Medium'  # Fallback
            
            # Convert to numeric score
            if risk_level == 'Low':
                risk = 25.0
            elif risk_level == 'Medium':
                risk = 50.0
            elif risk_level == 'High':
                risk = 75.0
            else:
                risk = 50.0  # Unknown/Neutral
            
            # Add slight noise + CSV-based adjustments (e.g., high complexity → higher risk)
            if project:
                if project.complexity_score > 7:
                    risk += 15
                if project.project_budget_usd > 1000000:
                    risk += 10
                if project.stakeholder_count > 15:
                    risk += 10
            
            risk = max(0, min(100, risk + np.random.normal(0, 5)))  # Clamp + noise
            risk_scores.append(risk)
        
        df['risk_score'] = risk_scores
        return df
    
    def predict_risk(self, db: Session, project_id: int) -> Dict[str, Any]:
        """Predict risk for a specific project"""
        if not self.model:
            raise ValueError("Model not trained yet")
        
        # Prepare features for the project
        df = self.prepare_features(db, project_id)
        
        if df.empty:
            raise ValueError(f"No data available for project {project_id}")
        
        X = df[self.feature_columns].fillna(0)
        X_scaled = self.scaler.transform(X)
        
        # Predict
        risk_score = self.model.predict(X_scaled)[0]
        feature_importance = dict(zip(self.feature_columns, self.model.feature_importances_))
        
        # Calculate component risks
        component_risks = self._calculate_component_risks(df.iloc[0])
        
        return {
            'project_id': project_id,
            'overall_risk_score': float(risk_score),
            'component_risks': component_risks,
            'feature_importance': feature_importance,
            'prediction_date': datetime.now().isoformat()
        }
    
    def _calculate_component_risks(self, project_data: pd.Series) -> Dict[str, float]:
        """Calculate individual component risks"""
        
        # Delay risk
        delay_risk = 0
        if project_data['completion_rate'] < 0.7 and project_data['days_to_end'] < 60:
            delay_risk = min(80, (0.7 - project_data['completion_rate']) * 100)
        
        # Budget risk
        budget_risk = min(90, project_data['budget_utilization'] * 100)
        
        # Quality risk (based on issues reported)
        quality_risk = min(70, project_data['issues_reported'] * 5)
        
        # Resource risk (based on team efficiency)
        expected_hours = project_data['team_size'] * 8 * 30  # 30 days
        if expected_hours > 0:
            resource_risk = max(0, min(60, (expected_hours - project_data['total_hours_30d']) / expected_hours * 100))
        else:
            resource_risk = 0
        
        return {
            'delay_risk': delay_risk,
            'budget_risk': budget_risk,
            'quality_risk': quality_risk,
            'resource_risk': resource_risk
        }
    
    def save_model(self, path: str):
        """Save trained model to disk"""
        if not self.model:
            raise ValueError("No model to save")
        
        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'feature_columns': self.feature_columns
        }
        
        joblib.dump(model_data, path)
        logger.info(f"Model saved to {path}")
    
    def load_model(self, path: str):
        """Load trained model from disk"""
        try:
            model_data = joblib.load(path)
            self.model = model_data['model']
            self.scaler = model_data['scaler']
            self.feature_columns = model_data['feature_columns']
            logger.info(f"Model loaded from {path}")
        except FileNotFoundError:
            logger.warning(f"Model file not found at {path}")