# dbt Project - IT Analytics Platform

## 📋 Overview

This dbt (data build tool) project handles data transformations and analytics for the IT Analytics Platform. It transforms raw data from PostgreSQL into analytics-ready models.

## 🏗️ Structure

```
dbt_project/
├── models/           # SQL transformation models
│   └── schema.yml    # Model documentation and tests
├── seeds/            # CSV data files for reference data
├── tests/            # Custom data tests
│   └── generic_tests.yml
├── dbt_project.yml   # Project configuration
└── README.md         # This file
```

## 🎯 Purpose

dbt transforms raw data into clean, analytics-ready datasets for:
- User performance metrics
- Project reports and KPIs
- Task completion statistics
- Feature engineering for ML models

## 🚀 Getting Started

### Prerequisites

```bash
# Install dbt with PostgreSQL adapter
pip install dbt-postgres
```

### Configuration

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
    
    prod:
      type: postgres
      host: production_host
      user: prod_user
      password: prod_password
      port: 5432
      dbname: it_analytics_prod
      schema: analytics
      threads: 4
```

## 📊 Planned Models

### Staging Models (stg_*)
- `stg_users` - Cleaned user data
- `stg_tasks` - Cleaned task data
- `stg_projects` - Cleaned project data

### Intermediate Models (int_*)
- `int_task_metrics` - Task-level calculations
- `int_user_activity` - User activity aggregations

### Mart Models (fct_* and dim_*)
- `fct_task_completion` - Fact table for task completion
- `fct_user_performance` - Fact table for user metrics
- `dim_users` - User dimension table
- `dim_projects` - Project dimension table

### ML Feature Models (ml_*)
- `ml_task_features` - Features for task assignment model
- `ml_bug_features` - Features for bug prediction model
- `ml_time_features` - Features for time estimation model

## 🔧 Commands

### Testing Connection

```bash
dbt debug
```

### Running Models

```bash
# Run all models
dbt run

# Run specific model
dbt run --select stg_users

# Run models in folder
dbt run --select staging.*

# Full refresh (rebuild from scratch)
dbt run --full-refresh
```

### Testing

```bash
# Run all tests
dbt test

# Test specific model
dbt test --select stg_users
```

### Documentation

```bash
# Generate documentation
dbt docs generate

# Serve documentation site
dbt docs serve
```

## 📝 Model Example

### Staging Model

```sql
-- models/staging/stg_users.sql
with source as (
    select * from {{ source('it_analytics', 'users') }}
),

cleaned as (
    select
        id as user_id,
        email,
        name,
        created_at,
        updated_at,
        case 
            when deleted_at is null then true 
            else false 
        end as is_active
    from source
)

select * from cleaned
```

### Mart Model

```sql
-- models/marts/fct_user_performance.sql
with tasks as (
    select * from {{ ref('stg_tasks') }}
),

user_metrics as (
    select
        assigned_to as user_id,
        count(*) as total_tasks,
        count(*) filter (where status = 'completed') as completed_tasks,
        avg(actual_hours) as avg_completion_time,
        sum(case when has_bugs then 1 else 0 end)::float / count(*) as bug_rate
    from tasks
    group by assigned_to
)

select * from user_metrics
```

## 🧪 Testing

### Schema Tests

Defined in `models/schema.yml`:

```yaml
models:
  - name: stg_users
    description: Cleaned user data
    columns:
      - name: user_id
        description: Primary key
        tests:
          - unique
          - not_null
      
      - name: email
        description: User email address
        tests:
          - unique
          - not_null
```

### Custom Tests

Located in `tests/`:

```sql
-- tests/assert_positive_completion_time.sql
select *
from {{ ref('fct_user_performance') }}
where avg_completion_time < 0
```

## 🔄 Development Workflow

1. **Create Model**
   ```bash
   # Create SQL file in models/
   touch models/staging/stg_new_model.sql
   ```

2. **Write Transformation**
   ```sql
   -- Write your SQL transformation
   select * from {{ source('schema', 'table') }}
   ```

3. **Document Model**
   ```yaml
   # Add to models/schema.yml
   - name: stg_new_model
     description: Description here
   ```

4. **Test Model**
   ```bash
   dbt run --select stg_new_model
   dbt test --select stg_new_model
   ```

5. **Generate Docs**
   ```bash
   dbt docs generate
   ```

## 📦 Packages (Planned)

Add useful dbt packages in `packages.yml`:

```yaml
packages:
  - package: dbt-labs/dbt_utils
    version: 1.1.1
  - package: calogica/dbt_expectations
    version: 0.9.0
```

Install packages:
```bash
dbt deps
```

## 🔍 Best Practices

1. **Naming Conventions**
   - Staging: `stg_<source>_<table>`
   - Intermediate: `int_<description>`
   - Facts: `fct_<description>`
   - Dimensions: `dim_<description>`

2. **Model Organization**
   ```
   models/
   ├── staging/      # One-to-one with source tables
   ├── intermediate/ # Business logic transformations
   └── marts/        # Final analytical models
   ```

3. **Testing**
   - Test all primary keys (unique, not_null)
   - Test foreign key relationships
   - Test business logic assumptions

4. **Documentation**
   - Document all models and columns
   - Explain transformations
   - Link to business definitions

## 🚀 Production Deployment

### Scheduling

Use a scheduler like:
- **dbt Cloud**
- **Airflow**
- **Prefect**
- **Dagster**

### Example Airflow DAG

```python
from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime

with DAG(
    'dbt_it_analytics',
    start_date=datetime(2024, 1, 1),
    schedule_interval='0 2 * * *',  # Daily at 2 AM
    catchup=False
) as dag:
    
    dbt_run = BashOperator(
        task_id='dbt_run',
        bash_command='cd /path/to/dbt_project && dbt run'
    )
    
    dbt_test = BashOperator(
        task_id='dbt_test',
        bash_command='cd /path/to/dbt_project && dbt test'
    )
    
    dbt_run >> dbt_test
```

## 📚 Resources

- [dbt Documentation](https://docs.getdbt.com/)
- [dbt Discourse Community](https://discourse.getdbt.com/)
- [dbt Learn](https://courses.getdbt.com/)
- [dbt Best Practices](https://docs.getdbt.com/guides/best-practices)

## 🔗 Related Documentation

- [Architecture Documentation](../docs/ARCHITECTURE.md)
- [Backend Documentation](../docs/backend.md)
- [Setup Guide](../docs/SETUP.md)
