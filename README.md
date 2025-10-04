# IT Analytics Platform

> A full-stack monorepo application for IT project analytics, task management, and ML-powered predictions.

[![Next.js](https://img.shields.io/badge/Next.js-15-black)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-latest-009688)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.13+-blue)](https://www.python.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5-blue)](https://www.typescriptlang.org/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

## 📋 Overview

The **IT Analytics Platform** is a comprehensive solution designed to help IT teams manage projects, track tasks, analyze performance, and make data-driven decisions using machine learning predictions. Built as a modern monorepo, it combines a powerful FastAPI backend with a sleek Next.js frontend.

### Key Features

🎯 **Task Management** - Create, assign, and track tasks with status updates
👥 **User Management** - Handle user profiles, skills, and authentication
📊 **Analytics & Reporting** - Generate insights on team performance and project metrics
🤖 **ML Predictions** - AI-powered recommendations for task assignment, bug prediction, and time estimation
⚡ **Real-time Updates** - Modern, responsive interface with instant feedback
🔐 **Secure** - JWT-based authentication and role-based access control

## 🏗️ Architecture

This is a **monorepo** managed with [Turborepo](https://turbo.build/) containing:

```
it-analytics-platform/
├── frontend/        # Next.js 15 + React 19 + Tailwind CSS
├── backend/         # FastAPI + PostgreSQL + ML Models
├── dbt_project/     # dbt analytics transformations
├── infra/           # Infrastructure & CI/CD configurations
├── data/            # Data storage (raw & processed)
└── docs/            # Comprehensive documentation
```

### Technology Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | Next.js 15, React 19, TypeScript 5, Tailwind CSS v4 |
| **Backend** | FastAPI, Python 3.13+, SQLModel, Alembic |
| **Database** | PostgreSQL |
| **Analytics** | dbt (data build tool) |
| **ML** | scikit-learn |
| **Package Managers** | npm (frontend), UV (backend) |
| **Monorepo** | Turborepo |
| **Containerization** | Docker + Docker Compose |

## 🚀 Quick Start

### Prerequisites

- [Node.js](https://nodejs.org/) (v18 or later)
- [Python](https://www.python.org/) (v3.13 or later)
- [UV](https://docs.astral.sh/uv/) (Python package manager)
- [PostgreSQL](https://www.postgresql.org/) (v15 or later) - optional with Docker

### Installation

1. **Clone the repository**

```bash
git clone <repository-url>
cd it-analytics-platform
```

2. **Install dependencies**

```bash
npm install
```

This will install dependencies for both frontend and backend.

3. **Set up environment variables**

```bash
cp .env.example .env
# Edit .env with your configuration
```

4. **Start development servers**

```bash
npm run dev
```

This starts:
- 🌐 Frontend: [http://localhost:3000](http://localhost:3000)
- 🔌 Backend API: [http://localhost:8000](http://localhost:8000)
- 📚 API Docs: [http://localhost:8000/docs](http://localhost:8000/docs)

## 📚 Documentation

Comprehensive documentation is available in the [`docs/`](./docs) directory:

- **[📖 Documentation Index](./docs/README.md)** - Complete documentation overview
- **[🏗️ Architecture](./docs/ARCHITECTURE.md)** - System design and technical details
- **[⚙️ Setup Guide](./docs/SETUP.md)** - Detailed installation instructions
- **[🤝 Contributing](./docs/CONTRIBUTING.md)** - How to contribute to the project
- **[🔧 Backend Docs](./docs/backend.md)** - Backend API and development guide
- **[🎨 Frontend Docs](./docs/frontend.md)** - Frontend development guide

## 🛠️ Development

### Available Scripts

From the root directory:

```bash
npm run dev      # Start development servers (frontend + backend)
npm run build    # Build both applications for production
npm run test     # Run tests for all applications
npm run clean    # Clean build artifacts and caches
```

### Frontend Commands

```bash
cd frontend
npm run dev      # Start Next.js dev server
npm run build    # Build for production
npm run start    # Start production server
npm run lint     # Run ESLint
```

### Backend Commands

```bash
cd backend
npm run dev      # Start FastAPI dev server with auto-reload
npm run test     # Run pytest tests
npm run clean    # Remove virtual environment
```

## 🐳 Docker Support

Run the entire stack with Docker Compose:

```bash
# Start all services
docker-compose up --build

# Run in background
docker-compose up -d

# Stop services
docker-compose down
```

## 🧪 Testing

```bash
# Run all tests
npm run test

# Frontend tests (to be implemented)
cd frontend && npm run test

# Backend tests
cd backend && pytest
```

## 📊 Project Status

### Current State

✅ Monorepo structure with Turborepo
✅ Next.js 15 frontend with Tailwind CSS
✅ FastAPI backend with CORS configuration
✅ Basic API endpoints
✅ Frontend-backend integration demo
✅ Comprehensive documentation

### Planned Features

🔄 User authentication (JWT)
🔄 Task management CRUD operations
🔄 Database models and migrations
🔄 ML model integration
🔄 Analytics dashboard
🔄 dbt transformations
🔄 CI/CD pipeline
🔄 Comprehensive test coverage

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](./docs/CONTRIBUTING.md) for details on:

- Code of conduct
- Development workflow
- Coding standards
- Pull request process
- Testing requirements

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

Built with:
- [Next.js](https://nextjs.org/) - The React Framework for the Web
- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- [Turborepo](https://turbo.build/) - High-performance build system
- [Tailwind CSS](https://tailwindcss.com/) - Utility-first CSS framework
- [SQLModel](https://sqlmodel.tiangolo.com/) - SQL databases with Python
- [UV](https://docs.astral.sh/uv/) - Fast Python package installer

## 📞 Support

- 📖 [Documentation](./docs/README.md)
- 🐛 [Report Issues](https://github.com/your-org/it-analytics-platform/issues)
- 💬 [Discussions](https://github.com/your-org/it-analytics-platform/discussions)

## 🗺️ Roadmap

### Phase 1: Foundation (Current)
- ✅ Monorepo setup
- ✅ Basic frontend and backend
- ✅ Documentation
- 🔄 Database schema
- 🔄 Authentication

### Phase 2: Core Features
- 🔄 Task management
- 🔄 User management
- 🔄 Basic analytics
- 🔄 API completion

### Phase 3: ML Integration
- 🔄 Task assignment predictor
- 🔄 Bug probability estimator
- 🔄 Time estimation model
- 🔄 Developer ranking

### Phase 4: Advanced Features
- 🔄 Real-time notifications
- 🔄 Advanced dashboards
- 🔄 Integrations (Jira, GitHub)
- 🔄 Mobile application

---

**Made with ❤️ by the IT Analytics Platform Team**
