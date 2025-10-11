import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Any, Optional, Generator
from pathlib import Path
from supabase import Client
from datetime import datetime, timedelta

from app.database import connect_db

logger = logging.getLogger(__name__)

class CSVLoaderService:
    def __init__(self):
        self.csv_file_path = "app/data/project_risk_dataset.csv"

    def load_csv_data(self, file_path: Optional[str] = None) -> pd.DataFrame:
        """Load CSV data into pandas DataFrame"""
        csv_path = file_path or self.csv_file_path

        try:
            if not Path(csv_path).exists():
                raise FileNotFoundError(f"CSV file not found: {csv_path}")

            df = pd.read_csv(csv_path)
            logger.info(f"Loaded CSV with {len(df)} rows and {len(df.columns)} columns")

            # Basic data cleaning
            df = self._clean_data(df)

            return df

        except Exception as e:
            logger.error(f"Error loading CSV: {e}")
            raise

    def _safe_int(self, value) -> Optional[int]:
        """Safely convert value to int, handling strings, floats, and edge cases"""
        try:
            if pd.isna(value) or value is None or value == '':
                return None
            
            # Handle string values that might be "nan", "NaN", etc.
            if isinstance(value, str):
                value_lower = value.lower().strip()
                if value_lower in ('nan', 'none', 'null', ''):
                    return None
            
            # Convert to float first to handle strings like "32.0" or numbers like 32.0
            float_value = float(value)
            
            # Check if the value is a whole number
            if float_value.is_integer():
                return int(float_value)
            
            # If not a whole number, round it and log a warning
            logger.warning(f"Value {value} is not a whole number ({float_value}), rounding to {round(float_value)}")
            return round(float_value)
            
        except (ValueError, TypeError) as e:
            logger.warning(f"Failed to convert {value} to int: {e}")
            return None


    def _clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and preprocess the CSV data"""
        # Convert column names to lowercase with underscores
        df.columns = [col.lower().replace(' ', '_') for col in df.columns]

        # Define columns that should be integers based on the projects table schema
        integer_columns = [
            'team_size',
            'stakeholder_count',
            'past_similar_projects',
            'external_dependencies_count',
            'historical_risk_incidents',
            'estimated_timeline_months',
            'cross_functional_dependencies'
        ]

        # Convert integer columns - CRITICAL FIX
        for col in integer_columns:
            if col in df.columns:
                # First convert to float to handle "32.0" strings
                df[col] = pd.to_numeric(df[col], errors='coerce')
                # Round to nearest integer
                df[col] = df[col].round()
                # Convert to Int64 (nullable integer type)
                df[col] = df[col].astype('Int64')
                logger.debug(f"Converted column {col} to integer, null count: {df[col].isna().sum()}")

        # Handle missing values for numeric (float) columns
        numeric_columns = df.select_dtypes(include=[np.number]).columns.difference(integer_columns)
        df[numeric_columns] = df[numeric_columns].fillna(df[numeric_columns].median())

        # Handle missing values for categorical columns
        categorical_columns = df.select_dtypes(include=['object']).columns
        df[categorical_columns] = df[categorical_columns].fillna('Unknown')

        # Standardize categorical values
        if 'risk_level' in df.columns:
            df['risk_level'] = df['risk_level'].str.strip().str.title()

        # Ensure specific columns are treated as strings
        string_columns = [
            'project_type', 'methodology_used', 'team_experience_level', 'change_request_frequency',
            'project_phase', 'requirement_stability', 'team_turnover_rate', 'communication_frequency',
            'resource_availability', 'project_manager_experience', 'stakeholder_engagement_level',
            'key_stakeholder_availability', 'team_colocation', 'regulatory_compliance_level',
            'executive_sponsorship', 'funding_source', 'organizational_change_frequency',
            'org_process_maturity', 'risk_management_maturity', 'change_control_maturity',
            'technology_familiarity', 'integration_complexity', 'technical_debt_level',
            'tech_environment_stability', 'data_security_requirements', 'market_volatility',
            'industry_volatility', 'geographical_distribution', 'client_experience_level',
            'contract_type', 'resource_contention_level', 'schedule_pressure', 'priority_level',
            'documentation_quality', 'project_start_month'
        ]
        for col in string_columns:
            if col in df.columns:
                df[col] = df[col].astype(str)

        logger.info("Data cleaning completed")
        return df

    def csv_to_database(self, db: Client = None, file_path: Optional[str] = None,
                   clear_existing: bool = False, batch_size: int = 100) -> Dict[str, Any]:
        """Load CSV data into database using batch inserts for better performance"""
        
        # Get database connection if not provided
        if db is None:
            db = connect_db()
            if db is None:
                raise Exception("Failed to connect to database")
        elif isinstance(db, Generator):
            # Handle case where db is a generator (e.g., from FastAPI dependency)
            db = next(db)  # Extract the Client from the generator
        
        if clear_existing:
            logger.info("Clearing existing projects...")
            db.table("projects").delete().neq("id", 0).execute()  # Use neq instead of empty delete

        df = self.load_csv_data(file_path)

        projects_created = 0
        projects_updated = 0
        errors = []

        # Get all existing project IDs in one query for faster lookups
        logger.info("Fetching existing projects...")
        existing_projects_response = db.table("projects").select("project_id, id").execute()
        existing_project_ids = {p['project_id']: p for p in existing_projects_response.data}
        logger.info(f"Found {len(existing_project_ids)} existing projects")

        # Separate new projects from updates
        new_projects = []
        projects_to_update = []

        for index, row in df.iterrows():
            try:
                project_id = str(row.get('project_id', f'proj_{index}'))
                
                if project_id in existing_project_ids:
                    # Prepare update data
                    existing_project = existing_project_ids[project_id]
                    update_data = self._prepare_update_data(row, existing_project)
                    projects_to_update.append({
                        'project_id': project_id,
                        'data': update_data
                    })
                else:
                    # Prepare new project
                    project = self._create_project_from_row(row, index)
                    new_projects.append(project)

            except Exception as e:
                error_msg = f"Error preparing row {index}: {e}"
                logger.error(error_msg)
                errors.append(error_msg)

        # Batch insert new projects
        if new_projects:
            logger.info(f"Inserting {len(new_projects)} new projects in batches of {batch_size}...")
            for i in range(0, len(new_projects), batch_size):
                batch = new_projects[i:i + batch_size]
                try:
                    db.table("projects").insert(batch).execute()
                    projects_created += len(batch)
                    logger.info(f"Inserted batch {i // batch_size + 1}: {len(batch)} projects")
                except Exception as e:
                    error_msg = f"Error inserting batch {i // batch_size + 1}: {e}"
                    logger.error(error_msg)
                    errors.append(error_msg)

        # Batch update existing projects
        if projects_to_update:
            logger.info(f"Updating {len(projects_to_update)} existing projects in batches of {batch_size}...")
            for i in range(0, len(projects_to_update), batch_size):
                batch = projects_to_update[i:i + batch_size]
                for update_item in batch:
                    try:
                        db.table("projects").update(update_item['data']).eq("project_id", update_item['project_id']).execute()
                        projects_updated += 1
                    except Exception as e:
                        error_msg = f"Error updating project {update_item['project_id']}: {e}"
                        logger.error(error_msg)
                        errors.append(error_msg)
                logger.info(f"Updated batch {i // batch_size + 1}: {len(batch)} projects")

        result = {
            "total_rows_processed": len(df),
            "projects_created": projects_created,
            "projects_updated": projects_updated,
            "errors": errors,
            "success_rate": ((projects_created + projects_updated) / len(df)) * 100
        }

        logger.info(f"CSV import completed: {result}")
        return result

    def _create_project_from_row(self, row: pd.Series, index: int) -> Dict:
        """Create a project dictionary from a CSV row"""

        project = {
            # Use project_id from CSV or generate one
            "project_id": str(row.get('project_id', f'PROJ_{index:03d}')),
            # Project Demographics
            "project_type": str(row.get('project_type', 'Unknown')),
            "team_size": self._safe_int(row.get('team_size')),
            "project_budget_usd": self._safe_float(row.get('project_budget_usd')),
            "estimated_timeline_months": self._safe_float(row.get('estimated_timeline_months')),
            "complexity_score": self._safe_float(row.get('complexity_score')),
            "stakeholder_count": self._safe_int(row.get('stakeholder_count')),
            "methodology_used": str(row.get('methodology_used', 'Unknown')),
            "team_experience_level": str(row.get('team_experience_level', 'Unknown')),
            "past_similar_projects": self._safe_int(row.get('past_similar_projects')),
            # Operational Metrics
            "external_dependencies_count": self._safe_int(row.get('external_dependencies_count')),
            "change_request_frequency": str(row.get('change_request_frequency', 'Unknown')),
            "project_phase": str(row.get('project_phase', 'Unknown')),
            "requirement_stability": str(row.get('requirement_stability', 'Unknown')),
            "team_turnover_rate": str(row.get('team_turnover_rate', 'Unknown')),
            "vendor_reliability_score": self._safe_float(row.get('vendor_reliability_score')),
            "historical_risk_incidents": self._safe_int(row.get('historical_risk_incidents')),
            "communication_frequency": str(row.get('communication_frequency', 'Unknown')),
            "budget_utilization_rate": self._safe_float(row.get('budget_utilization_rate')),
            "resource_availability": str(row.get('resource_availability', 'Unknown')),
            "current_phase_duration_months": self._safe_float(row.get('current_phase_duration_months')),
            # Human Factors
            "project_manager_experience": str(row.get('project_manager_experience', 'Unknown')),
            "stakeholder_engagement_level": str(row.get('stakeholder_engagement_level', 'Unknown')),
            "key_stakeholder_availability": str(row.get('key_stakeholder_availability', 'Unknown')),
            "team_colocation": str(row.get('team_colocation', 'Unknown')),
            # Organizational Context
            "regulatory_compliance_level": str(row.get('regulatory_compliance_level', 'Unknown')),
            "executive_sponsorship": str(row.get('executive_sponsorship', 'Unknown')),
            "funding_source": str(row.get('funding_source', 'Unknown')),
            "organizational_change_frequency": str(row.get('organizational_change_frequency', 'Unknown')),
            "org_process_maturity": str(row.get('org_process_maturity', 'Unknown')),
            "risk_management_maturity": str(row.get('risk_management_maturity', 'Unknown')),
            "change_control_maturity": str(row.get('change_control_maturity', 'Unknown')),
            # Technical Aspects
            "technology_familiarity": str(row.get('technology_familiarity', 'Unknown')),
            "integration_complexity": str(row.get('integration_complexity', 'Unknown')),
            "technical_debt_level": str(row.get('technical_debt_level', 'Unknown')),
            "tech_environment_stability": str(row.get('tech_environment_stability', 'Unknown')),
            "data_security_requirements": str(row.get('data_security_requirements', 'Unknown')),
            # External Influences
            "market_volatility": str(row.get('market_volatility', 'Unknown')),
            "industry_volatility": str(row.get('industry_volatility', 'Unknown')),
            "geographical_distribution": str(row.get('geographical_distribution', 'Unknown')),
            "client_experience_level": str(row.get('client_experience_level', 'Unknown')),
            "contract_type": str(row.get('contract_type', 'Unknown')),
            "resource_contention_level": str(row.get('resource_contention_level', 'Unknown')),
            # Additional Fields
            "schedule_pressure": str(row.get('schedule_pressure', 'Unknown')),
            "priority_level": str(row.get('priority_level', 'Unknown')),
            "cross_functional_dependencies": self._safe_int(row.get('cross_functional_dependencies')),
            "previous_delivery_success_rate": self._safe_float(row.get('previous_delivery_success_rate')),
            "documentation_quality": str(row.get('documentation_quality', 'Unknown')),
            "project_start_month": str(row.get('project_start_month', 'Unknown')),
            "seasonal_risk_factor": self._safe_float(row.get('seasonal_risk_factor')),
            # Target Variable
            "risk_level": str(row.get('risk_level', 'Unknown')),
            # System fields
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }

        return project

    def _prepare_update_data(self, row: pd.Series, existing_project: Dict) -> Dict:
        """Prepare update data for an existing project"""
        update_data = {
            "project_type": str(row.get('project_type', existing_project.get('project_type', 'Unknown'))),
            "team_size": self._safe_int(row.get('team_size')) or existing_project.get('team_size'),
            "project_budget_usd": self._safe_float(row.get('project_budget_usd')) or existing_project.get('project_budget_usd'),
            "estimated_timeline_months": self._safe_float(row.get('estimated_timeline_months')) or existing_project.get('estimated_timeline_months'),
            "complexity_score": self._safe_float(row.get('complexity_score')) or existing_project.get('complexity_score'),
            "stakeholder_count": self._safe_int(row.get('stakeholder_count')) or existing_project.get('stakeholder_count'),
            "methodology_used": str(row.get('methodology_used', existing_project.get('methodology_used', 'Unknown'))),
            "team_experience_level": str(row.get('team_experience_level', existing_project.get('team_experience_level', 'Unknown'))),
            "past_similar_projects": self._safe_int(row.get('past_similar_projects')) or existing_project.get('past_similar_projects'),
            "external_dependencies_count": self._safe_int(row.get('external_dependencies_count')) or existing_project.get('external_dependencies_count'),
            "change_request_frequency": str(row.get('change_request_frequency', existing_project.get('change_request_frequency', 'Unknown'))),
            "project_phase": str(row.get('project_phase', existing_project.get('project_phase', 'Unknown'))),
            "requirement_stability": str(row.get('requirement_stability', existing_project.get('requirement_stability', 'Unknown'))),
            "team_turnover_rate": str(row.get('team_turnover_rate', existing_project.get('team_turnover_rate', 'Unknown'))),
            "vendor_reliability_score": self._safe_float(row.get('vendor_reliability_score')) or existing_project.get('vendor_reliability_score'),
            "historical_risk_incidents": self._safe_int(row.get('historical_risk_incidents')) or existing_project.get('historical_risk_incidents'),
            "communication_frequency": str(row.get('communication_frequency', existing_project.get('communication_frequency', 'Unknown'))),
            "budget_utilization_rate": self._safe_float(row.get('budget_utilization_rate')) or existing_project.get('budget_utilization_rate'),
            "resource_availability": str(row.get('resource_availability', existing_project.get('resource_availability', 'Unknown'))),
            "current_phase_duration_months": self._safe_float(row.get('current_phase_duration_months')) or existing_project.get('current_phase_duration_months'),
            "project_manager_experience": str(row.get('project_manager_experience', existing_project.get('project_manager_experience', 'Unknown'))),
            "stakeholder_engagement_level": str(row.get('stakeholder_engagement_level', existing_project.get('stakeholder_engagement_level', 'Unknown'))),
            "key_stakeholder_availability": str(row.get('key_stakeholder_availability', existing_project.get('key_stakeholder_availability', 'Unknown'))),
            "team_colocation": str(row.get('team_colocation', existing_project.get('team_colocation', 'Unknown'))),
            "regulatory_compliance_level": str(row.get('regulatory_compliance_level', existing_project.get('regulatory_compliance_level', 'Unknown'))),
            "executive_sponsorship": str(row.get('executive_sponsorship', existing_project.get('executive_sponsorship', 'Unknown'))),
            "funding_source": str(row.get('funding_source', existing_project.get('funding_source', 'Unknown'))),
            "organizational_change_frequency": str(row.get('organizational_change_frequency', existing_project.get('organizational_change_frequency', 'Unknown'))),
            "org_process_maturity": str(row.get('org_process_maturity', existing_project.get('org_process_maturity', 'Unknown'))),
            "risk_management_maturity": str(row.get('risk_management_maturity', existing_project.get('risk_management_maturity', 'Unknown'))),
            "change_control_maturity": str(row.get('change_control_maturity', existing_project.get('change_control_maturity', 'Unknown'))),
            "technology_familiarity": str(row.get('technology_familiarity', existing_project.get('technology_familiarity', 'Unknown'))),
            "integration_complexity": str(row.get('integration_complexity', existing_project.get('integration_complexity', 'Unknown'))),
            "technical_debt_level": str(row.get('technical_debt_level', existing_project.get('technical_debt_level', 'Unknown'))),
            "tech_environment_stability": str(row.get('tech_environment_stability', existing_project.get('tech_environment_stability', 'Unknown'))),
            "data_security_requirements": str(row.get('data_security_requirements', existing_project.get('data_security_requirements', 'Unknown'))),
            "market_volatility": str(row.get('market_volatility', existing_project.get('market_volatility', 'Unknown'))),
            "industry_volatility": str(row.get('industry_volatility', existing_project.get('industry_volatility', 'Unknown'))),
            "geographical_distribution": str(row.get('geographical_distribution', existing_project.get('geographical_distribution', 'Unknown'))),
            "client_experience_level": str(row.get('client_experience_level', existing_project.get('client_experience_level', 'Unknown'))),
            "contract_type": str(row.get('contract_type', existing_project.get('contract_type', 'Unknown'))),
            "resource_contention_level": str(row.get('resource_contention_level', existing_project.get('resource_contention_level', 'Unknown'))),
            "schedule_pressure": str(row.get('schedule_pressure', existing_project.get('schedule_pressure', 'Unknown'))),
            "priority_level": str(row.get('priority_level', existing_project.get('priority_level', 'Unknown'))),
            "cross_functional_dependencies": self._safe_int(row.get('cross_functional_dependencies')) or existing_project.get('cross_functional_dependencies'),
            "previous_delivery_success_rate": self._safe_float(row.get('previous_delivery_success_rate')) or existing_project.get('previous_delivery_success_rate'),
            "documentation_quality": str(row.get('documentation_quality', existing_project.get('documentation_quality', 'Unknown'))),
            "project_start_month": str(row.get('project_start_month', existing_project.get('project_start_month', 'Unknown'))),
            "seasonal_risk_factor": self._safe_float(row.get('seasonal_risk_factor')) or existing_project.get('seasonal_risk_factor'),
            "risk_level": str(row.get('risk_level', existing_project.get('risk_level', 'Unknown'))),
            "updated_at": datetime.now().isoformat()
        }
        return update_data

    def _update_project_from_row(self, db: Client, project: Dict, row: pd.Series):
        """Update existing project with CSV row data"""
        update_data = {
            "project_type": str(row.get('project_type', project['project_type'])),
            "team_size": self._safe_int(row.get('team_size')) or project['team_size'],
            "project_budget_usd": self._safe_float(row.get('project_budget_usd')) or project['project_budget_usd'],
            "estimated_timeline_months": self._safe_float(row.get('estimated_timeline_months')) or project['estimated_timeline_months'],
            "complexity_score": self._safe_float(row.get('complexity_score')) or project['complexity_score'],
            "stakeholder_count": self._safe_int(row.get('stakeholder_count')) or project['stakeholder_count'],
            "methodology_used": str(row.get('methodology_used', project['methodology_used'])),
            "team_experience_level": str(row.get('team_experience_level', project['team_experience_level'])),
            "past_similar_projects": self._safe_int(row.get('past_similar_projects')) or project['past_similar_projects'],
            "external_dependencies_count": self._safe_int(row.get('external_dependencies_count')) or project['external_dependencies_count'],
            "change_request_frequency": str(row.get('change_request_frequency', project['change_request_frequency'])),
            "project_phase": str(row.get('project_phase', project['project_phase'])),
            "requirement_stability": str(row.get('requirement_stability', project['requirement_stability'])),
            "team_turnover_rate": str(row.get('team_turnover_rate', project['team_turnover_rate'])),
            "vendor_reliability_score": self._safe_float(row.get('vendor_reliability_score')) or project['vendor_reliability_score'],
            "historical_risk_incidents": self._safe_int(row.get('historical_risk_incidents')) or project['historical_risk_incidents'],
            "communication_frequency": str(row.get('communication_frequency', project['communication_frequency'])),
            "budget_utilization_rate": self._safe_float(row.get('budget_utilization_rate')) or project['budget_utilization_rate'],
            "resource_availability": str(row.get('resource_availability', project['resource_availability'])),
            "current_phase_duration_months": self._safe_float(row.get('current_phase_duration_months')) or project['current_phase_duration_months'],
            "project_manager_experience": str(row.get('project_manager_experience', project['project_manager_experience'])),
            "stakeholder_engagement_level": str(row.get('stakeholder_engagement_level', project['stakeholder_engagement_level'])),
            "key_stakeholder_availability": str(row.get('key_stakeholder_availability', project['key_stakeholder_availability'])),
            "team_colocation": str(row.get('team_colocation', project['team_colocation'])),
            "regulatory_compliance_level": str(row.get('regulatory_compliance_level', project['regulatory_compliance_level'])),
            "executive_sponsorship": str(row.get('executive_sponsorship', project['executive_sponsorship'])),
            "funding_source": str(row.get('funding_source', project['funding_source'])),
            "organizational_change_frequency": str(row.get('organizational_change_frequency', project['organizational_change_frequency'])),
            "org_process_maturity": str(row.get('org_process_maturity', project['org_process_maturity'])),
            "risk_management_maturity": str(row.get('risk_management_maturity', project['risk_management_maturity'])),
            "change_control_maturity": str(row.get('change_control_maturity', project['change_control_maturity'])),
            "technology_familiarity": str(row.get('technology_familiarity', project['technology_familiarity'])),
            "integration_complexity": str(row.get('integration_complexity', project['integration_complexity'])),
            "technical_debt_level": str(row.get('technical_debt_level', project['technical_debt_level'])),
            "tech_environment_stability": str(row.get('tech_environment_stability', project['tech_environment_stability'])),
            "data_security_requirements": str(row.get('data_security_requirements', project['data_security_requirements'])),
            "market_volatility": str(row.get('market_volatility', project['market_volatility'])),
            "industry_volatility": str(row.get('industry_volatility', project['industry_volatility'])),
            "geographical_distribution": str(row.get('geographical_distribution', project['geographical_distribution'])),
            "client_experience_level": str(row.get('client_experience_level', project['client_experience_level'])),
            "contract_type": str(row.get('contract_type', project['contract_type'])),
            "resource_contention_level": str(row.get('resource_contention_level', project['resource_contention_level'])),
            "schedule_pressure": str(row.get('schedule_pressure', project['schedule_pressure'])),
            "priority_level": str(row.get('priority_level', project['priority_level'])),
            "cross_functional_dependencies": self._safe_int(row.get('cross_functional_dependencies')) or project['cross_functional_dependencies'],
            "previous_delivery_success_rate": self._safe_float(row.get('previous_delivery_success_rate')) or project['previous_delivery_success_rate'],
            "documentation_quality": str(row.get('documentation_quality', project['documentation_quality'])),
            "project_start_month": str(row.get('project_start_month', project['project_start_month'])),
            "seasonal_risk_factor": self._safe_float(row.get('seasonal_risk_factor')) or project['seasonal_risk_factor'],
            "risk_level": str(row.get('risk_level', project['risk_level'])),
            "updated_at": datetime.now().isoformat()
        }
        db.table("projects").update(update_data).eq("project_id", project['project_id']).execute()

    def _safe_float(self, value) -> Optional[float]:
        """Safely convert value to float"""
        try:
            if pd.isna(value):
                return None
            return float(value)
        except (ValueError, TypeError):
            return None

    def get_data_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Get summary statistics of the loaded data"""

        summary = {
            "total_records": len(df),
            "columns": list(df.columns),
            "risk_level_distribution": df['risk_level'].value_counts().to_dict() if 'risk_level' in df.columns else {},
            "project_type_distribution": df['project_type'].value_counts().to_dict() if 'project_type' in df.columns else {},
            "missing_values": df.isnull().sum().to_dict(),
            "numeric_summary": df.describe().to_dict()
        }

        return summary