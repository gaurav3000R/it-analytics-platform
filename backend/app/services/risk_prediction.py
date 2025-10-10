import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from sklearn.feature_selection import SelectKBest, f_regression
from typing import Dict, List, Any, Optional, Tuple
import joblib
import logging
from datetime import datetime, timedelta
from supabase import Client
import warnings
import os
warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)

class RiskPredictionService:
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.feature_selector = None
        self.feature_columns = []
        
    def prepare_enhanced_features(self, db: Client, project_id: Optional[int] = None) -> pd.DataFrame:
        """
        Prepare comprehensive feature matrix with BATCH QUERIES (not N+1).
        This is the key optimization - fetch all data upfront.
        """
        logger.info("Fetching project data...")
        
        # FETCH ALL DATA IN BULK - Single queries instead of 4000+
        projects_query = db.table("projects").select("*")
        if project_id:
            projects_query = projects_query.eq("id", project_id)
        projects_df = pd.DataFrame(projects_query.execute().data)
        
        if projects_df.empty:
            raise ValueError("No projects available for training")
        
        logger.info(f"Loaded {len(projects_df)} projects")
        
        # Fetch ALL daily logs in one query (with date filter)
        cutoff_date = (datetime.now() - timedelta(days=60)).isoformat()
        all_logs_query = db.table("daily_logs").select("*").gte("date", cutoff_date)
        if project_id:
            all_logs_query = all_logs_query.eq("project_id", project_id)
        all_logs_df = pd.DataFrame(all_logs_query.execute().data)
        
        logger.info(f"Loaded {len(all_logs_df)} daily logs")
        
        # Fetch ALL sprints in one query
        all_sprints_query = db.table("sprints").select("*")
        if project_id:
            all_sprints_query = all_sprints_query.eq("project_id", project_id)
        all_sprints_df = pd.DataFrame(all_sprints_query.execute().data)
        
        logger.info(f"Loaded {len(all_sprints_df)} sprints")
        
        # Now process everything in pandas (MUCH faster than individual queries)
        features_df = self._engineer_features_vectorized(projects_df, all_logs_df, all_sprints_df)
        
        return self._clean_and_validate_features(features_df)
    
    def _engineer_features_vectorized(self, projects_df: pd.DataFrame, 
                                     logs_df: pd.DataFrame, 
                                     sprints_df: pd.DataFrame) -> pd.DataFrame:
        """
        Engineer ALL features using vectorized pandas operations.
        No loops over projects - process everything at once.
        """
        # Start with base project features
        features = projects_df[['id']].copy()
        features.rename(columns={'id': 'project_id'}, inplace=True)
        
        # Basic project metrics (already in projects_df)
        features['team_size'] = projects_df['team_size'].fillna(5)
        features['project_budget'] = projects_df['project_budget_usd'].fillna(100000)
        features['complexity_score'] = projects_df['complexity_score'].fillna(3.0)
        features['timeline_months'] = projects_df['estimated_timeline_months'].fillna(6.0)
        features['stakeholder_count'] = projects_df['stakeholder_count'].fillna(5)
        
        # Aggregate log metrics using groupby (vectorized)
        if not logs_df.empty:
            log_metrics = self._calculate_log_metrics_vectorized(logs_df)
            features = features.merge(log_metrics, left_on='project_id', right_index=True, how='left')
        else:
            # Add default columns if no logs
            features['total_hours_60d'] = 0
            features['avg_daily_hours'] = 0
            features['completion_rate'] = 50.0
            features['team_productivity'] = 0
            features['issues_reported'] = 0
            features['log_consistency'] = 0
            features['active_team_members'] = 1
        
        # Aggregate sprint metrics using groupby (vectorized)
        if not sprints_df.empty:
            sprint_metrics = self._calculate_sprint_metrics_vectorized(sprints_df)
            features = features.merge(sprint_metrics, left_on='project_id', right_index=True, how='left')
        else:
            features['avg_velocity'] = 30.0
            features['velocity_stability'] = 0
            features['sprint_completion_ratio'] = 0.8
            features['burndown_efficiency'] = 0.5
        
        # Encode risk factors (vectorized)
        risk_features = self._encode_risk_factors_vectorized(projects_df)
        features = pd.concat([features, risk_features], axis=1)
        
        # Create derived features (vectorized)
        derived = self._create_derived_features_vectorized(features)
        features = pd.concat([features, derived], axis=1)
        
        # Fill any remaining NaN values
        features = features.fillna(0)
        
        return features
    
    def _calculate_log_metrics_vectorized(self, logs_df: pd.DataFrame) -> pd.DataFrame:
        """Calculate log metrics for ALL projects at once using pandas groupby"""
        
        # Group by project_id and aggregate
        metrics = pd.DataFrame()
        
        grouped = logs_df.groupby('project_id')
        
        # Total hours
        metrics['total_hours_60d'] = grouped['hours_logged'].sum()
        
        # Average completion rate
        metrics['completion_rate'] = grouped['story_points_completed'].mean().fillna(50.0)
        
        # Issues reported
        metrics['issues_reported'] = grouped['bugs_found'].sum()
        
        # Unique dates per project (log consistency)
        logs_df['date_only'] = pd.to_datetime(logs_df['date']).dt.date
        unique_dates = logs_df.groupby('project_id')['date_only'].nunique()
        metrics['log_consistency'] = unique_dates / 60.0
        
        # Active team members
        metrics['active_team_members'] = logs_df.groupby('project_id')['employee_id'].nunique()
        
        # Team productivity
        metrics['team_productivity'] = metrics['total_hours_60d'] / metrics['active_team_members'].clip(lower=1)
        
        # Average daily hours
        metrics['avg_daily_hours'] = metrics['total_hours_60d'] / unique_dates.clip(lower=1)
        
        return metrics.fillna(0)
    
    def _calculate_sprint_metrics_vectorized(self, sprints_df: pd.DataFrame) -> pd.DataFrame:
        """Calculate sprint metrics for ALL projects at once"""
        
        # Sort by date and take last 5 sprints per project
        sprints_df = sprints_df.sort_values(['project_id', 'start_date'], ascending=[True, False])
        recent_sprints = sprints_df.groupby('project_id').head(5)
        
        metrics = pd.DataFrame()
        grouped = recent_sprints.groupby('project_id')
        
        # Average velocity
        metrics['avg_velocity'] = grouped['velocity'].mean().fillna(30.0)
        
        # Velocity stability (1 - normalized std)
        velocity_std = grouped['velocity'].std().fillna(0)
        velocity_mean = metrics['avg_velocity']
        metrics['velocity_stability'] = 1.0 - (velocity_std / velocity_mean.clip(lower=1)).clip(upper=1.0)
        
        # Sprint completion ratio
        completion_data = recent_sprints[['project_id', 'completed_story_points', 'planned_story_points']].copy()
        completion_data['ratio'] = (
            completion_data['completed_story_points'] / 
            completion_data['planned_story_points'].clip(lower=1)
        ).clip(upper=2.0)  # Cap at 200%
        metrics['sprint_completion_ratio'] = completion_data.groupby('project_id')['ratio'].mean().fillna(0.8)
        
        # Burndown efficiency
        metrics['burndown_efficiency'] = (metrics['avg_velocity'] / 40.0).clip(upper=1.0)
        
        return metrics.fillna({'avg_velocity': 30.0, 'velocity_stability': 0, 
                              'sprint_completion_ratio': 0.8, 'burndown_efficiency': 0.5})
    
    def _encode_risk_factors_vectorized(self, projects_df: pd.DataFrame) -> pd.DataFrame:
        """Encode categorical risk factors using vectorized mapping"""
        
        features = pd.DataFrame(index=projects_df.index)
        
        # Experience level encoding
        experience_map = {'Junior': 0.2, 'Mid': 0.5, 'Senior': 0.8, 'Expert': 1.0}
        features['team_experience_score'] = projects_df['team_experience_level'].map(experience_map).fillna(0.5)
        
        # Methodology encoding
        methodology_map = {'Waterfall': 0.3, 'Hybrid': 0.6, 'Agile': 0.8, 'Scrum': 0.9, 'Kanban': 0.85}
        features['methodology_score'] = projects_df['methodology_used'].map(methodology_map).fillna(0.5)
        
        # Historical risk
        risk_level_map = {'Low': 0.2, 'Medium': 0.5, 'High': 0.8}
        features['historical_risk_score'] = projects_df['risk_level'].map(risk_level_map).fillna(0.5)
        
        # External dependencies (normalized)
        features['external_dependencies_norm'] = (
            projects_df['external_dependencies_count'].fillna(0) / 10.0
        ).clip(upper=1.0)
        
        # Requirement stability
        stability_map = {'Unstable': 0.2, 'Moderate': 0.5, 'Stable': 0.8, 'Very Stable': 1.0}
        features['requirement_stability_score'] = projects_df['requirement_stability'].map(stability_map).fillna(0.5)
        
        # Technical debt
        debt_map = {'High': 0.2, 'Medium': 0.5, 'Low': 0.8, 'None': 1.0}
        features['technical_debt_score'] = projects_df['technical_debt_level'].map(debt_map).fillna(0.5)
        
        return features
    
    def _create_derived_features_vectorized(self, features: pd.DataFrame) -> pd.DataFrame:
        """Create derived features using vectorized operations"""
        
        derived = pd.DataFrame(index=features.index)
        
        # Budget per member
        derived['budget_per_member'] = (
            features['project_budget'] / features['team_size'].clip(lower=1)
        )
        
        # Timeline intensity
        derived['timeline_intensity'] = (
            features['team_size'] / features['timeline_months'].clip(lower=1)
        )
        
        # Complexity budget ratio
        derived['complexity_budget_ratio'] = (
            features['complexity_score'] / (features['project_budget'] / 10000).clip(lower=1)
        )
        
        # Productivity efficiency
        derived['productivity_efficiency'] = (
            features['team_productivity'] * features['completion_rate'] / 100.0
        )
        
        # Risk exposure
        derived['risk_exposure'] = (
            features['historical_risk_score'] + 
            (1 - features['velocity_stability']) + 
            (1 - features['log_consistency'])
        ) / 3.0
        
        return derived
    
    def _clean_and_validate_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and validate features"""
        
        # Remove constant features
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        constant_cols = [col for col in numeric_cols if df[col].nunique() <= 1]
        if constant_cols:
            logger.info(f"Removing {len(constant_cols)} constant features")
            df = df.drop(columns=constant_cols)
        
        # Handle infinite values
        df = df.replace([np.inf, -np.inf], np.nan)
        
        # Fill missing values with median
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            if df[col].isna().any():
                df[col] = df[col].fillna(df[col].median())
        
        logger.info(f"Final feature matrix: {df.shape[0]} samples, {df.shape[1]} features")
        return df
    
    def create_robust_targets(self, db: Client, df: pd.DataFrame) -> pd.DataFrame:
        """Create target variables using BATCH query"""
        
        # Fetch ALL risk levels at once
        project_ids = df['project_id'].tolist()
        risk_data = db.table("projects").select("id, risk_level").in_("id", project_ids).execute().data
        risk_df = pd.DataFrame(risk_data)
        
        # Map risk levels to scores
        risk_mapping = {
            'Very Low': 15.0,
            'Low': 30.0,
            'Medium': 50.0,
            'High': 70.0,
            'Very High': 85.0
        }
        
        risk_df['base_score'] = risk_df['risk_level'].map(risk_mapping)
        
        # Merge with features
        df = df.merge(risk_df[['id', 'base_score']], left_on='project_id', right_on='id', how='left')
        
        # Use calculated scores for missing risk levels
        df['base_score'] = df['base_score'].fillna(
            df.apply(lambda row: self._calculate_comprehensive_risk_score(row), axis=1)
        )
        
        # Add small random noise
        df['risk_score'] = (
            df['base_score'] + np.random.normal(0, 2, size=len(df))
        ).clip(5, 95)
        
        df = df.drop(columns=['id', 'base_score'], errors='ignore')
        
        return df
    
    def _calculate_comprehensive_risk_score(self, row: pd.Series) -> float:
        """Calculate synthetic risk score"""
        base_score = 50.0
        
        # Budget factors
        budget_utilization = row.get('budget_per_member', 0) / 20000
        if budget_utilization > 1.0:
            base_score += 15
        elif budget_utilization < 0.3:
            base_score -= 10
        
        # Timeline factors
        timeline_intensity = row.get('timeline_intensity', 1.0)
        if timeline_intensity > 2.0:
            base_score += 12
        
        # Team factors
        team_experience = row.get('team_experience_score', 0.5)
        base_score += (1 - team_experience) * 20
        
        # Productivity factors
        completion_rate = row.get('completion_rate', 50.0)
        if completion_rate < 40.0:
            base_score += 15
        elif completion_rate > 80.0:
            base_score -= 10
        
        # Stability factors
        velocity_stability = row.get('velocity_stability', 0.5)
        base_score += (1 - velocity_stability) * 15
        
        return max(10, min(90, base_score))
    
    def train_model(self, db: Client, use_hyperparameter_tuning: bool = False) -> Dict[str, Any]:
        """Train model with optimized data loading"""
        logger.info("Starting model training with optimized data loading...")
        
        try:
            # Single pass through data - no loops!
            df = self.prepare_enhanced_features(db)
            
            if len(df) < 10:
                raise ValueError(f"Insufficient data: only {len(df)} samples")
            
            logger.info(f"Training with {len(df)} samples")
            
            # Create targets
            df = self.create_robust_targets(db, df)
            
            # Prepare features
            feature_cols = [col for col in df.columns if col not in ['project_id', 'risk_score']]
            X = df[feature_cols]
            y = df['risk_score']
            
            # Feature selection
            if len(feature_cols) > 15:
                selector = SelectKBest(score_func=f_regression, k=15)
                X_selected = selector.fit_transform(X, y)
                self.feature_columns = X.columns[selector.get_support()].tolist()
                X = pd.DataFrame(X_selected, columns=self.feature_columns)
                self.feature_selector = selector
                logger.info(f"Selected top 15 features: {self.feature_columns}")
            else:
                self.feature_columns = feature_cols
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            
            # Scale features
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            # Train multiple models and select best
            models = {
                'random_forest': RandomForestRegressor(n_estimators=100, max_depth=10, random_state=42, n_jobs=-1),
                'gradient_boosting': GradientBoostingRegressor(n_estimators=100, max_depth=5, random_state=42),
                'linear': LinearRegression(n_jobs=-1)
            }
            
            best_model = None
            best_score = -float('inf')
            best_metrics = {}
            
            for name, model in models.items():
                logger.info(f"Training {name}...")
                model.fit(X_train_scaled, y_train)
                
                test_pred = model.predict(X_test_scaled)
                test_r2 = r2_score(y_test, test_pred)
                
                if test_r2 > best_score:
                    best_score = test_r2
                    best_model = model
                    best_metrics = {
                        'model_type': name,
                        'test_r2': test_r2,
                        'test_rmse': np.sqrt(mean_squared_error(y_test, test_pred)),
                        'test_mae': mean_absolute_error(y_test, test_pred),
                        'train_samples': len(X_train),
                        'test_samples': len(X_test),
                        'feature_count': len(self.feature_columns)
                    }
                    logger.info(f"✓ {name}: R²={test_r2:.3f}, RMSE={best_metrics['test_rmse']:.2f}")
            
            self.model = best_model
            
            # Cross-validation
            cv_scores = cross_val_score(best_model, X_train_scaled, y_train, 
                                       cv=min(5, len(X_train)//2), scoring='r2', n_jobs=-1)
            best_metrics['cv_mean_r2'] = np.mean(cv_scores)
            best_metrics['cv_std_r2'] = np.std(cv_scores)
            
            logger.info(f"✅ Training complete. Best model: {best_metrics['model_type']} with R²={best_metrics['test_r2']:.3f}")
            return best_metrics
            
        except Exception as e:
            logger.error(f"Training failed: {e}")
            raise
    
    def predict_risk(self, db: Client, project_id: int) -> Dict[str, Any]:
        """Predict risk for a single project"""
        if not self.model:
            raise ValueError("Model not trained. Call train_model() first.")
        
        df = self.prepare_enhanced_features(db, project_id)
        
        if df.empty:
            raise ValueError(f"No data for project {project_id}")
        
        X = df[self.feature_columns]
        X_scaled = self.scaler.transform(X)
        
        risk_score = float(self.model.predict(X_scaled)[0])
        risk_score = max(0, min(100, risk_score))
        
        # Calculate component risks
        project_data = df.iloc[0]
        component_risks = {
            'schedule_risk': float(max(0, min(100, (1 - project_data.get('sprint_completion_ratio', 0.8)) * 100))),
            'budget_risk': float(max(0, min(100, project_data.get('budget_per_member', 0) / 500))),
            'quality_risk': float(max(0, min(100, project_data.get('issues_reported', 0) * 2))),
            'resource_risk': float(max(0, min(100, (1 - project_data.get('team_experience_score', 0.5)) * 100))),
            'technical_risk': float(max(0, min(100, (1 - project_data.get('technical_debt_score', 0.5)) * 100)))
        }
        
        return {
            'project_id': project_id,
            'overall_risk_score': risk_score,
            'risk_level': self._get_risk_level(risk_score),
            'component_risks': component_risks,
            'prediction_date': datetime.now().isoformat()
        }
    
    def _get_risk_level(self, score: float) -> str:
        """Convert score to risk level"""
        if score >= 80:
            return "Very High"
        elif score >= 65:
            return "High"
        elif score >= 45:
            return "Medium"
        elif score >= 25:
            return "Low"
        return "Very Low"
    
    def save_model(self, path: str):
        """Save model"""
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
        """Load model"""
        model_data = joblib.load(path)
        self.model = model_data['model']
        self.scaler = model_data['scaler']
        self.feature_selector = model_data.get('feature_selector')
        self.feature_columns = model_data['feature_columns']
        logger.info(f"Model loaded from {path}")