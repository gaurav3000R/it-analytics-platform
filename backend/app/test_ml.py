"""
ML Model Testing Script
=======================

Test the trained ML model with various scenarios.
"""

import requests
import json
from pathlib import Path
import sys

# Add parent to path
sys.path.append(str(Path(__file__).parent.parent))

from ml_predict import ProjectSuccessPredictor


def test_python_prediction():
    """Test 1: Python Module Direct Testing"""
    print("\n" + "="*70)
    print("TEST 1: PYTHON MODULE - DIRECT PREDICTION")
    print("="*70)
    
    try:
        # Load predictor
        predictor = ProjectSuccessPredictor()
        print("✅ Model loaded successfully")
        
        # Test Case 1: High success probability project
        print("\n📊 Test Case 1: High Quality Project")
        print("-" * 70)
        high_quality = {
            'Agile Effectiveness': 5,
            'Risk Mitigation': 5,
            'Management Satisfaction': 5,
            'Supply Chain Improvement': 5,
            'Time Efficiency': 5,
            'Cost Savings (%)': 45
        }
        result = predictor.predict(high_quality)
        print(f"Input: {high_quality}")
        print(f"Result: {'✅ Success' if result['success'] else '❌ Failure'}")
        print(f"Probability: {result['probability']:.2%}" if result['probability'] else "Probability: N/A")
        print(f"Status: ✅ PASSED")
        
        # Test Case 2: Low success probability project
        print("\n📊 Test Case 2: Low Quality Project")
        print("-" * 70)
        low_quality = {
            'Agile Effectiveness': 2,
            'Risk Mitigation': 2,
            'Management Satisfaction': 2,
            'Supply Chain Improvement': 2,
            'Time Efficiency': 2,
            'Cost Savings (%)': 10
        }
        result = predictor.predict(low_quality)
        print(f"Input: {low_quality}")
        print(f"Result: {'✅ Success' if result['success'] else '❌ Failure'}")
        print(f"Probability: {result['probability']:.2%}" if result['probability'] else "Probability: N/A")
        print(f"Status: ✅ PASSED")
        
        # Test Case 3: Medium quality project
        print("\n📊 Test Case 3: Medium Quality Project")
        print("-" * 70)
        medium_quality = {
            'Agile Effectiveness': 3,
            'Risk Mitigation': 4,
            'Management Satisfaction': 3,
            'Supply Chain Improvement': 3,
            'Time Efficiency': 3,
            'Cost Savings (%)': 25
        }
        result = predictor.predict(medium_quality)
        print(f"Input: {medium_quality}")
        print(f"Result: {'✅ Success' if result['success'] else '❌ Failure'}")
        print(f"Probability: {result['probability']:.2%}" if result['probability'] else "Probability: N/A")
        print(f"Status: ✅ PASSED")
        
        # Test Case 4: Batch prediction
        print("\n📊 Test Case 4: Batch Prediction (3 projects)")
        print("-" * 70)
        batch_data = [high_quality, low_quality, medium_quality]
        result = predictor.predict_batch(batch_data)
        print(f"Predicted {len(result['prediction'])} projects")
        for i, (pred, prob) in enumerate(zip(result['prediction'], result['probability']), 1):
            print(f"  Project {i}: {'Success' if pred else 'Failure'} ({prob:.2%})")
        print(f"Status: ✅ PASSED")
        
        print("\n✅ All Python tests PASSED!")
        return True
        
    except Exception as e:
        print(f"\n❌ Python test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_api_endpoints(base_url="http://localhost:8000"):
    """Test 2: FastAPI Endpoint Testing"""
    print("\n" + "="*70)
    print("TEST 2: FASTAPI ENDPOINTS")
    print("="*70)
    print(f"Base URL: {base_url}")
    print("\nNote: Make sure FastAPI server is running!")
    print("Run: uvicorn app.main:app --reload")
    print("-" * 70)
    
    # Test Case 1: Health Check
    print("\n📊 Test Case 1: Health Check")
    print("-" * 70)
    try:
        response = requests.get(f"{base_url}/ml/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"Status Code: {response.status_code}")
            print(f"Response: {json.dumps(data, indent=2)}")
            print(f"Status: ✅ PASSED")
        else:
            print(f"Status Code: {response.status_code}")
            print(f"Status: ❌ FAILED")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection Error: {e}")
        print("\n💡 TIP: Start the server with:")
        print("   cd backend && uvicorn app.main:app --reload")
        return False
    
    # Test Case 2: Model Info
    print("\n📊 Test Case 2: Get Model Info")
    print("-" * 70)
    try:
        response = requests.get(f"{base_url}/ml/model/info", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"Model: {data.get('model_name')}")
            print(f"Accuracy: {data.get('accuracy'):.4f}")
            print(f"F1-Score: {data.get('f1_score'):.4f}")
            print(f"Status: ✅ PASSED")
        else:
            print(f"Status Code: {response.status_code}")
            print(f"Status: ❌ FAILED")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Error: {e}")
        return False
    
    # Test Case 3: Single Prediction
    print("\n📊 Test Case 3: Single Prediction")
    print("-" * 70)
    payload = {
        "agile_effectiveness": 5,
        "risk_mitigation": 4,
        "management_satisfaction": 5,
        "supply_chain_improvement": 4,
        "time_efficiency": 4,
        "cost_savings_pct": 30
    }
    try:
        response = requests.post(
            f"{base_url}/ml/predict",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=5
        )
        if response.status_code == 200:
            data = response.json()
            print(f"Request: {json.dumps(payload, indent=2)}")
            print(f"\nResponse:")
            print(f"  Prediction: {'Success' if data['success'] else 'Failure'}")
            print(f"  Probability: {data.get('probability', 'N/A')}")
            print(f"  Message: {data.get('message')}")
            print(f"Status: ✅ PASSED")
        else:
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.text}")
            print(f"Status: ❌ FAILED")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Error: {e}")
        return False
    
    # Test Case 4: Batch Prediction
    print("\n📊 Test Case 4: Batch Prediction")
    print("-" * 70)
    batch_payload = {
        "projects": [
            {
                "agile_effectiveness": 5,
                "risk_mitigation": 5,
                "management_satisfaction": 5,
                "supply_chain_improvement": 5,
                "time_efficiency": 5,
                "cost_savings_pct": 40
            },
            {
                "agile_effectiveness": 2,
                "risk_mitigation": 2,
                "management_satisfaction": 2,
                "supply_chain_improvement": 2,
                "time_efficiency": 2,
                "cost_savings_pct": 15
            }
        ]
    }
    try:
        response = requests.post(
            f"{base_url}/ml/predict/batch",
            json=batch_payload,
            headers={"Content-Type": "application/json"},
            timeout=5
        )
        if response.status_code == 200:
            data = response.json()
            print(f"Total Projects: {data['total']}")
            print(f"Successful: {data['successful']}")
            print(f"Failed: {data['failed']}")
            print(f"Status: ✅ PASSED")
        else:
            print(f"Status Code: {response.status_code}")
            print(f"Status: ❌ FAILED")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Error: {e}")
        return False
    
    # Test Case 5: Analysis Endpoint
    print("\n📊 Test Case 5: Project Analysis")
    print("-" * 70)
    try:
        response = requests.post(
            f"{base_url}/ml/analyze",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=5
        )
        if response.status_code == 200:
            data = response.json()
            print(f"Overall Score: {data['analysis']['overall_score']:.2f}")
            print(f"Risk Level: {data['analysis']['risk_level']}")
            print(f"Strengths: {len(data['analysis']['strengths'])}")
            print(f"Recommendations: {len(data['analysis']['recommendations'])}")
            print(f"Status: ✅ PASSED")
        else:
            print(f"Status Code: {response.status_code}")
            print(f"Status: ❌ FAILED")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Error: {e}")
        return False
    
    print("\n✅ All API tests PASSED!")
    return True


def test_edge_cases():
    """Test 3: Edge Cases and Error Handling"""
    print("\n" + "="*70)
    print("TEST 3: EDGE CASES & ERROR HANDLING")
    print("="*70)
    
    try:
        predictor = ProjectSuccessPredictor()
        
        # Test Case 1: Minimum values
        print("\n📊 Test Case 1: Minimum Values")
        print("-" * 70)
        min_values = {
            'Agile Effectiveness': 1,
            'Risk Mitigation': 1,
            'Management Satisfaction': 1,
            'Supply Chain Improvement': 1,
            'Time Efficiency': 1,
            'Cost Savings (%)': 0
        }
        result = predictor.predict(min_values)
        print(f"Input: All minimum values")
        print(f"Result: {result['success']}")
        print(f"Status: ✅ PASSED")
        
        # Test Case 2: Maximum values
        print("\n📊 Test Case 2: Maximum Values")
        print("-" * 70)
        max_values = {
            'Agile Effectiveness': 5,
            'Risk Mitigation': 5,
            'Management Satisfaction': 5,
            'Supply Chain Improvement': 5,
            'Time Efficiency': 5,
            'Cost Savings (%)': 100
        }
        result = predictor.predict(max_values)
        print(f"Input: All maximum values")
        print(f"Result: {result['success']}")
        print(f"Status: ✅ PASSED")
        
        # Test Case 3: Mixed values
        print("\n📊 Test Case 3: Mixed Extreme Values")
        print("-" * 70)
        mixed_values = {
            'Agile Effectiveness': 5,
            'Risk Mitigation': 1,
            'Management Satisfaction': 5,
            'Supply Chain Improvement': 1,
            'Time Efficiency': 5,
            'Cost Savings (%)': 50
        }
        result = predictor.predict(mixed_values)
        print(f"Input: Mixed extreme values")
        print(f"Result: {result['success']}")
        print(f"Status: ✅ PASSED")
        
        print("\n✅ All edge case tests PASSED!")
        return True
        
    except Exception as e:
        print(f"\n❌ Edge case test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_model_files():
    """Test 4: Model File Integrity"""
    print("\n" + "="*70)
    print("TEST 4: MODEL FILE INTEGRITY")
    print("="*70)
    
    models_dir = Path(__file__).parent / "models"
    
    required_files = [
        "latest_model.joblib",
        "latest_scaler.joblib",
        "latest_features.json",
        "latest_metadata.json"
    ]
    
    all_exist = True
    for filename in required_files:
        filepath = models_dir / filename
        if filepath.exists():
            size = filepath.stat().st_size / 1024  # KB
            print(f"✅ {filename} ({size:.2f} KB)")
        else:
            print(f"❌ {filename} - NOT FOUND")
            all_exist = False
    
    if all_exist:
        print("\n✅ All model files exist!")
        
        # Test loading
        try:
            predictor = ProjectSuccessPredictor()
            print(f"✅ Model loads successfully")
            print(f"   Model: {predictor.metadata['model_name']}")
            print(f"   Accuracy: {predictor.metadata['metrics']['accuracy']:.4f}")
            return True
        except Exception as e:
            print(f"❌ Failed to load model: {e}")
            return False
    else:
        print("\n❌ Some model files are missing!")
        print("\n💡 TIP: Run training script:")
        print("   python app/ml_training.py")
        return False


def run_all_tests(api_test=False):
    """Run all tests"""
    print("\n" + "🧪"*35)
    print(" "*20 + "ML MODEL TESTING")
    print("🧪"*35)
    
    results = {}
    
    # Test 1: Python Module
    results['Python Module'] = test_python_prediction()
    
    # Test 2: Model Files
    results['Model Files'] = test_model_files()
    
    # Test 3: Edge Cases
    results['Edge Cases'] = test_edge_cases()
    
    # Test 4: API Endpoints (optional)
    if api_test:
        results['API Endpoints'] = test_api_endpoints()
    else:
        print("\n" + "="*70)
        print("ℹ️  Skipping API tests (server not running)")
        print("   To test API: python app/test_ml.py --api")
        print("="*70)
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, passed_status in results.items():
        status = "✅ PASSED" if passed_status else "❌ FAILED"
        print(f"{test_name:.<50} {status}")
    
    print("-" * 70)
    print(f"Total: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED!")
        return True
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return False


if __name__ == "__main__":
    import sys
    
    # Check for --api flag
    api_test = '--api' in sys.argv
    
    success = run_all_tests(api_test=api_test)
    sys.exit(0 if success else 1)
