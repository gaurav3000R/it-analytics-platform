# it-analytics-platform-backend# IT Analytics Platform - Backend

backend/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── handler.py
│   ├── config.py
│   ├── database.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── project.py
│   │   ├── employee.py
│   │   └── risk.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── risk_prediction.py
│   │   ├── anomaly_detection.py
│   │   └── data_processor.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── projects.py
│   │   ├── risks.py
│   │   └── analytics.py
│   └── utils/
│       ├── __init__.py
│       └── helpers.py
├── tests/
├── data/
│   └── sample_data/
├── requirements.txt
├── Dockerfile
└── README.md


An AI-powered early warning system for IT services project management, featuring risk prediction and anomaly detection capabilities.

## 🚀 Features

### Core Features Implemented
1. **Risk Prediction Dashboard** - Real-time risk scoring for projects based on:
   - Task completion trends
   - Budget utilization
   - Team productivity metrics
   - Sprint velocity analysis

2. **Anomaly Detection** - Identifies unusual patterns in:
   - Employee daily logs (hours, productivity)
   - Missing log entries
   - Issue reporting spikes
   - Productivity anomalies

### Planned Features
- Cost overrun forecasting
- Resource utilization alerts
- Bug tracker insights
- Automated reporting

## 🏗️ Architecture

```
Backend/
├── FastAPI Application (handler.py, main.py)
├── Database Layer (SQLAlchemy models)
├── ML Services (Risk Prediction, Anomaly Detection)
├── API Endpoints (/projects, /risks, /analytics)
└── Data Processing & Sample Data Generation
```

## 🛠️ Tech Stack

- **Framework**: FastAPI
- **Database**: SQLAlchemy (SQLite/PostgreSQL)
- **ML Libraries**: scikit-learn, pandas, numpy
- **API Documentation**: Automatic OpenAPI/Swagger

## 📦 Installation

### Prerequisites
- Python 3.11+
- pip or uv

### Quick Start

1. **Clone and setup**:
```bash
cd backend
pip install -r requirements.txt
```

2. **Initialize with sample data**:
```bash
python app/main.py --setup-data
```

3. **Train ML models**:
```bash
python app/main.py --train-models
```

4. **Run the server**:
```bash
python app/main.py --run-server
# or
uvicorn app.handler:app --reload --port 8000
```

### Docker Setup
```bash
docker build -t it-analytics-backend .
docker run -p 8000:8000 it-analytics-backend
```

## 🔌 API Endpoints

### Projects
- `POST /api/v1/projects/generate-sample-data` - Generate demo data
- `GET /api/v1/projects/` - List all projects
- `GET /api/v1/projects/{id}` - Get project details
- `GET /api/v1/projects/{id}/dashboard` - Get project dashboard data

### Risk Management
- `POST /api/v1/risks/train-model` - Train risk prediction model
- `GET /api/v1/risks/predict/{project_id}` - Get risk prediction for project
- `GET /api/v1/risks/dashboard` - Get risk dashboard
- `POST /api/v1/risks/detect-anomalies` - Run anomaly detection
- `GET /api/v1/risks/anomalies/{project_id}` - Get project anomalies

### Analytics
- `GET /api/v1/analytics/overview` - Overall analytics overview
- `GET /api/v1/analytics/trends` - Trend data for charts
- `GET /api/v1/analytics/team-performance` - Team performance metrics

## 🎯 Usage Examples

### 1. Setup Demo Environment
```bash
# Generate sample data (10 projects, 20 employees)
curl -X POST "http://localhost:8000/api/v1/projects/generate-sample-data?num_projects=10&num_employees=20"

# Train ML models
curl -X POST "http://localhost:8000/api/v1/risks/train-model"
```

### 2. Get Risk Predictions
```bash
# Get risk prediction for project 1
curl "http://localhost:8000/api/v1/risks/predict/1"

# Get overall risk dashboard
curl "http://localhost:8000/api/v1/risks/dashboard"
```

### 3. Detect Anomalies
```bash
# Run anomaly detection for last 30 days
curl -X POST "http://localhost:8000/api/v1/risks/detect-anomalies?days_back=30"

# Get anomalies for specific project
curl "http://localhost:8000/api/v1/risks/anomalies/1?days_back=7"
```

## 🧪 Sample Data Structure

The system generates realistic sample data including:
- **Projects**: With budgets, timelines, team sizes, complexity scores
- **Employees**: Different roles (developer, tester, designer, manager)
- **Daily Logs**: Hours logged, task completion, issues reported
- **Sprints**: Velocity tracking, burndown data
- **Anomalies**: Intentionally injected unusual patterns

## 🤖 ML Models

### Risk Prediction Model
- **Algorithm**: Gradient Boosting Regressor
- **Features**: 
  - Hours logged trends
  - Completion rates
  - Budget utilization
  - Team productivity metrics
  - Sprint velocity trends
- **Output**: Risk score (0-100) with component breakdowns

### Anomaly Detection
- **Algorithm**: Isolation Forest + Statistical Analysis
- **Detects**:
  - Unusual working hours (over/under work)
  - Missing log entries
  - Productivity anomalies
  - Issue reporting spikes

## 🔧 Configuration

Environment variables (`.env`):
```env
DATABASE_URL=sqlite:///./it_analytics.db
SECRET_KEY=your-secret-key-here
LOG_LEVEL=INFO
REDIS_URL=redis://localhost:6379
```

## 📊 API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🧩 Extending the System

### Adding New Features
1. **Create new service** in `app/services/`
2. **Add API endpoints** in `app/api/`
3. **Update models** if needed in `app/models/`
4. **Include router** in `app/handler.py`

### Example: Adding Cost Overrun Forecasting
```python
# app/services/cost_forecasting.py
class CostForecastingService:
    def predict_cost_overrun(self, project_id: int):
        # Implementation here
        pass

# app/api/forecasting.py  
@router.get("/cost-overrun/{project_id}")
async def predict_cost_overrun(project_id: int):
    # API endpoint here
    pass
```

## 🐛 Troubleshooting

### Common Issues

1. **Model training fails**:
   - Ensure sample data is generated first
   - Check database connection

2. **Anomaly detection returns empty**:
   - Verify there's sufficient daily log data (>10 entries)
   - Check date ranges

3. **Database errors**:
   - Delete `it_analytics.db` and regenerate
   - Check SQLAlchemy logs

### Logs
```bash
# Check application logs
tail -f logs/app.log

# Database debug mode
export LOG_LEVEL=DEBUG
```

## 📈 Performance

- **Risk Prediction**: ~50ms per project
- **Anomaly Detection**: ~2s for 30 days of data
- **Dashboard Queries**: ~100ms average
- **Memory Usage**: ~200MB with sample data

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request



# Backend AI Agent Prompt – IT Analytics Platform

## 🎯 Goal

Create a **backend application** using the **latest FastAPI** (check latest docs) + **Postgres** + **SQLAlchemy/SQLModel**, with **ML model integration** for predictions. The backend must be production-ready, modular, and easy to extend.

This backend is part of a **monorepo** that also includes a frontend and dbt project. It should handle **tasks, users, analytics, and predictions**.

We want to use **UV (Python package manager)** instead of pip/conda to manage dependencies.

---

## 📦 Tech Stack

- **Backend Framework**: FastAPI (latest stable)
- **DB**: PostgreSQL (latest stable)
- **ORM**: SQLModel or SQLAlchemy 2.x
- **Migrations**: Alembic
- **ML**: scikit-learn / PyTorch / XGBoost (light models first)
- **Analytics Layer**: dbt (integrated with Postgres)
- **Package Manager**: UV (latest)
- **Containerization**: Docker + Docker Compose
- **Testing**: pytest + coverage
- **Auth**: JWT-based authentication
- **CI/CD**: GitHub Actions (lint, test, deploy)

---

## 📂 Folder Structure

```
backend/
├── app/
│   ├── api/               # FastAPI routers
│   ├── core/              # config, security
│   ├── db/                # models, session, migrations
│   ├── services/          # business logic
│   ├── ml/                # ML models + serving
│   ├── tests/             # pytest unit + integration tests
│   └── main.py            # entrypoint
├── alembic/               # migrations
├── pyproject.toml         # UV dependency file
├── uv.lock                # UV lock file
├── Dockerfile
├── docker-compose.yml
└── README.md
```

---
## 🔑 Core Features

### 1. **User Management**
- Register, login, update user.
- Assign skills to users.
- JWT authentication.

### 2. **Task Management**
- Create task, assign to user.
- Track status (pending, in-progress, completed).
- Store estimated vs actual time.

### 3. **Analytics (via dbt + Postgres)**
- Project-wise reports.
- User performance (avg completion time, bug rate).
- Prediction readiness tables.

### 4. **Predictions (ML models)**
- **Upcoming Task Prediction** → Which developer should take it.
- **Bug Probability** → Estimate if a task may generate bugs.
- **Time Estimation** → Predict how much time a task will take.
- **Developer Ranking** → List developers by skill + history.

### 5. **API Endpoints**
- `/users/` → CRUD users
- `/tasks/` → CRUD tasks
- `/analytics/` → Reports & KPIs
- `/predictions/` → ML results (task assignment, bug probability, ETA)

---

## 🚀 Getting Started

To get the application running, follow these steps:

1. **Build and run the containers:**

   ```bash
   docker-compose up --build
   ```

2. **Access the API:**

   The API will be available at [http://localhost:8000](http://localhost:8000).

---

## 📖 References (latest docs to use)

* FastAPI → [https://fastapi.tiangolo.com/](https://fastapi.tiangolo.com/)
* SQLModel → [https://sqlmodel.tiangolo.com/](https://sqlmodel.tiangolo.com/)
* Alembic → [https://alembic.sqlalchemy.org/](https://alembic.sqlalchemy.org/)
* dbt → [https://docs.getdbt.com/](https://docs.getdbt.com/)
* UV → [https://docs.astral.sh/uv/](https://docs.astral.sh/uv/)
* Docker → [https://docs.docker.com/](https://docs.docker.com/)

---

## ✅ Acceptance Criteria

* Code should follow  **PEP8 + typing** .
* Every endpoint must have  **tests** .
* DB migrations should work smoothly.
* ML endpoints return  **valid JSON responses** .
* System runs with one command: `docker-compose up --build`