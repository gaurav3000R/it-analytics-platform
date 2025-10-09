"""
Machine Learning Models for Risk Prediction
"""
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier, IsolationForest
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_squared_error, r2_score, classification_report, roc_auc_score
from sklearn.preprocessing import StandardScaler, LabelEncoder
import xgboost as xgb
import lightgbm as lgb
from typing import Dict, Tuple, Any, Optional, List
import joblib
import logging
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)


class DelayRiskPredictor:
    """Predict project delivery delay risk"""
    
    def __init__(self, model_type: str = 'xgboost'):
        self.model_type = model_type
        self.model = None
        self.scaler = StandardScaler()
        self.feature_names = []
        
        if model_type == 'xgboost':
            self.model = xgb.XGBRegressor(
                n_estimators=100,
                max_depth=6,
                learning_rate=0.1,
                random_state=42
            )
        elif model_type == 'random_forest':
            self.model = RandomForestRegressor(
                n_estimators=100,
                max_depth=10,
                random_state=42
            )
        elif model_type == 'lightgbm':
            self.model = lgb.LGBMRegressor(
                n_estimators=100,
                max_depth=6,
                learning_rate=0.1,
                random_state=42
            )
        else:
            raise ValueError(f"Unsupported model type: {model_type}")
    
    def prepare_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Prepare features for delay prediction"""
        features = df.copy()
        
        # Select relevant features
        feature_cols = [
            'sprint_velocity', 'completion_rate', 'bug_reopen_rate',
            'team_size', 'avg_utilization_rate', 'blocked_tasks',
            'days_behind_schedule', 'budget_variance_percent',
            'avg_task_cycle_time', 'total_tasks', 'completed_tasks'
        ]
        
        available_features = [col for col in feature_cols if col in features.columns]
        self.feature_names = available_features
        
        return features[available_features]
    
    def train(self, X: pd.DataFrame, y: pd.Series) -> Dict[str, float]:
        """
        Train delay prediction model
        
        Args:
            X: Feature DataFrame
            y: Target variable (delay in days)
            
        Returns:
            Dictionary with training metrics
        """
        logger.info(f"Training delay risk model with {self.model_type}")
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train model
        self.model.fit(X_train_scaled, y_train)
        
        # Predictions
        y_pred_train = self.model.predict(X_train_scaled)
        y_pred_test = self.model.predict(X_test_scaled)
        
        # Metrics
        metrics = {
            'train_rmse': np.sqrt(mean_squared_error(y_train, y_pred_train)),
            'test_rmse': np.sqrt(mean_squared_error(y_test, y_pred_test)),
            'train_r2': r2_score(y_train, y_pred_train),
            'test_r2': r2_score(y_test, y_pred_test)
        }
        
        logger.info(f"Model trained. Test RMSE: {metrics['test_rmse']:.2f}, Test R2: {metrics['test_r2']:.3f}")
        return metrics
    
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """Predict delay in days"""
        if self.model is None:
            raise ValueError("Model not trained yet")
        
        X_scaled = self.scaler.transform(X)
        predictions = self.model.predict(X_scaled)
        return np.maximum(predictions, 0)  # Ensure non-negative predictions
    
    def predict_with_confidence(self, X: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """Predict with confidence intervals"""
        predictions = self.predict(X)
        
        # Estimate uncertainty (using model-specific methods if available)
        if hasattr(self.model, 'estimators_'):
            # For Random Forest, use prediction variance across trees
            predictions_all = np.array([tree.predict(self.scaler.transform(X)) 
                                       for tree in self.model.estimators_])
            confidence = predictions_all.std(axis=0)
        else:
            # Default confidence estimation
            confidence = np.abs(predictions) * 0.2  # 20% of prediction
        
        return predictions, confidence
    
    def get_feature_importance(self) -> pd.DataFrame:
        """Get feature importance scores"""
        if self.model is None:
            raise ValueError("Model not trained yet")
        
        if hasattr(self.model, 'feature_importances_'):
            importance_df = pd.DataFrame({
                'feature': self.feature_names,
                'importance': self.model.feature_importances_
            }).sort_values('importance', ascending=False)
            
            return importance_df
        else:
            return pd.DataFrame()
    
    def save(self, path: str):
        """Save model to disk"""
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        joblib.dump({
            'model': self.model,
            'scaler': self.scaler,
            'feature_names': self.feature_names,
            'model_type': self.model_type
        }, path)
        logger.info(f"Model saved to {path}")
    
    def load(self, path: str):
        """Load model from disk"""
        data = joblib.load(path)
        self.model = data['model']
        self.scaler = data['scaler']
        self.feature_names = data['feature_names']
        self.model_type = data['model_type']
        logger.info(f"Model loaded from {path}")


class CostOverrunPredictor:
    """Predict project cost overrun"""
    
    def __init__(self, model_type: str = 'xgboost'):
        self.model_type = model_type
        self.model = None
        self.scaler = StandardScaler()
        self.feature_names = []
        
        if model_type == 'xgboost':
            self.model = xgb.XGBRegressor(
                n_estimators=100,
                max_depth=6,
                learning_rate=0.1,
                random_state=42
            )
        elif model_type == 'random_forest':
            self.model = RandomForestRegressor(
                n_estimators=100,
                max_depth=10,
                random_state=42
            )
        else:
            self.model = xgb.XGBRegressor(n_estimators=100, random_state=42)
    
    def prepare_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Prepare features for cost overrun prediction"""
        features = df.copy()
        
        feature_cols = [
            'planned_budget', 'actual_cost', 'team_size',
            'sprint_velocity', 'avg_utilization_rate',
            'days_behind_schedule', 'scope_change_count',
            'total_tasks', 'completed_tasks', 'blocked_tasks'
        ]
        
        available_features = [col for col in feature_cols if col in features.columns]
        self.feature_names = available_features
        
        return features[available_features]
    
    def train(self, X: pd.DataFrame, y: pd.Series) -> Dict[str, float]:
        """Train cost overrun model"""
        logger.info(f"Training cost overrun model with {self.model_type}")
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        self.model.fit(X_train_scaled, y_train)
        
        y_pred_train = self.model.predict(X_train_scaled)
        y_pred_test = self.model.predict(X_test_scaled)
        
        metrics = {
            'train_rmse': np.sqrt(mean_squared_error(y_train, y_pred_train)),
            'test_rmse': np.sqrt(mean_squared_error(y_test, y_pred_test)),
            'train_r2': r2_score(y_train, y_pred_train),
            'test_r2': r2_score(y_test, y_pred_test)
        }
        
        logger.info(f"Cost overrun model trained. Test RMSE: {metrics['test_rmse']:.2f}")
        return metrics
    
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """Predict cost overrun percentage"""
        if self.model is None:
            raise ValueError("Model not trained yet")
        
        X_scaled = self.scaler.transform(X)
        return self.model.predict(X_scaled)
    
    def save(self, path: str):
        """Save model"""
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        joblib.dump({
            'model': self.model,
            'scaler': self.scaler,
            'feature_names': self.feature_names,
            'model_type': self.model_type
        }, path)
        logger.info(f"Cost model saved to {path}")
    
    def load(self, path: str):
        """Load model"""
        data = joblib.load(path)
        self.model = data['model']
        self.scaler = data['scaler']
        self.feature_names = data['feature_names']
        self.model_type = data['model_type']
        logger.info(f"Cost model loaded from {path}")


class ResourceBottleneckDetector:
    """Detect resource utilization bottlenecks using clustering and anomaly detection"""
    
    def __init__(self):
        self.isolation_forest = IsolationForest(
            contamination=0.1,
            random_state=42
        )
        self.scaler = StandardScaler()
        self.feature_names = []
    
    def prepare_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Prepare features for resource analysis"""
        feature_cols = [
            'utilization_rate', 'tasks_assigned', 'tasks_completed',
            'avg_task_completion_time', 'bugs_created'
        ]
        
        available_features = [col for col in feature_cols if col in df.columns]
        self.feature_names = available_features
        
        return df[available_features]
    
    def fit(self, X: pd.DataFrame):
        """Fit anomaly detection model"""
        logger.info("Training resource bottleneck detector")
        
        X_scaled = self.scaler.fit_transform(X)
        self.isolation_forest.fit(X_scaled)
        
        logger.info("Bottleneck detector trained")
    
    def predict_anomalies(self, X: pd.DataFrame) -> np.ndarray:
        """
        Predict resource anomalies
        
        Returns:
            Array of predictions (-1 for anomaly, 1 for normal)
        """
        X_scaled = self.scaler.transform(X)
        predictions = self.isolation_forest.predict(X_scaled)
        return predictions
    
    def get_anomaly_scores(self, X: pd.DataFrame) -> np.ndarray:
        """Get anomaly scores (lower = more anomalous)"""
        X_scaled = self.scaler.transform(X)
        scores = self.isolation_forest.score_samples(X_scaled)
        return scores
    
    def identify_bottlenecks(self, df: pd.DataFrame, threshold: float = -0.5) -> pd.DataFrame:
        """
        Identify resource bottlenecks
        
        Args:
            df: Resource utilization DataFrame
            threshold: Anomaly score threshold
            
        Returns:
            DataFrame with bottleneck indicators
        """
        X = self.prepare_features(df)
        
        df_result = df.copy()
        df_result['anomaly_prediction'] = self.predict_anomalies(X)
        df_result['anomaly_score'] = self.get_anomaly_scores(X)
        df_result['is_bottleneck'] = df_result['anomaly_score'] < threshold
        
        logger.info(f"Identified {df_result['is_bottleneck'].sum()} resource bottlenecks")
        return df_result
    
    def save(self, path: str):
        """Save model"""
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        joblib.dump({
            'model': self.isolation_forest,
            'scaler': self.scaler,
            'feature_names': self.feature_names
        }, path)
    
    def load(self, path: str):
        """Load model"""
        data = joblib.load(path)
        self.isolation_forest = data['model']
        self.scaler = data['scaler']
        self.feature_names = data['feature_names']


class RiskScoreCalculator:
    """Calculate comprehensive risk scores"""
    
    def __init__(self):
        self.weights = {
            'delay_risk': 0.4,
            'cost_risk': 0.3,
            'resource_risk': 0.2,
            'quality_risk': 0.1
        }
    
    def calculate_delay_risk(self, predicted_delay_days: float, confidence: float) -> float:
        """Calculate delay risk score (0-100)"""
        # Normalize delay to 0-1 scale (assuming max acceptable delay is 30 days)
        normalized_delay = min(predicted_delay_days / 30.0, 1.0)
        
        # Adjust by confidence
        risk_score = normalized_delay * confidence * 100
        return min(risk_score, 100)
    
    def calculate_cost_risk(self, predicted_overrun_percent: float) -> float:
        """Calculate cost overrun risk score (0-100)"""
        # Normalize overrun percentage (assuming 50% overrun is maximum)
        normalized_overrun = min(abs(predicted_overrun_percent) / 50.0, 1.0)
        return normalized_overrun * 100
    
    def calculate_resource_risk(self, anomaly_score: float, utilization_rate: float) -> float:
        """Calculate resource bottleneck risk score (0-100)"""
        # Anomaly score is typically between -1 and 1
        anomaly_risk = (1 - (anomaly_score + 1) / 2) * 50
        
        # Utilization risk (both over and under-utilization are risky)
        utilization_risk = 0
        if utilization_rate > 1.0:
            utilization_risk = min((utilization_rate - 1.0) * 100, 50)
        elif utilization_rate < 0.7:
            utilization_risk = (0.7 - utilization_rate) * 50
        
        return min(anomaly_risk + utilization_risk, 100)
    
    def calculate_quality_risk(self, bug_rate: float, reopen_rate: float) -> float:
        """Calculate quality risk score (0-100)"""
        # Normalize bug rate (assuming 0.2 bugs per task is high)
        bug_risk = min(bug_rate / 0.2, 1.0) * 50
        
        # Reopen rate risk
        reopen_risk = min(reopen_rate, 1.0) * 50
        
        return min(bug_risk + reopen_risk, 100)
    
    def calculate_overall_risk(self, risk_scores: Dict[str, float]) -> Tuple[float, str]:
        """
        Calculate overall risk score
        
        Args:
            risk_scores: Dictionary with individual risk scores
            
        Returns:
            Tuple of (overall_score, risk_level)
        """
        overall_score = 0
        for risk_type, weight in self.weights.items():
            score = risk_scores.get(risk_type, 0)
            overall_score += score * weight
        
        # Determine risk level
        if overall_score < 25:
            risk_level = "low"
        elif overall_score < 50:
            risk_level = "medium"
        elif overall_score < 75:
            risk_level = "high"
        else:
            risk_level = "critical"
        
        return overall_score, risk_level
    
    def generate_risk_report(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive risk report for a project"""
        risk_scores = {
            'delay_risk': self.calculate_delay_risk(
                project_data.get('predicted_delay_days', 0),
                project_data.get('delay_confidence', 0.8)
            ),
            'cost_risk': self.calculate_cost_risk(
                project_data.get('predicted_cost_overrun_percent', 0)
            ),
            'resource_risk': self.calculate_resource_risk(
                project_data.get('anomaly_score', 0),
                project_data.get('avg_utilization_rate', 0.8)
            ),
            'quality_risk': self.calculate_quality_risk(
                project_data.get('bug_rate', 0),
                project_data.get('reopen_rate', 0)
            )
        }
        
        overall_score, risk_level = self.calculate_overall_risk(risk_scores)
        
        return {
            'overall_score': overall_score,
            'risk_level': risk_level,
            'risk_scores': risk_scores,
            'timestamp': datetime.utcnow().isoformat()
        }


class MLPipeline:
    """Complete ML pipeline for risk prediction"""
    
    def __init__(self, model_path: str = "./models"):
        self.model_path = Path(model_path)
        self.model_path.mkdir(parents=True, exist_ok=True)
        
        self.delay_predictor = DelayRiskPredictor('xgboost')
        self.cost_predictor = CostOverrunPredictor('xgboost')
        self.resource_detector = ResourceBottleneckDetector()
        self.risk_calculator = RiskScoreCalculator()
    
    def train_all_models(self, project_data: pd.DataFrame, resource_data: pd.DataFrame) -> Dict[str, Any]:
        """Train all ML models"""
        logger.info("Starting ML pipeline training")
        
        results = {}
        
        try:
            # Train delay predictor
            if 'delay_days' in project_data.columns:
                X_delay = self.delay_predictor.prepare_features(project_data)
                y_delay = project_data['delay_days']
                delay_metrics = self.delay_predictor.train(X_delay, y_delay)
                results['delay_model'] = delay_metrics
                
                # Save model
                self.delay_predictor.save(str(self.model_path / "delay_predictor.joblib"))
            
            # Train cost predictor
            if 'cost_overrun_percent' in project_data.columns:
                X_cost = self.cost_predictor.prepare_features(project_data)
                y_cost = project_data['cost_overrun_percent']
                cost_metrics = self.cost_predictor.train(X_cost, y_cost)
                results['cost_model'] = cost_metrics
                
                self.cost_predictor.save(str(self.model_path / "cost_predictor.joblib"))
            
            # Train resource detector
            X_resource = self.resource_detector.prepare_features(resource_data)
            self.resource_detector.fit(X_resource)
            results['resource_model'] = {'status': 'trained'}
            
            self.resource_detector.save(str(self.model_path / "resource_detector.joblib"))
            
            logger.info("All models trained successfully")
            
        except Exception as e:
            logger.error(f"Error training models: {e}")
            raise
        
        return results
    
    def load_all_models(self):
        """Load all trained models"""
        try:
            self.delay_predictor.load(str(self.model_path / "delay_predictor.joblib"))
            self.cost_predictor.load(str(self.model_path / "cost_predictor.joblib"))
            self.resource_detector.load(str(self.model_path / "resource_detector.joblib"))
            logger.info("All models loaded successfully")
        except Exception as e:
            logger.warning(f"Error loading models: {e}")
    
    def predict_project_risks(self, project_data: pd.DataFrame, resource_data: pd.DataFrame) -> Dict[str, Any]:
        """Generate predictions for a project"""
        try:
            # Delay prediction
            X_delay = self.delay_predictor.prepare_features(project_data)
            delay_pred, delay_conf = self.delay_predictor.predict_with_confidence(X_delay)
            
            # Cost prediction
            X_cost = self.cost_predictor.prepare_features(project_data)
            cost_pred = self.cost_predictor.predict(X_cost)
            
            # Resource bottleneck detection
            resource_analysis = self.resource_detector.identify_bottlenecks(resource_data)
            
            # Calculate risk scores
            risk_report = self.risk_calculator.generate_risk_report({
                'predicted_delay_days': delay_pred[0] if len(delay_pred) > 0 else 0,
                'delay_confidence': delay_conf[0] if len(delay_conf) > 0 else 0.8,
                'predicted_cost_overrun_percent': cost_pred[0] if len(cost_pred) > 0 else 0,
                'anomaly_score': resource_analysis['anomaly_score'].mean() if 'anomaly_score' in resource_analysis else 0,
                'avg_utilization_rate': resource_analysis['utilization_rate'].mean() if 'utilization_rate' in resource_analysis else 0.8,
                'bug_rate': 0,  # Calculate from actual data
                'reopen_rate': 0
            })
            
            return {
                'delay_prediction': {
                    'predicted_days': float(delay_pred[0]) if len(delay_pred) > 0 else 0,
                    'confidence': float(delay_conf[0]) if len(delay_conf) > 0 else 0
                },
                'cost_prediction': {
                    'predicted_overrun_percent': float(cost_pred[0]) if len(cost_pred) > 0 else 0
                },
                'resource_bottlenecks': {
                    'count': int(resource_analysis['is_bottleneck'].sum()) if 'is_bottleneck' in resource_analysis else 0,
                    'avg_anomaly_score': float(resource_analysis['anomaly_score'].mean()) if 'anomaly_score' in resource_analysis else 0
                },
                'risk_report': risk_report
            }
            
        except Exception as e:
            logger.error(f"Error generating predictions: {e}")
            raise
