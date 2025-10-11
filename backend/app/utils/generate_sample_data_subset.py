#!/usr/bin/env python3
"""
Script to generate sample data for a SUBSET of projects
Supports cost forecasting, anomaly detection, and utilization alerts
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import connect_db
import argparse
import traceback
import pandas as pd
import numpy as np#!/usr/bin/env python3
"""
Script to generate sample data for a SUBSET of projects
Supports cost forecasting, anomaly detection, and utilization alerts
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import connect_db
import argparse
import traceback
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any
from supabase import Client
import logging
import uuid
import random
from dataclasses import dataclass

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)  # Set logging level to INFO for progress

# ============================================================================
# CONFIGURATION & CONSTANTS
# ============================================================================

@dataclass
class Config:
    """Configuration for data generation"""
    num_employees: int = 35
    num_projects: int = 100
    start_date: str = "2024-01-01"
    end_date: str = "2024-10-11"
    anomaly_rate: float = 0.20  # 20% of employees will have anomalies
    
    # Business rules
    working_days_per_week: int = 5
    standard_hours_per_day: int = 8
    max_hours_per_day: int = 16
    max_projects_per_employee: int = 3
    weekend_work_probability: float = 0.05
    
    # Anomaly probabilities
    prob_underutilized: float = 0.08
    prob_overutilized: float = 0.10
    prob_chronic_underestimator: float = 0.12
    prob_chronic_overestimator: float = 0.08
    prob_sandbagger: float = 0.05
    prob_zombie_task_creator: float = 0.07
    prob_task_abandoner: float = 0.06


def convert_numpy_types(obj):
    """Recursively convert numpy types to Python native types"""
    if isinstance(obj, dict):
        return {key: convert_numpy_types(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_types(item) for item in obj]
    elif isinstance(obj, (np.integer, np.int64, np.int32)):
        return int(obj)
    elif isinstance(obj, (np.floating, np.float64, np.float32)):
        return float(obj)
    return obj

class SampleDataGenerator:
    """Generate realistic sample data for cost forecasting, anomaly detection, and resource utilization"""

    def __init__(self, config: Config = None):
        self.config = config if config is not None else Config()
        self.employee_patterns = {
            'consistent': {'reliability': 0.95, 'variance': 0.1},
            'inconsistent': {'reliability': 0.7, 'variance': 0.3},
            'sporadic': {'reliability': 0.5, 'variance': 0.5}
        }
        
    def generate_complete_sample_data(
        self, 
        db: Client, 
        num_employees: int = None,
        days_back: int = 90,
        selected_projects: List[Dict] = None
    ) -> Dict[str, Any]:
        """Generate complete sample data for selected projects"""
        # Use config values if parameters not provided
        if num_employees is None:
            num_employees = self.config.num_employees
            
        logger.info(f"Generating sample data: {num_employees} employees, {days_back} days")
        logger.info(f"Config: anomaly_rate={self.config.anomaly_rate}, weekend_work_prob={self.config.weekend_work_probability}")
        
        if selected_projects is None:
            projects_response = db.table("projects").select(
                "id, project_id, name, project_budget_usd, team_size, complexity_score, risk_level, "
                "estimated_timeline_months, start_date, end_date"
            ).execute()
            projects = projects_response.data
        else:
            projects = selected_projects
        
        if not projects:
            raise ValueError("No projects found. Please load project data first.")
        
        logger.info(f"Using {len(projects)} projects")
        
        logger.info("Starting employee creation...")
        employees = self._create_sample_employees(db, num_employees)
        logger.info(f"Created {len(employees)} employees")
        
        logger.info("Starting project assignments creation...")
        assignments = self._create_project_assignments(db, employees, projects)
        logger.info(f"Created {len(assignments)} project assignments")
        
        logger.info("Starting daily logs generation...")
        logs_created = self._generate_daily_logs_with_anomalies(
            db, employees, projects, assignments, days_back
        )
        logger.info(f"Created {logs_created} daily logs")
        
        logger.info("Starting sprints generation...")
        sprint_projects = random.sample(projects, min(200, len(projects)))
        sprints_created = self._generate_sprints(db, sprint_projects)
        logger.info(f"Created {sprints_created} sprints")
        
        logger.info("Starting project updates...")
        self._update_project_dates_and_spend(db, projects, days_back)
        logger.info("Updated project dates and spending")
        
        logger.info("🎉 Sample data generation complete!")
        
        return {
            "employees_created": len(employees),
            "assignments_created": len(assignments),
            "logs_created": logs_created,
            "sprints_created": sprints_created,
            "projects_used": len(projects)
        }
    
    def _create_sample_employees(self, db: Client, num_employees: int) -> List[Dict]:
        """Create sample employees with realistic profiles and patterns"""
        roles = ['Developer', 'Senior Developer', 'QA Engineer', 'DevOps Engineer', 
                 'Designer', 'Business Analyst', 'Project Manager', 'Tech Lead']
        skill_levels = ['Junior', 'Mid', 'Senior', 'Expert']
        patterns = ['consistent', 'inconsistent', 'sporadic']
        
        rate_ranges = {
            'Developer': (50, 80),
            'Senior Developer': (80, 120),
            'QA Engineer': (45, 75),
            'DevOps Engineer': (70, 110),
            'Designer': (55, 85),
            'Business Analyst': (60, 90),
            'Project Manager': (90, 140),
            'Tech Lead': (100, 150)
        }
        
        employees = []
        batch_size = 20
        employee_batch = []
        
        for i in range(num_employees):
            role = np.random.choice(roles)
            skill_level = np.random.choice(skill_levels, p=[0.2, 0.4, 0.3, 0.1])
            pattern = np.random.choice(patterns, p=[0.6, 0.25, 0.15])
            
            base_min, base_max = rate_ranges.get(role, (50, 100))
            if skill_level == 'Junior':
                hourly_rate = np.random.uniform(base_min * 0.7, base_min * 1.0)
            elif skill_level == 'Mid':
                hourly_rate = np.random.uniform(base_min * 0.9, base_max * 0.7)
            elif skill_level == 'Senior':
                hourly_rate = np.random.uniform(base_max * 0.6, base_max * 0.9)
            else:
                hourly_rate = np.random.uniform(base_max * 0.8, base_max * 1.2)
            
            # Use config for max hours calculation
            if 'Manager' in role or 'Lead' in role:
                max_hours = np.random.uniform(6, self.config.standard_hours_per_day)
            elif skill_level in ['Senior', 'Expert']:
                max_hours = np.random.uniform(7, self.config.standard_hours_per_day + 1)
            else:
                max_hours = np.random.uniform(7.5, self.config.standard_hours_per_day + 0.5)
            
            employee = {
                'name': f"Employee_{i+1:03d}",
                'email': f"employee{i+1:03d}_{uuid.uuid4().hex[:6]}@company.com",
                'role': role.lower(),
                'skill_level': skill_level,
                'hourly_rate': round(hourly_rate, 2),
                'max_hours_per_day': round(max_hours, 1),
                'is_active': bool(np.random.choice([True, False], p=[0.95, 0.05])),
                'hire_date': (datetime.now() - timedelta(days=np.random.randint(180, 1800))).date().isoformat(),
                'created_at': datetime.now().isoformat()
            }
            
            employee_batch.append(employee)
            
            if len(employee_batch) >= batch_size:
                try:
                    response = db.table('employees').insert(employee_batch).execute()
                    employees.extend(response.data)
                    logger.info(f"Inserted batch of {len(employee_batch)} employees. Total so far: {len(employees)}")
                    employee_batch = []
                except Exception as e:
                    logger.error(f"Failed to insert employee batch: {e}")
                    logger.error(f"Problematic batch: {employee_batch}")
                    raise
            
        if employee_batch:
            try:
                response = db.table('employees').insert(employee_batch).execute()
                employees.extend(response.data)
                logger.info(f"Inserted final batch of {len(employee_batch)} employees. Total: {len(employees)}")
            except Exception as e:
                logger.error(f"Failed to insert final employee batch: {e}")
                logger.error(f"Problematic batch: {employee_batch}")
                raise
        
        for emp in employees:
            emp['pattern'] = np.random.choice(patterns, p=[0.6, 0.25, 0.15])
        
        return employees
    
    def _create_project_assignments(
        self,
        db: Client,
        employees: List[Dict],
        projects: List[Dict]
    ) -> List[Dict]:
        """Create realistic project assignments with proper max_projects_per_employee constraint enforcement

        This method now tracks how many projects each employee is assigned to and skips employees
        who have reached the max_projects_per_employee limit, ensuring the constraint is enforced
        during assignment creation rather than just during daily logging.
        """
        assignments = []
        available_employees = employees.copy()
        np.random.shuffle(available_employees)

        # Track how many projects each employee is assigned to
        employee_project_count = {emp['id']: 0 for emp in employees}
        max_projects = self.config.max_projects_per_employee

        batch_size = 100
        assignment_batch = []

        for proj_idx, project in enumerate(projects):
            if proj_idx % 100 == 0 and proj_idx > 0:
                logger.info(f"Processed assignments for {proj_idx} projects so far")

            team_size = project.get('team_size')
            if team_size is None:
                team_size = np.random.randint(3, 12)
            else:
                team_size = int(float(team_size))
            team_size = max(2, min(team_size, 20))

            team = []
            employees_considered = 0

            # Find available employees who haven't reached the max project limit
            while len(team) < team_size and employees_considered < len(available_employees):
                # Cycle through employees in round-robin fashion
                emp_idx = employees_considered % len(available_employees)
                emp = available_employees[emp_idx]
                employees_considered += 1

                # Skip inactive employees or those at max project limit
                if not emp['is_active'] or employee_project_count[emp['id']] >= max_projects:
                    continue

                team.append(emp)
                employee_project_count[emp['id']] += 1

            # Log if we couldn't fill the team due to constraint
            if len(team) < team_size:
                logger.info(f"Project {project['id']}: Could only assign {len(team)}/{team_size} employees due to max_projects_per_employee constraint")
            
            project_start = pd.to_datetime(project.get('start_date') or (datetime.now() - timedelta(days=np.random.randint(90, 180))))
            project_end = pd.to_datetime(project.get('end_date') or (project_start + timedelta(days=np.random.randint(90, 720))))
            
            for emp in team:
                allocation = np.random.choice([50, 60, 70, 80, 90, 100], p=[0.15, 0.15, 0.15, 0.15, 0.15, 0.25])
                expected_hours = emp['max_hours_per_day'] * (allocation / 100.0)
                
                if not (0 <= allocation <= 100):
                    logger.warning(f"Invalid allocation_percentage {allocation} for employee {emp['id']}, project {project['id']}. Setting to 100.")
                    allocation = 100
                    expected_hours = emp['max_hours_per_day']
                
                assignment_start = project_start - timedelta(days=np.random.randint(0, 30))
                assignment_end = project_end - timedelta(days=np.random.randint(0, 30))
                
                assignment = {
                    "project_id": project['id'],
                    "employee_id": emp['id'],
                    "allocation_percentage": allocation,
                    "expected_hours_per_day": round(expected_hours, 2),
                    "start_date": assignment_start.date().isoformat(),
                    "end_date": assignment_end.date().isoformat(),
                    "is_active": bool(np.random.choice([True, False], p=[0.9, 0.1])),
                    "created_at": datetime.now().isoformat()
                }
                
                assignment_batch.append(assignment)
                
                if len(assignment_batch) >= batch_size:
                    try:
                        assignment_batch = convert_numpy_types(assignment_batch)
                        response = db.table("project_assignments").insert(assignment_batch).execute()
                        assignments.extend(response.data)
                        logger.info(f"Inserted batch of {len(assignment_batch)} assignments. Total so far: {len(assignments)}")
                        assignment_batch = []
                    except Exception as e:
                        logger.error(f"Failed to insert assignment batch: {e}")
                        logger.error(f"Problematic batch: {assignment_batch}")
                        raise
            
        if assignment_batch:
            try:
                assignment_batch = convert_numpy_types(assignment_batch)
                response = db.table("project_assignments").insert(assignment_batch).execute()
                assignments.extend(response.data)
                logger.info(f"Inserted final batch of {len(assignment_batch)} assignments. Total: {len(assignments)}")
            except Exception as e:
                logger.error(f"Failed to insert final assignment batch: {e}")
                logger.error(f"Problematic batch: {assignment_batch}")
                raise
        
        return assignments

        # Note: This method now properly enforces the max_projects_per_employee constraint
        # during assignment creation by:
        # 1. Tracking project count per employee in employee_project_count dictionary
        # 2. Skipping employees who have reached the limit when building teams
        # 3. Logging when teams can't be fully staffed due to the constraint
        # This ensures employees are never assigned to more projects than the configured limit.
    
    def _generate_daily_logs_with_anomalies(
        self, 
        db: Client, 
        employees: List[Dict], 
        projects: List[Dict],
        assignments: List[Dict],
        days_back: int
    ) -> int:
        logs_created = 0
        batch_size = 5000
        logs_batch = []
        
        projects_dict = {p['id']: p for p in projects}
        
        risk_multipliers = {
            'Very Low': (0.7, 0.9),
            'Low': (0.8, 1.0),
            'Medium': (0.9, 1.2),
            'High': (1.1, 1.5),
            'Very High': (1.3, 1.8)
        }
        
        assignment_map = {}
        for assignment in assignments:
            if assignment['is_active']:
                emp_id = assignment['employee_id']
                if emp_id not in assignment_map:
                    assignment_map[emp_id] = []
                assignment_map[emp_id].append(assignment)
        
        for days_ago in range(days_back, -1, -1):
            log_date = datetime.now() - timedelta(days=days_ago)
            is_weekend = log_date.weekday() >= 5
            
            # Use config for weekend work probability
            if is_weekend and np.random.random() < (1 - self.config.weekend_work_probability):
                continue
            
            if days_ago % 5 == 0:
                logger.info(f"Generating logs for day {days_ago} ago (date: {log_date.date()}). Logs created so far: {logs_created}")
            
            for emp in employees:
                if not emp['is_active']:
                    continue
                
                emp_assignments = assignment_map.get(emp['id'], [])
                if not emp_assignments:
                    continue
                
                pattern = emp.get('pattern', 'consistent')
                pattern_config = self.employee_patterns[pattern]
                
                if np.random.random() > pattern_config['reliability'] * np.random.uniform(0.95, 1.05):
                    continue
                
                num_projects = min(len(emp_assignments), np.random.randint(1, self.config.max_projects_per_employee + 1))
                selected_assignments = np.random.choice(emp_assignments, num_projects, replace=False)
                
                daily_total_hours = 0
                
                for assignment in selected_assignments:
                    if log_date < pd.to_datetime(assignment['start_date']) or log_date > pd.to_datetime(assignment['end_date']):
                        continue
                    
                    project = projects_dict[assignment['project_id']]
                    complexity = float(project.get('complexity_score', np.random.uniform(4, 6)))
                    risk_level = project.get('risk_level', np.random.choice(list(risk_multipliers.keys())))
                    risk_min, risk_max = risk_multipliers.get(risk_level, (0.9, 1.2))
                    risk_factor = np.random.uniform(risk_min, risk_max)
                    complexity_factor = 1 + (complexity - 5) * np.random.uniform(0.04, 0.06)
                    
                    expected_hours = assignment['expected_hours_per_day']
                    variance = pattern_config['variance'] * np.random.uniform(0.8, 1.2)
                    base_hours = np.random.normal(expected_hours, expected_hours * variance)
                    
                    hours_logged = base_hours * risk_factor * complexity_factor
                    
                    if is_weekend:
                        hours_logged *= np.random.uniform(0.3, 0.5)
                    
                    anomaly_type = self._introduce_anomaly(emp, log_date, days_ago)
                    if anomaly_type == 'sudden_drop':
                        hours_logged *= np.random.uniform(0.2, 0.4)
                    elif anomaly_type == 'overwork':
                        hours_logged *= np.random.uniform(1.5, 2.0)
                    elif anomaly_type == 'zero_hours':
                        hours_logged = 0
                    elif anomaly_type == 'spike':
                        hours_logged *= np.random.uniform(1.2, 1.5)
                    
                    hours_logged = max(0, round(hours_logged, 2))
                    
                    daily_total_hours += hours_logged
                    # Use config for max hours limit
                    if daily_total_hours > self.config.max_hours_per_day * 1.2:
                        hours_logged *= 0.8
                    
                    completion_percentage = self._calculate_completion_rate(hours_logged, expected_hours, pattern)
                    bugs_found = np.random.poisson(complexity * np.random.uniform(0.2, 0.4))
                    bugs_fixed = int(bugs_found * np.random.uniform(0.4, 0.95))
                    issues_reported = self._calculate_issues(hours_logged, pattern, anomaly_type)
                    story_points_completed = round(hours_logged / np.random.uniform(1.5, 2.5) * np.random.uniform(0.7, 1.3), 1)
                    code_quality_score = round(np.random.uniform(5.0, 10.0) if anomaly_type == 'overwork' else np.random.uniform(6.5, 9.5), 1)
                    tasks_completed = np.random.randint(0, 6) if hours_logged > 0 else 0
                    
                    daily_log = {
                        "project_id": assignment['project_id'],
                        "employee_id": emp['id'],
                        "date": log_date.date().isoformat(),
                        "hours_logged": hours_logged,
                        "task_description": self._generate_task_description(emp['role']),
                        "task_category": np.random.choice(['development', 'testing', 'design', 'planning', 'documentation', 'meeting'], p=[0.3, 0.2, 0.15, 0.15, 0.1, 0.1]),
                        "completion_percentage": round(completion_percentage, 2),
                        "issues_reported": issues_reported,
                        "bugs_found": bugs_found,
                        "bugs_fixed": bugs_fixed,
                        "story_points_completed": story_points_completed,
                        "code_quality_score": code_quality_score,
                        "tasks_completed": tasks_completed,
                        "created_at": datetime.now().isoformat()
                    }
                    
                    logs_batch.append(daily_log)
                    
                    if len(logs_batch) >= batch_size:
                        try:
                            db.table("daily_logs").insert(logs_batch).execute()
                            logs_created += len(logs_batch)
                            logger.info(f"Inserted batch of {len(logs_batch)} daily logs. Total so far: {logs_created}")
                            logs_batch = []
                        except Exception as e:
                            logger.warning(f"Failed to insert log batch: {e}")
                            logger.warning(f"Problematic batch: {logs_batch[:5]}...")
                            raise
            
        if logs_batch:
            try:
                db.table("daily_logs").insert(logs_batch).execute()
                logs_created += len(logs_batch)
                logger.info(f"Inserted final batch of {len(logs_batch)} daily logs. Total: {logs_created}")
            except Exception as e:
                logger.warning(f"Failed to insert final log batch: {e}")
                logger.warning(f"Problematic batch: {logs_batch[:5]}...")
                raise
        
        return logs_created
    
    def _introduce_anomaly(self, emp: Dict, log_date: datetime, days_ago: int) -> str:
        """Introduce anomalies based on config probabilities"""
        pattern = emp.get('pattern', 'consistent')
        # Use config anomaly rate
        base_prob = {'consistent': 0.05, 'inconsistent': 0.15, 'sporadic': 0.3}[pattern]
        anomaly_prob = base_prob * self.config.anomaly_rate * 5  # Scale up to match config rate
        anomaly_prob *= np.random.uniform(0.8, 1.2)
        
        if np.random.random() < anomaly_prob:
            return np.random.choice(['sudden_drop', 'overwork', 'zero_hours', 'spike'], p=[0.4, 0.25, 0.2, 0.15])
        return 'normal'
    
    def _calculate_completion_rate(self, hours: float, expected: float, pattern: str) -> float:
        if expected == 0:
            return np.random.uniform(40, 60)
        base_rate = (hours / expected * 100)
        adjust = {'consistent': np.random.uniform(0.9, 1.1), 'inconsistent': np.random.uniform(0.7, 1.0), 'sporadic': np.random.uniform(0.5, 0.9)}[pattern]
        rate = base_rate * adjust
        return max(0, min(100, rate))
    
    def _calculate_issues(self, hours: float, pattern: str, anomaly_type: str) -> int:
        base_lambda = hours / np.random.uniform(4, 6)
        if anomaly_type in ['overwork', 'spike']:
            base_lambda *= 1.5
        elif anomaly_type == 'sudden_drop':
            base_lambda *= 0.5
        issues = np.random.poisson(base_lambda)
        if pattern == 'sporadic':
            issues += np.random.randint(0, 3)
        return max(0, issues)
    
    def _generate_task_description(self, role: str) -> str:
        tasks = {
            'developer': ['Implemented new API endpoint', 'Fixed critical bug in authentication', 'Conducted code review for team', 'Optimized database queries', 'Developed frontend component'],
            'senior developer': ['Designed system architecture', 'Mentored junior developers', 'Refactored legacy code', 'Implemented performance improvements', 'Led technical discussions'],
            'qa engineer': ['Executed regression tests', 'Reported 5 new bugs', 'Automated UI tests', 'Performed load testing', 'Verified feature requirements'],
            'devops engineer': ['Set up CI/CD pipeline', 'Configured cloud infrastructure', 'Monitored system performance', 'Handled deployment to production', 'Implemented security measures'],
            'designer': ['Created UI mockups', 'Conducted user research', 'Designed user flows', 'Updated design system', 'Created visual assets'],
            'business analyst': ['Gathered requirements', 'Wrote user stories', 'Analyzed business processes', 'Conducted stakeholder interviews', 'Prepared reports'],
            'project manager': ['Facilitated sprint planning', 'Led daily standup', 'Managed project risks', 'Coordinated with clients', 'Tracked project metrics'],
            'tech lead': ['Reviewed technical designs', 'Guided team on best practices', 'Resolved technical blockers', 'Planned technical roadmap', 'Evaluated new technologies']
        }
        return np.random.choice(tasks.get(role, ['Worked on project tasks', 'Attended meetings', 'Documented code']))
    
    def _generate_sprints(self, db: Client, projects: List[Dict]) -> int:
        sprints_created = 0
        batch_size = 100
        sprint_batch = []
        
        for proj_idx, project in enumerate(projects):
            if proj_idx % 50 == 0 and proj_idx > 0:
                logger.info(f"Processed sprints for {proj_idx} projects so far")
            
            num_sprints = np.random.randint(3, 15)
            # Validate and handle start_date
            start_date_str = project.get('start_date')
            try:
                if start_date_str:
                    project_start = pd.to_datetime(start_date_str)
                else:
                    logger.warning(f"Project {project['id']} has no start_date. Using fallback: 180 days ago.")
                    project_start = pd.to_datetime(datetime.now() - timedelta(days=180))
            except Exception as e:
                logger.warning(f"Invalid start_date '{start_date_str}' for project {project['id']}: {e}. Using fallback: 180 days ago.")
                project_start = pd.to_datetime(datetime.now() - timedelta(days=180))
            
            sprint_start = project_start + timedelta(days=int(np.random.randint(0, 30)))
            
            for sprint_num in range(1, num_sprints + 1):
                sprint_duration = int(np.random.choice([7, 14, 21, 30], p=[0.1, 0.6, 0.2, 0.1]))
                sprint_end = sprint_start + timedelta(days=sprint_duration)
                
                planned_points = np.random.randint(15, 60)
                completion_rate = np.random.uniform(0.65, 1.05)
                completed_points = int(planned_points * completion_rate)
                velocity = completed_points / (sprint_duration / 7.0)
                
                sprint = {
                    "project_id": project['id'],
                    "sprint_number": sprint_num,
                    "start_date": sprint_start.date().isoformat(),
                    "end_date": sprint_end.date().isoformat(),
                    "planned_story_points": planned_points,
                    "completed_story_points": completed_points,
                    "velocity": round(velocity, 2),
                    "bugs_found": np.random.randint(0, 15),
                    "bugs_fixed": np.random.randint(0, 12),
                    "created_at": datetime.now().isoformat()
                }
                
                sprint_batch.append(sprint)
                
                if len(sprint_batch) >= batch_size:
                    try:
                        db.table("sprints").insert(sprint_batch).execute()
                        sprints_created += len(sprint_batch)
                        logger.info(f"Inserted batch of {len(sprint_batch)} sprints. Total so far: {sprints_created}")
                        sprint_batch = []
                    except Exception as e:
                        logger.warning(f"Failed to insert sprint batch: {e}")
                        logger.warning(f"Problematic batch: {sprint_batch[:5]}...")
                        raise
                
                sprint_start = sprint_end + timedelta(days=int(np.random.randint(1, 4)))
        
        if sprint_batch:
            try:
                db.table("sprints").insert(sprint_batch).execute()
                sprints_created += len(sprint_batch)
                logger.info(f"Inserted final batch of {len(sprint_batch)} sprints. Total: {sprints_created}")
            except Exception as e:
                logger.warning(f"Failed to insert final sprint batch: {e}")
                logger.warning(f"Problematic batch: {sprint_batch[:5]}...")
                raise
        
        return sprints_created
    
    def _update_project_dates_and_spend(self, db: Client, projects: List[Dict], days_back: int):
        start_date_base = datetime.now() - timedelta(days=days_back + np.random.randint(0, 30))
        
        for proj_idx, project in enumerate(projects):
            if proj_idx % 100 == 0 and proj_idx > 0:
                logger.info(f"Updated {proj_idx} projects so far")
            
            project_id = project['id']
            
            start_date = project.get('start_date') or start_date_base.date().isoformat()
            estimated_months = project.get('estimated_timeline_months')
            if estimated_months is None:
                estimated_months = np.random.randint(3, 24)
            else:
                estimated_months = int(float(estimated_months))
            estimated_months = max(2, min(estimated_months, 48))
            end_date = (pd.to_datetime(start_date) + timedelta(days=estimated_months * 30 + np.random.randint(-15, 15))).date().isoformat()
            
            try:
                logs_response = db.table('daily_logs').select(
                    'hours_logged, employee_id'
                ).eq('project_id', project_id).execute()
                
                logs = logs_response.data
                total_spend = 0.0
                
                if logs:
                    employee_ids = list(set(log['employee_id'] for log in logs))
                    employees_response = db.table('employees').select(
                        'id, hourly_rate'
                    ).in_('id', employee_ids).execute()
                    
                    employee_rates = {
                        emp['id']: float(emp.get('hourly_rate', np.random.uniform(60, 90))) 
                        for emp in employees_response.data
                    }
                    
                    total_spend = sum(
                        float(log['hours_logged']) * employee_rates.get(log['employee_id'], 75.0)
                        for log in logs
                    ) * np.random.uniform(0.95, 1.05)
                
                update_data = {
                    'start_date': start_date,
                    'end_date': end_date,
                    'current_spend': round(total_spend, 2),
                    'status': np.random.choice(['active', 'on_hold', 'completed'], p=[0.8, 0.15, 0.05]),
                    'name': project.get('name') or f"Project {project['project_id']}_{np.random.randint(1000,9999)}",
                    'updated_at': datetime.now().isoformat()
                }
                
                db.table("projects").update(update_data).eq('id', project_id).execute()
                
            except Exception as e:
                logger.error(f"Error updating project {project_id}: {e}")
        
        logger.info(f"Completed updating all {len(projects)} projects")

def main():
    parser = argparse.ArgumentParser(
        description="Generate sample data for subset of projects (cost, anomalies, utilization)"
    )
    parser.add_argument(
        "--employees",
        type=int,
        default=35,
        help="Number of employees to create (default: 35)"
    )
    parser.add_argument(
        "--days",
        type=int,
        default=45,
        help="Days of historical data to generate (default: 45)"
    )
    parser.add_argument(
        "--max-projects",
        type=int,
        default=800,
        help="Maximum number of projects to generate data for (default: 800)"
    )
    parser.add_argument(
        "--project-selection",
        choices=['random', 'high-budget', 'high-risk', 'first-n'],
        default='high-budget',
        help="How to select projects (default: high-budget)"
    )
    parser.add_argument(
        "--clear-logs",
        action="store_true",
        help="Clear existing daily logs before generating new data"
    )
    parser.add_argument(
        "--clear-employees",
        action="store_true",
        help="Clear existing employees before generating new data"
    )
    parser.add_argument(
        "--clear-assignments",
        action="store_true",
        help="Clear existing project assignments"
    )
    parser.add_argument(
        "--clear-sprints",
        action="store_true",
        help="Clear existing sprints"
    )
    parser.add_argument(
        "--clear-all",
        action="store_true",
        help="Clear all operational data before generating"
    )
    # Add config override arguments
    parser.add_argument(
        "--anomaly-rate",
        type=float,
        default=0.20,
        help="Anomaly rate (0.0-1.0, default: 0.20 = 20%%)"
    )
    parser.add_argument(
        "--standard-hours",
        type=int,
        default=8,
        help="Standard hours per day (default: 8)"
    )
    parser.add_argument(
        "--max-hours",
        type=int,
        default=16,
        help="Maximum hours per day (default: 16)"
    )
    parser.add_argument(
        "--weekend-work-prob",
        type=float,
        default=0.05,
        help="Probability of weekend work (0.0-1.0, default: 0.05 = 5%%)"
    )
    parser.add_argument(
        "--max-projects-per-employee",
        type=int,
        default=3,
        help="Maximum projects an employee can work on simultaneously (default: 3)"
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("Unified Sample Data Generator (SUBSET MODE)")
    print("=" * 60)
    print(f"Employees to create: {args.employees}")
    print(f"Days of history: {args.days}")
    print(f"Max projects: {args.max_projects}")
    print(f"Selection method: {args.project_selection}")
    print(f"Anomaly rate: {args.anomaly_rate * 100}%")
    print(f"Standard hours/day: {args.standard_hours}")
    print(f"Max hours/day: {args.max_hours}")
    print(f"Max projects/employee: {args.max_projects_per_employee}")
    print(f"Weekend work probability: {args.weekend_work_prob * 100}%")
    
    estimated_logs = args.max_projects * args.days * 4
    print(f"\n📊 Estimated daily log records: ~{estimated_logs:,}")
    print(f"⏱️  Estimated time: ~{int(estimated_logs / 4000)} minutes")
    print()
    
    print("Connecting to Supabase...")
    db = connect_db()
    
    if not db:
        print("❌ Failed to connect to database")
        print("Please check your SUPABASE_URL and SUPABASE_KEY in .env")
        return 1
    
    print("✅ Connected to Supabase")
    
    if args.clear_all:
        print("\n🗑️  Clearing all operational data...")
        try:
            db.table("daily_logs").delete().neq("id", 0).execute()
            db.table("sprints").delete().neq("id", 0).execute()
            db.table("project_assignments").delete().neq("id", 0).execute()
            db.table("anomalies").delete().neq("id", 0).execute()
            db.table("resource_utilization_alerts").delete().neq("id", 0).execute()
            db.table("anomaly_summary").delete().neq("id", 0).execute()
            db.table("employees").delete().neq("id", 0).execute()
            print("✅ All operational data cleared")
        except Exception as e:
            print(f"⚠️  Warning: Could not clear data: {e}")
    else:
        if args.clear_employees:
            print("\n🗑️  Clearing employees...")
            try:
                db.table('employees').delete().neq('id', 0).execute()
                print("✅ Employees cleared")
            except Exception as e:
                print(f"⚠️  Warning: {e}")
        
        if args.clear_logs:
            print("\n🗑️  Clearing daily logs...")
            try:
                db.table('daily_logs').delete().neq('id', 0).execute()
                print("✅ Daily logs cleared")
            except Exception as e:
                print(f"⚠️  Warning: {e}")
        
        if args.clear_assignments:
            print("\n🗑️  Clearing project assignments...")
            try:
                db.table('project_assignments').delete().neq('id', 0).execute()
                print("✅ Assignments cleared")
            except Exception as e:
                print(f"⚠️  Warning: {e}")
        
        if args.clear_sprints:
            print("\n🗑️  Clearing sprints...")
            try:
                db.table('sprints').delete().neq('id', 0).execute()
                print("✅ Sprints cleared")
            except Exception as e:
                print(f"⚠️  Warning: {e}")
    
    print(f"\n📊 Fetching projects with '{args.project_selection}' selection...")
    try:
        all_projects_response = db.table('projects').select(
            'id, project_id, name, project_budget_usd, team_size, '
            'complexity_score, risk_level, estimated_timeline_months, start_date, end_date'
        ).execute()
        
        all_projects = all_projects_response.data
        total_projects = len(all_projects)
        
        if total_projects == 0:
            print("❌ No projects found!")
            print("Please load project data first using:")
            print("  python main.py --load-csv")
            return 1
        
        print(f"✅ Found {total_projects} total projects")
        
        selected_projects = select_projects(
            all_projects, 
            args.max_projects, 
            args.project_selection
        )
        
        print(f"✅ Selected {len(selected_projects)} projects")
        
        if args.project_selection == 'high-budget':
            avg_budget = sum(float(p.get('project_budget_usd', 0) or 0) for p in selected_projects) / len(selected_projects)
            print(f"   Average budget: ${avg_budget:,.2f}")
        elif args.project_selection == 'high-risk':
            risk_dist = {}
            for p in selected_projects:
                risk = p.get('risk_level', 'Unknown')
                risk_dist[risk] = risk_dist.get(risk, 0) + 1
            print(f"   Risk distribution: {risk_dist}")
        
    except Exception as e:
        print(f"❌ Error fetching projects: {e}")
        return 1
    
    print(f"\n🎲 Generating sample data for {len(selected_projects)} projects...")
    print(f"   This may take a few minutes...")
    
    try:
        # Create config with command-line overrides
        config = Config(
            num_employees=args.employees,
            anomaly_rate=args.anomaly_rate,
            standard_hours_per_day=args.standard_hours,
            max_hours_per_day=args.max_hours,
            max_projects_per_employee=args.max_projects_per_employee,
            weekend_work_probability=args.weekend_work_prob
        )
        
        generator = SampleDataGenerator(config)
        
        results = generator.generate_complete_sample_data(
            db,
            num_employees=args.employees,
            days_back=args.days,
            selected_projects=selected_projects
        )
        
        print("\n" + "=" * 60)
        print("✅ Sample data generation completed successfully!")
        print("=" * 60)
        print(f"Employees created: {results['employees_created']}")
        print(f"Assignments created: {results['assignments_created']}")
        print(f"Daily logs created: {results['logs_created']}")
        print(f"Sprints created: {results['sprints_created']}")
        print(f"Projects updated: {results['projects_used']}")
        print("\nConfiguration used:")
        print(f"  Anomaly rate: {config.anomaly_rate * 100}%")
        print(f"  Standard hours: {config.standard_hours_per_day}h/day")
        print(f"  Max hours: {config.max_hours_per_day}h/day")
        print(f"  Max projects/employee: {config.max_projects_per_employee}")
        print(f"  Weekend work: {config.weekend_work_probability * 100}%")
        print("\nYou can now:")
        print("  1. Start the server: python main.py --run-server")
        print("  2. Test cost forecasting API:")
        print(f"     GET /api/v1/cost-forecasting/forecast/{selected_projects[0]['id']}")
        print("  3. View budget alerts:")
        print("     GET /api/v1/cost-forecasting/budget-alerts")
        print("  4. View anomaly detection:")
        print("     GET /api/v1/anomaly-detection/anomalies")
        print("  5. View resource utilization:")
        print("     GET /api/v1/resource-utilization/utilization-summary")
        print("\nNote: Features available for selected projects with data.")
        return 0
        
    except Exception as e:
        print(f"\n❌ Error generating sample data: {e}")
        traceback.print_exc()
        return 1

def select_projects(projects, max_count, method):
    """Select a subset of projects based on the specified method"""
    import random
    
    if len(projects) <= max_count:
        return projects
    
    if method == 'random':
        return random.sample(projects, max_count)
    
    elif method == 'high-budget':
        sorted_projects = sorted(
            projects, 
            key=lambda p: float(p.get('project_budget_usd', 0) or 0), 
            reverse=True
        )
        return sorted_projects[:max_count]
    
    elif method == 'high-risk':
        risk_priority = {'Very High': 5, 'High': 4, 'Medium': 3, 'Low': 2, 'Very Low': 1, 'Unknown': 0}
        sorted_projects = sorted(
            projects,
            key=lambda p: risk_priority.get(p.get('risk_level', 'Medium'), 3),
            reverse=True
        )
        return sorted_projects[:max_count]
    
    elif method == 'first-n':
        return projects[:max_count]
    
    return projects[:max_count]

if __name__ == "__main__":
    exit(main())