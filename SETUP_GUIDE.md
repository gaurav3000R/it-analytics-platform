# 🚀 AI-Powered Operational Risk Early Warning System - Quick Start Guide

## 📋 Overview

You have successfully set up an **AI-powered Operational Risk Early Warning System** for IT Services projects. This system predicts project delivery delays, cost overruns, and resource bottlenecks using:

- **Machine Learning**: XGBoost, Random Forest, Isolation Forest
- **Data Processing**: Automated ETL from Kaizen logs and Jira API
- **Real-time Analytics**: EDA, visualization, and anomaly detection
- **Modern Stack**: FastAPI + Next.js + Supabase

## 🏗️ What's Been Built

### Backend Components (/backend/app/)

1. **Database Models** (`db/models.py`)
   - Projects, Tasks, Users, Sprints
   - Project Metrics (time-series)
   - Resource Utilization
   - Risk Predictions
   - Anomaly Detections
   - Kaizen Logs, Jira Sync

2. **Data Processing** (`services/data_processing.py`)
   - Data extraction from CSV, JSON, Jira API
   - Data cleaning (missing values, outliers, duplicates)
   - Feature engineering (velocity, utilization, cycle time, etc.)
   - Complete ETL pipeline

3. **ML Models** (`ml/risk_models.py`)
   - **DelayRiskPredictor**: Predicts project delays (XGBoost/RF)
   - **CostOverrunPredictor**: Forecasts cost overruns
   - **ResourceBottleneckDetector**: Anomaly detection for resources
   - **RiskScoreCalculator**: Comprehensive risk scoring

4. **Visualization** (`services/visualization.py`)
   - Velocity trends, resource heatmaps
   - Bug analysis, correlation matrices
   - Risk gauges, project timelines
   - EDA and insight generation

5. **API Routes** (`api/risk_routes.py`)
   - `/api/v1/projects` - Project management
   - `/api/v1/predict` - Risk predictions
   - `/api/v1/train` - Model training
   - `/api/v1/analyze` - EDA analysis
   - `/api/v1/visualizations/dashboard` - Charts
   - `/api/v1/anomalies` - Anomaly alerts
   - `/api/v1/upload/*` - Data upload endpoints

### Frontend Component (/frontend/src/app/dashboard/)

- **Risk Dashboard**: Real-time risk monitoring
- Features: Risk cards, project table, status indicators
- Responsive design with Tailwind CSS
- API integration ready

### Utilities

- **Sample Data Generator** (`services/sample_data_generator.py`)
- Generates realistic project, task, and resource data
- Perfect for testing and development

## 🚀 Quick Start (5 Minutes)

### Step 1: Install Backend Dependencies

```bash
cd backend
uv sync
# or: pip install -e .
```

### Step 2: Configure Environment

```bash
# Copy the environment template
cp ../.env.example .env

# Edit the .env file (optional for development)
nano .env
```

**Minimum configuration for development:**
```env
DATABASE_URL="sqlite:///./it_analytics.db"  # Or use PostgreSQL
DEBUG=True
```

### Step 3: Generate Sample Data

```bash
# Generate test data
python -m app.services.sample_data_generator
```

This creates sample data in `./data/raw/sample/`:
- projects.csv
- sprints.csv
- tasks.csv
- project_metrics.csv
- resource_utilization.csv
- kaizen_logs.csv

### Step 4: Start Backend Server

```bash
# From backend directory
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

✅ Backend running at: **http://localhost:8000**
📚 API Docs at: **http://localhost:8000/docs**

### Step 5: Start Frontend (Optional)

```bash
# In a new terminal, from frontend directory
cd ../frontend
npm install
npm run dev
```

✅ Frontend running at: **http://localhost:3000**
📊 Dashboard at: **http://localhost:3000/dashboard**

## 📊 Using the System

### 1. Access API Documentation

Open your browser to http://localhost:8000/docs

You'll see interactive API documentation (Swagger UI) with all endpoints.

### 2. Test the API

#### Get Health Status
```bash
curl http://localhost:8000/health
```

#### Get Projects
```bash
curl http://localhost:8000/api/v1/projects
```

#### Get Risk Summary
```bash
curl http://localhost:8000/api/v1/reports/risk-summary
```

### 3. Train ML Models

Before making predictions, train the models with historical data:

```bash
curl -X POST http://localhost:8000/api/v1/train \
  -H "Content-Type: application/json" \
  -d '{
    "project_ids": [1, 2, 3],
    "model_types": ["delay", "cost", "resource"]
  }'
```

### 4. Generate Predictions

```bash
curl -X POST "http://localhost:8000/api/v1/predict?project_id=1"
```

### 5. Get Project Analysis

```bash
curl "http://localhost:8000/api/v1/analyze/1?analysis_type=comprehensive"
```

### 6. Upload Kaizen Logs

```bash
curl -X POST http://localhost:8000/api/v1/upload/kaizen \
  -F "file=@data/raw/sample/kaizen_logs.csv"
```

## 🔧 Development Workflow

### Loading Data into Database

Create a Python script to load sample data:

```python
# load_sample_data.py
import pandas as pd
from sqlmodel import Session, create_engine
from app.db.models import Project, ProjectMetrics, ResourceUtilization
from app.core.config import settings

# Create engine
engine = create_engine(settings.DATABASE_URL)

# Load projects
projects_df = pd.read_csv('./data/raw/sample/projects.csv')

with Session(engine) as session:
    for _, row in projects_df.iterrows():
        project = Project(
            name=row['project_name'],
            status=row['status'],
            start_date=pd.to_datetime(row['start_date']),
            planned_end_date=pd.to_datetime(row['planned_end_date']),
            planned_budget=row['planned_budget'],
            actual_cost=row['actual_cost']
        )
        session.add(project)
    session.commit()

print("Data loaded successfully!")
```

Run it:
```bash
python load_sample_data.py
```

### Training Models Programmatically

```python
from app.ml.risk_models import MLPipeline
import pandas as pd

# Initialize pipeline
pipeline = MLPipeline(model_path="./models")

# Load training data
project_data = pd.read_csv('./data/raw/sample/project_metrics.csv')
resource_data = pd.read_csv('./data/raw/sample/resource_utilization.csv')

# Train all models
results = pipeline.train_all_models(project_data, resource_data)
print("Training Results:", results)
```

### Making Predictions

```python
# Load models and predict
pipeline.load_all_models()

# Prepare current project data
current_data = pd.DataFrame({...})  # Your current metrics

# Get predictions
predictions = pipeline.predict_project_risks(current_data, resource_data)
print("Risk Predictions:", predictions)
```

## 📁 Project Structure

```
it-analytics-platform/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── risk_routes.py         # API endpoints
│   │   ├── core/
│   │   │   └── config.py              # Configuration
│   │   ├── db/
│   │   │   ├── models.py              # Database models
│   │   │   └── database.py            # DB connection
│   │   ├── ml/
│   │   │   └── risk_models.py         # ML models
│   │   ├── services/
│   │   │   ├── data_processing.py     # ETL pipeline
│   │   │   ├── visualization.py       # Charts & EDA
│   │   │   └── sample_data_generator.py
│   │   └── main.py                    # FastAPI app
│   ├── models/                        # Trained models (generated)
│   └── pyproject.toml                 # Dependencies
│
├── frontend/
│   └── src/app/dashboard/
│       └── page.tsx                   # Risk dashboard
│
├── data/
│   ├── raw/
│   │   └── sample/                    # Generated sample data
│   └── processed/                     # Processed data
│
├── docs/
│   └── RISK_EARLY_WARNING_SYSTEM.md  # Full documentation
│
└── .env.example                       # Environment template
```

## 🎯 Key Features Implemented

### ✅ Data Processing
- [x] Extract from CSV/JSON/Jira API
- [x] Handle missing values
- [x] Remove outliers and duplicates
- [x] Feature engineering (20+ derived features)
- [x] Time-series features

### ✅ Machine Learning
- [x] Delay risk prediction (XGBoost)
- [x] Cost overrun forecasting
- [x] Resource bottleneck detection (Isolation Forest)
- [x] Risk score calculation
- [x] Model training and persistence

### ✅ Visualization & EDA
- [x] Velocity trend charts
- [x] Resource utilization heatmap
- [x] Bug analysis dashboard
- [x] Risk gauges
- [x] Correlation analysis
- [x] Automated insights generation

### ✅ API Endpoints
- [x] Project management
- [x] Risk predictions
- [x] Model training
- [x] EDA analysis
- [x] Data upload
- [x] Anomaly detection

### ✅ Frontend
- [x] Risk dashboard page
- [x] Real-time data display
- [x] Responsive design
- [x] Error handling

## 🔍 Testing the System

### 1. Test API Health
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "application": "IT Analytics Platform - Risk Early Warning System",
  "version": "1.0.0"
}
```

### 2. Check API Documentation
Visit http://localhost:8000/docs

### 3. View Dashboard
Visit http://localhost:3000/dashboard

## 🐛 Troubleshooting

### Backend won't start
```bash
# Check if port 8000 is in use
lsof -i :8000

# Install dependencies again
cd backend
uv sync --force
```

### Database errors
```bash
# For SQLite (default)
# Delete the database and restart
rm it_analytics.db

# For PostgreSQL
# Check connection string in .env
```

### Import errors
```bash
# Make sure you're in the backend directory
cd backend

# Run with module syntax
python -m app.main
```

### Frontend can't connect to backend
```bash
# Check CORS settings in backend/app/main.py
# Verify API_BASE_URL in frontend (defaults to localhost:8000)
```

## 📚 Next Steps

### 1. Connect to Real Data Sources

**Supabase Setup:**
```env
# Update .env
SUPABASE_URL="https://your-project.supabase.co"
SUPABASE_KEY="your-anon-key"
DATABASE_URL="postgresql://postgres:[PASSWORD]@db.[PROJECT].supabase.co:5432/postgres"
```

**Jira Integration:**
```env
JIRA_URL="https://your-domain.atlassian.net"
JIRA_USERNAME="your-email@example.com"
JIRA_API_TOKEN="your-api-token"
```

### 2. Add Authentication

Implement JWT authentication for API endpoints (structure is already in place).

### 3. Deploy

- **Backend**: Deploy to Railway, Render, or AWS
- **Frontend**: Deploy to Vercel or Netlify
- **Database**: Use Supabase or managed PostgreSQL

### 4. Enhance Frontend

Add more pages:
- Individual project detail pages
- Resource management dashboard
- Anomaly alerts page
- Model performance metrics
- Settings and configuration

### 5. Add Real-time Features

- WebSocket connections for live updates
- Real-time notifications
- Auto-refresh dashboards

## 📖 Documentation

- **Full Documentation**: `/docs/RISK_EARLY_WARNING_SYSTEM.md`
- **API Reference**: http://localhost:8000/docs
- **Architecture**: `/docs/ARCHITECTURE.md`

## 💡 Tips

1. **Start Small**: Use sample data first, then gradually integrate real sources
2. **Train Regularly**: Retrain models weekly with new data
3. **Monitor Performance**: Track model accuracy and update as needed
4. **Customize Features**: Add domain-specific features to improve predictions
5. **Set Thresholds**: Adjust risk thresholds based on your organization's tolerance

## 🤝 Support

If you encounter issues:
1. Check the logs: Backend outputs detailed error messages
2. Verify environment variables in `.env`
3. Ensure all dependencies are installed
4. Check the troubleshooting section above

## 🎉 Success!

Your AI-powered Risk Early Warning System is now operational! The system provides:

- **Proactive Risk Detection**: Identify issues before they become critical
- **Data-Driven Insights**: Make informed decisions based on ML predictions
- **Comprehensive Analytics**: Understand project health at a glance
- **Automated Monitoring**: Continuous anomaly detection
- **Actionable Recommendations**: Get specific steps to mitigate risks

Happy monitoring! 🚀
