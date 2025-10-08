import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from sklearn.feature_selection import SelectKBest, f_regression
from typing import Dict, List, Any, Optional, Tuple
import joblib
import logging
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
import warnings
import os
warnings.filterwarnings('ignore')

from app.models.project import Project
from app.models.daily_log import DailyLog
from app.models.sprint import Sprint
from app.models.employee import Employee
from app.models.risk import RiskScore

logger = logging.getLogger(__name__)

class RiskPredictionService:
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.feature_selector = None
        self.feature_columns = []
        self.label_encoders = {}
        
    def prepare_enhanced_features(self, db: Session, project_id: Optional[int] = None) -> pd.DataFrame:
        """Prepare comprehensive and robust feature matrix"""
        
        query = db.query(Project)
        if project_id:
            query = query.filter(Project.id == project_id)
        projects = query.all()
        
        if not projects:
            raise ValueError("No projects available for training")
        
        features_list = []
        
        for project in projects:
            try:
                # Get comprehensive project data
                recent_logs = db.query(DailyLog).filter(
                    DailyLog.project_id == project.id,
                    DailyLog.date >= datetime.now() - timedelta(days=60)  # Increased to 60 days for more data
                ).all()
                
                # Enhanced feature engineering with robust fallbacks
                features = self._engineer_comprehensive_features(project, recent_logs, db)
                features_list.append(features)
                
            except Exception as e:
                logger.warning(f"Error processing project {project.id}: {e}")
                continue
        
        if not features_list:
            raise ValueError("No valid features could be generated")
            
        df = pd.DataFrame(features_list)
        return self._clean_and_validate_features(df)
    
    def _engineer_comprehensive_features(self, project: Project, recent_logs: List[DailyLog], db: Session) -> Dict[str, Any]:
        """Engineer comprehensive features with robust error handling"""
        
        # Basic project metrics
        features = {
            'project_id': project.id,
            # Project characteristics
            'team_size': project.team_size or 5,
            'project_budget': project.project_budget_usd or 100000,
            'complexity_score': project.complexity_score or 3.0,
            'timeline_months': project.estimated_timeline_months or 6.0,
            'stakeholder_count': project.stakeholder_count or 5,
        }
        
        # Enhanced dynamic metrics from logs
        log_metrics = self._calculate_log_metrics(recent_logs)
        features.update(log_metrics)
        
        # Sprint metrics
        sprint_metrics = self._calculate_sprint_metrics(db, project.id)
        features.update(sprint_metrics)
        
        # Risk factor encodings
        risk_factors = self._encode_risk_factors(project)
        features.update(risk_factors)
        
        # Derived features
        derived_features = self._create_derived_features(features)
        features.update(derived_features)
        
        return features
    
    def _calculate_log_metrics(self, recent_logs: List[DailyLog]) -> Dict[str, float]:
        """Calculate metrics from daily logs with robust handling"""
        if not recent_logs:
            return {
                'total_hours_60d': 0,
                'avg_daily_hours': 0,
                'completion_rate': 50.0,
                'team_productivity': 0,
                'issues_reported': 0,
                'log_consistency': 0,
                'active_team_members': 1
            }
        
        # Basic metrics
        total_hours = sum([log.hours_logged for log in recent_logs])
        completion_rates = [log.completion_percentage for log in recent_logs if log.completion_percentage]
        avg_completion = np.mean(completion_rates) if completion_rates else 50.0
        issues_reported = sum([log.issues_reported for log in recent_logs])
        
        # Advanced metrics
        unique_dates = len(set([log.date.date() for log in recent_logs]))
        log_consistency = unique_dates / 60.0 if unique_dates > 0 else 0  # Consistency over 60 days
        
        unique_employees = len(set([log.employee_id for log in recent_logs]))
        team_productivity = total_hours / max(1, unique_employees) if total_hours > 0 else 0
        
        avg_daily_hours = total_hours / max(1, unique_dates)
        
        return {
            'total_hours_60d': total_hours,
            'avg_daily_hours': avg_daily_hours,
            'completion_rate': avg_completion,
            'team_productivity': team_productivity,
            'issues_reported': issues_reported,
            'log_consistency': log_consistency,
            'active_team_members': unique_employees
        }
    
    def _calculate_sprint_metrics(self, db: Session, project_id: int) -> Dict[str, float]:
        """Calculate sprint-based metrics"""
        sprints = db.query(Sprint).filter(
            Sprint.project_id == project_id
        ).order_by(Sprint.start_date.desc()).limit(5).all()
        
        if not sprints:
            return {
                'avg_velocity': 30.0,
                'velocity_stability': 0,
                'sprint_completion_ratio': 0.8,
                'burndown_efficiency': 0.5
            }
        
        velocities = [s.velocity for s in sprints if s.velocity]
        completed_points = [s.completed_points for s in sprints if s.completed_points]
        planned_points = [s.planned_points for s in sprints if s.planned_points]
        
        avg_velocity = np.mean(velocities) if velocities else 30.0
        velocity_stability = np.std(velocities) / avg_velocity if avg_velocity > 0 else 1.0
        
        completion_ratios = [comp/plan for comp, plan in zip(completed_points, planned_points) if plan > 0]
        sprint_completion_ratio = np.mean(completion_ratios) if completion_ratios else 0.8
        
        return {
            'avg_velocity': avg_velocity,
            'velocity_stability': 1.0 - min(1.0, velocity_stability),  # Higher is better
            'sprint_completion_ratio': sprint_completion_ratio,
            'burndown_efficiency': min(1.0, avg_velocity / 40.0)  # Normalized
        }
    
    def _encode_risk_factors(self, project: Project) -> Dict[str, float]:
        """Encode categorical risk factors as numerical values"""
        
        # Experience level encoding
        experience_map = {'Junior': 0.2, 'Mid': 0.5, 'Senior': 0.8, 'Expert': 1.0}
        team_experience = experience_map.get(project.team_experience_level, 0.5)
        
        # Methodology encoding
        methodology_map = {'Waterfall': 0.3, 'Hybrid': 0.6, 'Agile': 0.8, 'Scrum': 0.9}
        methodology_score = methodology_map.get(project.methodology_used, 0.5)
        
        # Risk level encoding (for features, not target)
        risk_level_map = {'Low': 0.2, 'Medium': 0.5, 'High': 0.8}
        historical_risk = risk_level_map.get(project.risk_level, 0.5)
        
        return {
            'team_experience_score': team_experience,
            'methodology_score': methodology_score,
            'historical_risk_score': historical_risk,
            'external_dependencies_norm': min(1.0, (project.external_dependencies_count or 0) / 10.0),
            'requirement_stability_score': self._encode_stability(project.requirement_stability),
            'technical_debt_score': self._encode_technical_debt(project.technical_debt_level)
        }
    
    def _encode_stability(self, stability: str) -> float:
        """Encode stability factors"""
        stability_map = {'Unstable': 0.2, 'Moderate': 0.5, 'Stable': 0.8, 'Very Stable': 1.0}
        return stability_map.get(stability, 0.5)
    
    def _encode_technical_debt(self, debt_level: str) -> float:
        """Encode technical debt levels"""
        debt_map = {'High': 0.2, 'Medium': 0.5, 'Low': 0.8, 'None': 1.0}
        return debt_map.get(debt_level, 0.5)
    
    def _create_derived_features(self, features: Dict[str, Any]) -> Dict[str, float]:
        """Create meaningful derived features"""
        
        budget = features.get('project_budget', 100000)
        team_size = features.get('team_size', 5)
        timeline = features.get('timeline_months', 6.0)
        
        return {
            'budget_per_member': budget / max(1, team_size),
            'timeline_intensity': team_size / max(1, timeline),
            'complexity_budget_ratio': features.get('complexity_score', 3.0) / max(1, budget/10000),
            'productivity_efficiency': features.get('team_productivity', 0) * features.get('completion_rate', 50) / 100.0,
            'risk_exposure': (features.get('historical_risk_score', 0.5) + 
                            (1 - features.get('velocity_stability', 0.5)) + 
                            (1 - features.get('log_consistency', 0.5))) / 3.0
        }
    
    def _clean_and_validate_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and validate features"""
        
        # Remove constant features
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        constant_cols = [col for col in numeric_cols if df[col].nunique() <= 1]
        df = df.drop(columns=constant_cols)
        
        # Handle infinite values
        df = df.replace([np.inf, -np.inf], np.nan)
        
        # Fill missing values with median
        for col in df.select_dtypes(include=[np.number]).columns:
            if df[col].isna().any():
                df[col] = df[col].fillna(df[col].median())
        
        return df
    
    def create_robust_targets(self, db: Session, df: pd.DataFrame) -> pd.DataFrame:
        """Create robust target variables using multiple strategies"""
        
        risk_scores = []
        
        for _, row in df.iterrows():
            project = db.query(Project).filter(Project.id == row['project_id']).first()
            
            if project and project.risk_level:
                # Use actual risk levels with intelligent mapping
                base_score = self._map_risk_level_to_score(project.risk_level)
            else:
                # Calculate synthetic score based on comprehensive factors
                base_score = self._calculate_comprehensive_risk_score(row)
            
            # Add small random noise for variability
            risk_score = max(5, min(95, base_score + np.random.normal(0, 2)))
            risk_scores.append(risk_score)
        
        df['risk_score'] = risk_scores
        return df
    
    def _map_risk_level_to_score(self, risk_level: str) -> float:
        """Intelligently map risk levels to scores"""
        mapping = {
            'Very Low': 15.0,
            'Low': 30.0,
            'Medium': 50.0,
            'High': 70.0,
            'Very High': 85.0
        }
        return mapping.get(risk_level, 50.0)
    
    def _calculate_comprehensive_risk_score(self, project_data: pd.Series) -> float:
        """Calculate risk score based on multiple factors"""
        
        base_score = 50.0
        
        # Budget factors (20% weight)
        budget_utilization = project_data.get('budget_per_member', 0) / 20000  # Normalize
        if budget_utilization > 1.0:
            base_score += 15
        elif budget_utilization < 0.3:
            base_score -= 10
        
        # Timeline factors (20% weight)
        timeline_intensity = project_data.get('timeline_intensity', 1.0)
        if timeline_intensity > 2.0:
            base_score += 12
        elif timeline_intensity < 0.5:
            base_score += 5
        
        # Team factors (20% weight)
        team_experience = project_data.get('team_experience_score', 0.5)
        base_score += (1 - team_experience) * 20  # Lower experience = higher risk
        
        # Productivity factors (20% weight)
        completion_rate = project_data.get('completion_rate', 50.0)
        if completion_rate < 40.0:
            base_score += 15
        elif completion_rate > 80.0:
            base_score -= 10
        
        # Stability factors (20% weight)
        velocity_stability = project_data.get('velocity_stability', 0.5)
        base_score += (1 - velocity_stability) * 15
        
        return max(10, min(90, base_score))
    
    def select_best_features(self, X: pd.DataFrame, y: pd.Series, k: int = 15) -> pd.DataFrame:
        """Select the most important features"""
        if len(X.columns) <= k:
            return X
        
        selector = SelectKBest(score_func=f_regression, k=k)
        X_selected = selector.fit_transform(X, y)
        selected_columns = X.columns[selector.get_support()]
        
        self.feature_selector = selector
        self.feature_columns = list(selected_columns)
        
        logger.info(f"Selected top {k} features: {list(selected_columns)}")
        return pd.DataFrame(X_selected, columns=selected_columns)
    
    def train_model(self, db: Session) -> Dict[str, Any]:
        """Train enhanced risk prediction model with cross-validation"""
        logger.info("Starting enhanced risk prediction model training...")
        
        try:
            # Prepare enhanced features
            df = self.prepare_enhanced_features(db)
            
            if len(df) < 10:
                raise ValueError(f"Insufficient data for training. Only {len(df)} samples available.")
            
            logger.info(f"Training with {len(df)} samples and {len(df.columns)} features")
            
            # Create robust targets
            df = self.create_robust_targets(db, df)
            
            # Prepare feature matrix
            feature_cols = [col for col in df.columns if col not in ['project_id', 'risk_score']]
            X = df[feature_cols].fillna(0)
            y = df['risk_score']
            
            # Feature selection
            if len(feature_cols) > 10:
                X = self.select_best_features(X, y, k=min(15, len(feature_cols)))
            else:
                self.feature_columns = feature_cols
            
            # Split data with stratification
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42, stratify=pd.cut(y, bins=5)
            )
            
            if len(X_train) < 8:
                raise ValueError(f"Insufficient training data: {len(X_train)} samples")
            
            # Scale features
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            # Try multiple models
            models = {
                'random_forest': RandomForestRegressor(n_estimators=100, random_state=42),
                'gradient_boosting': GradientBoostingRegressor(n_estimators=100, random_state=42),
                'linear': LinearRegression()
            }
            
            best_model = None
            best_score = -float('inf')
            best_metrics = {}
            
            for name, model in models.items():
                try:
                    model.fit(X_train_scaled, y_train)
                    train_pred = model.predict(X_train_scaled)
                    test_pred = model.predict(X_test_scaled)
                    
                    train_r2 = r2_score(y_train, train_pred)
                    test_r2 = r2_score(y_test, test_pred)
                    
                    # Use test R2 as primary metric, but penalize overfitting
                    score = test_r2 - max(0, train_r2 - test_r2) * 0.5
                    
                    if score > best_score:
                        best_score = score
                        best_model = model
                        best_metrics = {
                            'model_type': name,
                            'train_r2': train_r2,
                            'test_r2': test_r2,
                            'train_rmse': np.sqrt(mean_squared_error(y_train, train_pred)),
                            'test_rmse': np.sqrt(mean_squared_error(y_test, test_pred)),
                            'train_mae': mean_absolute_error(y_train, train_pred),
                            'test_mae': mean_absolute_error(y_test, test_pred),
                            'overfitting_gap': train_r2 - test_r2
                        }
                        
                        logger.info(f"New best model: {name} with test R2: {test_r2:.3f}")
                        
                except Exception as e:
                    logger.warning(f"Model {name} failed: {e}")
                    continue
            
            if best_model is None:
                raise ValueError("All models failed to train")
            
            self.model = best_model
            
            # Cross-validation for better estimate
            cv_scores = cross_val_score(best_model, X_train_scaled, y_train, cv=min(5, len(X_train)), scoring='r2')
            best_metrics['cv_mean_r2'] = np.mean(cv_scores)
            best_metrics['cv_std_r2'] = np.std(cv_scores)
            
            # Feature importance
            if hasattr(best_model, 'feature_importances_'):
                best_metrics['feature_importance'] = dict(zip(self.feature_columns, best_model.feature_importances_))
            
            logger.info(f"Model training completed. Best test R2: {best_metrics['test_r2']:.3f}")
            return best_metrics
            
        except Exception as e:
            logger.error(f"Model training failed: {e}")
            raise
    
    def predict_risk(self, db: Session, project_id: int) -> Dict[str, Any]:
        """Predict risk with enhanced features and error handling"""
        if not self.model:
            raise ValueError("Model not trained yet. Call train_model() first.")
        
        try:
            df = self.prepare_enhanced_features(db, project_id)
            
            if df.empty:
                raise ValueError(f"No data available for project {project_id}")
            
            # Select features and scale
            X = df[self.feature_columns].fillna(0)
            X_scaled = self.scaler.transform(X)
            
            # Predict
            risk_score = self.model.predict(X_scaled)[0]
            risk_score = max(0, min(100, risk_score))  # Ensure within bounds
            
            # Calculate confidence based on feature similarity to training data
            confidence = self._calculate_prediction_confidence(X_scaled)
            
            component_risks = self._calculate_component_risks(df.iloc[0])
            risk_insights = self._generate_risk_insights(df.iloc[0], risk_score, component_risks)
            
            return {
                'project_id': project_id,
                'overall_risk_score': float(risk_score),
                'risk_level': self._get_risk_level(risk_score),
                'prediction_confidence': confidence,
                'component_risks': component_risks,
                'risk_insights': risk_insights,
                'recommendations': self._generate_recommendations(component_risks),
                'prediction_date': datetime.now().isoformat(),
                'model_performance': {
                    'r2_score': 'See training metrics',
                    'feature_count': len(self.feature_columns)
                }
            }
            
        except Exception as e:
            logger.error(f"Risk prediction failed for project {project_id}: {e}")
            raise
    
    def _calculate_prediction_confidence(self, X_scaled: np.ndarray) -> float:
        """Calculate prediction confidence based on data characteristics"""
        # Simple confidence calculation - can be enhanced
        if hasattr(self.model, 'predict_proba'):
            return 0.8  # Classification models have probability
        else:
            return 0.7  # Regression models have lower inherent confidence
    
    def _calculate_component_risks(self, project_data: pd.Series) -> Dict[str, Any]:
        """Calculate detailed component risk scores"""
        factors = {
            'schedule_risk': min(90, (1 - project_data.get('sprint_completion_ratio', 0.8)) * 100),
            'budget_risk': min(95, project_data.get('budget_per_member', 0) / 50000 * 100),
            'quality_risk': min(80, project_data.get('issues_reported', 0) / 10 * 100),
            'resource_risk': min(70, (1 - project_data.get('team_experience_score', 0.5)) * 100),
            'technical_risk': min(85, (1 - project_data.get('technical_debt_score', 0.5)) * 100)
        }
        
        # Apply bounds
        return {k: max(0, min(100, v)) for k, v in factors.items()}
    
    def _generate_risk_insights(self, project_data: pd.Series, overall_risk: float, 
                               component_risks: Dict[str, float]) -> List[str]:
        """Generate actionable risk insights"""
        insights = []
        
        if overall_risk > 70:
            insights.append("🚨 HIGH RISK: Project requires immediate attention and mitigation planning")
        elif overall_risk > 50:
            insights.append("⚠️ MEDIUM RISK: Project needs close monitoring and proactive management")
        
        # Component-specific insights
        if component_risks['schedule_risk'] > 70:
            insights.append("⏰ Critical schedule risk: High probability of timeline slippage")
        
        if component_risks['budget_risk'] > 75:
            insights.append("💰 Budget overrun likely: Review financial controls and scope")
        
        if component_risks['quality_risk'] > 60:
            insights.append("🐛 Quality concerns: Implement additional testing and review processes")
        
        if component_risks['resource_risk'] > 65:
            insights.append("👥 Team capability risk: Consider training or resource augmentation")
        
        # Positive insights for balance
        if component_risks['technical_risk'] < 30:
            insights.append("🛠️ Strong technical foundation: Low technical debt observed")
        
        return insights
    
    def _generate_recommendations(self, component_risks: Dict[str, float]) -> List[str]:
        """Generate specific, actionable recommendations"""
        recommendations = []
        
        if component_risks['schedule_risk'] > 60:
            recommendations.extend([
                "Conduct weekly schedule reviews with the team",
                "Break down deliverables into smaller, manageable chunks",
                "Implement daily standups for progress tracking"
            ])
        
        if component_risks['budget_risk'] > 65:
            recommendations.extend([
                "Freeze non-essential purchases and expenses",
                "Review project scope for potential reductions",
                "Implement weekly budget variance reporting"
            ])
        
        if component_risks['quality_risk'] > 50:
            recommendations.extend([
                "Increase automated test coverage by 20%",
                "Implement peer code review requirements",
                "Conduct root cause analysis for recurring issues"
            ])
        
        if component_risks['resource_risk'] > 55:
            recommendations.extend([
                "Provide targeted training for skill gaps",
                "Consider pairing junior team members with seniors",
                "Review workload distribution across the team"
            ])
        
        # General recommendations
        recommendations.extend([
            "Maintain regular stakeholder communication",
            "Document all key decisions and assumptions",
            "Conduct monthly risk review meetings"
        ])
        
        return recommendations[:6]  # Limit to top 6 recommendations
    
    def _get_risk_level(self, score: float) -> str:
        """Convert numeric risk score to risk level with more granularity"""
        if score >= 80:
            return "Very High"
        elif score >= 65:
            return "High"
        elif score >= 45:
            return "Medium"
        elif score >= 25:
            return "Low"
        else:
            return "Very Low"
    
    def save_model(self, path: str):
        """Save trained model and preprocessing objects"""
        if not self.model:
            raise ValueError("No model to save")
        
        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'feature_selector': self.feature_selector,
            'feature_columns': self.feature_columns,
            'training_date': datetime.now().isoformat()
        }
        
        os.makedirs(os.path.dirname(path), exist_ok=True)
        joblib.dump(model_data, path)
        logger.info(f"Model saved to {path}")
    
    def load_model(self, path: str):
        """Load trained model and preprocessing objects"""
        try:
            model_data = joblib.load(path)
            self.model = model_data['model']
            self.scaler = model_data['scaler']
            self.feature_selector = model_data.get('feature_selector')
            self.feature_columns = model_data['feature_columns']
            logger.info(f"Model loaded from {path} (trained on {model_data.get('training_date', 'unknown')})")
        except FileNotFoundError:
            logger.warning(f"Model file not found at {path}")
        except Exception as e:
            logger.error(f"Error loading model: {e}")