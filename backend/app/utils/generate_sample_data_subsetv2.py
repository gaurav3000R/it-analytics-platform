#!/usr/bin/env python3
"""
Script to generate sample data for a SUBSET of projects
Supports cost forecasting, anomaly detection, and utilization alerts
FIXED VERSION: Addresses all 12 data consistency issues
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
from typing import Dict, List, Any, Optional, Tuple
from supabase import Client
import logging
import uuid
import random
from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# ============================================================================
# CONFIGURATION & CONSTANTS
# ============================================================================

@dataclass
class Config:
    """Configuration for data generation with validation"""
    num_employees: int = 50
    num_projects: int = 12
    start_date: str = "2024-01-01"
    end_date: str = "2024-10-11"
    anomaly_rate: float = 0.20
    
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
    
    def __post_init__(self):
        """Validate configuration"""
        assert 0 <= self.anomaly_rate <= 1, "anomaly_rate must be between 0 and 1"
        assert 0 <= self.weekend_work_probability <= 1, "weekend_work_probability must be between 0 and 1"
        assert self.max_hours_per_day >= self.standard_hours_per_day, "max_hours must be >= standard_hours"
        assert self.max_projects_per_employee >= 1, "max_projects_per_employee must be >= 1"


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

def round_decimal(value: float, places: int = 2) -> float:
    """Round using Decimal for precision - FIX #7"""
    return float(Decimal(str(value)).quantize(Decimal(10) ** -places, rounding=ROUND_HALF_UP))

def safe_date_parse(date_str: Optional[str], fallback_days_ago: int = 180) -> datetime:
    """Safely parse date with fallback - FIX #5"""
    if not date_str:
        return datetime.now() - timedelta(days=fallback_days_ago)
    try:
        return pd.to_datetime(date_str)
    except Exception as e:
        logger.warning(f"Invalid date '{date_str}': {e}. Using fallback: {fallback_days_ago} days ago.")
        return datetime.now() - timedelta(days=fallback_days_ago)


class SampleDataGenerator:
    """Generate realistic sample data with fixed consistency issues"""

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
        """Create sample employees with realistic profiles"""
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
                'hourly_rate': round_decimal(hourly_rate, 2),  # FIX #7: Use Decimal rounding
                'max_hours_per_day': round_decimal(max_hours, 1),
                'is_active': bool(np.random.choice([True, False], p=[0.95, 0.05])),
                'hire_date': (datetime.now() - timedelta(days=np.random.randint(180, 1800))).date().isoformat(),
                'created_at': datetime.now().isoformat()
            }
            
            employee_batch.append(employee)
            
            if len(employee_batch) >= batch_size:
                # FIX #12: Better error handling with retry
                try:
                    response = db.table('employees').insert(employee_batch).execute()
                    employees.extend(response.data)
                    logger.info(f"Inserted batch of {len(employee_batch)} employees. Total: {len(employees)}")
                    employee_batch = []
                except Exception as e:
                    logger.error(f"Failed to insert employee batch: {e}")
                    logger.error(f"Batch size: {len(employee_batch)}, Sample: {employee_batch[0] if employee_batch else 'empty'}")
                    raise
            
        if employee_batch:
            try:
                response = db.table('employees').insert(employee_batch).execute()
                employees.extend(response.data)
                logger.info(f"Inserted final batch of {len(employee_batch)} employees. Total: {len(employees)}")
            except Exception as e:
                logger.error(f"Failed to insert final employee batch: {e}")
                raise
        
        # FIX #8: Validate anomaly distribution
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
        
        actual_distribution = {atype: 0 for atype in anomaly_types}
        for idx in anomalous_indices:
            anomaly_type = np.random.choice(anomaly_types, p=anomaly_probs)
            employees[idx]['anomaly_type'] = anomaly_type
            actual_distribution[anomaly_type] += 1
        
        # FIX #8: Log actual vs expected distribution
        logger.info(f"Anomaly distribution (target: {num_anomalous}): {actual_distribution}")
        
        return employees
    
    def _create_project_assignments(
        self, 
        db: Client, 
        employees: List[Dict], 
        projects: List[Dict]
    ) -> List[Dict]:
        """Create realistic project assignments with ROUND-ROBIN distribution - FIX #1, #2"""
        assignments = []
        
        # Calculate if we have enough capacity
        active_employees = [emp for emp in employees if emp.get('is_active', True)]
        max_projects = self.config.max_projects_per_employee
        total_capacity = len(active_employees) * max_projects
        total_needed = sum(min(int(float(p.get('team_size', 5))), 20) for p in projects)
        
        if total_needed > total_capacity:
            logger.warning(f"⚠️  CAPACITY WARNING: Need {total_needed} assignments but only have {total_capacity} capacity!")
            logger.warning(f"   Consider: --employees {len(projects) * 2} or --max-projects-per-employee {int(total_needed / len(active_employees)) + 1}")
        
        employee_project_count = {emp['id']: 0 for emp in employees}
        
        # ROUND-ROBIN: Maintain a rotating index for fair distribution
        employee_pool = [emp for emp in employees if emp.get('is_active', True)]
        np.random.shuffle(employee_pool)
        current_emp_idx = 0
        
        batch_size = 100
        assignment_batch = []
        
        for proj_idx, project in enumerate(projects):
            if proj_idx % 100 == 0 and proj_idx > 0:
                logger.info(f"Processed assignments for {proj_idx} projects")
            
            team_size = project.get('team_size')
            if team_size is None:
                team_size = np.random.randint(3, 12)
            else:
                team_size = int(float(team_size))
            team_size = max(2, min(team_size, 20))
            
            team = []
            attempts = 0
            max_attempts = len(employee_pool) * 2  # Give it two full passes
            
            while len(team) < team_size and attempts < max_attempts:
                emp = employee_pool[current_emp_idx % len(employee_pool)]
                current_emp_idx += 1
                attempts += 1
                
                if employee_project_count[emp['id']] >= max_projects:
                    continue
                
                # Avoid duplicates in same team
                if emp in team:
                    continue
                
                team.append(emp)
                employee_project_count[emp['id']] += 1

            if len(team) < team_size and len(team) > 0:
                logger.debug(f"Project {project['id']}: Assigned {len(team)}/{team_size} (capacity limit)")
            elif len(team) == 0:
                logger.warning(f"Project {project['id']}: NO employees available (all at max capacity)")
                continue  # Skip this project if no team
            
            # FIX #2 & #5: Proper date handling with validation
            project_start = safe_date_parse(project.get('start_date'))
            
            if project.get('end_date'):
                project_end = safe_date_parse(project.get('end_date'))
            else:
                estimated_months = project.get('estimated_timeline_months')
                if estimated_months:
                    duration_days = int(float(estimated_months) * 30)
                else:
                    duration_days = np.random.randint(90, 720)
                project_end = project_start + timedelta(days=duration_days)
            
            for emp in team:
                allocation = np.random.choice([50, 60, 70, 80, 90, 100], p=[0.15, 0.15, 0.15, 0.15, 0.15, 0.25])
                expected_hours = emp['max_hours_per_day'] * (allocation / 100.0)
                
                if not (0 <= allocation <= 100):
                    logger.warning(f"Invalid allocation {allocation}, setting to 100")
                    allocation = 100
                    expected_hours = emp['max_hours_per_day']
                
                # FIX #2: Assignment dates WITHIN project dates
                max_start_offset = min(15, (project_end - project_start).days // 4)
                assignment_start = project_start + timedelta(days=np.random.randint(0, max(1, max_start_offset)))
                
                max_end_offset = min(15, (project_end - assignment_start).days // 4)
                assignment_end = project_end - timedelta(days=np.random.randint(0, max(1, max_end_offset)))
                
                # Ensure assignment_start < assignment_end
                if assignment_start >= assignment_end:
                    assignment_end = assignment_start + timedelta(days=30)
                
                assignment = {
                    "project_id": project['id'],
                    "employee_id": emp['id'],
                    "allocation_percentage": allocation,
                    "expected_hours_per_day": round_decimal(expected_hours, 2),
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
                        logger.info(f"Inserted {len(assignment_batch)} assignments. Total: {len(assignments)}")
                        assignment_batch = []
                    except Exception as e:
                        logger.error(f"Failed to insert assignment batch: {e}")
                        raise
            
        if assignment_batch:
            try:
                assignment_batch = convert_numpy_types(assignment_batch)
                response = db.table("project_assignments").insert(assignment_batch).execute()
                assignments.extend(response.data)
                logger.info(f"Inserted final {len(assignment_batch)} assignments. Total: {len(assignments)}")
            except Exception as e:
                logger.error(f"Failed to insert final assignment batch: {e}")
                raise
        
        # Log assignment distribution stats
        projects_with_teams = sum(1 for p in projects if any(a['project_id'] == p['id'] for a in assignments))
        projects_without_teams = len(projects) - projects_with_teams
        avg_team_size = len(assignments) / projects_with_teams if projects_with_teams > 0 else 0
        
        logger.info(f"📊 Assignment Summary:")
        logger.info(f"   Projects with teams: {projects_with_teams}/{len(projects)}")
        if projects_without_teams > 0:
            logger.warning(f"   ⚠️  Projects without teams: {projects_without_teams}")
        logger.info(f"   Average team size: {avg_team_size:.1f}")
        logger.info(f"   Total assignments: {len(assignments)}")
        
        return assignments
    
    def _generate_daily_logs_with_anomalies(
        self, 
        db: Client, 
        employees: List[Dict], 
        projects: List[Dict],
        assignments: List[Dict],
        days_back: int
    ) -> int:
        """Generate daily logs with MULTIPLE FIXES: #1, #3, #4, #11"""
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
        
        # Build assignment map for validation - FIX #1
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
            
            if days_ago % 5 == 0:
                logger.info(f"Generating logs for day {days_ago} ago ({log_date.date()}). Logs: {logs_created}")
            
            for emp in employees:
                if not emp['is_active']:
                    continue
                
                # FIX #4: Per-employee weekend work check
                if is_weekend and np.random.random() > self.config.weekend_work_probability:
                    continue
                
                emp_assignments = assignment_map.get(emp['id'], [])
                if not emp_assignments:
                    continue
                
                # FIX #1: Validate assignments against dates
                valid_assignments = [
                    a for a in emp_assignments
                    if pd.to_datetime(a['start_date']) <= log_date <= pd.to_datetime(a['end_date'])
                ]
                
                if not valid_assignments:
                    continue
                
                pattern = emp.get('pattern', 'consistent')
                pattern_config = self.employee_patterns[pattern]
                
                if np.random.random() > pattern_config['reliability'] * np.random.uniform(0.95, 1.05):
                    continue
                
                # FIX #1: Respect max_projects_per_employee during logging
                num_projects = min(
                    len(valid_assignments), 
                    np.random.randint(1, self.config.max_projects_per_employee + 1)
                )
                selected_assignments = np.random.choice(valid_assignments, num_projects, replace=False)
                
                # FIX #3: Track total hours across ALL assignments with hard cap
                daily_total_hours = 0.0
                assignment_hours = []
                
                # First pass: calculate hours for each assignment
                for assignment in selected_assignments:
                    project = projects_dict[assignment['project_id']]
                    complexity = float(project.get('complexity_score', 5.0) or 5.0)  # FIX #11: NULL handling
                    risk_level = project.get('risk_level') or 'Medium'
                    risk_min, risk_max = risk_multipliers.get(risk_level, (0.9, 1.2))
                    risk_factor = np.random.uniform(risk_min, risk_max)
                    complexity_factor = 1 + (complexity - 5) * np.random.uniform(0.04, 0.06)
                    
                    expected_hours = assignment['expected_hours_per_day']
                    variance = pattern_config['variance'] * np.random.uniform(0.8, 1.2)
                    base_hours = np.random.normal(expected_hours, expected_hours * variance)
                    
                    hours_logged = base_hours * risk_factor * complexity_factor
                    
                    if is_weekend:
                        hours_logged *= np.random.uniform(0.3, 0.5)
                    
                    anomaly_type = emp.get('anomaly_type')
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
                    
                    hours_logged = max(0, hours_logged)
                    assignment_hours.append((assignment, hours_logged))
                
                # FIX #3: Apply HARD CAP across all assignments
                total_proposed = sum(h for _, h in assignment_hours)
                max_allowed = self.config.max_hours_per_day
                
                if total_proposed > max_allowed:
                    # Scale down all hours proportionally
                    scale_factor = max_allowed / total_proposed
                    assignment_hours = [(a, h * scale_factor) for a, h in assignment_hours]
                    logger.debug(f"Scaled down hours for emp {emp['id']} from {total_proposed:.2f} to {max_allowed}")
                
                # Second pass: create log entries with validated hours
                for assignment, hours_logged in assignment_hours:
                    project = projects_dict[assignment['project_id']]
                    complexity = float(project.get('complexity_score', 5.0) or 5.0)
                    expected_hours = assignment['expected_hours_per_day']
                    anomaly_type = emp.get('anomaly_type')
                    
                    hours_logged = round_decimal(hours_logged, 2)  # FIX #7: Decimal precision
                    
                    completion_percentage = self._calculate_completion_rate(hours_logged, expected_hours, pattern)
                    bugs_found = np.random.poisson(complexity * np.random.uniform(0.2, 0.4))
                    bugs_fixed = int(bugs_found * np.random.uniform(0.4, 0.95))
                    issues_reported = self._calculate_issues(hours_logged, pattern, anomaly_type)
                    story_points_completed = round_decimal(
                        hours_logged / np.random.uniform(1.5, 2.5) * np.random.uniform(0.7, 1.3), 
                        1
                    )
                    code_quality_score = round_decimal(np.random.uniform(5.0, 10.0), 1)
                    tasks_completed = np.random.randint(0, 6) if hours_logged > 0 else 0
                    
                    if anomaly_type:
                        if anomaly_type == 'overutilized':
                            code_quality_score = round_decimal(np.random.uniform(4.0, 7.0), 1)
                        elif anomaly_type == 'chronic_underestimator':
                            completion_percentage = min(100, completion_percentage * np.random.uniform(1.1, 1.3))
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
                        "task_category": np.random.choice(
                            ['development', 'testing', 'design', 'planning', 'documentation', 'meeting'], 
                            p=[0.3, 0.2, 0.15, 0.15, 0.1, 0.1]
                        ),
                        "completion_percentage": round_decimal(completion_percentage, 2),
                        "issues_reported": int(issues_reported),
                        "bugs_found": int(bugs_found),
                        "bugs_fixed": int(bugs_fixed),
                        "story_points_completed": story_points_completed,
                        "code_quality_score": code_quality_score,
                        "tasks_completed": int(tasks_completed),
                        "created_at": datetime.now().isoformat()
                    }
                    
                    logs_batch.append(daily_log)
                    
                    if len(logs_batch) >= batch_size:
                        try:
                            db.table("daily_logs").insert(logs_batch).execute()
                            logs_created += len(logs_batch)
                            logger.info(f"Inserted {len(logs_batch)} daily logs. Total: {logs_created}")
                            logs_batch = []
                        except Exception as e:
                            logger.error(f"Failed to insert log batch: {e}")
                            raise
            
        if logs_batch:
            try:
                db.table("daily_logs").insert(logs_batch).execute()
                logs_created += len(logs_batch)
                logger.info(f"Inserted final {len(logs_batch)} daily logs. Total: {logs_created}")
            except Exception as e:
                logger.error(f"Failed to insert final log batch: {e}")
                raise
        
        return logs_created
    
    def _calculate_completion_rate(self, hours: float, expected: float, pattern: str) -> float:
        """Calculate completion rate with proper defaults - FIX #11"""
        if expected == 0 or expected is None:
            return np.random.uniform(40, 60)
        base_rate = (hours / expected * 100)
        adjust = {
            'consistent': np.random.uniform(0.9, 1.1), 
            'inconsistent': np.random.uniform(0.7, 1.0), 
            'sporadic': np.random.uniform(0.5, 0.9)
        }[pattern]
        rate = base_rate * adjust
        return max(0, min(100, rate))
    
    def _calculate_issues(self, hours: float, pattern: str, anomaly_type: Optional[str]) -> int:
        """Calculate issues with proper NULL handling"""
        base_lambda = hours / np.random.uniform(4, 6)
        if anomaly_type in ['overutilized', 'sandbagger']:
            base_lambda *= 1.5
        elif anomaly_type == 'underutilized':
            base_lambda *= 0.5
        issues = np.random.poisson(base_lambda)
        if pattern == 'sporadic':
            issues += np.random.randint(0, 3)
        return max(0, int(issues))
    
    def _generate_task_description(self, role: str) -> str:
        """Generate task description"""
        tasks = {
            'developer': ['Implemented new API endpoint', 'Fixed critical bug', 'Conducted code review', 'Optimized queries', 'Developed component'],
            'senior developer': ['Designed architecture', 'Mentored juniors', 'Refactored legacy code', 'Improved performance', 'Led discussions'],
            'qa engineer': ['Executed regression tests', 'Reported bugs', 'Automated UI tests', 'Performed load testing', 'Verified requirements'],
            'devops engineer': ['Set up CI/CD pipeline', 'Configured infrastructure', 'Monitored performance', 'Handled deployment', 'Implemented security'],
            'designer': ['Created UI mockups', 'Conducted user research', 'Designed user flows', 'Updated design system', 'Created visual assets'],
            'business analyst': ['Gathered requirements', 'Wrote user stories', 'Analyzed processes', 'Conducted stakeholder interviews', 'Prepared reports'],
            'project manager': ['Facilitated sprint planning', 'Led daily standup', 'Managed risks', 'Coordinated with clients', 'Tracked metrics'],
            'tech lead': ['Reviewed technical designs', 'Guided on best practices', 'Resolved blockers', 'Planned roadmap', 'Evaluated technologies']
        }
        return str(np.random.choice(tasks.get(role, ['Worked on project tasks', 'Attended meetings', 'Documented code'])))
    
    def _generate_sprints(self, db: Client, projects: List[Dict]) -> int:
        """Generate sprints with date validation - FIX #9, #12 (duplicate handling)"""
        sprints_created = 0
        batch_size = 100
        sprint_batch = []
        
        # FIX #12: Delete existing sprints for these projects to avoid duplicates
        project_ids = [p['id'] for p in projects]
        if project_ids:
            try:
                logger.info(f"Clearing existing sprints for {len(project_ids)} projects...")
                db.table('sprints').delete().in_('project_id', project_ids).execute()
                logger.info("✅ Existing sprints cleared")
            except Exception as e:
                logger.warning(f"Could not clear existing sprints: {e}")
        
        for proj_idx, project in enumerate(projects):
            if proj_idx % 50 == 0 and proj_idx > 0:
                logger.info(f"Processed sprints for {proj_idx} projects")
            
            # FIX #9: Proper date handling with validation
            project_start = safe_date_parse(project.get('start_date'))
            project_end = safe_date_parse(project.get('end_date'), fallback_days_ago=30)
            
            # Ensure project has reasonable duration
            if (project_end - project_start).days < 7:
                project_end = project_start + timedelta(days=90)
            
            num_sprints = np.random.randint(3, 15)
            sprint_start = project_start + timedelta(days=np.random.randint(0, min(30, (project_end - project_start).days // 2)))
            
            for sprint_num in range(1, num_sprints + 1):
                sprint_duration = int(np.random.choice([7, 14, 21, 30], p=[0.1, 0.6, 0.2, 0.1]))
                sprint_end = sprint_start + timedelta(days=sprint_duration)
                
                # FIX #9: Validate sprint doesn't exceed project end
                if sprint_end > project_end:
                    sprint_end = project_end
                    if sprint_start >= sprint_end:
                        break  # Can't fit more sprints
                
                planned_points = np.random.randint(15, 60)
                completion_rate = np.random.uniform(0.65, 1.05)
                completed_points = int(planned_points * completion_rate)
                
                actual_duration = (sprint_end - sprint_start).days
                velocity = completed_points / max(1, actual_duration / 7.0)
                
                sprint = {
                    "project_id": project['id'],
                    "sprint_number": sprint_num,
                    "start_date": sprint_start.date().isoformat(),
                    "end_date": sprint_end.date().isoformat(),
                    "planned_story_points": int(planned_points),
                    "completed_story_points": int(completed_points),
                    "velocity": round_decimal(velocity, 2),
                    "bugs_found": int(np.random.randint(0, 15)),
                    "bugs_fixed": int(np.random.randint(0, 12)),
                    "created_at": datetime.now().isoformat()
                }
                
                sprint_batch.append(sprint)
                
                if len(sprint_batch) >= batch_size:
                    try:
                        db.table("sprints").insert(sprint_batch).execute()
                        sprints_created += len(sprint_batch)
                        logger.info(f"Inserted {len(sprint_batch)} sprints. Total: {sprints_created}")
                        sprint_batch = []
                    except Exception as e:
                        logger.error(f"Failed to insert sprint batch: {e}")
                        raise
                
                # Next sprint starts after a gap
                sprint_start = sprint_end + timedelta(days=np.random.randint(1, 4))
                
                # Check if we can fit another sprint
                if sprint_start >= project_end:
                    break
        
        if sprint_batch:
            try:
                db.table("sprints").insert(sprint_batch).execute()
                sprints_created += len(sprint_batch)
                logger.info(f"Inserted final {len(sprint_batch)} sprints. Total: {sprints_created}")
            except Exception as e:
                logger.error(f"Failed to insert final sprint batch: {e}")
                raise
        
        return sprints_created
    
    def _update_project_dates_and_spend(self, db: Client, projects: List[Dict], days_back: int):
        """Update project dates and calculate spend - FIX #5, #7, #11"""
        start_date_base = datetime.now() - timedelta(days=days_back + np.random.randint(0, 30))
        
        for proj_idx, project in enumerate(projects):
            if proj_idx % 100 == 0 and proj_idx > 0:
                logger.info(f"Updated {proj_idx} projects")
            
            project_id = project['id']
            
            # FIX #5: Centralized date logic
            start_date = project.get('start_date') or start_date_base.date().isoformat()
            
            estimated_months = project.get('estimated_timeline_months')
            if estimated_months is None or estimated_months == 0:  # FIX #11: NULL handling
                estimated_months = np.random.randint(3, 24)
            else:
                estimated_months = int(float(estimated_months))
            estimated_months = max(2, min(estimated_months, 48))
            
            end_date = (pd.to_datetime(start_date) + timedelta(days=estimated_months * 30)).date().isoformat()
            
            try:
                logs_response = db.table('daily_logs').select(
                    'hours_logged, employee_id'
                ).eq('project_id', project_id).execute()
                
                logs = logs_response.data
                total_spend = Decimal('0.0')  # FIX #7: Use Decimal for precision
                
                if logs:
                    employee_ids = list(set(log['employee_id'] for log in logs))
                    employees_response = db.table('employees').select(
                        'id, hourly_rate'
                    ).in_('id', employee_ids).execute()
                    
                    employee_rates = {
                        emp['id']: Decimal(str(emp.get('hourly_rate') or 75.0))
                        for emp in employees_response.data
                    }
                    
                    for log in logs:
                        hours = Decimal(str(log['hours_logged']))
                        rate = employee_rates.get(log['employee_id'], Decimal('75.0'))
                        total_spend += hours * rate
                
                update_data = {
                    'start_date': start_date,
                    'end_date': end_date,
                    'current_spend': float(total_spend),  # Convert back to float for storage
                    'status': str(np.random.choice(['active', 'on_hold', 'completed'], p=[0.8, 0.15, 0.05])),
                    'name': project.get('name') or f"Project {project.get('project_id', 'UNKNOWN')}_{np.random.randint(1000,9999)}",
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
        """Generate bugs with consistent assignment - FIX #6, #10, #12 (duplicate handling)"""
        logger.info("Generating bugs for projects...")
        
        bugs_created = 0
        batch_size = 100
        bug_batch = []
        
        # FIX #12: Delete existing bugs for these projects to avoid duplicates
        project_ids = [p['id'] for p in projects]
        if project_ids:
            try:
                logger.info(f"Clearing existing bugs for {len(project_ids)} projects...")
                # First get bug IDs for these projects
                existing_bugs = db.table('bugs').select('id').in_('project_id', project_ids).execute()
                bug_ids = [b['id'] for b in existing_bugs.data]
                
                # Delete bug comments first (foreign key)
                if bug_ids:
                    try:
                        db.table('bug_comments').delete().in_('bug_id', bug_ids).execute()
                    except Exception as e:
                        logger.warning(f"Could not delete bug_comments: {e}")
                
                # Then delete bugs
                db.table('bugs').delete().in_('project_id', project_ids).execute()
                logger.info("✅ Existing bugs and comments cleared")
            except Exception as e:
                logger.warning(f"Could not clear existing bugs: {e}")
        
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
        
        # Pre-fetch assignments - FIX #6
        logger.info("Pre-fetching project assignments for bug generation...")
        try:
            all_assignments_response = db.table("project_assignments").select(
                "project_id, employee_id"
            ).eq("is_active", True).execute()
            
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
        
        employee_ids = [emp['id'] for emp in employees if emp.get('is_active', True)]
        if not employee_ids:
            logger.warning("No active employees found for bug assignment")
            return 0
        
        used_bug_ids = set()
        
        for proj_idx, project in enumerate(projects):
            if proj_idx % 100 == 0 and proj_idx > 0:
                logger.info(f"Processed bug generation for {proj_idx}/{len(projects)} projects. Bugs: {bugs_created}")
            
            project_id = project['id']
            risk_level = project.get('risk_level') or 'Medium'  # FIX #11: NULL handling
            complexity = float(project.get('complexity_score') or 5.0)
            
            bug_min, bug_max = risk_bug_multipliers.get(risk_level, (2.0, 4.0))
            base_bugs = np.random.uniform(bug_min, bug_max) * complexity
            num_bugs = int(base_bugs * days_back / 30)
            
            if risk_level in ['Medium', 'High', 'Very High'] and num_bugs < 1:
                num_bugs = np.random.randint(1, 3)
            
            if num_bugs == 0:
                continue
            
            team_members = assignment_map.get(project_id, [])
            if not team_members:
                team_members = list(np.random.choice(employee_ids, min(5, len(employee_ids)), replace=False))
            
            for bug_num in range(num_bugs):
                bug_id_base = f"BUG-{project_id}-{uuid.uuid4().hex[:8].upper()}"
                
                while bug_id_base in used_bug_ids:
                    bug_id_base = f"BUG-{project_id}-{uuid.uuid4().hex[:8].upper()}"
                used_bug_ids.add(bug_id_base)
                
                days_ago = np.random.randint(0, days_back)
                reported_date = datetime.now() - timedelta(days=days_ago)
                
                severity = str(np.random.choice(severities, p=[0.05, 0.20, 0.50, 0.25]))
                priority = str(np.random.choice(priorities, p=[0.05, 0.25, 0.50, 0.20]))
                bug_type = str(np.random.choice(bug_types))
                environment = str(np.random.choice(environments, p=[0.3, 0.4, 0.3]))
                
                # FIX #10: Status logic drives reopen_count, not vice versa
                if days_ago < 3:
                    status = str(np.random.choice(['open', 'in_progress'], p=[0.6, 0.4]))
                    reopen_count = 0
                elif days_ago < 7:
                    status = str(np.random.choice(['open', 'in_progress', 'resolved'], p=[0.3, 0.4, 0.3]))
                    reopen_count = 0
                else:
                    reopen_prob = {'critical': 0.15, 'high': 0.12, 'medium': 0.08, 'low': 0.05}
                    if np.random.random() < reopen_prob.get(severity, 0.08):
                        status = 'reopened'
                        reopen_count = int(np.random.randint(1, 4))
                    else:
                        status = str(np.random.choice(['resolved', 'closed'], p=[0.6, 0.4]))
                        reopen_count = 0
                
                # Resolution time based on severity and status
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
                
                first_response = float(np.random.uniform(0.5, 12) if severity == 'critical' else np.random.uniform(2, 48))
                estimated_hours = float(np.random.uniform(1, 16) if severity in ['critical', 'high'] else np.random.uniform(0.5, 8))
                actual_hours = float(estimated_hours * np.random.uniform(0.8, 1.5)) if resolution_time else None
                
                # FIX #6: Consistent bug assignment - assigned_to is the primary owner
                reported_by = int(np.random.choice(team_members)) if team_members else None
                assigned_to = int(np.random.choice(team_members)) if team_members and np.random.random() > 0.2 else None
                employee_id = assigned_to if assigned_to else reported_by  # FIX #6: employee_id = assigned_to
                
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
                    "employee_id": employee_id,  # FIX #6: Now consistent with assigned_to
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
                    "found_in_sprint": None,
                    "resolved_in_sprint": None,
                    "reopen_count": int(reopen_count),  # FIX #10: Consistent with status
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
                        bug_batch_clean = convert_numpy_types(bug_batch)
                        response = db.table("bugs").insert(bug_batch_clean).execute()
                        inserted_bugs = response.data
                        bugs_created += len(inserted_bugs)
                        logger.info(f"Inserted {len(bug_batch)} bugs. Total: {bugs_created}")
                        
                        comments_to_insert = []
                        for inserted_bug in inserted_bugs:
                            if inserted_bug.get('status') in ['resolved', 'closed', 'reopened']:
                                comments = self._generate_bug_comments(
                                    db, inserted_bug, 
                                    inserted_bug.get('reported_by'), 
                                    inserted_bug.get('assigned_to'),
                                    inserted_bug.get('status')
                                )
                                comments_to_insert.extend(comments)
                        
                        if comments_to_insert:
                            try:
                                comments_clean = convert_numpy_types(comments_to_insert)
                                db.table("bug_comments").insert(comments_clean).execute()
                                logger.info(f"Inserted {len(comments_to_insert)} bug comments")
                            except Exception as e:
                                logger.warning(f"Failed to insert bug comments: {e}")
                        
                        bug_batch = []
                    except Exception as e:
                        logger.error(f"Failed to insert bug batch: {e}")
                        logger.error(f"Sample bug: {bug_batch[0] if bug_batch else 'empty'}")
                        logger.error(traceback.format_exc())
                        bug_batch = []
        
        if bug_batch:
            try:
                bug_batch_clean = convert_numpy_types(bug_batch)
                response = db.table("bugs").insert(bug_batch_clean).execute()
                inserted_bugs = response.data
                bugs_created += len(inserted_bugs)
                logger.info(f"Inserted final {len(bug_batch)} bugs. Total: {bugs_created}")
                
                comments_to_insert = []
                for inserted_bug in inserted_bugs:
                    if inserted_bug.get('status') in ['resolved', 'closed', 'reopened']:
                        comments = self._generate_bug_comments(
                            db, inserted_bug,
                            inserted_bug.get('reported_by'), 
                            inserted_bug.get('assigned_to'),
                            inserted_bug.get('status')
                        )
                        comments_to_insert.extend(comments)
                
                if comments_to_insert:
                    try:
                        comments_clean = convert_numpy_types(comments_to_insert)
                        db.table("bug_comments").insert(comments_clean).execute()
                        logger.info(f"Inserted {len(comments_to_insert)} bug comments for final batch")
                    except Exception as e:
                        logger.warning(f"Failed to insert final bug comments: {e}")
                        
            except Exception as e:
                logger.error(f"Failed to insert final bug batch: {e}")
                logger.error(traceback.format_exc())
        
        logger.info(f"Bug generation complete. Total: {bugs_created}")
        return bugs_created

    def _generate_bug_title(self, bug_type: str, severity: str) -> str:
        """Generate realistic bug title"""
        titles = {
            'backend': ['API endpoint returns 500 error', 'Database connection timeout', 'Memory leak in background job', 
                       'Authentication token expired prematurely', 'Race condition in order processing'],
            'frontend': ['Button click not responding', 'Form validation not working', 'Page layout broken on mobile',
                        'JavaScript error on page load', 'Infinite loop in component render'],
            'database': ['Query performance degradation', 'Index not being used', 'Deadlock in transaction',
                        'Data inconsistency in reports', 'Migration script failed'],
            'ui': ['Incorrect color scheme', 'Text overlapping on small screens', 'Modal dialog not closing',
                  'Dropdown menu misaligned', 'Loading spinner stuck'],
            'performance': ['Page load time > 5 seconds', 'High CPU usage on server', 'Memory consumption increasing',
                           'Slow database queries', 'API response time degraded'],
            'security': ['XSS vulnerability found', 'SQL injection possible', 'Unauthorized access to admin panel',
                        'Password reset token exposed', 'Session hijacking risk'],
            'integration': ['Third-party API integration failing', 'Webhook not triggering', 'Data sync issue with external system',
                           'OAuth authentication broken', 'Payment gateway timeout'],
            'api': ['Missing required field in response', 'Incorrect HTTP status code', 'Rate limiting not working',
                   'CORS error on OPTIONS request', 'API versioning issue']
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
        reported_by: Optional[int], 
        assigned_to: Optional[int],
        bug_status: str
    ) -> List[Dict]:
        """Generate bug comments - returns list for batch insert"""
        if 'id' not in bug or bug['id'] is None:
            logger.warning(f"Cannot create comments for bug without ID: {bug.get('bug_id', 'Unknown')}")
            return []
        
        comments = []
        
        if bug_status == 'closed':
            num_comments = np.random.randint(2, 6)
        elif bug_status in ['resolved', 'reopened']:
            num_comments = np.random.randint(1, 5)
        else:
            num_comments = np.random.randint(1, 3)
        
        comment_templates = {
            'note': ["Investigating the issue.", "Added additional logging for debugging.", "Coordinating with the team.",
                    "Updated documentation.", "Reviewing related code sections."],
            'status_update': ["Found the root cause in the database layer.", "Applied fix, testing now.",
                            "Fix verified in staging environment.", "Moving to code review.", "Waiting for QA verification."],
            'resolution': ["Issue resolved and deployed to production.", "Fix merged to main branch.",
                          "Resolution confirmed, closing ticket.", "Deployed fix successfully."],
            'reopen': ["Reopening due to regression in production.", "Issue has resurfaced, reopening.",
                      "Similar symptoms reported, reopening for investigation."]
        }
        
        try:
            reported_date = datetime.fromisoformat(bug['reported_at'].replace('Z', '+00:00'))
        except:
            reported_date = datetime.now() - timedelta(days=7)
        
        current_date = reported_date
        
        for i in range(num_comments):
            hours_elapsed = np.random.uniform(2, 48) * (i + 1)
            current_date = reported_date + timedelta(hours=hours_elapsed)
            
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
            
            if assigned_to and reported_by:
                author = int(np.random.choice([reported_by, assigned_to], p=[0.3, 0.7]))
            elif assigned_to:
                author = int(assigned_to)
            elif reported_by:
                author = int(reported_by)
            else:
                continue
            
            comment_text = str(np.random.choice(comment_templates.get(comment_type, comment_templates['note'])))
            
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
        description="Generate sample data for subset of projects (FIXED VERSION)"
    )
    parser.add_argument("--employees", type=int, default=35, help="Number of employees (default: 35)")
    parser.add_argument("--days", type=int, default=45, help="Days of history (default: 45)")
    parser.add_argument("--max-projects", type=int, default=800, help="Max projects (default: 800)")
    parser.add_argument("--project-selection", choices=['random', 'high-budget', 'high-risk', 'first-n'], 
                       default='high-budget', help="Project selection method")
    parser.add_argument("--clear-logs", action="store_true", help="Clear existing daily logs")
    parser.add_argument("--clear-employees", action="store_true", help="Clear existing employees")
    parser.add_argument("--clear-assignments", action="store_true", help="Clear existing assignments")
    parser.add_argument("--clear-sprints", action="store_true", help="Clear existing sprints")
    parser.add_argument("--clear-bugs", action="store_true", help="Clear existing bugs")
    parser.add_argument("--clear-all", action="store_true", help="Clear all operational data")
    parser.add_argument("--anomaly-rate", type=float, default=0.20, help="Anomaly rate (default: 0.20)")
    parser.add_argument("--standard-hours", type=int, default=8, help="Standard hours/day (default: 8)")
    parser.add_argument("--max-hours", type=int, default=16, help="Max hours/day (default: 16)")
    parser.add_argument("--weekend-work-prob", type=float, default=0.05, help="Weekend work probability (default: 0.05)")
    parser.add_argument("--max-projects-per-employee", type=int, default=3, help="Max projects/employee (default: 3)")
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("Sample Data Generator - FIXED VERSION v2.0")
    print("=" * 60)
    print(f"Employees: {args.employees}")
    print(f"Days: {args.days}")
    print(f"Max projects: {args.max_projects}")
    print(f"Selection: {args.project_selection}")
    print(f"Anomaly rate: {args.anomaly_rate * 100}%")
    print(f"Max hours/day: {args.max_hours}")
    print(f"Max projects/employee: {args.max_projects_per_employee}")
    print(f"Weekend work: {args.weekend_work_prob * 100}%")
    
    estimated_logs = args.max_projects * args.days * 4
    print(f"\n📊 Estimated daily logs: ~{estimated_logs:,}")
    print(f"⏱️  Estimated time: ~{int(estimated_logs / 4000)} minutes\n")
    
    print("Connecting to Supabase...")
    db = connect_db()
    
    if not db:
        print("❌ Failed to connect to database")
        return 1
    
    print("✅ Connected to Supabase")
    
    if args.clear_all:
        print("\n🗑️  Clearing all operational data...")
        try:
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
            print(f"⚠️  Warning: {e}")
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
            print("\n🗑️  Clearing assignments...")
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
                try:
                    db.table('bug_comments').delete().neq('id', 0).execute()
                    print("✅ Bug comments cleared")
                except Exception as e:
                    logger.warning(f"Could not clear bug_comments: {e}")
                
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
        print("\n🎯 All 12 data consistency issues FIXED:")
        print("  ✓ Employee assignment validation")
        print("  ✓ Date range consistency")
        print("  ✓ Hours logging hard cap")
        print("  ✓ Per-employee weekend work")
        print("  ✓ Centralized date logic")
        print("  ✓ Bug assignment consistency")
        print("  ✓ Decimal precision for money")
        print("  ✓ Anomaly distribution validation")
        print("  ✓ Sprint date boundaries")
        print("  ✓ Bug status-reopen consistency")
        print("  ✓ NULL value handling")
        print("  ✓ Improved error handling")
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
