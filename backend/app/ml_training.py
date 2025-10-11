"""
Machine Learning Training Pipeline for Agile Project Success Prediction
========================================================================

This script implements a complete ML pipeline:
1. Data Collection & Loading
2. Data Cleaning & Preprocessing
3. Feature Selection
4. Train/Test Split
5. Model Selection & Training
6. Model Evaluation
7. Hyperparameter Tuning
8. Model Saving

Target: Predict Project Success (Binary Classification)
"""

import os
import pandas as pd
import numpy as np
import joblib
import json
from datetime import datetime
from pathlib import Path

# Machine Learning
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, classification_report, roc_auc_score, roc_curve
)

# Models
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import (
    RandomForestClassifier, 
    GradientBoostingClassifier,
    AdaBoostClassifier
)
from sklearn.svm import SVC
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier

# Visualization
import matplotlib.pyplot as plt
import seaborn as sns

# Set random seed for reproducibility
RANDOM_STATE = 42
np.random.seed(RANDOM_STATE)

# Paths
BASE_DIR = Path(__file__).parent
MODELS_DIR = BASE_DIR / "models"
MODELS_DIR.mkdir(exist_ok=True)

DATA_PATH = Path.home() / ".cache/kagglehub/datasets/digrok/agile-project-dataset-2024/versions/1/Agile_Projects_Dataset.xlsx"


class MLTrainingPipeline:
    """Complete ML Training Pipeline"""
    
    def __init__(self):
        self.df = None
        self.X_train = None
        self.X_test = None
        self.y_train = None
        self.y_test = None
        self.scaler = None
        self.best_model = None
        self.best_model_name = None
        self.feature_names = None
        self.results = {}
        
    def step1_load_data(self):
        """Step 1: Collect Data - Load dataset"""
        print("\n" + "="*70)
        print("STEP 1: COLLECT DATA")
        print("="*70)
        
        try:
            self.df = pd.read_excel(DATA_PATH)
            print(f"✅ Data loaded successfully!")
            print(f"   Shape: {self.df.shape[0]} rows × {self.df.shape[1]} columns")
            print(f"\n📊 Dataset Preview:")
            print(self.df.head())
            return True
        except Exception as e:
            print(f"❌ Error loading data: {e}")
            return False
    
    def step2_clean_data(self):
        """Step 2: Clean Data - Handle missing values, duplicates, types"""
        print("\n" + "="*70)
        print("STEP 2: CLEAN DATA")
        print("="*70)
        
        # Check for missing values
        missing = self.df.isnull().sum()
        print(f"\n🔍 Missing Values:")
        if missing.sum() == 0:
            print("   ✅ No missing values found!")
        else:
            print(missing[missing > 0])
            # Handle missing values (if any)
            self.df = self.df.dropna()
            print(f"   ✅ Dropped rows with missing values")
        
        # Check for duplicates
        duplicates = self.df.duplicated().sum()
        print(f"\n🔍 Duplicate Rows: {duplicates}")
        if duplicates > 0:
            self.df = self.df.drop_duplicates()
            print(f"   ✅ Removed {duplicates} duplicate rows")
        else:
            print("   ✅ No duplicates found!")
        
        # Check data types
        print(f"\n📋 Data Types:")
        print(self.df.dtypes)
        
        print(f"\n✅ Data cleaned!")
        print(f"   Final shape: {self.df.shape[0]} rows × {self.df.shape[1]} columns")
        return True
    
    def step3_select_features(self):
        """Step 3: Select Features - Choose input columns and target"""
        print("\n" + "="*70)
        print("STEP 3: SELECT FEATURES")
        print("="*70)
        
        # Target variable
        target = 'Project Success'
        
        # Features (all columns except target)
        features = [col for col in self.df.columns if col != target]
        
        print(f"\n🎯 Target Variable: {target}")
        print(f"   Values: {self.df[target].unique()}")
        print(f"   Distribution: {dict(self.df[target].value_counts())}")
        
        print(f"\n📊 Features ({len(features)}):")
        for i, feature in enumerate(features, 1):
            print(f"   {i}. {feature}")
        
        # Store for later use
        self.feature_names = features
        
        # Correlation analysis
        print(f"\n📈 Correlation with Target:")
        correlations = self.df[features].corrwith(self.df[target]).sort_values(ascending=False)
        print(correlations)
        
        # Separate features and target
        X = self.df[features]
        y = self.df[target]
        
        print(f"\n✅ Features selected!")
        print(f"   X shape: {X.shape}")
        print(f"   y shape: {y.shape}")
        
        return X, y
    
    def step4_split_data(self, X, y, test_size=0.2):
        """Step 4: Split Data - Create train/test sets"""
        print("\n" + "="*70)
        print("STEP 4: SPLIT DATA")
        print("="*70)
        
        # Split the data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=RANDOM_STATE, stratify=y
        )
        
        print(f"\n📊 Split ratio: {int((1-test_size)*100)}/{int(test_size*100)}")
        print(f"   Training set: {X_train.shape[0]} samples")
        print(f"   Test set: {X_test.shape[0]} samples")
        
        print(f"\n📈 Class distribution:")
        print(f"   Train: {dict(y_train.value_counts())}")
        print(f"   Test: {dict(y_test.value_counts())}")
        
        # Scale features
        print(f"\n⚙️  Scaling features...")
        self.scaler = StandardScaler()
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Convert back to DataFrame
        X_train_scaled = pd.DataFrame(X_train_scaled, columns=X_train.columns)
        X_test_scaled = pd.DataFrame(X_test_scaled, columns=X_test.columns)
        
        print(f"   ✅ Features scaled using StandardScaler")
        
        self.X_train = X_train_scaled
        self.X_test = X_test_scaled
        self.y_train = y_train
        self.y_test = y_test
        
        return True
    
    def step5_choose_and_train_models(self):
        """Step 5: Choose & Train Multiple Models"""
        print("\n" + "="*70)
        print("STEP 5: CHOOSE & TRAIN MODELS")
        print("="*70)
        
        # Define models to test
        models = {
            'Logistic Regression': LogisticRegression(random_state=RANDOM_STATE, max_iter=1000),
            'Decision Tree': DecisionTreeClassifier(random_state=RANDOM_STATE),
            'Random Forest': RandomForestClassifier(random_state=RANDOM_STATE, n_estimators=100),
            'Gradient Boosting': GradientBoostingClassifier(random_state=RANDOM_STATE),
            'AdaBoost': AdaBoostClassifier(random_state=RANDOM_STATE),
            'SVM': SVC(random_state=RANDOM_STATE, probability=True),
            'Naive Bayes': GaussianNB(),
            'K-Nearest Neighbors': KNeighborsClassifier()
        }
        
        print(f"\n🔍 Training {len(models)} different models...\n")
        
        results = []
        
        for name, model in models.items():
            print(f"   Training {name}...")
            
            # Train model
            model.fit(self.X_train, self.y_train)
            
            # Make predictions
            y_pred = model.predict(self.X_test)
            y_pred_proba = model.predict_proba(self.X_test)[:, 1] if hasattr(model, 'predict_proba') else None
            
            # Calculate metrics
            accuracy = accuracy_score(self.y_test, y_pred)
            precision = precision_score(self.y_test, y_pred, zero_division=0)
            recall = recall_score(self.y_test, y_pred, zero_division=0)
            f1 = f1_score(self.y_test, y_pred, zero_division=0)
            
            # Cross-validation score
            cv_scores = cross_val_score(model, self.X_train, self.y_train, cv=5)
            cv_mean = cv_scores.mean()
            
            # ROC AUC (if probability available)
            roc_auc = roc_auc_score(self.y_test, y_pred_proba) if y_pred_proba is not None else 0
            
            results.append({
                'Model': name,
                'Accuracy': accuracy,
                'Precision': precision,
                'Recall': recall,
                'F1-Score': f1,
                'ROC-AUC': roc_auc,
                'CV Mean': cv_mean,
                'Model Object': model
            })
            
            print(f"      Accuracy: {accuracy:.4f} | F1: {f1:.4f} | ROC-AUC: {roc_auc:.4f}")
        
        # Create results DataFrame
        results_df = pd.DataFrame(results)
        results_df = results_df.sort_values('F1-Score', ascending=False)
        
        self.results = results_df
        
        print(f"\n✅ All models trained!")
        return results_df
    
    def step6_evaluate_models(self):
        """Step 6: Evaluate Models - Compare performance"""
        print("\n" + "="*70)
        print("STEP 6: EVALUATE MODELS")
        print("="*70)
        
        print(f"\n📊 Model Comparison:")
        print(self.results[['Model', 'Accuracy', 'Precision', 'Recall', 'F1-Score', 'ROC-AUC', 'CV Mean']].to_string(index=False))
        
        # Select best model based on F1-Score
        best_idx = self.results['F1-Score'].idxmax()
        self.best_model = self.results.loc[best_idx, 'Model Object']
        self.best_model_name = self.results.loc[best_idx, 'Model']
        
        print(f"\n🏆 Best Model: {self.best_model_name}")
        print(f"   F1-Score: {self.results.loc[best_idx, 'F1-Score']:.4f}")
        print(f"   Accuracy: {self.results.loc[best_idx, 'Accuracy']:.4f}")
        print(f"   ROC-AUC: {self.results.loc[best_idx, 'ROC-AUC']:.4f}")
        
        # Detailed evaluation of best model
        y_pred = self.best_model.predict(self.X_test)
        
        print(f"\n📈 Classification Report (Best Model):")
        print(classification_report(self.y_test, y_pred))
        
        print(f"\n🎯 Confusion Matrix:")
        cm = confusion_matrix(self.y_test, y_pred)
        print(cm)
        
        return True
    
    def step7_tune_model(self):
        """Step 7: Tune Model - Hyperparameter optimization"""
        print("\n" + "="*70)
        print("STEP 7: TUNE MODEL (HYPERPARAMETER OPTIMIZATION)")
        print("="*70)
        
        print(f"\n⚙️  Tuning {self.best_model_name}...\n")
        
        # Define parameter grids for different models
        param_grids = {
            'Random Forest': {
                'n_estimators': [50, 100, 200],
                'max_depth': [10, 20, None],
                'min_samples_split': [2, 5, 10]
            },
            'Gradient Boosting': {
                'n_estimators': [50, 100, 200],
                'learning_rate': [0.01, 0.1, 0.2],
                'max_depth': [3, 5, 7]
            },
            'Logistic Regression': {
                'C': [0.001, 0.01, 0.1, 1, 10],
                'penalty': ['l2'],
                'solver': ['lbfgs', 'liblinear']
            },
            'SVM': {
                'C': [0.1, 1, 10],
                'kernel': ['rbf', 'linear'],
                'gamma': ['scale', 'auto']
            }
        }
        
        if self.best_model_name in param_grids:
            param_grid = param_grids[self.best_model_name]
            
            # Grid search
            grid_search = GridSearchCV(
                self.best_model,
                param_grid,
                cv=5,
                scoring='f1',
                n_jobs=-1,
                verbose=1
            )
            
            grid_search.fit(self.X_train, self.y_train)
            
            # Update best model
            self.best_model = grid_search.best_estimator_
            
            print(f"\n✅ Best Parameters:")
            for param, value in grid_search.best_params_.items():
                print(f"   {param}: {value}")
            
            print(f"\n📈 Improved F1-Score: {grid_search.best_score_:.4f}")
            
            # Re-evaluate
            y_pred = self.best_model.predict(self.X_test)
            new_f1 = f1_score(self.y_test, y_pred)
            new_accuracy = accuracy_score(self.y_test, y_pred)
            
            print(f"\n🎯 Test Set Performance:")
            print(f"   Accuracy: {new_accuracy:.4f}")
            print(f"   F1-Score: {new_f1:.4f}")
        else:
            print(f"   ℹ️  No hyperparameter tuning defined for {self.best_model_name}")
            print(f"   Using default parameters")
        
        return True
    
    def step8_save_model(self):
        """Step 8: Save Model - Export for deployment"""
        print("\n" + "="*70)
        print("STEP 8: SAVE MODEL")
        print("="*70)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save model
        model_filename = f"project_success_model_{timestamp}.joblib"
        model_path = MODELS_DIR / model_filename
        joblib.dump(self.best_model, model_path)
        print(f"\n✅ Model saved: {model_path}")
        
        # Save scaler
        scaler_filename = f"scaler_{timestamp}.joblib"
        scaler_path = MODELS_DIR / scaler_filename
        joblib.dump(self.scaler, scaler_path)
        print(f"✅ Scaler saved: {scaler_path}")
        
        # Save feature names
        features_filename = f"features_{timestamp}.json"
        features_path = MODELS_DIR / features_filename
        with open(features_path, 'w') as f:
            json.dump(self.feature_names, f)
        print(f"✅ Features saved: {features_path}")
        
        # Save metadata
        metadata = {
            'model_name': self.best_model_name,
            'model_file': model_filename,
            'scaler_file': scaler_filename,
            'features_file': features_filename,
            'feature_names': self.feature_names,
            'training_date': timestamp,
            'train_samples': len(self.X_train),
            'test_samples': len(self.X_test),
            'metrics': {
                'accuracy': float(accuracy_score(self.y_test, self.best_model.predict(self.X_test))),
                'f1_score': float(f1_score(self.y_test, self.best_model.predict(self.X_test))),
                'precision': float(precision_score(self.y_test, self.best_model.predict(self.X_test))),
                'recall': float(recall_score(self.y_test, self.best_model.predict(self.X_test)))
            }
        }
        
        metadata_filename = f"metadata_{timestamp}.json"
        metadata_path = MODELS_DIR / metadata_filename
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        print(f"✅ Metadata saved: {metadata_path}")
        
        # Save also as "latest" for easy loading
        latest_model_path = MODELS_DIR / "latest_model.joblib"
        latest_scaler_path = MODELS_DIR / "latest_scaler.joblib"
        latest_features_path = MODELS_DIR / "latest_features.json"
        latest_metadata_path = MODELS_DIR / "latest_metadata.json"
        
        joblib.dump(self.best_model, latest_model_path)
        joblib.dump(self.scaler, latest_scaler_path)
        with open(latest_features_path, 'w') as f:
            json.dump(self.feature_names, f)
        with open(latest_metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print(f"\n✅ Latest versions saved for easy loading:")
        print(f"   • latest_model.joblib")
        print(f"   • latest_scaler.joblib")
        print(f"   • latest_features.json")
        print(f"   • latest_metadata.json")
        
        return metadata
    
    def run_full_pipeline(self):
        """Run the complete ML pipeline"""
        print("\n" + "🚀"*35)
        print(" "*20 + "ML TRAINING PIPELINE")
        print("🚀"*35)
        
        # Execute all steps
        if not self.step1_load_data():
            return False
        
        self.step2_clean_data()
        X, y = self.step3_select_features()
        self.step4_split_data(X, y)
        self.step5_choose_and_train_models()
        self.step6_evaluate_models()
        self.step7_tune_model()
        metadata = self.step8_save_model()
        
        # Final summary
        print("\n" + "="*70)
        print("🎉 TRAINING COMPLETE!")
        print("="*70)
        
        print(f"\n📊 Final Results:")
        print(f"   Best Model: {self.best_model_name}")
        print(f"   Accuracy: {metadata['metrics']['accuracy']:.4f}")
        print(f"   F1-Score: {metadata['metrics']['f1_score']:.4f}")
        print(f"   Precision: {metadata['metrics']['precision']:.4f}")
        print(f"   Recall: {metadata['metrics']['recall']:.4f}")
        
        print(f"\n📁 Model files saved in: {MODELS_DIR}")
        print(f"\n✅ Model is ready for deployment!")
        
        return True


def main():
    """Main execution function"""
    pipeline = MLTrainingPipeline()
    pipeline.run_full_pipeline()


if __name__ == "__main__":
    main()
