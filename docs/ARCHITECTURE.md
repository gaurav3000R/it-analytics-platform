# IT Analytics Platform - Architecture

## 📋 Overview

The IT Analytics Platform is a full-stack application designed to provide analytics, predictions, and insights for IT project management. It helps teams track tasks, manage users, analyze performance, and predict outcomes using machine learning.

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         Client Layer                         │
│              (Next.js 15 + React 19 + Tailwind)             │
└─────────────────────┬───────────────────────────────────────┘
                      │ HTTP/REST API
┌─────────────────────▼───────────────────────────────────────┐
│                      API Gateway                             │
│                  (FastAPI + CORS)                           │
└─────────────┬─────────────────┬─────────────────────────────┘
              │                 │
┌─────────────▼────────┐  ┌────▼──────────────────────────────┐
│   Business Logic     │  │      ML Service Layer             │
│   (Services)         │  │  (scikit-learn Models)           │
└─────────────┬────────┘  └───────────────────────────────────┘
              │
┌─────────────▼────────────────────────────────────────────────┐
│              Data Layer (SQLModel/SQLAlchemy)                │
└─────────────┬────────────────────────────────────────────────┘
              │
┌─────────────▼────────────────────────────────────────────────┐
│                   PostgreSQL Database                        │
│                  (Managed with Alembic)                      │
└──────────────────────────────────────────────────────────────┘
              │
┌─────────────▼────────────────────────────────────────────────┐
│                Analytics Layer (dbt)                         │
│              (Data Transformation & Analytics)               │
└──────────────────────────────────────────────────────────────┘
```

## 📁 Monorepo Structure

The project is organized as a monorepo using **Turborepo** for efficient build orchestration:

```
it-analytics-platform/
├── frontend/           # Next.js web application
├── backend/            # FastAPI server with ML models
├── dbt_project/        # dbt analytics & transformations
├── infra/              # Infrastructure & CI/CD configs
├── data/               # Data storage (raw & processed)
└── docs/               # Project documentation
```

## 🔧 Technology Stack

### Frontend
- **Framework**: Next.js 15 (React 19)
- **Styling**: Tailwind CSS v4
- **Language**: TypeScript 5
- **Build Tool**: Turbo (via Turborepo)

### Backend
- **Framework**: FastAPI (latest)
- **Language**: Python 3.13+
- **Package Manager**: UV (Astral)
- **ORM**: SQLModel (based on SQLAlchemy 2.x)
- **Database**: PostgreSQL
- **Migrations**: Alembic
- **Testing**: pytest
- **ML Libraries**: scikit-learn

### Analytics
- **Tool**: dbt (data build tool)
- **Target**: PostgreSQL

### Infrastructure
- **Containerization**: Docker + Docker Compose
- **Orchestration**: Turborepo
- **CI/CD**: GitHub Actions (planned)

## 🎯 Core Features

### 1. User Management
- User registration and authentication (JWT-based)
- User profile management
- Skills assignment and tracking
- Role-based access control

### 2. Task Management
- Task creation and assignment
- Status tracking (pending, in-progress, completed)
- Time estimation vs actual tracking
- Task prioritization

### 3. Analytics & Reporting
- Project-wise reports
- User performance metrics
- Task completion statistics
- Bug rate analysis
- Time estimation accuracy

### 4. ML-Powered Predictions
- **Task Assignment**: Predict best developer for upcoming tasks
- **Bug Probability**: Estimate likelihood of bugs in tasks
- **Time Estimation**: Predict task duration based on historical data
- **Developer Ranking**: Rank developers by skills and performance

## 🔄 Data Flow

1. **User Request** → Frontend (Next.js)
2. **API Call** → Backend FastAPI endpoints
3. **Authentication** → JWT validation
4. **Business Logic** → Service layer processing
5. **Data Operations** → SQLModel ORM queries
6. **Database** → PostgreSQL storage
7. **Analytics** → dbt transformations
8. **ML Predictions** → scikit-learn models
9. **Response** → JSON data back to frontend

## 🔐 Security

- **Authentication**: JWT-based token authentication
- **CORS**: Configured to allow frontend origin
- **Environment Variables**: Sensitive data stored in `.env` files
- **API Rate Limiting**: (To be implemented)
- **Input Validation**: Pydantic models for request validation

## 🚀 Deployment Strategy

### Development
```bash
npm run dev  # Starts both frontend and backend
```

### Production
```bash
npm run build  # Builds optimized production bundles
docker-compose up  # Containerized deployment
```

## 📊 Database Schema (Planned)

### Core Tables
- **users**: User accounts and profiles
- **tasks**: Project tasks and assignments
- **projects**: Project information
- **skills**: Skills taxonomy
- **user_skills**: User-to-skill mappings
- **task_history**: Historical task data for ML training

### Analytics Tables (dbt)
- **user_performance**: Aggregated user metrics
- **project_reports**: Project-level KPIs
- **prediction_features**: Feature tables for ML models

## 🔮 Future Enhancements

- Real-time notifications (WebSockets)
- Advanced ML models (deep learning)
- Multi-tenancy support
- Advanced reporting dashboards
- Integration with project management tools (Jira, GitHub)
- Mobile application (React Native)

## 📚 Related Documentation

- [Setup Guide](./SETUP.md)
- [Backend Documentation](./backend.md)
- [Frontend Documentation](./frontend.md)
- [Contributing Guidelines](./CONTRIBUTING.md)
