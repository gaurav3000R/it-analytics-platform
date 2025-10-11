#!/usr/bin/env python3
"""
Initialize database schema for cost forecasting feature
Run this to add necessary columns and tables
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import get_pg_connection
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_cost_forecasting_schema():
    """Initialize cost forecasting schema"""
    
    print("=" * 60)
    print("Initializing Cost Forecasting Schema")
    print("=" * 60)
    
    sql_statements = [
        # Add missing columns to employees table
        """
        ALTER TABLE employees 
        ADD COLUMN IF NOT EXISTS hourly_rate DECIMAL(10, 2) DEFAULT 75.00;
        """,
        """
        ALTER TABLE employees 
        ADD COLUMN IF NOT EXISTS hire_date DATE DEFAULT CURRENT_DATE;
        """,
        
        # Add missing columns to projects table
        """
        ALTER TABLE projects 
        ADD COLUMN IF NOT EXISTS name VARCHAR(255);
        """,
        """
        ALTER TABLE projects 
        ADD COLUMN IF NOT EXISTS client VARCHAR(255);
        """,
        """
        ALTER TABLE projects 
        ADD COLUMN IF NOT EXISTS start_date DATE;
        """,
        """
        ALTER TABLE projects 
        ADD COLUMN IF NOT EXISTS end_date DATE;
        """,
        """
        ALTER TABLE projects 
        ADD COLUMN IF NOT EXISTS status VARCHAR(50) DEFAULT 'active';
        """,
        """
        ALTER TABLE projects 
        ADD COLUMN IF NOT EXISTS current_spend DECIMAL(15, 2) DEFAULT 0;
        """,
        
        # Add missing columns to daily_logs
        """
        ALTER TABLE daily_logs 
        ADD COLUMN IF NOT EXISTS task_description TEXT;
        """,
        """
        ALTER TABLE daily_logs 
        ADD COLUMN IF NOT EXISTS task_category VARCHAR(100);
        """,
        """
        ALTER TABLE daily_logs 
        ADD COLUMN IF NOT EXISTS completion_percentage DECIMAL(5, 2) DEFAULT 0;
        """,
        """
        ALTER TABLE daily_logs 
        ADD COLUMN IF NOT EXISTS issues_reported INTEGER DEFAULT 0;
        """,
        
        # Create cost_forecasts table
        """
        CREATE TABLE IF NOT EXISTS cost_forecasts (
            id SERIAL PRIMARY KEY,
            project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
            forecast_date DATE DEFAULT CURRENT_DATE,
            current_spend DECIMAL(15, 2),
            total_budget DECIMAL(15, 2),
            forecasted_additional_cost DECIMAL(15, 2),
            projected_final_cost DECIMAL(15, 2),
            overrun_probability DECIMAL(5, 4),
            overrun_amount DECIMAL(15, 2),
            days_remaining INTEGER,
            avg_daily_burn_rate DECIMAL(15, 2),
            forecast_accuracy_score DECIMAL(5, 2),
            model_confidence DECIMAL(5, 2),
            risk_factors JSONB,
            recommendations JSONB,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            CONSTRAINT unique_forecast UNIQUE(project_id, forecast_date)
        );
        """,
        
        # Create cost_tracking table
        """
        CREATE TABLE IF NOT EXISTS cost_tracking (
            id SERIAL PRIMARY KEY,
            project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
            date DATE NOT NULL,
            daily_cost DECIMAL(15, 2),
            cumulative_cost DECIMAL(15, 2),
            budget_utilization_percentage DECIMAL(5, 2),
            burn_rate DECIMAL(15, 2),
            team_size INTEGER,
            avg_hourly_rate DECIMAL(10, 2),
            hours_logged DECIMAL(10, 2),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            CONSTRAINT unique_cost_tracking UNIQUE(project_id, date)
        );
        """,
        
        # Create indexes
        """
        CREATE INDEX IF NOT EXISTS idx_cost_forecasts_project_id 
        ON cost_forecasts(project_id);
        """,
        """
        CREATE INDEX IF NOT EXISTS idx_cost_forecasts_forecast_date 
        ON cost_forecasts(forecast_date);
        """,
        """
        CREATE INDEX IF NOT EXISTS idx_cost_tracking_project_id 
        ON cost_tracking(project_id);
        """,
        """
        CREATE INDEX IF NOT EXISTS idx_cost_tracking_date 
        ON cost_tracking(date);
        """,
        """
        CREATE INDEX IF NOT EXISTS idx_employees_hourly_rate 
        ON employees(hourly_rate);
        """,
        
        # Create view for cost summary
        """
        CREATE OR REPLACE VIEW project_cost_summary AS
        SELECT 
            p.id,
            p.project_id,
            p.name,
            p.project_budget_usd as total_budget,
            p.current_spend,
            COALESCE(ct.cumulative_cost, 0) as tracked_cumulative_cost,
            COALESCE(cf.projected_final_cost, 0) as projected_final_cost,
            COALESCE(cf.overrun_probability, 0) as overrun_probability,
            COALESCE(cf.overrun_amount, 0) as overrun_amount,
            p.start_date,
            p.end_date,
            CASE 
                WHEN p.end_date IS NOT NULL THEN 
                    GREATEST(0, (p.end_date - CURRENT_DATE))
                ELSE 180
            END as days_remaining
        FROM projects p
        LEFT JOIN LATERAL (
            SELECT cumulative_cost 
            FROM cost_tracking 
            WHERE project_id = p.id 
            ORDER BY date DESC 
            LIMIT 1
        ) ct ON true
        LEFT JOIN LATERAL (
            SELECT projected_final_cost, overrun_probability, overrun_amount
            FROM cost_forecasts 
            WHERE project_id = p.id 
            ORDER BY forecast_date DESC 
            LIMIT 1
        ) cf ON true;
        """
    ]
    
    try:
        with get_pg_connection() as conn:
            cursor = conn.cursor()
            
            for i, sql in enumerate(sql_statements, 1):
                try:
                    cursor.execute(sql)
                    # Extract table/column name for better logging
                    if 'ADD COLUMN' in sql:
                        column_name = sql.split('ADD COLUMN IF NOT EXISTS')[1].split()[0]
                        print(f"✅ [{i}/{len(sql_statements)}] Added column: {column_name}")
                    elif 'CREATE TABLE' in sql:
                        table_name = sql.split('CREATE TABLE IF NOT EXISTS')[1].split()[0]
                        print(f"✅ [{i}/{len(sql_statements)}] Created table: {table_name}")
                    elif 'CREATE INDEX' in sql:
                        index_name = sql.split('CREATE INDEX IF NOT EXISTS')[1].split()[0]
                        print(f"✅ [{i}/{len(sql_statements)}] Created index: {index_name}")
                    elif 'CREATE OR REPLACE VIEW' in sql:
                        view_name = sql.split('CREATE OR REPLACE VIEW')[1].split()[0]
                        print(f"✅ [{i}/{len(sql_statements)}] Created view: {view_name}")
                    else:
                        print(f"✅ [{i}/{len(sql_statements)}] Executed SQL statement")
                except Exception as e:
                    print(f"⚠️  [{i}/{len(sql_statements)}] Warning: {e}")
            
            cursor.close()
            
        print("\n" + "=" * 60)
        print("✅ Cost Forecasting Schema Initialized Successfully!")
        print("=" * 60)
        print("\nNext steps:")
        print("  1. Load project CSV data: python main.py --load-csv")
        print("  2. Generate sample cost data: python generate_cost_data.py")
        print("  3. Start the server: python main.py --run-server")
        return 0
        
    except Exception as e:
        print(f"\n❌ Error initializing schema: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit(init_cost_forecasting_schema())