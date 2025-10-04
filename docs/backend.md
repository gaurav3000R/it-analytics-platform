# Backend Documentation

## 📋 Overview

The backend is built with **FastAPI**, a modern Python web framework designed for building APIs quickly with automatic interactive documentation. It serves as the core API layer and ML service provider for the IT Analytics Platform.

## 🏗️ Architecture

```
backend/
├── app/
│   ├── api/              # API route handlers
│   │   ├── __init__.py
│   │   └── main.py       # Main API router
│   ├── core/             # Core configuration (settings, security)
│   │   └── __init__.py
│   ├── db/               # Database models and session management
│   │   └── __init__.py
│   ├── services/         # Business logic layer
│   │   └── __init__.py
│   ├── ml/               # Machine learning models and utilities
│   │   └── __init__.py
│   ├── tests/            # Test files
│   │   └── __init__.py
│   └── main.py           # Application entry point
├── alembic/              # Database migrations
├── pyproject.toml        # Python dependencies (UV)
├── uv.lock               # UV lock file
├── package.json          # npm scripts for monorepo
├── Dockerfile            # Container definition
├── docker-compose.yml    # Local development setup
└── README.md             # Backend-specific documentation
```

## 🔧 Technology Stack

- **Framework**: FastAPI (latest stable version)
- **Language**: Python 3.13+
- **Package Manager**: UV by Astral
- **ORM**: SQLModel (built on SQLAlchemy 2.x)
- **Database**: PostgreSQL
- **Migrations**: Alembic
- **Testing**: pytest
- **ML Libraries**: scikit-learn
- **API Documentation**: Swagger UI (auto-generated)

## 🚀 Getting Started

### Installation

From the backend directory:

```bash
# Install dependencies
uv sync

# Activate virtual environment
source .venv/bin/activate  # Linux/Mac
# or
.venv\Scripts\activate  # Windows
```

### Running the Server

```bash
# Development mode (with auto-reload)
npm run dev
# or
uvicorn app.main:app --reload

# Production mode
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Access Points

- **API Base**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## 📡 API Structure

### Current Endpoints

#### Root Endpoints
- `GET /` - Welcome message
- `GET /health` - Health check

#### API Endpoints (prefix: `/api`)
- `GET /api/hello` - Test endpoint

### Planned Endpoints

#### Users (`/api/users`)
- `POST /api/users/register` - Register new user
- `POST /api/users/login` - User login (JWT)
- `GET /api/users/me` - Get current user
- `GET /api/users/{id}` - Get user by ID
- `PUT /api/users/{id}` - Update user
- `DELETE /api/users/{id}` - Delete user

#### Tasks (`/api/tasks`)
- `GET /api/tasks` - List all tasks
- `POST /api/tasks` - Create new task
- `GET /api/tasks/{id}` - Get task by ID
- `PUT /api/tasks/{id}` - Update task
- `DELETE /api/tasks/{id}` - Delete task
- `POST /api/tasks/{id}/assign` - Assign task to user

#### Analytics (`/api/analytics`)
- `GET /api/analytics/users/{id}/performance` - User performance metrics
- `GET /api/analytics/projects/{id}/report` - Project report
- `GET /api/analytics/tasks/completion-rate` - Task completion statistics

#### Predictions (`/api/predictions`)
- `POST /api/predictions/task-assignment` - Predict best developer for task
- `POST /api/predictions/bug-probability` - Estimate bug likelihood
- `POST /api/predictions/time-estimation` - Predict task duration
- `GET /api/predictions/developer-ranking` - Rank developers

## 🗄️ Database

### Models (Planned)

```python
# User Model
class User(SQLModel, table=True):
    id: int = Field(primary_key=True)
    email: str = Field(unique=True, index=True)
    name: str
    hashed_password: str
    created_at: datetime
    updated_at: datetime

# Task Model
class Task(SQLModel, table=True):
    id: int = Field(primary_key=True)
    title: str
    description: str
    status: str  # pending, in_progress, completed
    assigned_to: int = Field(foreign_key="user.id")
    estimated_hours: float
    actual_hours: float | None
    created_at: datetime
    updated_at: datetime
```

### Migrations

```bash
# Create a new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1

# View migration history
alembic history
```

## 🤖 Machine Learning

### Models (Planned)

1. **Task Assignment Predictor**
   - Input: Task description, required skills, developer availability
   - Output: Recommended developer with confidence score

2. **Bug Probability Estimator**
   - Input: Task complexity, developer experience, historical data
   - Output: Bug probability (0-1)

3. **Time Estimation Model**
   - Input: Task description, developer skill level, historical data
   - Output: Estimated completion time in hours

4. **Developer Ranking**
   - Input: Skills, performance history, availability
   - Output: Ranked list of developers

### ML Pipeline

```python
# Example ML service structure
class TaskAssignmentPredictor:
    def __init__(self):
        self.model = load_model()
    
    async def predict(self, task_data: TaskData) -> PredictionResult:
        features = self.extract_features(task_data)
        prediction = self.model.predict(features)
        return PredictionResult(
            developer_id=prediction.developer_id,
            confidence=prediction.confidence
        )
```

## 🔐 Authentication & Security

### JWT Authentication (Planned)

```python
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer

security = HTTPBearer()

async def get_current_user(token: str = Depends(security)):
    """Verify JWT token and return current user"""
    payload = verify_token(token)
    user = await get_user_by_id(payload.user_id)
    return user
```

### CORS Configuration

```python
# Configured in app/main.py
origins = [
    "http://localhost:3000",  # Frontend development
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 🧪 Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest app/tests/test_users.py

# Run with verbose output
pytest -v
```

### Test Structure

```python
# Example test
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

@pytest.mark.asyncio
async def test_create_user():
    user_data = {
        "email": "test@example.com",
        "name": "Test User",
        "password": "secret123"
    }
    response = client.post("/api/users/register", json=user_data)
    assert response.status_code == 201
```

## 🐳 Docker

### Development

```bash
# Build and run
docker-compose up --build

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f backend

# Stop services
docker-compose down
```

### Production

```bash
# Build production image
docker build -t it-analytics-backend .

# Run container
docker run -p 8000:8000 --env-file .env it-analytics-backend
```

## 📊 Performance

### Async Operations

FastAPI supports async/await for better performance:

```python
@router.get("/users")
async def get_users(db: Session = Depends(get_db)):
    """Async endpoint for better concurrency"""
    users = await fetch_users_async(db)
    return users
```

### Database Connection Pooling

Configure in SQLModel/SQLAlchemy:

```python
engine = create_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=10,
    pool_pre_ping=True
)
```

## 🔍 Monitoring & Logging

### Logging Configuration (To be implemented)

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)
```

### Health Checks

```python
@app.get("/health")
async def health_check():
    """System health check endpoint"""
    return {
        "status": "ok",
        "database": await check_database(),
        "ml_models": await check_ml_models()
    }
```

## 📚 API Documentation

FastAPI automatically generates interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Custom Documentation

Add detailed descriptions to endpoints:

```python
@router.post(
    "/users/register",
    response_model=UserResponse,
    status_code=201,
    summary="Register a new user",
    description="Create a new user account with email and password",
    tags=["users"]
)
async def register_user(user: UserCreate):
    """
    Register a new user with the following information:
    
    - **email**: Unique email address
    - **name**: User's full name
    - **password**: Strong password (min 8 characters)
    
    Returns the created user object with ID and timestamps.
    """
    return await create_user(user)
```

## 🚀 Deployment

### Environment Variables

```bash
# .env file
DATABASE_URL=postgresql://user:pass@host:5432/dbname
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
ENVIRONMENT=production
```

### Production Checklist

- [ ] Set strong `SECRET_KEY`
- [ ] Configure production database
- [ ] Enable HTTPS
- [ ] Set up monitoring
- [ ] Configure logging
- [ ] Enable rate limiting
- [ ] Set up backups
- [ ] Configure CI/CD

## 🔗 Related Documentation

- [FastAPI Official Docs](https://fastapi.tiangolo.com/)
- [SQLModel Documentation](https://sqlmodel.tiangolo.com/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [UV Documentation](https://docs.astral.sh/uv/)
- [pytest Documentation](https://docs.pytest.org/)

For more details, see the [Backend README](../backend/README.md).
