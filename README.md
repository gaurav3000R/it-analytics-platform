# IT Analytics Platform

> An AI-powered FastAPI backend for IT project analytics, cost forecasting, resource utilization, and intelligent insights.

[![FastAPI](https://img.shields.io/badge/FastAPI-latest-009688)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.13+-blue)](https://www.python.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-latest-316192)](https://www.postgresql.org/)
[![Google Gemini](https://img.shields.io/badge/Google-Gemini_AI-4285F4)](https://ai.google.dev/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

## 📋 Overview

The **IT Analytics Platform** is a comprehensive FastAPI-based backend system designed to provide IT teams with advanced analytics, intelligent insights, and predictive capabilities. It leverages Google's Gemini AI for enhanced decision-making and includes robust monitoring and cost management features.

### Key Features

🎯 **Project Management** - Track and manage IT projects with comprehensive analytics  
📊 **Cost Forecasting** - ML-powered cost predictions and budget management  
💻 **Resource Utilization** - Monitor and optimize resource allocation across projects  
🐛 **Bug Tracking** - Advanced bug tracking with priority management  
⚠️ **Risk Management** - Identify and mitigate project risks proactively  
🤖 **AI Insights** - Google Gemini-powered intelligent recommendations and analysis  
📈 **Analytics Dashboard** - Real-time metrics and performance indicators  
🔐 **Secure API** - Production-ready with authentication and monitoring

## 🏗️ Architecture

This is a modern Python backend built with FastAPI:

```
it-analytics-platform/
├── app/
│   ├── api/                  # API route handlers
│   │   ├── projects.py      # Project management endpoints
│   │   ├── cost_forecasting.py  # Cost prediction APIs
│   │   ├── resource_utilization.py  # Resource tracking
│   │   ├── bug_tracker.py   # Bug management
│   │   ├── risks.py         # Risk assessment
│   │   ├── analytics.py     # Analytics endpoints
│   │   └── ai_insights.py   # AI-powered insights
│   ├── services/            # Business logic layer
│   ├── models/              # Database models
│   ├── middleware/          # Custom middleware (monitoring, etc.)
│   ├── utils/               # Utility functions & Gemini client
│   ├── config.py            # Application configuration
│   ├── database.py          # Database connection
│   └── main.py              # FastAPI application entry
├── tests/                   # Test suite
├── monitoring/              # Monitoring configurations
├── scripts/                 # Utility scripts
├── agentic-ai/             # AI agent implementations
└── docker-compose.yml       # Docker orchestration
```

### Technology Stack

| Component | Technology |
|-----------|-----------|
| **Framework** | FastAPI with async/await support |
| **Language** | Python 3.13+ |
| **Database** | PostgreSQL with asyncpg |
| **ORM** | SQLAlchemy with Alembic migrations |
| **AI/ML** | Google Gemini AI, scikit-learn |
| **Data Processing** | Pandas, NumPy, SciPy |
| **Visualization** | Matplotlib, Plotly |
| **Task Queue** | Celery with Redis |
| **Monitoring** | Prometheus, psutil |
| **Package Manager** | UV (ultra-fast Python package installer) |
| **Containerization** | Docker + Docker Compose |

## 🚀 Quick Start

### Prerequisites

- [Python](https://www.python.org/) (v3.13 or later)
- [UV](https://docs.astral.sh/uv/) (Fast Python package manager - **recommended**)
- [PostgreSQL](https://www.postgresql.org/) (v15 or later)
- [Redis](https://redis.io/) (for Celery task queue)
- [Docker](https://www.docker.com/) (optional - for containerized setup)

### Installation

#### Option 1: Local Development Setup

1. **Clone the repository**

```bash
git clone <repository-url>
cd it-analytics-platform
```

2. **Install UV (if not already installed)**

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

3. **Install dependencies**

```bash
uv sync
```

4. **Set up environment variables**

```bash
cp .env.example .env
# Edit .env with your configuration (database URL, API keys, etc.)
```

Required environment variables:
- `DATABASE_URL` - PostgreSQL connection string
- `GEMINI_API_KEY` - Google Gemini AI API key
- `REDIS_URL` - Redis connection string for Celery
- `SECRET_KEY` - Secret key for JWT tokens

5. **Start the development server**

```bash
make dev
# or
npm run dev
# or manually
. .venv/bin/activate && uvicorn app.main:app --reload
```

The API will be available at:
- 🔌 Backend API: [http://localhost:8000](http://localhost:8000)
- 📚 Interactive API Docs: [http://localhost:8000/docs](http://localhost:8000/docs)
- 📖 Alternative Docs: [http://localhost:8000/redoc](http://localhost:8000/redoc)

#### Option 2: Docker Setup

1. **Start all services with Docker Compose**

```bash
docker-compose up --build
```

This starts:
- FastAPI backend
- PostgreSQL database
- Redis cache
- All necessary services

2. **Access the application**

- API: [http://localhost:8000](http://localhost:8000)
- Docs: [http://localhost:8000/docs](http://localhost:8000/docs)

## 📚 API Endpoints

### Project Management
- `GET /api/projects` - List all projects
- `POST /api/projects` - Create new project
- `GET /api/projects/{id}` - Get project details
- `PUT /api/projects/{id}` - Update project
- `DELETE /api/projects/{id}` - Delete project

### Cost Forecasting
- `POST /api/cost-forecasting/forecast` - Generate cost forecast
- `GET /api/cost-forecasting/trends` - Get cost trends
- `POST /api/cost-forecasting/budget-analysis` - Analyze budget vs actual

### Resource Utilization
- `GET /api/resource-utilization/overview` - Resource usage overview
- `GET /api/resource-utilization/by-project/{id}` - Project-specific resources
- `POST /api/resource-utilization/optimize` - Get optimization recommendations

### Bug Tracking
- `GET /api/bugs` - List bugs
- `POST /api/bugs` - Report new bug
- `PUT /api/bugs/{id}` - Update bug status
- `GET /api/bugs/analytics` - Bug analytics and trends

### Risk Management
- `GET /api/risks` - List project risks
- `POST /api/risks/assess` - Assess project risks
- `PUT /api/risks/{id}` - Update risk status

### Analytics
- `GET /api/analytics/dashboard` - Main analytics dashboard
- `GET /api/analytics/metrics` - Key performance metrics
- `POST /api/analytics/custom-report` - Generate custom report

### AI Insights
- `POST /api/ai-insights/analyze` - Get AI-powered project analysis
- `POST /api/ai-insights/recommendations` - Get recommendations
- `POST /api/ai-insights/predict` - ML-based predictions

## 📚 Documentation

Comprehensive documentation files are available in the root directory:

- **[📖 Getting Started](./GETTING_STARTED.md)** - Quick start guide
- **[🎨 Frontend Documentation](./FRONTEND_DOCUMENTATION.md)** - Frontend development guide
- **[📊 Project Summary](./PROJECT_SUMMARY.md)** - Complete project overview
- **[✅ Project Completion Report](./PROJECT_COMPLETION_REPORT.md)** - Implementation status
- **[🎨 Theme Analysis](./THEME_ANALYSIS.md)** - UI/UX theme documentation

## 🛠️ Development

### Available Scripts

#### Using Makefile

```bash
make dev          # Start development server
make test         # Run tests
make lint         # Run linting
make format       # Format code with black
make clean        # Clean up cache and build files
```

#### Using npm scripts

```bash
npm run dev       # Start development server with auto-reload
npm run test      # Run pytest tests
npm run clean     # Remove virtual environment
```

#### Manual commands

```bash
# Activate virtual environment
. .venv/bin/activate

# Start server
uvicorn app.main:app --reload

# Run tests
pytest

# Run tests with coverage
pytest --cov=app tests/

# Format code
black app/
isort app/

# Lint code
flake8 app/
```

### Project Structure

```
app/
├── api/              # API route handlers
│   ├── __init__.py
│   ├── projects.py
│   ├── cost_forecasting.py
│   ├── resource_utilization.py
│   ├── bug_tracker.py
│   ├── risks.py
│   ├── analytics.py
│   └── ai_insights.py
├── services/         # Business logic
├── models/           # Database models
├── middleware/       # Custom middleware
│   ├── monitoring.py
│   └── __init__.py
├── utils/           # Utilities
│   ├── helpers.py
│   └── gemini_client.py
├── config.py        # Configuration
├── database.py      # DB connection
└── main.py          # App entry point
```

### Database Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1

# View migration history
alembic history
```

## 🐳 Docker Support

### Using Docker Compose

Run the entire stack with Docker Compose:

```bash
# Start all services
docker-compose up --build

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

### Docker Services

The `docker-compose.yml` includes:
- **FastAPI Backend** - Main application server
- **PostgreSQL** - Database server
- **Redis** - Cache and message broker
- **Celery Worker** - Background task processor (if configured)

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app tests/

# Run specific test file
pytest tests/test_api.py

# Run with verbose output
pytest -v

# Run and watch for changes
pytest-watch
```

### Writing Tests

Tests are located in the `tests/` directory:

```python
# tests/test_api.py
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
```

## 📊 Features Overview

### Cost Forecasting
- **ML-powered predictions** using historical data and scikit-learn models
- **Budget tracking** with variance analysis
- **Cost trend visualization** with Plotly and Matplotlib
- **Automated alerts** for budget overruns

### Resource Utilization
- **Real-time monitoring** of team and infrastructure resources
- **Capacity planning** with optimization algorithms
- **Resource allocation recommendations** using AI
- **Utilization metrics** and efficiency scores

### Bug Tracking & Management
- **Priority-based bug classification**
- **Automated severity assessment** using AI
- **Bug trend analysis** and prediction
- **Integration-ready** for external bug tracking systems

### Risk Management
- **Automated risk identification** from project data
- **Risk scoring and prioritization**
- **Mitigation strategy recommendations** powered by Gemini AI
- **Real-time risk monitoring**

### AI-Powered Insights
- **Natural language queries** via Gemini AI
- **Predictive analytics** for project outcomes
- **Intelligent recommendations** for resource allocation
- **Pattern recognition** in project data

### Analytics & Reporting
- **Customizable dashboards** with key metrics
- **Export capabilities** for reports
- **Real-time data updates**
- **Historical trend analysis**

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the root directory:

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/it_analytics

# Google Gemini AI
GEMINI_API_KEY=your_gemini_api_key_here

# Redis
REDIS_URL=redis://localhost:6379/0

# Application
SECRET_KEY=your_secret_key_here
ENVIRONMENT=development
DEBUG=True
LOG_LEVEL=INFO

# API Settings
API_V1_PREFIX=/api
CORS_ORIGINS=["http://localhost:3000", "http://localhost:8000"]

# Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

### Configuration Files

- **`app/config.py`** - Application configuration settings
- **`pyproject.toml`** - Python project dependencies and metadata
- **`docker-compose.yml`** - Docker service definitions
- **`makefile`** - Development automation commands

## 🔐 Security

- **Environment-based configuration** - No hardcoded secrets
- **Input validation** using Pydantic models
- **SQL injection protection** via SQLAlchemy ORM
- **CORS configuration** for cross-origin requests
- **Rate limiting** (configurable)
- **API authentication** ready for JWT implementation

## 🚀 Deployment

### Production Deployment

1. **Build the Docker image**

```bash
docker build -t it-analytics-platform:latest .
```

2. **Set production environment variables**

```bash
export DATABASE_URL=postgresql://...
export GEMINI_API_KEY=...
export REDIS_URL=...
```

3. **Run the container**

```bash
docker run -p 8000:8000 --env-file .env.production it-analytics-platform:latest
```

### Cloud Deployment Options

- **AWS**: Deploy using ECS, Elastic Beanstalk, or EC2
- **Google Cloud**: Use Cloud Run or Compute Engine
- **Azure**: Deploy with App Service or Container Instances
- **Heroku**: Simple deployment with Heroku Postgres addon

### Health Checks

The API includes health check endpoints:

```bash
# Basic health check
curl http://localhost:8000/health

# Detailed system info
curl http://localhost:8000/api/analytics/system-health
```

## 📈 Monitoring & Observability

### Prometheus Metrics

The application exposes Prometheus metrics at `/metrics`:

- Request count and latency
- Database connection pool stats
- AI API call metrics
- Custom business metrics

### Logging

Structured logging is implemented throughout the application:

```python
import logging
logger = logging.getLogger(__name__)
logger.info("Operation completed", extra={"project_id": 123})
```

### Performance Monitoring

- **psutil** for system resource monitoring
- **Custom middleware** for request timing
- **Database query optimization** with SQLAlchemy logging

## 🤝 Contributing

We welcome contributions! Here's how to get started:

1. **Fork the repository**
2. **Create a feature branch** (`git checkout -b feature/AmazingFeature`)
3. **Make your changes**
4. **Run tests** (`pytest`)
5. **Format code** (`black . && isort .`)
6. **Commit changes** (`git commit -m 'Add AmazingFeature'`)
7. **Push to branch** (`git push origin feature/AmazingFeature`)
8. **Open a Pull Request**

### Coding Standards

- Follow **PEP 8** style guide
- Use **type hints** for function parameters and returns
- Write **docstrings** for all public functions
- Maintain **test coverage** above 80%
- Use **async/await** for I/O operations

### Commit Message Convention

```
type(scope): subject

body

footer
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

## 🛣️ Roadmap

### Current Phase: Core Features ✅

- ✅ FastAPI backend architecture
- ✅ Project management APIs
- ✅ Cost forecasting with ML
- ✅ Resource utilization tracking
- ✅ Bug tracking system
- ✅ Risk management
- ✅ Google Gemini AI integration
- ✅ Analytics endpoints
- ✅ Database models and connections
- ✅ Docker containerization
- ✅ Monitoring and logging

### Phase 2: Enhancement 🔄

- 🔄 User authentication & authorization (JWT)
- 🔄 Role-based access control (RBAC)
- 🔄 Advanced ML models for predictions
- 🔄 Real-time notifications
- 🔄 WebSocket support for live updates
- 🔄 Enhanced data visualization APIs
- 🔄 Audit logging
- 🔄 API rate limiting

### Phase 3: Integration 📋

- 📋 Frontend application (React/Next.js)
- 📋 Third-party integrations (Jira, GitHub, Slack)
- 📋 CI/CD pipeline
- 📋 Automated testing suite
- 📋 API versioning
- 📋 GraphQL support
- 📋 Multi-tenancy support

### Phase 4: Advanced Features 🎯

- 🎯 Advanced AI agents for autonomous analysis
- 🎯 Natural language interface
- 🎯 Predictive maintenance for infrastructure
- 🎯 Custom plugin system
- 🎯 Mobile app support
- 🎯 Advanced reporting engine
- 🎯 Data export/import capabilities

## 🐛 Troubleshooting

### Common Issues

**Database Connection Error**
```bash
# Check PostgreSQL is running
pg_isready -h localhost -p 5432

# Verify DATABASE_URL in .env
echo $DATABASE_URL
```

**Gemini AI API Error**
```bash
# Verify API key is set
echo $GEMINI_API_KEY

# Check API quota and limits
```

**Import Errors**
```bash
# Reinstall dependencies
uv sync --force

# Activate virtual environment
. .venv/bin/activate
```

**Port Already in Use**
```bash
# Find process using port 8000
lsof -i :8000

# Kill the process
kill -9 <PID>
```

## 📚 Additional Resources

### Learning Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Google Gemini AI](https://ai.google.dev/)
- [SQLAlchemy Guide](https://docs.sqlalchemy.org/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [UV Package Manager](https://docs.astral.sh/uv/)

### Related Projects

- [FastAPI Best Practices](https://github.com/zhanymkanov/fastapi-best-practices)
- [Awesome FastAPI](https://github.com/mjhea0/awesome-fastapi)
- [Python Type Checking](https://mypy.readthedocs.io/)

## 📞 Support & Contact

- 📖 **Documentation**: Check this README and project docs
- 🐛 **Bug Reports**: [Create an issue](https://github.com/your-org/it-analytics-platform/issues)
- 💡 **Feature Requests**: [Open a discussion](https://github.com/your-org/it-analytics-platform/discussions)
- 💬 **Questions**: Use GitHub Discussions or project chat

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

Built with amazing open-source technologies:

- **[FastAPI](https://fastapi.tiangolo.com/)** - Modern, fast web framework for Python
- **[Google Gemini](https://ai.google.dev/)** - Advanced AI and machine learning
- **[PostgreSQL](https://www.postgresql.org/)** - Powerful open-source database
- **[SQLAlchemy](https://www.sqlalchemy.org/)** - Python SQL toolkit and ORM
- **[Pydantic](https://docs.pydantic.dev/)** - Data validation using Python type hints
- **[UV](https://docs.astral.sh/uv/)** - Lightning-fast Python package installer
- **[Celery](https://docs.celeryq.dev/)** - Distributed task queue
- **[Redis](https://redis.io/)** - In-memory data structure store
- **[scikit-learn](https://scikit-learn.org/)** - Machine learning in Python
- **[Pandas](https://pandas.pydata.org/)** - Data analysis and manipulation tool
- **[Plotly](https://plotly.com/)** - Interactive graphing library

## 📊 Project Stats

- **Language**: Python 3.13+
- **Framework**: FastAPI
- **Database**: PostgreSQL with asyncpg
- **AI/ML**: Google Gemini, scikit-learn
- **Architecture**: Async/await, RESTful API
- **Code Style**: Black, isort, flake8
- **Testing**: pytest with coverage

---

**Made with ❤️ by Team Innovatrix**

*Building intelligent solutions for IT project management*
