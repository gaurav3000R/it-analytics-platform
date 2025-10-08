# Resolving bug: Updating _create_sample_projects in data_processor.py to match model fields
# Remove/set only existing fields, map 'budget' to 'project_budget_usd', etc.

#===== ./app/services/data_processor.py =====

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func
import logging

from app.models import Project, DailyLog, Sprint  # FIXED
from app.models.employee import Employee

logger = logging.getLogger(__name__)

class DataProcessorService:
    
    def generate_sample_data(self, db: Session, num_projects: int = 10, num_employees: int = 20):
        """Generate sample data for demonstration"""
        logger.info(f"Generating sample data: {num_projects} projects, {num_employees} employees")
        
        # Create sample employees
        employees = self._create_sample_employees(db, num_employees)
        
        # Create sample projects
        projects = self._create_sample_projects(db, num_projects)
        
        # Create sample daily logs
        self._create_sample_daily_logs(db, projects, employees)
        
        # Create sample sprints
        self._create_sample_sprints(db, projects)
        
        logger.info("Sample data generation completed")
    
    def _create_sample_employees(self, db: Session, num_employees: int) -> List[Employee]:
        """Create sample employees"""
        roles = ['developer', 'tester', 'designer', 'manager', 'devops']
        skill_levels = ['junior', 'mid', 'senior']
        
        employees = []
        
        for i in range(num_employees):
            employee = Employee(
                name=f"Employee_{i+1:02d}",
                email=f"employee{i+1:02d}@company.com",
                role=np.random.choice(roles),
                skill_level=np.random.choice(skill_levels),
                hourly_rate=np.random.uniform(50, 150),
                max_hours_per_day=8.0,
                hire_date=datetime.now() - timedelta(days=np.random.randint(30, 1000))
            )
            db.add(employee)
            employees.append(employee)
        
        db.commit()
        return employees
    
    def _create_sample_projects(self, db: Session, num_projects: int) -> List[Project]:
        """Create sample projects"""
        project_types = ['web', 'mobile', 'data_science', 'devops', 'api']
        clients = ['ClientA', 'ClientB', 'ClientC', 'ClientD', 'ClientE']
        methodologies = ['Agile', 'Waterfall', 'Scrum']
        experience_levels = ['Junior', 'Mid', 'Senior']
        
        projects = []
        
        for i in range(num_projects):
            start_date = datetime.now() - timedelta(days=np.random.randint(30, 180))
            duration = np.random.randint(60, 300)  # 2-10 months
            end_date = start_date + timedelta(days=duration)
            
            project = Project(
                project_id=f"PROJ_SAMPLE_{i+1:03d}",
                name=f"Sample Project {i+1}",  # NEW
                client=np.random.choice(clients),  # NEW
                start_date=start_date,  # NEW
                end_date=end_date,  # NEW
                status='active',  # NEW
                current_spend=np.random.uniform(10000, 300000),  # NEW
                
                project_type=np.random.choice(project_types),
                team_size=np.random.randint(3, 12),
                project_budget_usd=np.random.uniform(50000, 500000),
                complexity_score=np.random.uniform(1, 5),
                methodology_used=np.random.choice(methodologies),
                team_experience_level=np.random.choice(experience_levels),
                # Add other fields with random values to match CSV structure
                estimated_timeline_months=duration / 30.0,
                stakeholder_count=np.random.randint(5, 20),
                past_similar_projects=np.random.randint(0, 5),
                external_dependencies_count=np.random.randint(0, 5),
                change_request_frequency=np.random.choice(['Low', 'Medium', 'High']),
                project_phase=np.random.choice(['Planning', 'Execution', 'Monitoring']),
                requirement_stability=np.random.choice(['Stable', 'Moderate', 'Unstable']),
                team_turnover_rate=np.random.choice(['Low', 'Medium', 'High']),
                vendor_reliability_score=np.random.uniform(0.5, 1.0),
                historical_risk_incidents=np.random.randint(0, 10),
                communication_frequency=np.random.choice(['Daily', 'Weekly', 'Monthly']),
                budget_utilization_rate=np.random.uniform(0.2, 0.9),
                resource_availability=np.random.choice(['High', 'Medium', 'Low']),
                current_phase_duration_months=np.random.uniform(1, 6),
                project_manager_experience=np.random.choice(['Low', 'Mid', 'High']),
                stakeholder_engagement_level=np.random.choice(['Low', 'Medium', 'High']),
                key_stakeholder_availability=np.random.choice(['Limited', 'Available']),
                team_colocation=np.random.choice(['Fully Colocated', 'Partial', 'Remote']),
                regulatory_compliance_level=np.random.choice(['Low', 'Medium', 'High']),
                executive_sponsorship=np.random.choice(['Strong', 'Moderate', 'Weak']),
                funding_source=np.random.choice(['Internal', 'External', 'Government']),
                organizational_change_frequency=np.random.choice(['Low', 'Medium', 'High']),
                org_process_maturity=np.random.choice(['Initial', 'Managed', 'Defined']),
                risk_management_maturity=np.random.choice(['Basic', 'Intermediate', 'Advanced']),
                change_control_maturity=np.random.choice(['Basic', 'Intermediate', 'Advanced']),
                technology_familiarity=np.random.choice(['Expert', 'Familiar', 'New']),
                integration_complexity=np.random.choice(['Low', 'Medium', 'High']),
                technical_debt_level=np.random.choice(['Low', 'Medium', 'High']),
                tech_environment_stability=np.random.choice(['Stable', 'Moderate', 'Unstable']),
                data_security_requirements=np.random.choice(['Low', 'Medium', 'High']),
                market_volatility=np.random.choice(['Low', 'Medium', 'High']),
                industry_volatility=np.random.choice(['Low', 'Medium', 'High']),
                geographical_distribution=np.random.choice(['Local', 'Regional', 'Global']),
                client_experience_level=np.random.choice(['Experienced', 'Moderate', 'First-time']),
                contract_type=np.random.choice(['Fixed Price', 'Time & Materials']),
                resource_contention_level=np.random.choice(['Low', 'Medium', 'High']),
                schedule_pressure=np.random.choice(['Low', 'Medium', 'High']),
                priority_level=np.random.choice(['Low', 'Medium', 'High']),
                cross_functional_dependencies=np.random.randint(0, 10),
                previous_delivery_success_rate=np.random.uniform(0.5, 1.0),
                documentation_quality=np.random.choice(['Poor', 'Fair', 'Good']),
                project_start_month=str(np.random.randint(1, 13)),
                seasonal_risk_factor=np.random.uniform(0.5, 1.5),
                risk_level=np.random.choice(['Low', 'Medium', 'High'])
            )
            db.add(project)
            projects.append(project)
        
        db.commit()
        return projects
    
    def _create_sample_daily_logs(self, db: Session, projects: List[Project], employees: List[Employee]):
        """Create sample daily logs"""
        task_categories = ['development', 'testing', 'design', 'meeting', 'documentation', 'bug_fix']
        
        # Generate logs for last 60 days
        for days_ago in range(60):
            log_date = datetime.now() - timedelta(days=days_ago)
            
            # Skip weekends
            if log_date.weekday() >= 5:
                continue
            
            # Each employee logs for some projects each day
            for employee in employees:
                # Probability of logging on any given day
                if np.random.random() > 0.8:  # 20% chance of not logging
                    continue
                
                # Number of projects they work on per day
                num_projects_today = np.random.choice([1, 2, 3], p=[0.7, 0.25, 0.05])
                
                working_projects = np.random.choice(projects, num_projects_today, replace=False)
                
                for project in working_projects:
                    # Generate realistic hours based on employee role and project
                    base_hours = np.random.normal(6, 2)
                    if employee.role == 'manager':
                        base_hours *= 0.7  # Managers spend less time on individual projects
                    
                    hours = max(0.5, min(12, base_hours))
                    
                    # Add some anomalies randomly
                    if np.random.random() < 0.05:  # 5% chance of anomaly
                        if np.random.random() < 0.5:
                            hours *= 0.2  # Very low hours
                        else:
                            hours *= 2  # Very high hours
                    
                    daily_log = DailyLog(
                        project_id=project.id,
                        employee_id=employee.id,
                        date=log_date,
                        hours_logged=hours,
                        task_description=f"Working on {np.random.choice(task_categories)}",
                        task_category=np.random.choice(task_categories),
                        completion_percentage=np.random.uniform(10, 95),
                        issues_reported=np.random.poisson(0.5)  # Average 0.5 issues per day
                    )
                    db.add(daily_log)
        
        db.commit()
    
    def _create_sample_sprints(self, db: Session, projects: List[Project]):
        """Create sample sprints"""
        for project in projects:
            # Create 3-5 sprints per project
            num_sprints = np.random.randint(3, 6)
            
            sprint_start = project.start_date
            
            for sprint_num in range(1, num_sprints + 1):
                sprint_duration = 14  # 2 weeks
                sprint_end = sprint_start + timedelta(days=sprint_duration)
                
                planned_points = np.random.randint(20, 50)
                completed_points = np.random.randint(15, planned_points + 5)
                
                # Calculate velocity
                velocity = completed_points / (sprint_duration / 7)  # Points per week
                
                # Add some velocity degradation for later sprints (realistic)
                if sprint_num > 2:
                    velocity *= np.random.uniform(0.8, 1.1)
                
                sprint = Sprint(
                    project_id=project.id,
                    sprint_number=sprint_num,
                    start_date=sprint_start,
                    end_date=sprint_end,
                    planned_points=planned_points,
                    completed_points=completed_points,
                    velocity=velocity,
                    burndown_data={
                        f"day_{i}": max(0, planned_points - (i * completed_points / sprint_duration))
                        for i in range(sprint_duration + 1)
                    }
                )
                db.add(sprint)
                
                sprint_start = sprint_end + timedelta(days=1)
        
        db.commit()
    
    def get_project_dashboard_data(self, db: Session, project_id: int) -> Dict[str, Any]:
        """Get comprehensive project dashboard data"""
        
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise ValueError(f"Project {project_id} not found")
        
        # Get recent daily logs (last 30 days)
        recent_logs = db.query(DailyLog).filter(
            DailyLog.project_id == project_id,
            DailyLog.date >= datetime.now() - timedelta(days=30)
        ).all()
        
        # Get sprint data
        sprints = db.query(Sprint).filter(
            Sprint.project_id == project_id
        ).order_by(Sprint.start_date).all()
        
        # Calculate metrics
        total_hours_logged = sum([log.hours_logged for log in recent_logs])
        avg_completion_rate = np.mean([log.completion_percentage for log in recent_logs]) if recent_logs else 0
        total_issues = sum([log.issues_reported for log in recent_logs])
        
        # Team metrics
        active_team_members = len(set([log.employee_id for log in recent_logs]))
        
        # Sprint metrics
        latest_sprint = sprints[-1] if sprints else None
        avg_velocity = np.mean([s.velocity for s in sprints if s.velocity]) if sprints else 0
        
        # Budget metrics
        budget_utilization = (project.current_spend / project.budget * 100) if project.budget > 0 else 0
        
        # Timeline metrics
        days_elapsed = (datetime.now() - project.start_date).days if project.start_date else 0
        total_duration = (project.end_date - project.start_date).days if project.end_date and project.start_date else 0
        timeline_progress = (days_elapsed / total_duration * 100) if total_duration > 0 else 0
        
        return {
            'project_info': {
                'id': project.id,
                'name': project.name,
                'client': project.client,
                'status': project.status,
                'type': project.project_type,
                'complexity': project.complexity_score
            },
            'timeline': {
                'start_date': project.start_date.isoformat() if project.start_date else None,
                'end_date': project.end_date.isoformat() if project.end_date else None,
                'days_elapsed': days_elapsed,
                'total_duration': total_duration,
                'progress_percentage': timeline_progress
            },
            'budget': {
                'total_budget': project.budget,
                'current_spend': project.current_spend,
                'utilization_percentage': budget_utilization,
                'remaining': project.budget - project.current_spend if project.budget else 0
            },
            'team': {
                'team_size': project.team_size,
                'active_members': active_team_members,
                'total_hours_30d': total_hours_logged,
                'avg_hours_per_member': total_hours_logged / active_team_members if active_team_members > 0 else 0
            },
            'performance': {
                'avg_completion_rate': avg_completion_rate,
                'total_issues_30d': total_issues,
                'avg_velocity': avg_velocity,
                'current_sprint': {
                    'number': latest_sprint.sprint_number if latest_sprint else None,
                    'planned_points': latest_sprint.planned_points if latest_sprint else None,
                    'completed_points': latest_sprint.completed_points if latest_sprint else None,
                    'velocity': latest_sprint.velocity if latest_sprint else None
                } if latest_sprint else None
            },
            'recent_activity': [
                {
                    'date': log.date.isoformat(),
                    'employee_id': log.employee_id,
                    'hours': log.hours_logged,
                    'completion': log.completion_percentage,
                    'issues': log.issues_reported,
                    'category': log.task_category
                }
                for log in recent_logs[-10:]  # Last 10 entries
            ]
        }