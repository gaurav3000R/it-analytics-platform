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

<pre class="overflow-visible!" data-start="2240" data-end="3318"><div class="contain-inline-size rounded-2xl relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"></div></div></pre>



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
## ⚙️ Setup Instructions

1. **Init Project**

```bash
uv init backend
cd backend
uv add fastapi[all] sqlmodel psycopg2 alembic pydantic scikit-learn
uv add pytest httpx
```


2. **Docker Setup**

* Create `Dockerfile` with FastAPI + UV.
* Create `docker-compose.yml` with services:
  * backend
  * postgres
  * dbt

3. **DB Setup**

* Use Alembic migrations.
* Define models: `User`, `Task`, `Skill`, `TaskHistory`.

4. **ML Integration**

* Store training data in Postgres.
* Train ML models offline (scikit-learn).
* Serve via `/predictions/`.

5. **Testing**

* Write pytest unit + integration tests.
* GitHub Actions workflow:
  * Install with UV.
  * Run tests + coverage.
  * Build docker image.

---

## 🚀 Deliverables for the Agent

1. Fully working **FastAPI backend** with all endpoints.
2. **Postgres integration** (CRUD for users, tasks).
3. **ML prediction endpoints** implemented with mock models (train → serve).
4. **dbt integration** for analytics tables.
5. **Dockerized project** with `docker-compose` (backend + postgres + dbt).
6. **CI/CD pipeline** (tests + lint).
7. **Documentation** in `README.md`.

---

## 📖 References (latest docs to use)

* FastAPI → [https://fastapi.tiangolo.com/]()
* SQLModel → [https://sqlmodel.tiangolo.com/]()
* Alembic → [https://alembic.sqlalchemy.org/]()
* dbt → [https://docs.getdbt.com/]()
* UV → [https://docs.astral.sh/uv/]()
* Docker → [https://docs.docker.com/]()

---

## ✅ Acceptance Criteria

* Code should follow  **PEP8 + typing** .
* Every endpoint must have  **tests** .
* DB migrations should work smoothly.
* ML endpoints return  **valid JSON responses** .
* System runs with one command:
  <pre class="overflow-visible!" data-start="4773" data-end="4814"><div class="contain-inline-size rounded-2xl relative bg-token-sidebar-surface-primary"><div class="sticky top-9"><div class="absolute end-0 bottom-0 flex h-9 items-center pe-2"><div class="bg-token-bg-elevated-secondary text-token-text-secondary flex items-center gap-4 rounded-sm px-2 font-sans text-xs"></div></div></div><div class="overflow-y-auto p-4" dir="ltr"><code class="whitespace-pre! language-bash"><span><span>docker-compose up --build</span></span></code></div></div></pre>
