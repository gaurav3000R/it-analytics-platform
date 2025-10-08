import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session
from pathlib import Path

from app.models.project import Project
from app.database import get_db, SessionLocal

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
    
    def _clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and preprocess the CSV data"""
        
        # Convert column names to lowercase with underscores
        df.columns = [col.lower().replace(' ', '_') for col in df.columns]
        
        # Handle missing values
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        df[numeric_columns] = df[numeric_columns].fillna(df[numeric_columns].median())
        
        categorical_columns = df.select_dtypes(include=['object']).columns
        df[categorical_columns] = df[categorical_columns].fillna('Unknown')
        
        # Standardize categorical values
        if 'risk_level' in df.columns:
            df['risk_level'] = df['risk_level'].str.strip().str.title()
        
        logger.info("Data cleaning completed")
        return df
    
    def csv_to_database(self, db: Session, file_path: Optional[str] = None, 
                       clear_existing: bool = False) -> Dict[str, Any]:
        """Load CSV data into database"""
        
        if clear_existing:
            logger.info("Clearing existing projects...")
            db.query(Project).delete()
            db.commit()
        
        df = self.load_csv_data(file_path)
        
        projects_created = 0
        projects_updated = 0
        errors = []
        
        for index, row in df.iterrows():
            try:
                # Check if project already exists
                existing_project = db.query(Project).filter(
                    Project.project_id == str(row.get('project_id', f'proj_{index}'))
                ).first()
                
                if existing_project:
                    # Update existing project
                    self._update_project_from_row(existing_project, row)
                    projects_updated += 1
                else:
                    # Create new project
                    project = self._create_project_from_row(row, index)
                    db.add(project)
                    projects_created += 1
                
                # Commit every 10 records to avoid large transactions
                if (index + 1) % 10 == 0:
                    db.commit()
                    
            except Exception as e:
                error_msg = f"Error processing row {index}: {e}"
                logger.error(error_msg)
                errors.append(error_msg)
                db.rollback()
        
        # Final commit
        db.commit()
        
        result = {
            "total_rows_processed": len(df),
            "projects_created": projects_created,
            "projects_updated": projects_updated,
            "errors": errors,
            "success_rate": ((projects_created + projects_updated) / len(df)) * 100
        }
        
        logger.info(f"CSV import completed: {result}")
        return result
    
    def _create_project_from_row(self, row: pd.Series, index: int) -> Project:
        """Create a Project instance from a CSV row"""
        
        project = Project(
            # Use project_id from CSV or generate one
            project_id=str(row.get('project_id', f'PROJ_{index:03d}')),
            
            # Project Demographics
            project_type=str(row.get('project_type', 'Unknown')),
            team_size=self._safe_int(row.get('team_size')),
            project_budget_usd=self._safe_float(row.get('project_budget_usd')),
            estimated_timeline_months=self._safe_float(row.get('estimated_timeline_months')),
            complexity_score=self._safe_float(row.get('complexity_score')),
            stakeholder_count=self._safe_int(row.get('stakeholder_count')),
            methodology_used=str(row.get('methodology_used', 'Unknown')),
            team_experience_level=str(row.get('team_experience_level', 'Unknown')),
            past_similar_projects=self._safe_int(row.get('past_similar_projects')),
            
            # Operational Metrics
            external_dependencies_count=self._safe_int(row.get('external_dependencies_count')),
            change_request_frequency=str(row.get('change_request_frequency', 'Unknown')),
            project_phase=str(row.get('project_phase', 'Unknown')),
            requirement_stability=str(row.get('requirement_stability', 'Unknown')),
            team_turnover_rate=str(row.get('team_turnover_rate', 'Unknown')),
            vendor_reliability_score=self._safe_float(row.get('vendor_reliability_score')),
            historical_risk_incidents=self._safe_int(row.get('historical_risk_incidents')),
            communication_frequency=str(row.get('communication_frequency', 'Unknown')),
            budget_utilization_rate=self._safe_float(row.get('budget_utilization_rate')),
            resource_availability=str(row.get('resource_availability', 'Unknown')),
            current_phase_duration_months=self._safe_float(row.get('current_phase_duration_months')),
            
            # Human Factors
            project_manager_experience=str(row.get('project_manager_experience', 'Unknown')),
            stakeholder_engagement_level=str(row.get('stakeholder_engagement_level', 'Unknown')),
            key_stakeholder_availability=str(row.get('key_stakeholder_availability', 'Unknown')),
            team_colocation=str(row.get('team_colocation', 'Unknown')),
            
            # Organizational Context
            regulatory_compliance_level=str(row.get('regulatory_compliance_level', 'Unknown')),
            executive_sponsorship=str(row.get('executive_sponsorship', 'Unknown')),
            funding_source=str(row.get('funding_source', 'Unknown')),
            organizational_change_frequency=str(row.get('organizational_change_frequency', 'Unknown')),
            org_process_maturity=str(row.get('org_process_maturity', 'Unknown')),
            risk_management_maturity=str(row.get('risk_management_maturity', 'Unknown')),
            change_control_maturity=str(row.get('change_control_maturity', 'Unknown')),
            
            # Technical Aspects
            technology_familiarity=str(row.get('technology_familiarity', 'Unknown')),
            integration_complexity=str(row.get('integration_complexity', 'Unknown')),
            technical_debt_level=str(row.get('technical_debt_level', 'Unknown')),
            tech_environment_stability=str(row.get('tech_environment_stability', 'Unknown')),
            data_security_requirements=str(row.get('data_security_requirements', 'Unknown')),
            
            # External Influences
            market_volatility=str(row.get('market_volatility', 'Unknown')),
            industry_volatility=str(row.get('industry_volatility', 'Unknown')),
            geographical_distribution=str(row.get('geographical_distribution', 'Unknown')),
            client_experience_level=str(row.get('client_experience_level', 'Unknown')),
            contract_type=str(row.get('contract_type', 'Unknown')),
            resource_contention_level=str(row.get('resource_contention_level', 'Unknown')),
            
            # Additional Fields
            schedule_pressure=str(row.get('schedule_pressure', 'Unknown')),
            priority_level=str(row.get('priority_level', 'Unknown')),
            cross_functional_dependencies=self._safe_int(row.get('cross_functional_dependencies')),
            previous_delivery_success_rate=self._safe_float(row.get('previous_delivery_success_rate')),
            documentation_quality=str(row.get('documentation_quality', 'Unknown')),
            project_start_month=str(row.get('project_start_month', 'Unknown')),
            seasonal_risk_factor=self._safe_float(row.get('seasonal_risk_factor')),
            
            # Target Variable
            risk_level=str(row.get('risk_level', 'Unknown'))
        )
        
        return project
    
    def _update_project_from_row(self, project: Project, row: pd.Series):
        """Update existing project with CSV row data"""
        
        # Update all fields from CSV
        project.project_type = str(row.get('project_type', project.project_type))
        project.team_size = self._safe_int(row.get('team_size')) or project.team_size
        project.project_budget_usd = self._safe_float(row.get('project_budget_usd')) or project.project_budget_usd
        # ... (update all other fields similarly)
        project.risk_level = str(row.get('risk_level', project.risk_level))
    
    def _safe_int(self, value) -> Optional[int]:
        """Safely convert value to int"""
        try:
            if pd.isna(value):
                return None
            return int(float(value))
        except (ValueError, TypeError):
            return None
    
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
