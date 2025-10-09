# AI-Powered Operational Risk Early Warning System

## 🎯 Overview

The **AI-Powered Operational Risk Early Warning System** is a comprehensive solution for predicting and preventing project delivery delays, cost overruns, and resource bottlenecks in IT Services projects. The system leverages machine learning models, real-time data processing, and intelligent visualization to provide actionable insights.

## 🏗️ System Architecture

### Backend Stack
- **Framework**: FastAPI (Python 3.13+)
- **Database**: Supabase (PostgreSQL-based)
- **ML Libraries**: XGBoost, LightGBM, scikit-learn, Prophet
- **Data Processing**: pandas, numpy
- **Visualization**: Plotly, Seaborn, Matplotlib

### Frontend Stack
- **Framework**: Next.js 15 + React 19
- **Styling**: Tailwind CSS v4
- **State Management**: React Context / Zustand
- **Visualization**: Recharts / Plotly.js

### Data Sources
1. **Kaizen Logs**: CSV/JSON files with project improvement logs
2. **Jira API**: Real-time task and issue tracking data
3. **Internal Records**: Project metrics, resource utilization, cost data

## 📊 Core Features

### 1. Data Processing & Cleaning

**Features**:
- Extract data from multiple sources (Kaizen logs, Jira API, CSV/JSON)
- Handle missing values with configurable strategies (mean, median, mode, forward/backward fill)
- Remove duplicates and normalize dates
- Handle outliers using IQR or Z-score methods
- Clean text fields and validate data quality

**Implementation**:
```python
from app.services.data_processing import DataPipeline

pipeline = DataPipeline()
cleaned_data = pipeline.process_project_data(raw_data)
```

### 2. Feature Engineering

**Derived Features**:
- **Task Velocity**: Story points completed per sprint
- **Utilization Rate**: Actual hours / Allocated hours
- **Bug Reopen Ratio**: Reopened bugs / Total bugs
- **Cycle Time**: Time from task creation to completion
- **Schedule Variance**: Planned date - Actual date
- **Cost Variance**: Planned budget - Actual cost
- **Time-based Features**: Day of week, week of year, month, quarter
- **Lag Features**: Previous period metrics (lag 1, 2, 3)
- **Rolling Features**: Moving averages and standard deviations

**Implementation**:
```python
from app.services.data_processing import FeatureEngineer

engineer = FeatureEngineer()
data = engineer.calculate_task_velocity(data)
data = engineer.calculate_utilization_rate(data)
data = engineer.create_time_based_features(data)
```

### 3. Machine Learning Models

#### A. Delay Risk Predictor
- **Algorithm**: XGBoost / Random Forest / LightGBM
- **Type**: Regression
- **Target**: Predicted delay in days
- **Features**: Velocity, completion rate, bug rate, team size, utilization, blocked tasks

```python
from app.ml.risk_models import DelayRiskPredictor

predictor = DelayRiskPredictor('xgboost')
predictor.train(X_train, y_train)
predictions, confidence = predictor.predict_with_confidence(X_test)
```

#### B. Cost Overrun Forecaster
- **Algorithm**: XGBoost / Time-series models
- **Type**: Regression
- **Target**: Cost overrun percentage
- **Features**: Budget, team size, velocity, utilization, schedule variance

```python
from app.ml.risk_models import CostOverrunPredictor

predictor = CostOverrunPredictor('xgboost')
predictor.train(X_train, y_train)
cost_predictions = predictor.predict(X_test)
```

#### C. Resource Bottleneck Detector
- **Algorithm**: Isolation Forest
- **Type**: Anomaly Detection
- **Purpose**: Identify over/under-utilized resources
- **Features**: Utilization rate, tasks assigned/completed, completion time, bugs created

```python
from app.ml.risk_models import ResourceBottleneckDetector

detector = ResourceBottleneckDetector()
detector.fit(resource_data)
bottlenecks = detector.identify_bottlenecks(current_data)
```

#### D. Risk Score Calculator
- **Type**: Ensemble scoring system
- **Components**:
  - Delay Risk (40% weight)
  - Cost Risk (30% weight)
  - Resource Risk (20% weight)
  - Quality Risk (10% weight)
- **Output**: Overall risk score (0-100) and risk level (Low/Medium/High/Critical)

```python
from app.ml.risk_models import RiskScoreCalculator

calculator = RiskScoreCalculator()
risk_report = calculator.generate_risk_report(project_data)
```

### 4. EDA & Visualization

**Available Visualizations**:
1. **Velocity Trend Chart**: Sprint velocity over time with moving average
2. **Resource Utilization Heatmap**: Team member utilization across weeks
3. **Bug Analysis Dashboard**: Bug creation trends and reopen rates
4. **Risk Score Gauge**: Real-time risk indicator
5. **Project Timeline**: Gantt chart with project phases
6. **Correlation Heatmap**: Risk factor correlations
7. **Cost Variance Chart**: Planned vs actual costs
8. **Anomaly Scatter Plot**: Resource anomaly detection visualization

**Implementation**:
```python
from app.services.visualization import DataVisualizer

visualizer = DataVisualizer()
velocity_chart = visualizer.create_velocity_trend_chart(metrics_df)
heatmap = visualizer.create_resource_utilization_heatmap(resource_df)
```

**EDA Analytics**:
```python
from app.services.visualization import EDAAnalyzer

analyzer = EDAAnalyzer()
summary_stats = analyzer.generate_summary_statistics(df)
risk_trends = analyzer.analyze_risk_trends(metrics_df)
insights = analyzer.generate_insights(df, 'project_metrics')
```

## 🔌 API Endpoints

### Health & Info
```
GET /health                          - Health check
GET /                                - API information
```

### Projects
```
GET /api/v1/projects                 - List all projects
GET /api/v1/projects/{id}/risk       - Get risk analysis for project
```

### Predictions
```
POST /api/v1/predict                 - Generate risk predictions
  Body: { "project_id": 1 }
  
POST /api/v1/train                   - Train ML models
  Body: {
    "project_ids": [1, 2, 3],
    "model_types": ["delay", "cost", "resource"]
  }
```

### Analysis
```
GET /api/v1/analyze/{project_id}     - Perform EDA and generate insights
  Query: analysis_type=comprehensive
```

### Visualizations
```
GET /api/v1/visualizations/dashboard - Get dashboard visualizations
  Query: project_id=1
```

### Anomalies
```
GET /api/v1/anomalies                - Get detected anomalies
  Query: project_id=1&severity=high
```

### Data Upload
```
POST /api/v1/upload/kaizen          - Upload Kaizen logs
  Body: multipart/form-data (CSV/JSON file)
  
POST /api/v1/upload/jira-sync       - Sync data from Jira
  Body: { "project_key": "PROJ" }
```

### Reports
```
GET /api/v1/reports/risk-summary    - Overall risk summary
```

## 🗄️ Database Schema

### Core Tables

#### Projects
```sql
- id, name, description, status
- start_date, planned_end_date, actual_end_date
- planned_budget, actual_cost
- risk_score, risk_level
- delay_probability, cost_overrun_probability
```

#### Tasks
```sql
- id, title, description, task_type, status, priority
- estimated_hours, actual_hours, story_points
- is_bug, bug_severity, reopen_count
- is_blocked, has_dependencies
- project_id, sprint_id, assignee_id
```

#### Project Metrics (Time-series)
```sql
- project_id, metric_date
- sprint_velocity, completion_rate, bug_reopen_rate
- total_tasks, completed_tasks, blocked_tasks
- team_size, avg_utilization_rate
- days_behind_schedule, budget_variance_percent
```

#### Resource Utilization
```sql
- user_id, project_id, week_start_date
- allocated_hours, actual_hours, utilization_rate
- tasks_assigned, tasks_completed
- is_overallocated, is_underutilized
```

#### Risk Predictions
```sql
- project_id, prediction_date
- delay_risk_score, predicted_delay_days
- cost_overrun_risk_score, predicted_cost_overrun_percent
- resource_bottleneck_risk
- overall_risk_score, risk_level
```

#### Anomaly Detections
```sql
- project_id, user_id, detection_date
- anomaly_type, severity, anomaly_score
- metric_name, expected_value, actual_value
- description, recommended_action
```

## 🚀 Quick Start

### 1. Installation

```bash
# Navigate to backend
cd backend

# Install dependencies with UV
uv sync

# Or with pip
pip install -r requirements.txt
```

### 2. Environment Configuration

```bash
# Copy environment template
cp ../.env.example .env

# Edit .env with your settings
nano .env
```

### 3. Database Setup

```bash
# Run migrations
alembic upgrade head

# Or let FastAPI create tables on startup
# Tables will be created automatically when the app starts
```

### 4. Generate Sample Data

```bash
# Generate sample data for testing
python -m app.services.sample_data_generator

# Data will be created in: ./data/raw/sample/
```

### 5. Start the Server

```bash
# Development mode
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or using npm (from backend directory)
npm run dev
```

### 6. Access the API

- **API Documentation**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## 📈 Usage Examples

### Training Models

```bash
# Train models via API
curl -X POST http://localhost:8000/api/v1/train \
  -H "Content-Type: application/json" \
  -d '{
    "project_ids": [1, 2, 3, 4, 5],
    "model_types": ["delay", "cost", "resource"]
  }'
```

### Getting Predictions

```bash
# Get risk predictions for a project
curl -X POST http://localhost:8000/api/v1/predict?project_id=1

# Get project risk summary
curl http://localhost:8000/api/v1/projects/1/risk
```

### Uploading Data

```bash
# Upload Kaizen logs
curl -X POST http://localhost:8000/api/v1/upload/kaizen \
  -F "file=@kaizen_logs.csv"
```

### Python Client Example

```python
import requests

# API base URL
BASE_URL = "http://localhost:8000/api/v1"

# Get projects
response = requests.get(f"{BASE_URL}/projects")
projects = response.json()

# Generate predictions
response = requests.post(
    f"{BASE_URL}/predict",
    params={"project_id": 1}
)
predictions = response.json()

# Get visualizations
response = requests.get(
    f"{BASE_URL}/visualizations/dashboard",
    params={"project_id": 1}
)
visualizations = response.json()
```

## 🎨 Frontend Integration

### Dashboard Pages

1. **Dashboard**: Overall risk summary, key metrics, alerts
2. **Projects**: List of projects with risk indicators
3. **Resources**: Team utilization heatmap, bottleneck alerts
4. **Anomalies**: Detected anomalies with recommended actions
5. **Reports**: Detailed analytics and trend analysis
6. **Model Insights**: Feature importance, model performance
7. **Settings**: User preferences, notification settings

### Sample React Component

```tsx
'use client';

import { useEffect, useState } from 'react';

export default function RiskDashboard() {
  const [riskData, setRiskData] = useState(null);

  useEffect(() => {
    fetch('http://localhost:8000/api/v1/reports/risk-summary')
      .then(res => res.json())
      .then(data => setRiskData(data));
  }, []);

  return (
    <div className="dashboard">
      <h1>Risk Dashboard</h1>
      {riskData && (
        <div className="metrics">
          <div className="metric-card">
            <h3>Total Projects</h3>
            <p>{riskData.total_projects}</p>
          </div>
          <div className="metric-card high-risk">
            <h3>At Risk Projects</h3>
            <p>{riskData.at_risk_projects}</p>
          </div>
          <div className="metric-card">
            <h3>Average Risk Score</h3>
            <p>{riskData.avg_risk_score}</p>
          </div>
        </div>
      )}
    </div>
  );
}
```

## 🧪 Testing

### Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest app/tests/test_risk_models.py
```

### Sample Test

```python
from app.ml.risk_models import DelayRiskPredictor
import pandas as pd

def test_delay_predictor():
    predictor = DelayRiskPredictor('xgboost')
    
    # Sample data
    X_train = pd.DataFrame({
        'sprint_velocity': [30, 35, 32],
        'completion_rate': [0.8, 0.85, 0.75]
    })
    y_train = pd.Series([5, 3, 7])  # Delay in days
    
    # Train
    metrics = predictor.train(X_train, y_train)
    
    assert 'test_rmse' in metrics
    assert metrics['test_rmse'] >= 0
```

## 📊 Performance Optimization

### Model Optimization
- Use gradient boosting for better accuracy
- Hyperparameter tuning with GridSearchCV
- Feature selection to reduce overfitting
- Cross-validation for robust evaluation

### Data Processing
- Batch processing for large datasets
- Caching of processed features
- Incremental learning for online updates
- Parallel processing with multiprocessing

### API Performance
- Background tasks for long-running operations
- Response caching
- Database query optimization
- Connection pooling

## 🔒 Security

- JWT-based authentication
- API rate limiting
- Input validation with Pydantic
- SQL injection protection via SQLModel ORM
- CORS configuration
- Environment variable for secrets

## 🐛 Troubleshooting

### Common Issues

1. **Database Connection Error**
   ```bash
   # Check DATABASE_URL in .env
   # Ensure PostgreSQL is running
   ```

2. **Model Not Found**
   ```bash
   # Train models first
   curl -X POST http://localhost:8000/api/v1/train
   ```

3. **Import Errors**
   ```bash
   # Reinstall dependencies
   uv sync
   # or
   pip install -e .
   ```

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLModel Documentation](https://sqlmodel.tiangolo.com/)
- [XGBoost Documentation](https://xgboost.readthedocs.io/)
- [Plotly Python](https://plotly.com/python/)
- [Supabase Documentation](https://supabase.com/docs)

## 🤝 Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch
3. Write tests for new features
4. Ensure all tests pass
5. Submit a pull request

## 📝 License

MIT License - see LICENSE file for details

## 📧 Support

For issues and questions:
- Create an issue on GitHub
- Email: support@itanalytics.com

---

**Built with ❤️ by the IT Analytics Platform Team**
