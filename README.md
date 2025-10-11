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

This is a **Turborepo monorepo** containing a FastAPI backend and Next.js frontend:

```
it-analytics-platform/
├── backend/                 # Python FastAPI backend
│   ├── app/
│   │   ├── api/            # API route handlers
│   │   │   ├── projects.py
│   │   │   ├── cost_forecasting.py
│   │   │   ├── resource_utilization.py
│   │   │   ├── bug_tracker.py
│   │   │   ├── risks.py
│   │   │   ├── analytics.py
│   │   │   └── ai_insights.py
│   │   ├── services/       # Business logic layer
│   │   ├── models/         # Database models
│   │   ├── middleware/     # Custom middleware
│   │   ├── utils/          # Utilities & Gemini client
│   │   ├── config.py       # Configuration
│   │   ├── database.py     # DB connection
│   │   └── main.py         # FastAPI app entry
│   ├── tests/              # Backend tests
│   ├── monitoring/         # Monitoring configs
│   ├── scripts/            # Utility scripts
│   ├── agentic-ai/         # AI agent implementations
│   ├── pyproject.toml      # Python dependencies (UV)
│   ├── package.json        # Backend npm scripts
│   └── docker-compose.yml  # Backend services
│
├── frontend/               # Next.js 15 + React 19 frontend
│   ├── src/
│   │   ├── app/           # Next.js app directory
│   │   ├── components/    # React components
│   │   ├── lib/           # Utilities & helpers
│   │   └── styles/        # Global styles
│   ├── public/            # Static assets
│   ├── package.json       # Frontend dependencies
│   └── next.config.ts     # Next.js config
│
├── dbt_project/           # dbt analytics transformations (optional)
├── data/                  # Data storage
├── docs/                  # Additional documentation
├── infra/                 # Infrastructure configs
│
├── package.json           # Monorepo root (Turborepo)
├── turbo.json             # Turborepo configuration
└── dev-start.sh          # Convenient dev startup script
```

### Technology Stack

| Layer | Technology |
|-------|-----------|
| **Monorepo** | Turborepo for build orchestration |
| **Frontend** | Next.js 15, React 19, TypeScript 5 |
| **Styling** | Tailwind CSS v4, Radix UI components |
| **State Management** | Zustand, TanStack Query |
| **Backend** | FastAPI with async/await support |
| **Language** | Python 3.13+ |
| **Database** | PostgreSQL with asyncpg, SQLite for dev |
| **ORM** | SQLAlchemy, SQLModel, Alembic migrations |
| **AI/ML** | Google Gemini AI, scikit-learn |
| **Data Processing** | Pandas, NumPy, SciPy |
| **Visualization** | Matplotlib, Plotly, Recharts |
| **Task Queue** | Celery with Redis |
| **Monitoring** | Prometheus, psutil |
| **Package Managers** | npm (workspace), UV (Python) |
| **Containerization** | Docker + Docker Compose |

## 🚀 Quick Start

### Prerequisites

- **[Node.js](https://nodejs.org/)** v20+ and npm
- **[Python](https://www.python.org/)** v3.13+
- **[UV](https://docs.astral.sh/uv/)** (Fast Python package manager - **recommended**)
- **[PostgreSQL](https://www.postgresql.org/)** v15+ (optional - SQLite works for development)
- **[Redis](https://redis.io/)** (optional - for Celery task queue)
- **[Docker](https://www.docker.com/)** (optional - for containerized setup)

### Installation

#### Option 1: Quick Start with Turbo (Recommended)

This monorepo uses [Turborepo](https://turbo.build/) for efficient builds and development.

1. **Clone the repository**

```bash
git clone <repository-url>
cd it-analytics-platform
```

2. **Install UV (if not already installed)**

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

3. **Install all dependencies (monorepo root)**

```bash
npm install
```

This will install:
- Turborepo and root dependencies
- Frontend (Next.js) dependencies
- Backend (Python) dependencies via UV

4. **Set up environment variables**

```bash
# Backend environment
cp backend/.env.example backend/.env
# Edit backend/.env with your configuration
```

Required environment variables in `backend/.env`:
- `DATABASE_URL` - Database connection (defaults to SQLite)
- `GOOGLE_API_KEY` - Google Gemini AI API key (optional)
- `REDIS_URL` - Redis connection string (optional)
- `SECRET_KEY` - Secret key for JWT tokens

5. **Start both frontend and backend**

```bash
npm run dev
```

This starts:
- 🌐 **Frontend**: [http://localhost:3000](http://localhost:3000)
- 🔌 **Backend API**: [http://localhost:8000](http://localhost:8000)
- 📚 **API Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
- 📖 **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

#### Option 2: Using the Dev Start Script

We provide a convenient bash script that handles everything:

```bash
chmod +x dev-start.sh
./dev-start.sh
```

The script will:
- Check if required ports (3000, 8000) are available
- Create Python virtual environment if needed
- Install frontend dependencies if needed
- Initialize database with sample data
- Start both servers concurrently

#### Option 3: Manual Setup (Individual Services)

**Backend Setup:**

```bash
cd backend

# Install Python dependencies with UV
uv sync

# Or use traditional pip/venv
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e .

# Set up environment
cp .env.example .env
# Edit .env as needed

# Start backend server
npm run dev
# or manually: uvicorn app.main:app --reload
```

**Frontend Setup:**

```bash
cd frontend

# Install Node dependencies
npm install

# Start frontend server
npm run dev
```

#### Option 4: Docker Setup

For a fully containerized environment:

```bash
# Start all services
docker-compose up --build

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

Docker Compose includes:
- FastAPI backend (port 8000)
- PostgreSQL database (port 5432)
- Redis cache (port 6379)
- Next.js frontend (port 3000)

**Access the application:**
- Frontend: [http://localhost:3000](http://localhost:3000)
- API: [http://localhost:8000](http://localhost:8000)
- API Docs: [http://localhost:8000/docs](http://localhost:8000/docs)

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

### Available Scripts (Monorepo Root)

The monorepo uses Turborepo to orchestrate tasks across workspaces:

```bash
npm run dev       # Start both frontend and backend in dev mode
npm run build     # Build both applications for production
npm run test      # Run tests for all workspaces
npm run clean     # Clean build artifacts and caches
```

### Frontend Commands

```bash
cd frontend

npm run dev       # Start Next.js dev server (port 3000)
npm run build     # Build for production
npm run start     # Start production server
npm run lint      # Run ESLint
npm run clean     # Clean .next and node_modules
```

### Backend Commands

```bash
cd backend

# Using npm scripts
npm run dev       # Start FastAPI with auto-reload (port 8000)
npm run test      # Run pytest tests
npm run clean     # Remove .venv

# Manual commands
uv sync           # Sync Python dependencies
. .venv/bin/activate  # Activate virtual environment
uvicorn app.main:app --reload  # Start server manually
pytest            # Run tests
pytest --cov=app  # Run tests with coverage
```

### Using Makefile (Backend)

```bash
cd backend

make dev          # Start development server
make test         # Run tests
make lint         # Run linting
make format       # Format code with black
make clean        # Clean up cache and build files
```

### Project Structure

**Backend Structure:**
```
backend/app/
├── api/                 # API route handlers
│   ├── __init__.py
│   ├── projects.py
│   ├── cost_forecasting.py
│   ├── resource_utilization.py
│   ├── bug_tracker.py
│   ├── risks.py
│   ├── analytics.py
│   └── ai_insights.py
├── services/            # Business logic
├── models/              # Database models
├── middleware/          # Custom middleware
│   ├── monitoring.py
│   └── __init__.py
├── utils/              # Utilities
│   ├── helpers.py
│   └── gemini_client.py
├── config.py           # Configuration
├── database.py         # DB connection
└── main.py             # App entry point
```

**Frontend Structure:**
```
frontend/src/
├── app/                # Next.js App Router
│   ├── layout.tsx     # Root layout
│   ├── page.tsx       # Home page
│   ├── dashboard/     # Dashboard routes
│   └── api/           # API routes
├── components/         # React components
│   ├── ui/            # Reusable UI components
│   ├── layout/        # Layout components
│   └── features/      # Feature-specific components
├── lib/               # Utilities
│   ├── api.ts         # API client
│   └── utils.ts       # Helper functions
└── styles/            # Global styles
    └── globals.css    # Tailwind CSS imports
```

### Database Migrations

Using Alembic for database migrations:

```bash
cd backend

# Activate virtual environment
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# Create new migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1

# View migration history
alembic history

# Check current version
alembic current
```

### Code Quality

**Backend (Python):**

```bash
cd backend

# Format code
black app/
isort app/

# Lint code
flake8 app/

# Type checking (if using mypy)
mypy app/
```

**Frontend (TypeScript):**

```bash
cd frontend

# Lint and fix
npm run lint

# Type check
npx tsc --noEmit
```

## 🐳 Docker Support

### Using Docker Compose

The project includes Docker support for both backend and frontend services.

**Backend Docker Compose (backend/docker-compose.yml):**

```bash
cd backend

# Start backend services (FastAPI, PostgreSQL, Redis)
docker-compose up --build

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f backend

# Stop services
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

**Full Stack Docker (if configured at root):**

```bash
# From project root
docker-compose up --build

# Run in background
docker-compose up -d

# View all logs
docker-compose logs -f

# Stop all services
docker-compose down
```

### Docker Services

The `docker-compose.yml` typically includes:
- **FastAPI Backend** - Main application server (port 8000)
- **PostgreSQL** - Database server (port 5432)
- **Redis** - Cache and message broker (port 6379)
- **Next.js Frontend** - Frontend application (port 3000) [if configured]

### Building Individual Docker Images

**Backend:**
```bash
cd backend
docker build -t it-analytics-backend:latest .
docker run -p 8000:8000 --env-file .env it-analytics-backend:latest
```

**Frontend:**
```bash
cd frontend
docker build -t it-analytics-frontend:latest .
docker run -p 3000:3000 it-analytics-frontend:latest
```

## 🧪 Testing

### Running All Tests (Monorepo)

```bash
# From root - runs tests for all workspaces
npm run test
```

### Backend Tests

```bash
cd backend

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

# Run only failed tests
pytest --lf
```

### Frontend Tests (when implemented)

```bash
cd frontend

# Run tests
npm run test

# Run tests in watch mode
npm run test:watch

# Run tests with coverage
npm run test:coverage
```

### Writing Tests

**Backend Tests (pytest):**

```python
# tests/test_api.py
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "message" in response.json()

def test_get_projects():
    response = client.get("/api/projects")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
```

**Frontend Tests (Jest/Vitest - when implemented):**

```typescript
// components/__tests__/Button.test.tsx
import { render, screen } from '@testing-library/react'
import { Button } from '../Button'

describe('Button', () => {
  it('renders button with text', () => {
    render(<Button>Click me</Button>)
    expect(screen.getByText('Click me')).toBeInTheDocument()
  })
})
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

**Backend (`backend/.env`):**

```env
# Database Configuration
DATABASE_URL=sqlite:///./it_analytics.db
# For PostgreSQL: postgresql://user:password@localhost:5432/it_analytics
# For async PostgreSQL: postgresql+asyncpg://user:password@localhost:5432/it_analytics

# Google Gemini AI (Optional - leave empty to disable AI features)
GOOGLE_API_KEY=your_gemini_api_key_here

# Redis (Optional - for caching and Celery)
REDIS_URL=redis://localhost:6379/0

# Security
SECRET_KEY=your-secret-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Application Settings
ENVIRONMENT=development
DEBUG=True
LOG_LEVEL=INFO
API_V1_PREFIX=/api

# CORS Origins (comma-separated)
CORS_ORIGINS=http://localhost:3000,http://localhost:8000

# Celery (Optional)
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

**Frontend (if needed - `frontend/.env.local`):**

```env
# Backend API URL
NEXT_PUBLIC_API_URL=http://localhost:8000

# Optional: Other frontend environment variables
NEXT_PUBLIC_APP_NAME=IT Analytics Platform
```

### Configuration Files

**Monorepo Configuration:**
- **`package.json`** - Root workspace configuration
- **`turbo.json`** - Turborepo pipeline configuration

**Backend Configuration:**
- **`backend/app/config.py`** - Application settings and configuration
- **`backend/pyproject.toml`** - Python dependencies and project metadata
- **`backend/package.json`** - Backend npm scripts
- **`backend/docker-compose.yml`** - Backend Docker services
- **`backend/makefile`** - Development automation commands
- **`backend/alembic.ini`** - Database migration configuration

**Frontend Configuration:**
- **`frontend/package.json`** - Frontend dependencies
- **`frontend/next.config.ts`** - Next.js configuration
- **`frontend/tsconfig.json`** - TypeScript configuration
- **`frontend/tailwind.config.ts`** - Tailwind CSS configuration (if exists)
- **`frontend/postcss.config.mjs`** - PostCSS configuration

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

**Port Already in Use**
```bash
# Check what's using port 3000 or 8000
lsof -i :3000
lsof -i :8000

# Kill the process
kill -9 <PID>

# Or use the dev-start.sh script which checks ports automatically
./dev-start.sh
```

**Backend - Database Connection Error**
```bash
# Check if PostgreSQL is running (if using PostgreSQL)
pg_isready -h localhost -p 5432

# Verify DATABASE_URL in backend/.env
cd backend
cat .env | grep DATABASE_URL

# For SQLite (default), ensure directory permissions
ls -la it_analytics.db
```

**Backend - Import Errors**
```bash
cd backend

# Reinstall dependencies with UV
uv sync --force

# Or with traditional pip
rm -rf .venv
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

**Backend - Gemini AI API Error**
```bash
# Verify API key is set
cd backend
cat .env | grep GOOGLE_API_KEY

# The application should work without Gemini - it's optional
# Check logs for specific error messages
```

**Frontend - Module Not Found**
```bash
cd frontend

# Clear cache and reinstall
rm -rf node_modules .next
npm install

# Clear npm cache if needed
npm cache clean --force
npm install
```

**Frontend - Build Errors**
```bash
cd frontend

# Check Node version (needs v20+)
node --version

# Clear Next.js cache
rm -rf .next

# Rebuild
npm run build
```

**Turborepo Cache Issues**
```bash
# Clear Turbo cache
npx turbo clean
rm -rf .turbo

# Or use the clean script
npm run clean
```

**Python Version Issues**
```bash
# Check Python version (needs 3.13+)
python3 --version

# If using UV, it should handle Python version
uv --version

# Install specific Python version with pyenv
pyenv install 3.13
pyenv local 3.13
```

**Dependencies Out of Sync**
```bash
# Reinstall everything from root
npm install

# Force reinstall backend dependencies
cd backend && uv sync --force

# Force reinstall frontend dependencies
cd frontend && npm ci
```

## 🏢 Monorepo Structure

This project uses **Turborepo** to manage a monorepo containing multiple workspaces:

### Why Turborepo?

- **Fast Builds**: Intelligent caching and parallelization
- **Task Orchestration**: Run tasks across multiple packages efficiently
- **Dependency Management**: Shared dependencies and consistent versions
- **Developer Experience**: Simple commands to manage complex workflows

### Workspace Configuration

The monorepo is configured in `package.json`:

```json
{
  "workspaces": [
    "frontend",
    "backend"
  ]
}
```

### Pipeline Configuration

Tasks are defined in `turbo.json`:

```json
{
  "tasks": {
    "dev": {
      "cache": false,
      "persistent": true
    },
    "build": {
      "dependsOn": ["^build"]
    },
    "test": {
      "dependsOn": ["^build"]
    }
  }
}
```

### Benefits

1. **Unified Development**: Start both frontend and backend with one command
2. **Shared Tools**: Common linting, formatting, and CI/CD configurations
3. **Incremental Builds**: Only rebuild what changed
4. **Better DX**: Consistent workflows across the entire stack

## 📚 Additional Resources

### Learning Resources

**Monorepo & Build Tools:**
- [Turborepo Documentation](https://turbo.build/repo/docs)
- [npm Workspaces](https://docs.npmjs.com/cli/v8/using-npm/workspaces)
- [Monorepo Best Practices](https://monorepo.tools/)

**Frontend:**
- [Next.js 15 Documentation](https://nextjs.org/docs)
- [React 19 Documentation](https://react.dev/)
- [Tailwind CSS v4](https://tailwindcss.com/)
- [Radix UI](https://www.radix-ui.com/)
- [TanStack Query](https://tanstack.com/query/latest)

**Backend:**
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Google Gemini AI](https://ai.google.dev/)
- [SQLAlchemy Guide](https://docs.sqlalchemy.org/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [UV Package Manager](https://docs.astral.sh/uv/)
- [Alembic Migrations](https://alembic.sqlalchemy.org/)

**Testing:**
- [pytest Documentation](https://docs.pytest.org/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [React Testing Library](https://testing-library.com/react)

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

**Monorepo & Build Tools:**
- **[Turborepo](https://turbo.build/)** - High-performance build system for monorepos
- **[npm Workspaces](https://docs.npmjs.com/)** - Dependency management for monorepos

**Frontend Stack:**
- **[Next.js](https://nextjs.org/)** - The React framework for production
- **[React](https://react.dev/)** - A JavaScript library for building user interfaces
- **[TypeScript](https://www.typescriptlang.org/)** - Typed superset of JavaScript
- **[Tailwind CSS](https://tailwindcss.com/)** - Utility-first CSS framework
- **[Radix UI](https://www.radix-ui.com/)** - Unstyled, accessible UI components
- **[TanStack Query](https://tanstack.com/query/)** - Powerful data synchronization
- **[Zustand](https://zustand-demo.pmnd.rs/)** - State management
- **[Recharts](https://recharts.org/)** - Composable charting library
- **[Framer Motion](https://www.framer.com/motion/)** - Animation library

**Backend Stack:**
- **[FastAPI](https://fastapi.tiangolo.com/)** - Modern, fast web framework for Python
- **[Google Gemini](https://ai.google.dev/)** - Advanced AI and machine learning
- **[PostgreSQL](https://www.postgresql.org/)** - Powerful open-source database
- **[SQLAlchemy](https://www.sqlalchemy.org/)** - Python SQL toolkit and ORM
- **[Pydantic](https://docs.pydantic.dev/)** - Data validation using Python type hints
- **[UV](https://docs.astral.sh/uv/)** - Lightning-fast Python package installer
- **[Celery](https://docs.celeryq.dev/)** - Distributed task queue
- **[Redis](https://redis.io/)** - In-memory data structure store
- **[Alembic](https://alembic.sqlalchemy.org/)** - Database migration tool

**Data & ML:**
- **[scikit-learn](https://scikit-learn.org/)** - Machine learning in Python
- **[Pandas](https://pandas.pydata.org/)** - Data analysis and manipulation tool
- **[NumPy](https://numpy.org/)** - Fundamental package for scientific computing
- **[Plotly](https://plotly.com/)** - Interactive graphing library
- **[Matplotlib](https://matplotlib.org/)** - Visualization with Python

**DevOps & Testing:**
- **[Docker](https://www.docker.com/)** - Containerization platform
- **[pytest](https://pytest.org/)** - Python testing framework
- **[Prometheus](https://prometheus.io/)** - Monitoring and alerting toolkit

## 📊 Project Stats

- **Architecture**: Turborepo Monorepo
- **Frontend**: Next.js 15, React 19, TypeScript 5, Tailwind CSS v4
- **Backend**: FastAPI, Python 3.13+
- **Database**: PostgreSQL with asyncpg (SQLite for dev)
- **AI/ML**: Google Gemini, scikit-learn
- **State Management**: Zustand, TanStack Query
- **UI Components**: Radix UI, Custom components
- **Styling**: Tailwind CSS v4, Framer Motion
- **Build System**: Turborepo with npm workspaces
- **Package Managers**: npm (frontend), UV (backend)
- **Code Quality**: Black, isort, flake8 (Python); ESLint (TypeScript)
- **Testing**: pytest (backend), Jest/Vitest planned (frontend)

---

**Made with ❤️ by Team Innovatrix**

*Building intelligent solutions for IT project management*
