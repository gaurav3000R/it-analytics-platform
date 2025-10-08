#===== ./app/services/data_processor.py =====

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func
import logging

from app.models.project import Project
from app.models.daily_log import DailyLog
from app.models.sprint import Sprint
from app.models.employee import Employee

logger = logging.getLogger(__name__)

class DataProcessorService:
    
    def generate_enhanced_sample_data(self, db: Session, num_projects: int = 50, num_employees: int = 30):
        """Generate enhanced sample data with realistic risk patterns"""
        logger.info(f"Generating ENHANCED sample data: {num_projects} projects, {num_employees} employees")
        
        # Clear existing data for fresh start
        self._clear_existing_data(db)
        
        # Create sample employees
        employees = self._create_enhanced_employees(db, num_employees)
        
        # Create sample projects with realistic risk patterns
        projects = self._create_enhanced_projects(db, num_projects)
        
        # Create realistic daily logs that correlate with project risks
        self._create_enhanced_daily_logs(db, projects, employees)
        
        # Create sample sprints
        self._create_enhanced_sprints(db, projects)
        
        logger.info("✅ Enhanced sample data generation completed")
    
    def _clear_existing_data(self, db: Session):
        """Clear existing data for fresh training"""
        try:
            db.query(DailyLog).delete()
            db.query(Sprint).delete()
            db.query(Project).delete()
            db.query(Employee).delete()
            db.commit()
            logger.info("Cleared existing data")
        except Exception as e:
            logger.warning(f"Error clearing data: {e}")
            db.rollback()
    
    def _create_enhanced_employees(self, db: Session, num_employees: int) -> List[Employee]:
        """Create employees with realistic skill distributions"""
        roles = ['developer', 'developer', 'developer', 'tester', 'designer', 'manager', 'devops']
        skill_levels = ['junior', 'mid', 'senior']
        skill_weights = [0.3, 0.5, 0.2]  # More mid-level, fewer seniors
        
        employees = []
        
        for i in range(num_employees):
            role = np.random.choice(roles)
            skill_level = np.random.choice(skill_levels, p=skill_weights)
            
            # Realistic hourly rates based on role and skill
            if skill_level == 'junior':
                hourly_rate = np.random.uniform(40, 70)
            elif skill_level == 'mid':
                hourly_rate = np.random.uniform(65, 110)
            else:  # senior
                hourly_rate = np.random.uniform(100, 180)
            
            # Adjust for role
            if role == 'manager':
                hourly_rate *= 1.3
            elif role == 'devops':
                hourly_rate *= 1.2
            
            employee = Employee(
                name=f"Employee_{i+1:03d}",
                email=f"employee{i+1:03d}@company.com",
                role=role,
                skill_level=skill_level,
                hourly_rate=hourly_rate,
                max_hours_per_day=8.0,
                hire_date=datetime.now() - timedelta(days=np.random.randint(180, 2000))
            )
            db.add(employee)
            employees.append(employee)
        
        db.commit()
        logger.info(f"Created {len(employees)} enhanced employees")
        return employees
    
    def _create_enhanced_projects(self, db: Session, num_projects: int) -> List[Project]:
        """Create projects with realistic risk patterns that ML can learn"""
        project_types = ['web_development', 'mobile_app', 'data_platform', 'api_integration', 'cloud_migration']
        clients = ['TechCorp', 'FinanceGlobal', 'HealthSystems', 'RetailPlus', 'StartupInnovate']
        methodologies = ['Agile', 'Scrum', 'Waterfall', 'Hybrid']
        
        # Define realistic project patterns that correlate with risk
        project_patterns = [
            # (type, team_size_range, budget_range, complexity_range, expected_risk)
            ('web_development', (3, 6), (50000, 150000), (2.0, 4.0), 'Low'),
            ('mobile_app', (4, 8), (80000, 200000), (3.0, 5.0), 'Medium'),
            ('data_platform', (6, 12), (150000, 400000), (4.0, 6.0), 'High'),
            ('api_integration', (3, 5), (40000, 120000), (3.5, 5.5), 'Medium'),
            ('cloud_migration', (5, 10), (100000, 300000), (4.5, 6.5), 'High'),
        ]
        
        projects = []
        
        for i in range(num_projects):
            # Select a project pattern
            pattern = project_patterns[i % len(project_patterns)]
            project_type, team_range, budget_range, complexity_range, expected_risk = pattern
            
            # Generate realistic values based on pattern
            team_size = np.random.randint(team_range[0], team_range[1] + 1)
            budget = np.random.uniform(budget_range[0], budget_range[1])
            complexity = np.random.uniform(complexity_range[0], complexity_range[1])
            
            # Calculate timeline based on complexity and team size
            base_timeline = complexity * 2  # months
            adjusted_timeline = base_timeline * (8 / team_size)  # Adjust for team size
            
            start_date = datetime.now() - timedelta(days=np.random.randint(30, 365))
            timeline_days = adjusted_timeline * 30
            end_date = start_date + timedelta(days=timeline_days)
            
            # Calculate current spend based on risk level (high risk = higher spend)
            risk_spend_multiplier = {'Low': 0.3, 'Medium': 0.5, 'High': 0.7}[expected_risk]
            current_spend = budget * risk_spend_multiplier * np.random.uniform(0.8, 1.2)
            
            # Generate realistic risk factors based on expected risk
            risk_factors = self._generate_risk_factors(expected_risk, team_size, complexity)
            
            project = Project(
                # Basic info
                project_id=f"PROJ_{i+1:04d}",
                name=f"{project_type.replace('_', ' ').title()} {i+1}",
                client=np.random.choice(clients),
                start_date=start_date,
                end_date=end_date,
                status='active',
                current_spend=current_spend,
                budget=budget,
                
                # Core characteristics
                project_type=project_type,
                team_size=team_size,
                project_budget_usd=budget,
                estimated_timeline_months=adjusted_timeline,
                complexity_score=complexity,
                
                # Risk-influenced factors
                risk_level=expected_risk,
                team_experience_level=risk_factors['team_experience'],
                methodology_used=np.random.choice(methodologies),
                stakeholder_count=np.random.randint(3, 15),
                past_similar_projects=risk_factors['past_projects'],
                
                # Operational metrics correlated with risk
                external_dependencies_count=risk_factors['dependencies'],
                change_request_frequency=risk_factors['change_frequency'],
                project_phase=self._get_project_phase(start_date, end_date),
                requirement_stability=risk_factors['requirement_stability'],
                team_turnover_rate=risk_factors['turnover_rate'],
                vendor_reliability_score=risk_factors['vendor_reliability'],
                historical_risk_incidents=risk_factors['risk_incidents'],
                communication_frequency=risk_factors['communication_freq'],
                budget_utilization_rate=current_spend / budget,
                resource_availability=risk_factors['resource_availability'],
                current_phase_duration_months=adjusted_timeline * 0.3,
                
                # Human factors
                project_manager_experience=risk_factors['pm_experience'],
                stakeholder_engagement_level=risk_factors['stakeholder_engagement'],
                key_stakeholder_availability=risk_factors['stakeholder_availability'],
                team_colocation=np.random.choice(['Fully Colocated', 'Partial', 'Remote']),
                
                # Organizational context
                regulatory_compliance_level=np.random.choice(['Low', 'Medium', 'High']),
                executive_sponsorship=risk_factors['executive_sponsorship'],
                funding_source=np.random.choice(['Internal', 'External', 'Government']),
                organizational_change_frequency=np.random.choice(['Low', 'Medium', 'High']),
                org_process_maturity=risk_factors['process_maturity'],
                risk_management_maturity=risk_factors['risk_maturity'],
                change_control_maturity=risk_factors['change_maturity'],
                
                # Technical aspects
                technology_familiarity=risk_factors['tech_familiarity'],
                integration_complexity=risk_factors['integration_complexity'],
                technical_debt_level=risk_factors['technical_debt'],
                tech_environment_stability=risk_factors['environment_stability'],
                data_security_requirements=np.random.choice(['Low', 'Medium', 'High']),
                
                # External influences
                market_volatility=np.random.choice(['Low', 'Medium', 'High']),
                industry_volatility=np.random.choice(['Low', 'Medium', 'High']),
                geographical_distribution=np.random.choice(['Local', 'Regional', 'Global']),
                client_experience_level=risk_factors['client_experience'],
                contract_type=np.random.choice(['Fixed Price', 'Time & Materials']),
                resource_contention_level=risk_factors['resource_contention'],
                
                # Additional fields
                schedule_pressure=risk_factors['schedule_pressure'],
                priority_level=risk_factors['priority_level'],
                cross_functional_dependencies=risk_factors['cross_dependencies'],
                previous_delivery_success_rate=risk_factors['success_rate'],
                documentation_quality=risk_factors['documentation_quality'],
                project_start_month=start_date.strftime('%B'),
                seasonal_risk_factor=np.random.uniform(0.8, 1.2),
            )
            db.add(project)
            projects.append(project)
        
        db.commit()
        logger.info(f"Created {len(projects)} enhanced projects with realistic risk patterns")
        return projects
    
    def _generate_risk_factors(self, expected_risk: str, team_size: int, complexity: float) -> Dict[str, Any]:
        """Generate risk factors that correlate with expected risk level"""
        risk_profiles = {
            'Low': {
                'team_experience': 'Senior',
                'past_projects': np.random.randint(3, 8),
                'dependencies': np.random.randint(0, 3),
                'change_frequency': 'Low',
                'requirement_stability': 'Stable',
                'turnover_rate': 'Low',
                'vendor_reliability': np.random.uniform(0.8, 1.0),
                'risk_incidents': np.random.randint(0, 2),
                'communication_freq': 'Weekly',
                'resource_availability': 'High',
                'pm_experience': 'High',
                'stakeholder_engagement': 'High',
                'stakeholder_availability': 'Available',
                'executive_sponsorship': 'Strong',
                'process_maturity': 'Defined',
                'risk_maturity': 'Advanced',
                'change_maturity': 'Advanced',
                'tech_familiarity': 'Expert',
                'integration_complexity': 'Low',
                'technical_debt': 'Low',
                'environment_stability': 'Stable',
                'client_experience': 'Experienced',
                'resource_contention': 'Low',
                'schedule_pressure': 'Low',
                'priority_level': 'Low',
                'cross_dependencies': np.random.randint(0, 3),
                'success_rate': np.random.uniform(0.8, 1.0),
                'documentation_quality': 'Good',
            },
            'Medium': {
                'team_experience': 'Mid',
                'past_projects': np.random.randint(1, 5),
                'dependencies': np.random.randint(2, 6),
                'change_frequency': 'Medium',
                'requirement_stability': 'Moderate',
                'turnover_rate': 'Medium',
                'vendor_reliability': np.random.uniform(0.6, 0.9),
                'risk_incidents': np.random.randint(1, 5),
                'communication_freq': 'Bi-Weekly',
                'resource_availability': 'Medium',
                'pm_experience': 'Mid',
                'stakeholder_engagement': 'Medium',
                'stakeholder_availability': 'Limited',
                'executive_sponsorship': 'Moderate',
                'process_maturity': 'Managed',
                'risk_maturity': 'Intermediate',
                'change_maturity': 'Intermediate',
                'tech_familiarity': 'Familiar',
                'integration_complexity': 'Medium',
                'technical_debt': 'Medium',
                'environment_stability': 'Moderate',
                'client_experience': 'Moderate',
                'resource_contention': 'Medium',
                'schedule_pressure': 'Medium',
                'priority_level': 'Medium',
                'cross_dependencies': np.random.randint(2, 6),
                'success_rate': np.random.uniform(0.6, 0.9),
                'documentation_quality': 'Fair',
            },
            'High': {
                'team_experience': 'Junior',
                'past_projects': np.random.randint(0, 3),
                'dependencies': np.random.randint(4, 10),
                'change_frequency': 'High',
                'requirement_stability': 'Unstable',
                'turnover_rate': 'High',
                'vendor_reliability': np.random.uniform(0.4, 0.7),
                'risk_incidents': np.random.randint(3, 10),
                'communication_freq': 'Monthly',
                'resource_availability': 'Low',
                'pm_experience': 'Low',
                'stakeholder_engagement': 'Low',
                'stakeholder_availability': 'Limited',
                'executive_sponsorship': 'Weak',
                'process_maturity': 'Initial',
                'risk_maturity': 'Basic',
                'change_maturity': 'Basic',
                'tech_familiarity': 'New',
                'integration_complexity': 'High',
                'technical_debt': 'High',
                'environment_stability': 'Unstable',
                'client_experience': 'First-time',
                'resource_contention': 'High',
                'schedule_pressure': 'High',
                'priority_level': 'High',
                'cross_dependencies': np.random.randint(5, 10),
                'success_rate': np.random.uniform(0.4, 0.7),
                'documentation_quality': 'Poor',
            }
        }
        
        return risk_profiles[expected_risk]
    
    def _get_project_phase(self, start_date: datetime, end_date: datetime) -> str:
        """Determine current project phase based on timeline"""
        total_duration = (end_date - start_date).days
        elapsed_duration = (datetime.now() - start_date).days
        progress = elapsed_duration / total_duration if total_duration > 0 else 0
        
        if progress < 0.3:
            return 'Planning'
        elif progress < 0.7:
            return 'Execution'
        else:
            return 'Monitoring'
    
    def _create_enhanced_daily_logs(self, db: Session, projects: List[Project], employees: List[Employee]):
        """Create daily logs that realistically correlate with project risks"""
        task_categories = ['development', 'testing', 'design', 'planning', 'documentation', 'bug_fix', 'meeting']
        
        logger.info("Creating enhanced daily logs...")
        
        # Generate logs for last 90 days (more data for better training)
        for days_ago in range(90):
            log_date = datetime.now() - timedelta(days=days_ago)
            
            # Skip weekends (reduce activity)
            if log_date.weekday() >= 5:
                if np.random.random() < 0.1:  # 10% chance of weekend work
                    self._create_weekend_logs(db, projects, employees, log_date, task_categories)
                continue
            
            # Weekday logging
            for employee in employees:
                # Probability of logging based on employee reliability
                reliability = self._get_employee_reliability(employee)
                if np.random.random() > reliability:
                    continue
                
                # Number of projects based on employee capacity
                max_projects = 2 if employee.role == 'manager' else 3
                num_projects_today = np.random.randint(1, max_projects + 1)
                
                working_projects = np.random.choice(projects, num_projects_today, replace=False)
                
                for project in working_projects:
                    # Generate realistic hours based on project risk and employee role
                    base_hours = self._calculate_realistic_hours(project, employee, log_date)
                    
                    daily_log = DailyLog(
                        project_id=project.id,
                        employee_id=employee.id,
                        date=log_date,
                        hours_logged=base_hours,
                        task_description=f"Working on {np.random.choice(task_categories)} for {project.name}",
                        task_category=np.random.choice(task_categories),
                        completion_percentage=self._calculate_completion(project, base_hours),
                        issues_reported=self._calculate_issues(project, base_hours)
                    )
                    db.add(daily_log)
            
            # Commit every 10 days to manage transaction size
            if days_ago % 10 == 0:
                db.commit()
        
        db.commit()
        logger.info("✅ Enhanced daily logs created")
    
    def _get_employee_reliability(self, employee: Employee) -> float:
        """Calculate employee logging reliability"""
        reliability_map = {'junior': 0.7, 'mid': 0.85, 'senior': 0.95}
        return reliability_map.get(employee.skill_level, 0.8)
    
    def _calculate_realistic_hours(self, project: Project, employee: Employee, date: datetime) -> float:
        """Calculate realistic working hours based on project risk and other factors"""
        base_hours = np.random.normal(6.5, 1.5)  # Typical workday
        
        # Adjust based on project risk (high risk = more variability)
        risk_adjustment = {
            'Low': np.random.normal(0, 0.5),
            'Medium': np.random.normal(0, 1.0),
            'High': np.random.normal(0, 2.0)
        }[project.risk_level]
        
        # Adjust based on employee role
        role_adjustment = {
            'manager': -1.0,  # Managers spend less time on individual tasks
            'devops': 0.5,    # DevOps often work longer
            'developer': 0.0,
            'tester': 0.0,
            'designer': 0.0
        }.get(employee.role, 0.0)
        
        # Adjust based on project phase
        elapsed_duration = (date - project.start_date).days
        total_duration = (project.end_date - project.start_date).days
        progress = elapsed_duration / total_duration if total_duration > 0 else 0.5
        
        if progress < 0.3:  # Planning phase
            phase_adjustment = -0.5
        elif progress > 0.8:  # Final phase
            phase_adjustment = 1.0  # Crunch time
        else:  # Execution phase
            phase_adjustment = 0.0
        
        total_hours = base_hours + risk_adjustment + role_adjustment + phase_adjustment
        
        # Ensure reasonable bounds
        return max(0.5, min(12.0, total_hours))
    
    def _calculate_completion(self, project: Project, hours: float) -> float:
        """Calculate realistic completion percentage based on project risk"""
        base_completion = hours / 8.0 * 10  # Base completion rate
        
        # High risk projects have lower completion rates
        risk_multiplier = {
            'Low': np.random.uniform(0.9, 1.1),
            'Medium': np.random.uniform(0.7, 1.0),
            'High': np.random.uniform(0.5, 0.9)
        }[project.risk_level]
        
        completion = base_completion * risk_multiplier
        
        return max(5.0, min(95.0, completion))
    
    def _calculate_issues(self, project: Project, hours: float) -> int:
        """Calculate realistic issue count based on project risk"""
        base_issues = hours / 4.0  # Base issue rate
        
        # High risk projects have more issues
        risk_multiplier = {
            'Low': np.random.poisson(0.5),
            'Medium': np.random.poisson(1.0),
            'High': np.random.poisson(2.0)
        }[project.risk_level]
        
        return int(max(0, base_issues + risk_multiplier))
    
    def _create_weekend_logs(self, db: Session, projects: List[Project], employees: List[Employee], 
                           date: datetime, task_categories: List[str]):
        """Create limited weekend logs for critical projects"""
        # Only high-risk projects have weekend work
        high_risk_projects = [p for p in projects if p.risk_level == 'High']
        if not high_risk_projects:
            return
        
        # Select a few employees working on weekends
        weekend_workers = np.random.choice(employees, min(3, len(employees)), replace=False)
        
        for employee in weekend_workers:
            project = np.random.choice(high_risk_projects)
            hours = np.random.uniform(2.0, 6.0)  # Shorter weekend hours
            
            daily_log = DailyLog(
                project_id=project.id,
                employee_id=employee.id,
                date=date,
                hours_logged=hours,
                task_description=f"Weekend work on {np.random.choice(task_categories)}",
                task_category='development',
                completion_percentage=np.random.uniform(20, 60),
                issues_reported=np.random.poisson(1)
            )
            db.add(daily_log)
    
    def _create_enhanced_sprints(self, db: Session, projects: List[Project]):
        """Create realistic sprints that correlate with project risks"""
        logger.info("Creating enhanced sprints...")
        
        for project in projects:
            # Number of sprints based on project duration
            project_duration = (project.end_date - project.start_date).days
            num_sprints = max(2, int(project_duration / 21))  # 3-week sprints
            
            sprint_start = project.start_date
            
            for sprint_num in range(1, num_sprints + 1):
                sprint_duration = 21  # 3 weeks
                sprint_end = sprint_start + timedelta(days=sprint_duration)
                
                # Sprint metrics influenced by project risk
                risk_factors = self._get_sprint_risk_factors(project.risk_level)
                
                planned_points = np.random.randint(20, 40)
                completed_points = int(planned_points * risk_factors['completion_rate'])
                
                velocity = completed_points / (sprint_duration / 7)  # Points per week
                
                sprint = Sprint(
                    project_id=project.id,
                    sprint_number=sprint_num,
                    start_date=sprint_start,
                    end_date=sprint_end,
                    planned_points=planned_points,
                    completed_points=completed_points,
                    velocity=velocity,
                    burndown_data=self._generate_burndown_data(planned_points, completed_points, sprint_duration)
                )
                db.add(sprint)
                
                sprint_start = sprint_end + timedelta(days=2)  # 2-day gap between sprints
        
        db.commit()
        logger.info("✅ Enhanced sprints created")
    
    def _get_sprint_risk_factors(self, risk_level: str) -> Dict[str, float]:
        """Get sprint performance factors based on project risk"""
        return {
            'Low': {'completion_rate': np.random.uniform(0.9, 1.1)},
            'Medium': {'completion_rate': np.random.uniform(0.7, 1.0)},
            'High': {'completion_rate': np.random.uniform(0.5, 0.9)}
        }[risk_level]
    
    def _generate_burndown_data(self, planned_points: int, completed_points: int, duration: int) -> Dict[str, float]:
        """Generate realistic burndown chart data"""
        burndown = {}
        ideal_rate = planned_points / duration
        
        for day in range(duration + 1):
            # Realistic burndown with some variability
            if day == 0:
                remaining = planned_points
            else:
                daily_completion = ideal_rate * np.random.uniform(0.8, 1.2)
                remaining = max(0, planned_points - (day * daily_completion))
            
            burndown[f"day_{day}"] = remaining
        
        return burndown

    # Keep the original method for backward compatibility
    def generate_sample_data(self, db: Session, num_projects: int = 10, num_employees: int = 20):
        """Original method - now uses enhanced data generation"""
        return self.generate_enhanced_sample_data(db, num_projects, num_employees)
    
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