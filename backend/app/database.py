# database.py

from supabase import create_client, Client
from app.config import settings
import logging
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from typing import Optional, Generator
from contextlib import contextmanager

logger = logging.getLogger(__name__)

# Initialize Supabase client as singleton
supabase: Client = create_client(
    supabase_url=settings.SUPABASE_URL,
    supabase_key=settings.SUPABASE_KEY
)


def get_db() -> Generator[Client, None, None]:
    """
    Dependency that returns the Supabase client.
    This maintains compatibility with the existing FastAPI dependency injection pattern.
    """
    try:
        yield supabase
    except Exception as e:
        logger.error(f"Error in Supabase client dependency: {e}")
        raise


def connect_db() -> Optional[Client]:
    """
    Establishes and returns a Supabase client connection for API operations.
    
    Returns:
        Client: Supabase client object or None if error.
    """
    try:
        if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
            raise ValueError("SUPABASE_URL or SUPABASE_KEY not set in environment variables")
        
        # Return the singleton instance
        logger.info("✅ Supabase client connected successfully")
        return supabase
    except Exception as e:
        logger.error(f"❌ Supabase connection error: {e}")
        return None


@contextmanager
def get_pg_connection():
    """Context manager for PostgreSQL connections with automatic cleanup."""
    if not settings.SUPABASE_DATABASE_URL:
        raise ValueError("SUPABASE_DATABASE_URL is required for database initialization")
    
    conn = None
    try:
        conn = psycopg2.connect(settings.SUPABASE_DATABASE_URL)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        yield conn
    except psycopg2.OperationalError as e:
        logger.error(f"❌ Database connection error: {e}")
        logger.error("Please verify SUPABASE_DATABASE_URL is correct and database is accessible")
        raise
    finally:
        if conn:
            conn.close()
            logger.debug("Database connection closed")


def init_db():
    """
    Initialize database tables if they don't exist using direct PostgreSQL connection.
    This should be called on application startup.
    """
    
    # Table definitions with better organization
    TABLE_DEFINITIONS = {
        'projects': """
            CREATE TABLE IF NOT EXISTS projects (
                id SERIAL PRIMARY KEY,
                project_id VARCHAR(255) UNIQUE NOT NULL,
                project_type VARCHAR(100),
                project_budget_usd DECIMAL(15, 2),
                team_size INTEGER,
                complexity_score DECIMAL(5, 2),
                risk_level VARCHAR(50),
                team_experience_level VARCHAR(50),
                methodology_used VARCHAR(100),
                stakeholder_count INTEGER,
                change_request_frequency VARCHAR(50),
                budget_utilization_rate DECIMAL(5, 2),
                technical_debt_level VARCHAR(50),
                market_volatility VARCHAR(50),
                estimated_timeline_months INTEGER,
                past_similar_projects INTEGER,
                external_dependencies_count INTEGER,
                project_phase VARCHAR(50),
                requirement_stability VARCHAR(50),
                team_turnover_rate VARCHAR(50),
                vendor_reliability_score DECIMAL(5, 2),
                historical_risk_incidents INTEGER,
                communication_frequency VARCHAR(50),
                resource_availability VARCHAR(50),
                current_phase_duration_months DECIMAL(5, 2),
                project_manager_experience VARCHAR(50),
                stakeholder_engagement_level VARCHAR(50),
                key_stakeholder_availability VARCHAR(50),
                team_colocation VARCHAR(50),
                regulatory_compliance_level VARCHAR(50),
                executive_sponsorship VARCHAR(50),
                funding_source VARCHAR(50),
                organizational_change_frequency VARCHAR(50),
                org_process_maturity VARCHAR(50),
                risk_management_maturity VARCHAR(50),
                change_control_maturity VARCHAR(50),
                technology_familiarity VARCHAR(50),
                integration_complexity VARCHAR(50),
                tech_environment_stability VARCHAR(50),
                data_security_requirements VARCHAR(50),
                industry_volatility VARCHAR(50),
                geographical_distribution VARCHAR(50),
                client_experience_level VARCHAR(50),
                contract_type VARCHAR(50),
                resource_contention_level VARCHAR(50),
                schedule_pressure VARCHAR(50),
                priority_level VARCHAR(50),
                cross_functional_dependencies INTEGER,
                previous_delivery_success_rate DECIMAL(5, 2),
                documentation_quality VARCHAR(50),
                project_start_month VARCHAR(50),
                seasonal_risk_factor DECIMAL(5, 2),
                ai_risk_analysis TEXT,
                ai_recommendations TEXT,
                ai_insights_updated_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """,
        'employees': """
            CREATE TABLE IF NOT EXISTS employees (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                role VARCHAR(100),
                email VARCHAR(255) UNIQUE,
                max_hours_per_day DECIMAL(5, 2),
                skill_level VARCHAR(50),
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """,
        'daily_logs': """
            CREATE TABLE IF NOT EXISTS daily_logs (
                id SERIAL PRIMARY KEY,
                project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
                employee_id INTEGER REFERENCES employees(id) ON DELETE CASCADE,
                date DATE NOT NULL,
                hours_logged DECIMAL(5, 2),
                tasks_completed INTEGER,
                bugs_found INTEGER,
                bugs_fixed INTEGER,
                story_points_completed DECIMAL(5, 2),
                code_quality_score DECIMAL(5, 2),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                CONSTRAINT unique_daily_log UNIQUE(project_id, employee_id, date)
            )
        """,
        'risk_scores': """
            CREATE TABLE IF NOT EXISTS risk_scores (
                id SERIAL PRIMARY KEY,
                project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
                date DATE DEFAULT CURRENT_DATE,
                overall_risk_score DECIMAL(5, 2),
                schedule_risk DECIMAL(5, 2),
                budget_risk DECIMAL(5, 2),
                quality_risk DECIMAL(5, 2),
                resource_risk DECIMAL(5, 2),
                technical_risk DECIMAL(5, 2),
                risk_factors JSONB,
                predictions JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                CONSTRAINT unique_risk_score UNIQUE(project_id, date)
            )
        """,
        'anomalies': """
            CREATE TABLE IF NOT EXISTS anomalies (
                id SERIAL PRIMARY KEY,
                project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
                employee_id INTEGER REFERENCES employees(id) ON DELETE SET NULL,
                anomaly_type VARCHAR(100),
                severity VARCHAR(50),
                description TEXT,
                detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_resolved BOOLEAN DEFAULT FALSE,
                resolved_at TIMESTAMP,
                metadata JSONB
            )
        """,
        'sprints': """
            CREATE TABLE IF NOT EXISTS sprints (
                id SERIAL PRIMARY KEY,
                project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
                sprint_number INTEGER,
                start_date DATE,
                end_date DATE,
                planned_story_points DECIMAL(5, 2),
                completed_story_points DECIMAL(5, 2),
                velocity DECIMAL(5, 2),
                bugs_found INTEGER,
                bugs_fixed INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                CONSTRAINT unique_sprint UNIQUE(project_id, sprint_number)
            )
        """
    }

    # Index definitions with better organization
    INDEX_DEFINITIONS = [
        ("idx_projects_project_id", "projects", "project_id"),
        ("idx_projects_risk_level", "projects", "risk_level"),
        ("idx_daily_logs_project_id", "daily_logs", "project_id"),
        ("idx_daily_logs_employee_id", "daily_logs", "employee_id"),
        ("idx_daily_logs_date", "daily_logs", "date"),
        ("idx_risk_scores_project_id", "risk_scores", "project_id"),
        ("idx_risk_scores_date", "risk_scores", "date"),
        ("idx_anomalies_project_id", "anomalies", "project_id"),
        ("idx_anomalies_detected_at", "anomalies", "detected_at"),
        ("idx_anomalies_is_resolved", "anomalies", "is_resolved"),
        ("idx_sprints_project_id", "sprints", "project_id")
    ]

    try:
        with get_pg_connection() as conn:
            cursor = conn.cursor()

            # Create tables
            logger.info("Creating tables...")
            for table_name, table_sql in TABLE_DEFINITIONS.items():
                try:
                    cursor.execute(table_sql)
                    logger.debug(f"  ✓ Table '{table_name}' created/verified")
                except Exception as e:
                    logger.error(f"  ✗ Error creating table '{table_name}': {e}")
                    raise

            # Create indexes
            logger.info("Creating indexes...")
            for idx_name, table_name, column_name in INDEX_DEFINITIONS:
                try:
                    cursor.execute(f"CREATE INDEX IF NOT EXISTS {idx_name} ON {table_name}({column_name})")
                    logger.debug(f"  ✓ Index '{idx_name}' created/verified")
                except Exception as e:
                    logger.warning(f"  ⚠ Index '{idx_name}' warning: {e}")

            # Verify table creation
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name IN ('projects', 'employees', 'daily_logs', 'risk_scores', 'anomalies', 'sprints')
                ORDER BY table_name
            """)
            
            created_tables = [row[0] for row in cursor.fetchall()]
            
            if len(created_tables) == len(TABLE_DEFINITIONS):
                logger.info(f"✅ Database initialized successfully with {len(created_tables)} tables")
            else:
                missing = set(TABLE_DEFINITIONS.keys()) - set(created_tables)
                logger.warning(f"⚠ Missing tables: {', '.join(missing)}")
                
            cursor.close()

    except psycopg2.Error as e:
        logger.error(f"❌ PostgreSQL error during database initialization: {e}")
        raise
    except Exception as e:
        logger.error(f"❌ Unexpected error initializing database: {e}")
        raise


def test_connection() -> bool:
    """
    Test database connection and return status.
    
    Returns:
        bool: True if connection is successful, False otherwise
    """
    try:
        response = supabase.table('projects').select("id").limit(1).execute()
        logger.info("✅ Database connection test successful")
        return True
    except Exception as e:
        logger.error(f"❌ Database connection test failed: {e}")
        return False


def get_table_stats() -> dict:
    """
    Get statistics about all tables in the database.
    
    Returns:
        dict: Dictionary with table names as keys and row counts as values
    """
    stats = {}
    try:
        with get_pg_connection() as conn:
            cursor = conn.cursor()
            for table_name in ['projects', 'employees', 'daily_logs', 'risk_scores', 'anomalies', 'sprints']:
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = cursor.fetchone()[0]
                stats[table_name] = count
            cursor.close()
        logger.info(f"📊 Table statistics: {stats}")
        return stats
    except Exception as e:
        logger.error(f"❌ Error getting table stats: {e}")
        return {}