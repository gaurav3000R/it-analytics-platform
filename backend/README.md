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