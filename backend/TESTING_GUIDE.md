# 🧪 ML Model Testing Guide

## Quick Start

### Method 1: Run All Tests (Recommended)
```bash
cd backend
python app/test_ml.py
```

### Method 2: Use Test Script
```bash
cd backend
./test-ml.sh
```

### Method 3: Test with API
```bash
# Terminal 1: Start server
cd backend
uvicorn app.main:app --reload

# Terminal 2: Run tests
cd backend
python app/test_ml.py --api
```

---

## 📋 Test Coverage

### ✅ Test 1: Python Module Tests
Tests direct Python module functionality without API.

**What's Tested:**
- Model loading
- Single predictions
- Batch predictions
- Different quality inputs

**Command:**
```bash
python app/test_ml.py
```

**Expected Output:**
```
Test Case 1: High Quality Project ✅
Test Case 2: Low Quality Project ✅
Test Case 3: Medium Quality Project ✅
Test Case 4: Batch Prediction ✅
```

### ✅ Test 2: Model File Integrity
Verifies all model files exist and are loadable.

**Files Checked:**
- `latest_model.joblib`
- `latest_scaler.joblib`
- `latest_features.json`
- `latest_metadata.json`

**What's Tested:**
- File existence
- File sizes
- Model loading
- Metadata integrity

### ✅ Test 3: Edge Cases
Tests boundary conditions and extreme values.

**Scenarios:**
- Minimum values (all 1s and 0%)
- Maximum values (all 5s and 100%)
- Mixed extreme values
- Error handling

### ✅ Test 4: API Endpoints (Optional)
Tests FastAPI REST endpoints.

**Endpoints Tested:**
- `GET /ml/health` - Health check
- `GET /ml/model/info` - Model information
- `POST /ml/predict` - Single prediction
- `POST /ml/predict/batch` - Batch predictions
- `POST /ml/analyze` - Project analysis

**Requirements:**
- Server must be running on port 8000

---

## 🚀 Testing Methods

### 1. Python Script Testing

#### Basic Test:
```bash
cd backend
source .venv/bin/activate
python app/test_ml.py
```

#### With API Tests:
```bash
python app/test_ml.py --api
```

### 2. Interactive Python Testing

```python
from app.ml_predict import ProjectSuccessPredictor

# Load model
predictor = ProjectSuccessPredictor()

# Test prediction
result = predictor.predict({
    'Agile Effectiveness': 5,
    'Risk Mitigation': 4,
    'Management Satisfaction': 5,
    'Supply Chain Improvement': 4,
    'Time Efficiency': 4,
    'Cost Savings (%)': 30
})

print(result)
```

### 3. curl Testing (API)

```bash
# Health Check
curl http://localhost:8000/ml/health

# Model Info
curl http://localhost:8000/ml/model/info

# Prediction
curl -X POST http://localhost:8000/ml/predict \
  -H "Content-Type: application/json" \
  -d '{
    "agile_effectiveness": 5,
    "risk_mitigation": 4,
    "management_satisfaction": 5,
    "supply_chain_improvement": 4,
    "time_efficiency": 4,
    "cost_savings_pct": 30
  }'
```

### 4. Postman/Insomnia Testing

**Collection Export:**
```json
{
  "name": "ML Predictions API",
  "requests": [
    {
      "name": "Health Check",
      "method": "GET",
      "url": "http://localhost:8000/ml/health"
    },
    {
      "name": "Predict Success",
      "method": "POST",
      "url": "http://localhost:8000/ml/predict",
      "body": {
        "agile_effectiveness": 5,
        "risk_mitigation": 4,
        "management_satisfaction": 5,
        "supply_chain_improvement": 4,
        "time_efficiency": 4,
        "cost_savings_pct": 30
      }
    }
  ]
}
```

---

## 📊 Test Scenarios

### Scenario 1: High Success Project
```json
{
  "agile_effectiveness": 5,
  "risk_mitigation": 5,
  "management_satisfaction": 5,
  "supply_chain_improvement": 5,
  "time_efficiency": 5,
  "cost_savings_pct": 45
}
```

**Expected:** Success with 50%+ probability

### Scenario 2: High Risk Project
```json
{
  "agile_effectiveness": 2,
  "risk_mitigation": 2,
  "management_satisfaction": 2,
  "supply_chain_improvement": 2,
  "time_efficiency": 2,
  "cost_savings_pct": 10
}
```

**Expected:** Failure with <50% probability

### Scenario 3: Balanced Project
```json
{
  "agile_effectiveness": 3,
  "risk_mitigation": 3,
  "management_satisfaction": 3,
  "supply_chain_improvement": 3,
  "time_efficiency": 3,
  "cost_savings_pct": 25
}
```

**Expected:** ~50% probability

### Scenario 4: Batch Test
```json
{
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
```

---

## 🐛 Troubleshooting

### Issue: Model Not Found
**Error:** `FileNotFoundError: Model file not found`

**Solution:**
```bash
cd backend
python app/ml_training.py
```

### Issue: Import Error
**Error:** `ModuleNotFoundError: No module named 'app'`

**Solution:**
```bash
cd backend
source .venv/bin/activate
python app/test_ml.py
```

### Issue: API Connection Refused
**Error:** `Connection refused on port 8000`

**Solution:**
```bash
# Start the server first
uvicorn app.main:app --reload
```

### Issue: Dependencies Missing
**Error:** `ImportError: Missing required dependencies`

**Solution:**
```bash
cd backend
uv sync
```

---

## 📈 Performance Testing

### Load Testing with Python
```python
import time
from app.ml_predict import ProjectSuccessPredictor

predictor = ProjectSuccessPredictor()

# Test 1000 predictions
test_data = {
    'Agile Effectiveness': 4,
    'Risk Mitigation': 4,
    'Management Satisfaction': 4,
    'Supply Chain Improvement': 4,
    'Time Efficiency': 4,
    'Cost Savings (%)': 30
}

start = time.time()
for _ in range(1000):
    predictor.predict(test_data)
end = time.time()

print(f"1000 predictions in {end-start:.2f} seconds")
print(f"Average: {(end-start)/1000*1000:.2f}ms per prediction")
```

### Load Testing with curl
```bash
# Install Apache Bench
brew install httpd  # macOS
# or
sudo apt install apache2-utils  # Linux

# Run load test
ab -n 1000 -c 10 -p payload.json -T application/json \
   http://localhost:8000/ml/predict
```

---

## ✅ Acceptance Criteria

### All Tests Should Pass:
- ✅ Model loads without errors
- ✅ Predictions return valid results
- ✅ All model files exist
- ✅ Edge cases handled gracefully
- ✅ API endpoints respond correctly (if tested)

### Performance Requirements:
- Single prediction: < 100ms
- Batch prediction (10): < 500ms
- Model loading: < 5s

### Response Format:
```json
{
  "prediction": 0 or 1,
  "success": true or false,
  "probability": 0.0 to 1.0,
  "confidence": 0.0 to 1.0,
  "model": "Naive Bayes",
  "message": "Project likely to succeed..."
}
```

---

## 🎯 Next Steps After Testing

1. ✅ All tests passed → Ready for integration
2. ❌ Tests failed → Check error messages
3. 📊 Performance issues → Optimize model
4. 🚀 Ready → Deploy to production

---

## 📞 Getting Help

If tests fail:
1. Check error messages in console
2. Verify all dependencies installed
3. Ensure model was trained successfully
4. Review TESTING_GUIDE.md (this file)
5. Check ML_TRAINING_SUMMARY.md

For additional help:
- Training guide: `ML_TRAINING_SUMMARY.md`
- API documentation: FastAPI `/docs` endpoint
- Model files: `backend/app/models/`

---

## 🎉 Success Checklist

- [ ] Model trained successfully
- [ ] All model files present
- [ ] Python tests passing
- [ ] Edge cases handled
- [ ] API tests passing (optional)
- [ ] Performance acceptable
- [ ] Ready for integration

Once all checked, your ML model is production-ready! 🚀

