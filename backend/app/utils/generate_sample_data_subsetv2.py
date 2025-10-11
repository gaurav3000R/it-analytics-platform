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
    num_employees: int = 50
    num_projects: int = 12
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
    elif isinstance(obj, np.str_):
        return str(obj)
    elif isinstance(obj, np.bool_):
        return bool(obj)
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
        
        logger.info("Starting bugs generation...")
        bugs_created = self._generate_bugs_for_projects(db, projects, employees, days_back)
        logger.info(f"Created {bugs_created} bugs")
        
        logger.info("Starting project updates...")
        self._update_project_dates_and_spend(db, projects, days_back)
        logger.info("Updated project dates and spending")
        
        logger.info("🎉 Sample data generation complete!")
        
        return {
            "employees_created": len(employees),
            "assignments_created": len(assignments),
            "logs_created": logs_created,
            "sprints_created": sprints_created,
            "bugs_created": bugs_created,
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
        
        anomaly_types = [
            'underutilized', 'overutilized', 'chronic_underestimator', 'chronic_overestimator',
            'sandbagger', 'zombie_task_creator', 'task_abandoner'
        ]
        anomaly_probs = [
            self.config.prob_underutilized, self.config.prob_overutilized,
            self.config.prob_chronic_underestimator, self.config.prob_chronic_overestimator,
            self.config.prob_sandbagger, self.config.prob_zombie_task_creator,
            self.config.prob_task_abandoner
        ]
        anomaly_probs = np.array(anomaly_probs) / sum(anomaly_probs)
        
        for emp in employees:
            emp['pattern'] = np.random.choice(patterns, p=[0.6, 0.25, 0.15])
            emp['anomaly_type'] = None
        
        num_anomalous = int(len(employees) * self.config.anomaly_rate)
        anomalous_indices = np.random.choice(range(len(employees)), num_anomalous, replace=False)
        for idx in anomalous_indices:
            employees[idx]['anomaly_type'] = np.random.choice(anomaly_types, p=anomaly_probs)
        
        return employees
    
    def _create_project_assignments(
        self, 
        db: Client, 
        employees: List[Dict], 
        projects: List[Dict]
    ) -> List[Dict]:
        """Create realistic project assignments with possible overbooking"""
        assignments = []
        available_employees = employees.copy()
        np.random.shuffle(available_employees)
        employee_idx = 0
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
            for _ in range(team_size):
                if employee_idx >= len(available_employees):
                    employee_idx = 0
                emp = available_employees[employee_idx]
                if emp['is_active']:
                    team.append(emp)
                employee_idx += 1
            
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
                    
                    anomaly_type = emp.get('anomaly_type', None)
                    if anomaly_type:
                        if anomaly_type == 'underutilized':
                            if np.random.random() < 0.3:
                                hours_logged = 0
                            else:
                                hours_logged *= np.random.uniform(0.4, 0.7)
                        elif anomaly_type == 'overutilized':
                            hours_logged *= np.random.uniform(1.3, 1.8)
                        elif anomaly_type == 'sandbagger':
                            hours_logged *= np.random.uniform(1.1, 1.4)
                    
                    hours_logged = max(0, round(hours_logged, 2))
                    
                    daily_total_hours += hours_logged
                    if daily_total_hours > self.config.max_hours_per_day * 1.2:
                        hours_logged *= 0.8
                    
                    completion_percentage = self._calculate_completion_rate(hours_logged, expected_hours, pattern)
                    bugs_found = np.random.poisson(complexity * np.random.uniform(0.2, 0.4))
                    bugs_fixed = int(bugs_found * np.random.uniform(0.4, 0.95))
                    issues_reported = self._calculate_issues(hours_logged, pattern, anomaly_type)
                    story_points_completed = round(hours_logged / np.random.uniform(1.5, 2.5) * np.random.uniform(0.7, 1.3), 1)
                    code_quality_score = round(np.random.uniform(5.0, 10.0), 1)
                    tasks_completed = np.random.randint(0, 6) if hours_logged > 0 else 0
                    
                    if anomaly_type:
                        if anomaly_type == 'overutilized':
                            code_quality_score = round(np.random.uniform(4.0, 7.0), 1)
                        elif anomaly_type == 'chronic_underestimator':
                            completion_percentage *= np.random.uniform(1.1, 1.3)
                            completion_percentage = min(100, completion_percentage)
                        elif anomaly_type == 'chronic_overestimator':
                            completion_percentage *= np.random.uniform(0.7, 0.9)
                        elif anomaly_type == 'sandbagger':
                            completion_percentage *= np.random.uniform(0.6, 0.8)
                        elif anomaly_type == 'zombie_task_creator':
                            tasks_completed += np.random.randint(3, 8)
                            issues_reported += np.random.randint(2, 5)
                            completion_percentage *= np.random.uniform(0.5, 0.7)
                        elif anomaly_type == 'task_abandoner':
                            bugs_found += np.random.randint(2, 6)
                            bugs_fixed = int(bugs_found * np.random.uniform(0.1, 0.4))
                            issues_reported += np.random.randint(1, 4)
                    
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
    
    def _calculate_completion_rate(self, hours: float, expected: float, pattern: str) -> float:
        if expected == 0:
            return np.random.uniform(40, 60)
        base_rate = (hours / expected * 100)
        adjust = {'consistent': np.random.uniform(0.9, 1.1), 'inconsistent': np.random.uniform(0.7, 1.0), 'sporadic': np.random.uniform(0.5, 0.9)}[pattern]
        rate = base_rate * adjust
        return max(0, min(100, rate))
    
    def _calculate_issues(self, hours: float, pattern: str, anomaly_type: str) -> int:
        base_lambda = hours / np.random.uniform(4, 6)
        if anomaly_type in ['overutilized', 'sandbagger']:
            base_lambda *= 1.5
        elif anomaly_type == 'underutilized':
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
        
    def _generate_bugs_for_projects(
        self, 
        db: Client, 
        projects: List[Dict],
        employees: List[Dict],
        days_back: int
    ) -> int:
        """Generate realistic bug data for projects"""
        logger.info("Generating bugs for projects...")
        
        bugs_created = 0
        batch_size = 100
        bug_batch = []
        
        bug_types = ['backend', 'frontend', 'database', 'ui', 'performance', 'security', 'integration', 'api']
        environments = ['production', 'staging', 'development']
        severities = ['critical', 'high', 'medium', 'low']
        priorities = ['urgent', 'high', 'medium', 'low']
        statuses = ['open', 'in_progress', 'resolved', 'closed', 'reopened']
        
        risk_bug_multipliers = {
            'Very Low': (0.5, 1.0),
            'Low': (1.0, 2.0),
            'Medium': (2.0, 4.0),
            'High': (3.0, 6.0),
            'Very High': (4.0, 8.0)
        }
        
        # Pre-fetch all assignments to avoid repeated queries
        logger.info("Pre-fetching project assignments for bug generation...")
        try:
            all_assignments_response = db.table("project_assignments").select(
                "project_id, employee_id"
            ).eq("is_active", True).execute()
            
            # Build a map of project_id -> list of employee_ids
            assignment_map = {}
            for assignment in all_assignments_response.data:
                proj_id = assignment['project_id']
                emp_id = assignment['employee_id']
                if proj_id not in assignment_map:
                    assignment_map[proj_id] = []
                assignment_map[proj_id].append(emp_id)
            
            logger.info(f"Found assignments for {len(assignment_map)} projects")
        except Exception as e:
            logger.error(f"Failed to fetch assignments: {e}")
            assignment_map = {}
        
        # Create a pool of employee IDs for fallback
        employee_ids = [emp['id'] for emp in employees if emp.get('is_active', True)]
        if not employee_ids:
            logger.warning("No active employees found for bug assignment")
            return 0
        
        # Track bug IDs to ensure uniqueness
        used_bug_ids = set()
        
        for proj_idx, project in enumerate(projects):
            if proj_idx % 100 == 0 and proj_idx > 0:
                logger.info(f"Processed bug generation for {proj_idx}/{len(projects)} projects. Bugs created: {bugs_created}")
            
            project_id = project['id']
            risk_level = project.get('risk_level', 'Medium')
            complexity = float(project.get('complexity_score', 5.0))
            
            # Calculate expected bugs based on risk and complexity
            bug_min, bug_max = risk_bug_multipliers.get(risk_level, (2.0, 4.0))
            base_bugs = np.random.uniform(bug_min, bug_max) * complexity
            num_bugs = int(base_bugs * days_back / 30)  # Scale by time period
            
            # Ensure at least 1 bug for Medium+ risk projects
            if risk_level in ['Medium', 'High', 'Very High'] and num_bugs < 1:
                num_bugs = np.random.randint(1, 3)
            
            if num_bugs == 0:
                continue
            
            # Get team members for this project from pre-fetched map
            team_members = assignment_map.get(project_id, [])
            
            # Fallback: if no team members, randomly select some employees
            if not team_members:
                team_members = list(np.random.choice(employee_ids, min(5, len(employee_ids)), replace=False))
            
            for bug_num in range(num_bugs):
                # Generate unique bug_id using UUID to avoid collisions
                # Format: BUG-{project_internal_id}-{uuid_short}
                bug_id_base = f"BUG-{project_id}-{uuid.uuid4().hex[:8].upper()}"
                
                # Ensure uniqueness (unlikely but possible collision)
                while bug_id_base in used_bug_ids:
                    bug_id_base = f"BUG-{project_id}-{uuid.uuid4().hex[:8].upper()}"
                used_bug_ids.add(bug_id_base)
                
                # Generate bug timing
                days_ago = np.random.randint(0, days_back)
                reported_date = datetime.now() - timedelta(days=days_ago)
                
                # Bug characteristics
                severity = str(np.random.choice(severities, p=[0.05, 0.20, 0.50, 0.25]))
                priority = str(np.random.choice(priorities, p=[0.05, 0.25, 0.50, 0.20]))
                bug_type = str(np.random.choice(bug_types))
                environment = str(np.random.choice(environments, p=[0.3, 0.4, 0.3]))
                
                # Status based on age and severity
                if days_ago < 3:
                    status = str(np.random.choice(['open', 'in_progress'], p=[0.6, 0.4]))
                elif days_ago < 7:
                    status = str(np.random.choice(['open', 'in_progress', 'resolved'], p=[0.3, 0.4, 0.3]))
                else:
                    status = str(np.random.choice(['resolved', 'closed', 'reopened'], p=[0.5, 0.4, 0.1]))
                
                # Reopen probability based on severity
                reopen_prob = {'critical': 0.15, 'high': 0.12, 'medium': 0.08, 'low': 0.05}
                reopen_count = 0
                if status == 'reopened' or np.random.random() < reopen_prob.get(severity, 0.08):
                    reopen_count = int(np.random.randint(1, 4))
                    if reopen_count >= 3:
                        status = 'reopened'
                
                # Resolution time based on severity
                if status in ['resolved', 'closed']:
                    base_hours = {'critical': 8, 'high': 24, 'medium': 48, 'low': 72}
                    resolution_time = np.random.normal(
                        base_hours.get(severity, 48),
                        base_hours.get(severity, 48) * 0.3
                    )
                    resolution_time = max(1.0, float(resolution_time))
                    resolved_at = reported_date + timedelta(hours=resolution_time)
                else:
                    resolution_time = None
                    resolved_at = None
                
                # First response time
                first_response = float(np.random.uniform(0.5, 12) if severity == 'critical' else np.random.uniform(2, 48))
                
                # Estimated vs actual hours
                estimated_hours = float(np.random.uniform(1, 16) if severity in ['critical', 'high'] else np.random.uniform(0.5, 8))
                actual_hours = float(estimated_hours * np.random.uniform(0.8, 1.5)) if resolution_time else None
                
                # Assign to team member - pick a random team member as employee_id
                employee_id = int(np.random.choice(team_members)) if team_members else None
                reported_by = int(np.random.choice(team_members)) if team_members else None
                assigned_to = int(np.random.choice(team_members)) if team_members and np.random.random() > 0.2 else None
                
                # Generate tags and metadata with proper type conversion
                tags_dict = {
                    "complexity": float(complexity),
                    "risk_level": str(risk_level)
                }
                
                metadata_dict = {
                    "browser": str(np.random.choice(['Chrome', 'Firefox', 'Safari', 'Edge'])) if bug_type in ['frontend', 'ui'] else None,
                    "os": str(np.random.choice(['Windows', 'Mac', 'Linux'])),
                    "version": f"{np.random.randint(1, 5)}.{np.random.randint(0, 10)}.{np.random.randint(0, 100)}"
                }
                
                bug = {
                    "project_id": int(project_id),
                    "employee_id": employee_id,  # Main employee working on the bug
                    "bug_id": bug_id_base,
                    "title": self._generate_bug_title(bug_type, severity),
                    "description": self._generate_bug_description(bug_type),
                    "severity": severity,
                    "priority": priority,
                    "status": status,
                    "bug_type": bug_type,
                    "environment": environment,
                    "reported_by": reported_by,
                    "assigned_to": assigned_to,
                    "found_in_sprint": None,  # Could be enhanced to link to sprints
                    "resolved_in_sprint": None,
                    "reopen_count": int(reopen_count),
                    "resolution_time_hours": float(resolution_time) if resolution_time else None,
                    "first_response_time_hours": float(first_response),
                    "estimated_hours": float(estimated_hours),
                    "actual_hours": float(actual_hours) if actual_hours else None,
                    "tags": tags_dict,
                    "metadata": metadata_dict,
                    "reported_at": reported_date.isoformat(),
                    "resolved_at": resolved_at.isoformat() if resolved_at else None,
                    "closed_at": resolved_at.isoformat() if status == 'closed' and resolved_at else None,
                    "created_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat()
                }
                
                bug_batch.append(bug)
                
                if len(bug_batch) >= batch_size:
                    try:
                        # Convert all numpy types before insertion
                        bug_batch_clean = convert_numpy_types(bug_batch)
                        response = db.table("bugs").insert(bug_batch_clean).execute()
                        inserted_bugs = response.data
                        bugs_created += len(inserted_bugs)
                        logger.info(f"Inserted batch of {len(bug_batch)} bugs. Total so far: {bugs_created}")
                        
                        # Generate comments for inserted bugs
                        comments_to_insert = []
                        for inserted_bug in inserted_bugs:
                            if inserted_bug.get('status') in ['resolved', 'closed', 'reopened']:
                                comments = self._generate_bug_comments(
                                    db, 
                                    inserted_bug, 
                                    inserted_bug.get('reported_by'), 
                                    inserted_bug.get('assigned_to'),
                                    inserted_bug.get('status')
                                )
                                comments_to_insert.extend(comments)
                        
                        # Insert comments in batch
                        if comments_to_insert:
                            try:
                                comments_clean = convert_numpy_types(comments_to_insert)
                                db.table("bug_comments").insert(comments_clean).execute()
                                logger.info(f"Inserted {len(comments_to_insert)} bug comments")
                            except Exception as e:
                                logger.warning(f"Failed to insert bug comments batch: {e}")
                        
                        bug_batch = []
                    except Exception as e:
                        logger.error(f"Failed to insert bug batch: {e}")
                        if bug_batch:
                            logger.error(f"First bug in problematic batch: {bug_batch[0]}")
                            logger.error(f"Sample bug_id: {bug_batch[0].get('bug_id', 'N/A')}")
                        logger.error(traceback.format_exc())
                        # Clear the problematic batch and continue
                        bug_batch = []
        
        # Insert remaining bugs
        if bug_batch:
            try:
                bug_batch_clean = convert_numpy_types(bug_batch)
                response = db.table("bugs").insert(bug_batch_clean).execute()
                inserted_bugs = response.data
                bugs_created += len(inserted_bugs)
                logger.info(f"Inserted final batch of {len(bug_batch)} bugs. Total: {bugs_created}")
                
                # Generate comments for inserted bugs
                comments_to_insert = []
                for inserted_bug in inserted_bugs:
                    if inserted_bug.get('status') in ['resolved', 'closed', 'reopened']:
                        comments = self._generate_bug_comments(
                            db, 
                            inserted_bug, 
                            inserted_bug.get('reported_by'), 
                            inserted_bug.get('assigned_to'),
                            inserted_bug.get('status')
                        )
                        comments_to_insert.extend(comments)
                
                # Insert comments in batch
                if comments_to_insert:
                    try:
                        comments_clean = convert_numpy_types(comments_to_insert)
                        db.table("bug_comments").insert(comments_clean).execute()
                        logger.info(f"Inserted {len(comments_to_insert)} bug comments for final batch")
                    except Exception as e:
                        logger.warning(f"Failed to insert final bug comments batch: {e}")
                        
            except Exception as e:
                logger.error(f"Failed to insert final bug batch: {e}")
                if bug_batch:
                    logger.error(f"First bug in problematic batch: {bug_batch[0]}")
                logger.error(traceback.format_exc())
        
        logger.info(f"Bug generation complete. Total bugs created: {bugs_created}")
        return bugs_created


    def _generate_bug_title(self, bug_type: str, severity: str) -> str:
        """Generate realistic bug title"""
        titles = {
            'backend': [
                'API endpoint returns 500 error',
                'Database connection timeout',
                'Memory leak in background job',
                'Authentication token expired prematurely',
                'Race condition in order processing'
            ],
            'frontend': [
                'Button click not responding',
                'Form validation not working',
                'Page layout broken on mobile',
                'JavaScript error on page load',
                'Infinite loop in component render'
            ],
            'database': [
                'Query performance degradation',
                'Index not being used',
                'Deadlock in transaction',
                'Data inconsistency in reports',
                'Migration script failed'
            ],
            'ui': [
                'Incorrect color scheme',
                'Text overlapping on small screens',
                'Modal dialog not closing',
                'Dropdown menu misaligned',
                'Loading spinner stuck'
            ],
            'performance': [
                'Page load time > 5 seconds',
                'High CPU usage on server',
                'Memory consumption increasing',
                'Slow database queries',
                'API response time degraded'
            ],
            'security': [
                'XSS vulnerability found',
                'SQL injection possible',
                'Unauthorized access to admin panel',
                'Password reset token exposed',
                'Session hijacking risk'
            ],
            'integration': [
                'Third-party API integration failing',
                'Webhook not triggering',
                'Data sync issue with external system',
                'OAuth authentication broken',
                'Payment gateway timeout'
            ],
            'api': [
                'Missing required field in response',
                'Incorrect HTTP status code',
                'Rate limiting not working',
                'CORS error on OPTIONS request',
                'API versioning issue'
            ]
        }
        
        base_title = str(np.random.choice(titles.get(bug_type, ['Generic bug'])))
        
        if severity in ['critical', 'high']:
            prefixes = ['URGENT:', 'CRITICAL:', 'BLOCKER:', 'PRODUCTION:']
            return f"{np.random.choice(prefixes)} {base_title}"
        
        return base_title


    def _generate_bug_description(self, bug_type: str) -> str:
        """Generate bug description"""
        descriptions = [
            "Steps to reproduce:\n1. Navigate to the page\n2. Click on the button\n3. Observe the error",
            "Expected behavior: System should process the request successfully\nActual behavior: Error message displayed",
            "This issue is blocking deployment and needs immediate attention",
            "Intermittent issue that occurs under high load conditions",
            "User reported issue affecting multiple customers"
        ]
        return str(np.random.choice(descriptions))


    def _generate_bug_comments(
        self, 
        db: Client, 
        bug: Dict, 
        reported_by: int, 
        assigned_to: int,
        bug_status: str
    ) -> List[Dict]:
        """Generate bug comments/history - returns list to be inserted in batch"""
        # Only generate comments if bug has been inserted and has an ID
        if 'id' not in bug or bug['id'] is None:
            logger.warning(f"Cannot create comments for bug without ID: {bug.get('bug_id', 'Unknown')}")
            return []
        
        comments = []
        
        # Generate 1-5 comments based on bug status
        if bug_status == 'closed':
            num_comments = np.random.randint(2, 6)
        elif bug_status in ['resolved', 'reopened']:
            num_comments = np.random.randint(1, 5)
        else:
            num_comments = np.random.randint(1, 3)
        
        comment_templates = {
            'note': [
                "Investigating the issue.",
                "Added additional logging for debugging.",
                "Coordinating with the team on this.",
                "Updated documentation to reflect changes.",
                "Reviewing related code sections."
            ],
            'status_update': [
                "Found the root cause in the database layer.",
                "Applied fix, testing now.",
                "Fix verified in staging environment.",
                "Moving to code review.",
                "Waiting for QA verification."
            ],
            'resolution': [
                "Issue resolved and deployed to production.",
                "Fix merged to main branch.",
                "Resolution confirmed, closing ticket.",
                "Deployed fix successfully."
            ],
            'reopen': [
                "Reopening due to regression in production.",
                "Issue has resurfaced, reopening.",
                "Similar symptoms reported, reopening for investigation."
            ]
        }
        
        try:
            reported_date = datetime.fromisoformat(bug['reported_at'].replace('Z', '+00:00'))
        except:
            reported_date = datetime.now() - timedelta(days=7)
        
        current_date = reported_date
        
        for i in range(num_comments):
            # Progress comments over time
            hours_elapsed = np.random.uniform(2, 48) * (i + 1)
            current_date = reported_date + timedelta(hours=hours_elapsed)
            
            # Select comment type based on position and bug status
            if i == 0:
                comment_type = 'note'
            elif i == num_comments - 1 and bug_status in ['resolved', 'closed']:
                comment_type = 'resolution'
            elif bug_status == 'reopened' and i == num_comments - 1:
                comment_type = 'reopen'
            elif i > 0:
                comment_type = str(np.random.choice(['note', 'status_update'], p=[0.4, 0.6]))
            else:
                comment_type = 'note'
            
            # Pick author (favor assigned_to if available)
            if assigned_to and reported_by:
                author = int(np.random.choice([reported_by, assigned_to], p=[0.3, 0.7]))
            elif assigned_to:
                author = int(assigned_to)
            elif reported_by:
                author = int(reported_by)
            else:
                continue  # Skip if no valid author
            
            # Select comment text
            comment_text = str(np.random.choice(comment_templates.get(comment_type, comment_templates['note'])))
            
            # Set old_value and new_value for status changes
            if comment_type == 'resolution':
                old_value = 'in_progress'
                new_value = 'resolved'
            elif comment_type == 'reopen':
                old_value = 'resolved'
                new_value = 'reopened'
            else:
                old_value = None
                new_value = None
            
            comment = {
                "bug_id": int(bug['id']),
                "employee_id": int(author),
                "comment_type": str(comment_type),
                "comment": comment_text,
                "old_value": str(old_value) if old_value else None,
                "new_value": str(new_value) if new_value else None,
                "created_at": current_date.isoformat()
            }
            
            comments.append(comment)
        
        return comments

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
        "--clear-bugs",
        action="store_true",
        help="Clear existing bugs and bug comments"
    )
    parser.add_argument(
        "--clear-all",
        action="store_true",
        help="Clear all operational data before generating"
    )
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
            # Delete in correct order to respect foreign key constraints
            try:
                db.table("bug_comments").delete().neq("id", 0).execute()
            except Exception as e:
                logger.warning(f"Could not clear bug_comments: {e}")
            
            db.table("bugs").delete().neq("id", 0).execute()
            db.table("daily_logs").delete().neq("id", 0).execute()
            db.table("sprints").delete().neq("id", 0).execute()
            db.table("project_assignments").delete().neq("id", 0).execute()
            
            try:
                db.table("anomalies").delete().neq("id", 0).execute()
                db.table("resource_utilization_alerts").delete().neq("id", 0).execute()
                db.table("anomaly_summary").delete().neq("id", 0).execute()
            except Exception as e:
                logger.warning(f"Could not clear analytics tables: {e}")
            
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
        
        if args.clear_bugs:
            print("\n🗑️  Clearing bugs and bug comments...")
            try:
                # Delete comments first (foreign key constraint)
                try:
                    db.table('bug_comments').delete().neq('id', 0).execute()
                    print("✅ Bug comments cleared")
                except Exception as e:
                    logger.warning(f"Could not clear bug_comments table: {e}")
                
                # Then delete bugs
                db.table('bugs').delete().neq('id', 0).execute()
                print("✅ Bugs cleared")
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
        print(f"Bugs created: {results['bugs_created']}")
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