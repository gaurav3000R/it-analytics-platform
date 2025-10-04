# IT Analytics Platform - Setup Guide

## 📋 Prerequisites

Before you begin, ensure you have the following installed on your system:

### Required Software
- **Node.js** (v18 or later) - [Download](https://nodejs.org/)
- **npm** (v8 or later) - Comes with Node.js
- **Python** (v3.13 or later) - [Download](https://www.python.org/)
- **UV** (Python package manager) - [Installation Guide](https://docs.astral.sh/uv/)
- **Git** - [Download](https://git-scm.com/)

### Optional (for containerized deployment)
- **Docker** - [Download](https://www.docker.com/)
- **Docker Compose** - Usually comes with Docker Desktop

### Database (Choose One)
- **PostgreSQL** (v15 or later) - [Download](https://www.postgresql.org/)
- **OR** Use Docker to run PostgreSQL (recommended for development)

---

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone <repository-url>
cd it-analytics-platform
```

### 2. Environment Setup

Create a `.env` file in the root directory (copy from `.env.example`):

```bash
cp .env.example .env
```

Update the `.env` file with your configuration:

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/it_analytics

# Backend
BACKEND_PORT=8000
SECRET_KEY=your-secret-key-here

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 3. Install Dependencies

From the root directory, install all dependencies:

```bash
npm install
```

This will install dependencies for:
- Root workspace (Turborepo)
- Frontend application
- Backend application

### 4. Start Development Servers

Start both frontend and backend development servers:

```bash
npm run dev
```

This will start:
- **Frontend**: http://localhost:3000
- **Backend**: http://localhost:8000
- **Backend API Docs**: http://localhost:8000/docs

---

## 🔧 Detailed Setup

### Frontend Setup

Navigate to the frontend directory:

```bash
cd frontend
```

#### Install Dependencies
```bash
npm install
```

#### Run Development Server
```bash
npm run dev
```

#### Build for Production
```bash
npm run build
```

#### Start Production Server
```bash
npm run start
```

### Backend Setup

Navigate to the backend directory:

```bash
cd backend
```

#### Install Python Dependencies with UV

```bash
# Sync dependencies
uv sync

# Activate virtual environment
source .venv/bin/activate  # On Linux/Mac
# or
.venv\Scripts\activate  # On Windows
```

#### Setup Database

1. Start PostgreSQL (if using Docker):

```bash
docker-compose up -d postgres
```

2. Run database migrations:

```bash
# From backend directory
alembic upgrade head
```

#### Run Development Server

```bash
# With UV (recommended)
npm run dev

# Or manually
uvicorn app.main:app --reload
```

#### Run Tests

```bash
pytest
```

### dbt Setup

Navigate to the dbt project directory:

```bash
cd dbt_project
```

#### Install dbt

```bash
pip install dbt-postgres
```

#### Configure dbt Profile

Create or update `~/.dbt/profiles.yml`:

```yaml
it_analytics:
  target: dev
  outputs:
    dev:
      type: postgres
      host: localhost
      user: your_user
      password: your_password
      port: 5432
      dbname: it_analytics
      schema: analytics
      threads: 4
```

#### Run dbt

```bash
# Test connection
dbt debug

# Run models
dbt run

# Run tests
dbt test
```

---

## 🐳 Docker Setup (Alternative)

### Using Docker Compose

The easiest way to run the entire stack:

```bash
# Build and start all services
docker-compose up --build

# Run in detached mode
docker-compose up -d

# Stop services
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

This will start:
- PostgreSQL database
- Backend API server
- Frontend application

Access the applications:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

---

## 🧪 Testing

### Run All Tests

From the root directory:

```bash
npm run test
```

### Frontend Tests

```bash
cd frontend
npm run test
```

### Backend Tests

```bash
cd backend
pytest

# With coverage
pytest --cov=app --cov-report=html
```

---

## 🧹 Cleanup

### Clean Build Artifacts

```bash
# From root directory
npm run clean
```

This will remove:
- `node_modules` directories
- `.next` build directory (frontend)
- `.venv` virtual environment (backend)
- `__pycache__` directories
- `.turbo` cache

### Manual Cleanup

```bash
# Remove all node_modules
find . -name "node_modules" -type d -exec rm -rf {} +

# Remove Python cache
find . -name "__pycache__" -type d -exec rm -rf {} +

# Remove virtual environment
rm -rf backend/.venv
```

---

## 🔍 Troubleshooting

### Port Already in Use

If you get port conflicts:

```bash
# Find process using port 3000 (frontend)
lsof -i :3000
kill -9 <PID>

# Find process using port 8000 (backend)
lsof -i :8000
kill -9 <PID>
```

### Database Connection Issues

1. Verify PostgreSQL is running
2. Check database credentials in `.env`
3. Ensure database exists:

```bash
psql -U postgres -c "CREATE DATABASE it_analytics;"
```

### UV Installation Issues

```bash
# Linux/Mac
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Verify installation
uv --version
```

### Node Package Issues

```bash
# Clear npm cache
npm cache clean --force

# Remove lock files and reinstall
rm -rf node_modules package-lock.json
npm install
```

---

## 📝 Next Steps

After setup is complete:

1. Read the [Architecture Documentation](./ARCHITECTURE.md)
2. Check out [Backend Documentation](./backend.md)
3. Review [Frontend Documentation](./frontend.md)
4. See [Contributing Guidelines](./CONTRIBUTING.md)

---

## 🆘 Getting Help

If you encounter issues:

1. Check this setup guide
2. Review the [troubleshooting section](#-troubleshooting)
3. Search existing GitHub issues
4. Create a new issue with detailed information

---

## 📚 Additional Resources

- [Turborepo Documentation](https://turbo.build/)
- [Next.js Documentation](https://nextjs.org/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [UV Documentation](https://docs.astral.sh/uv/)
- [dbt Documentation](https://docs.getdbt.com/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
