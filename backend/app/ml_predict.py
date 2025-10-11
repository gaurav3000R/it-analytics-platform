"""
ML Model Prediction Module
===========================

Load trained model and make predictions on new data.
"""

import joblib
import json
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Union

# Paths
BASE_DIR = Path(__file__).parent
MODELS_DIR = BASE_DIR / "models"


class ProjectSuccessPredictor:
    """Load and use trained model for predictions"""
    
    def __init__(self, model_path=None):
        """
        Initialize predictor with trained model
        
        Args:
            model_path: Path to model file (if None, uses latest)
        """
        if model_path is None:
            model_path = MODELS_DIR / "latest_model.joblib"
            scaler_path = MODELS_DIR / "latest_scaler.joblib"
            features_path = MODELS_DIR / "latest_features.json"
            metadata_path = MODELS_DIR / "latest_metadata.json"
        else:
            # Extract timestamp from model path
            timestamp = model_path.stem.split('_')[-1]
            scaler_path = MODELS_DIR / f"scaler_{timestamp}.joblib"
            features_path = MODELS_DIR / f"features_{timestamp}.json"
            metadata_path = MODELS_DIR / f"metadata_{timestamp}.json"
        
        # Load model
        self.model = joblib.load(model_path)
        self.scaler = joblib.load(scaler_path)
        
        with open(features_path, 'r') as f:
            self.feature_names = json.load(f)
        
        with open(metadata_path, 'r') as f:
            self.metadata = json.load(f)
        
        print(f"✅ Model loaded: {self.metadata['model_name']}")
        print(f"   Accuracy: {self.metadata['metrics']['accuracy']:.4f}")
        print(f"   F1-Score: {self.metadata['metrics']['f1_score']:.4f}")
    
    def predict(self, data: Union[Dict, pd.DataFrame]) -> Dict:
        """
        Make prediction on new data
        
        Args:
            data: Dictionary or DataFrame with feature values
        
        Returns:
            Dictionary with prediction results
        """
        # Convert dict to DataFrame if needed
        if isinstance(data, dict):
            # Handle single prediction
            if not isinstance(list(data.values())[0], list):
                data = {k: [v] for k, v in data.items()}
            df = pd.DataFrame(data)
        else:
            df = data.copy()
        
        # Ensure correct column order
        df = df[self.feature_names]
        
        # Scale features
        X_scaled = self.scaler.transform(df)
        
        # Make prediction
        prediction = self.model.predict(X_scaled)
        
        # Get probability if available
        if hasattr(self.model, 'predict_proba'):
            probabilities = self.model.predict_proba(X_scaled)
            probability = probabilities[0][1] if len(prediction) == 1 else probabilities[:, 1].tolist()
        else:
            probability = None
        
        # Format result
        result = {
            'prediction': int(prediction[0]) if len(prediction) == 1 else prediction.tolist(),
            'success': bool(prediction[0]) if len(prediction) == 1 else [bool(p) for p in prediction],
            'probability': float(probability) if probability is not None and not isinstance(probability, list) else probability,
            'confidence': float(probability) if probability is not None and not isinstance(probability, list) else None,
            'model': self.metadata['model_name'],
            'features': dict(zip(self.feature_names, df.values[0])) if len(df) == 1 else None
        }
        
        return result
    
    def predict_batch(self, data_list: List[Dict]) -> List[Dict]:
        """
        Make predictions on multiple data points
        
        Args:
            data_list: List of dictionaries with feature values
        
        Returns:
            List of prediction results
        """
        df = pd.DataFrame(data_list)
        return self.predict(df)


def demo_prediction():
    """Demo function showing how to use the predictor"""
    print("\n" + "="*70)
    print("DEMO: Making Predictions with Trained Model")
    print("="*70)
    
    # Load predictor
    predictor = ProjectSuccessPredictor()
    
    # Example 1: Single prediction
    print("\n📊 Example 1: Single Prediction")
    print("-" * 70)
    
    sample_data = {
        'Agile Effectiveness': 5,
        'Risk Mitigation': 5,
        'Management Satisfaction': 5,
        'Supply Chain Improvement': 5,
        'Time Efficiency': 5,
        'Cost Savings (%)': 35
    }
    
    print(f"Input: {sample_data}")
    result = predictor.predict(sample_data)
    
    print(f"\n✅ Prediction Result:")
    print(f"   Success: {'✅ YES' if result['success'] else '❌ NO'}")
    print(f"   Probability: {result['probability']:.2%}" if result['probability'] else "   Probability: N/A")
    print(f"   Model: {result['model']}")
    
    # Example 2: Batch prediction
    print("\n📊 Example 2: Batch Prediction")
    print("-" * 70)
    
    batch_data = [
        {
            'Agile Effectiveness': 2,
            'Risk Mitigation': 2,
            'Management Satisfaction': 2,
            'Supply Chain Improvement': 2,
            'Time Efficiency': 2,
            'Cost Savings (%)': 15
        },
        {
            'Agile Effectiveness': 5,
            'Risk Mitigation': 5,
            'Management Satisfaction': 5,
            'Supply Chain Improvement': 5,
            'Time Efficiency': 5,
            'Cost Savings (%)': 45
        },
        {
            'Agile Effectiveness': 3,
            'Risk Mitigation': 3,
            'Management Satisfaction': 3,
            'Supply Chain Improvement': 3,
            'Time Efficiency': 3,
            'Cost Savings (%)': 25
        }
    ]
    
    results = predictor.predict_batch(batch_data)
    
    print(f"\nPredicting {len(batch_data)} projects...")
    for i, (data, result) in enumerate(zip(batch_data, results['probability']), 1):
        success = results['prediction'][i-1]
        prob = result
        print(f"\n   Project {i}:")
        print(f"      Agile Effectiveness: {data['Agile Effectiveness']}")
        print(f"      Risk Mitigation: {data['Risk Mitigation']}")
        print(f"      Result: {'✅ Success' if success else '❌ Failure'} (Prob: {prob:.2%})")
    
    # Example 3: Using current test data
    print("\n📊 Example 3: Test on Sample Data")
    print("-" * 70)
    
    # Load original dataset
    import pandas as pd
    data_path = Path.home() / ".cache/kagglehub/datasets/digrok/agile-project-dataset-2024/versions/1/Agile_Projects_Dataset.xlsx"
    df = pd.read_excel(data_path)
    
    # Get a few samples
    samples = df.sample(5, random_state=42)
    X_samples = samples[predictor.feature_names]
    y_true = samples['Project Success'].values
    
    print("\nTesting on 5 random samples from dataset:")
    for i, (idx, row) in enumerate(X_samples.iterrows(), 1):
        result = predictor.predict(row.to_dict())
        actual = y_true[i-1]
        predicted = result['prediction']
        correct = "✅" if predicted == actual else "❌"
        
        print(f"\n   Sample {i}: {correct}")
        print(f"      Predicted: {'Success' if predicted else 'Failure'}")
        print(f"      Actual: {'Success' if actual else 'Failure'}")
        print(f"      Probability: {result['probability']:.2%}" if result['probability'] else "")
    
    print("\n" + "="*70)
    print("✅ Demo Complete!")
    print("="*70)


if __name__ == "__main__":
    demo_prediction()
