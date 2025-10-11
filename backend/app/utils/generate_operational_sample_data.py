# backend/app/utils/generate_operational_sample_data.py

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Any
from supabase import Client
import logging

logger = logging.getLogger(__name__)

class OperationalSampleDataGenerator:
    """Generate realistic sample data for anomaly detection and resource utilization"""
    
    def __init__(self):
        self.employee_patterns = {
            'consistent': {'reliability': 0.95, 'variance': 0.1},
            'inconsistent': {'reliability': 0.7, 'variance': 0.3},
            'sporadic': {'reliability': 0.5, 'variance': 0.5}
        }
        
    def generate_complete_operational_data(
        self, 
        db: Client, 
        num_employees: int = 50,
        days_back: int = 90
    ):
        """Generate complete operational data including employees, assignments, and logs"""
        logger.info(f"Generating operational data: {num_employees} employees, {days_back} days")
        
        # Step 1: Get existing projects (4000 projects from CSV)
        projects_response = db.table("projects").select("id, project_id, name, team_size, start_date, end_date").execute()
        projects = projects_response.data
        
        if not projects:
            raise ValueError("No projects found. Please load project data first.")
        
        logger.info(f"Found {len(projects)} existing projects")
        
        # Step 2: Clear existing operational data
        self._clear_operational_data(db)
        
        # Step 3: Create employees with different patterns
        employees = self._create_employees(db, num_employees)
        logger.info(f"Created {len(employees)} employees")
        
        # Step 4: Create project assignments
        assignments = self._create_project_assignments(db, employees, projects)
        logger.info(f"Created {len(assignments)} project assignments")
        
        # Step 5: Generate daily logs with anomalies
        logs_created = self._generate_daily_logs_with_anomalies(
            db, employees, projects, assignments, days_back
        )
        logger.info(f"Created {logs_created} daily logs")
        
        # Step 6: Generate sprints for selected projects
        sprints_created = self._generate_sprints(db, projects[:100])  # First 100 projects
        logger.info(f"Created {sprints_created} sprints")
        
        return {
            "employees_created": len(employees),
            "assignments_created": len(assignments),
            "logs_created": logs_created,
            "sprints_created": sprints_created,
            "projects_used": len(projects)
        }
    
    def _clear_operational_data(self, db: Client):
        """Clear existing operational data"""
        try:
            db.table("daily_logs").delete().neq("id", 0).execute()
            db.table("sprints").delete().neq("id", 0).execute()
            db.table("project_assignments").delete().neq("id", 0).execute()
            db.table("anomalies").delete().neq("id", 0).execute()
            db.table("resource_utilization_alerts").delete().neq("id", 0).execute()
            db.table("anomaly_summary").delete().neq("id", 0).execute()
            db.table("employees").delete().neq("id", 0).execute()
            logger.info("Cleared existing operational data")
        except Exception as e:
            logger.warning(f"Error clearing data: {e}")
    
    def _create_employees(self, db: Client, num_employees: int) -> List[Dict]:
        """Create employees with different behavioral patterns"""
        roles = ['developer', 'developer', 'developer', 'tester', 'designer', 'devops', 'manager']
        skill_levels = ['junior', 'mid', 'senior']
        patterns = ['consistent', 'consistent', 'consistent', 'inconsistent', 'sporadic']
        
        employees = []
        
        for i in range(num_employees):
            role = np.random.choice(roles)
            skill_level = np.random.choice(skill_levels, p=[0.3, 0.5, 0.2])
            pattern = np.random.choice(patterns, p=[0.6, 0.25, 0.15])
            
            # Calculate hourly rate
            base_rates = {'junior': 50, 'mid': 85, 'senior': 130}
            role_multipliers = {'manager': 1.4, 'devops': 1.2, 'designer': 1.1, 'developer': 1.0, 'tester': 0.95}
            hourly_rate = base_rates[skill_level] * role_multipliers.get(role, 1.0) * np.random.uniform(0.9, 1.1)
            
            # Determine max hours based on role
            if role == 'manager':
                max_hours = np.random.uniform(6, 8)
            elif skill_level == 'senior':
                max_hours = np.random.uniform(7, 9)
            else:
                max_hours = 8.0
            
            employee = {
                "name": f"Employee_{i+1:03d}",
                "email": f"employee{i+1:03d}@company.com",
                "role": role,
                "skill_level": skill_level,
                "hourly_rate": round(hourly_rate, 2),
                "max_hours_per_day": round(max_hours, 1),
                "hire_date": (datetime.now() - timedelta(days=np.random.randint(180, 1800))).date().isoformat(),
                "is_active": True,
                "created_at": datetime.now().isoformat()
            }
            
            response = db.table("employees").insert(employee).execute()
            employee_record = response.data[0]
            employee_record['pattern'] = pattern  # Store pattern for later use
            employees.append(employee_record)
        
        return employees
    
    def _create_project_assignments(
        self, 
        db: Client, 
        employees: List[Dict], 
        projects: List[Dict]
    ) -> List[Dict]:
        """Create realistic project assignments"""
        assignments = []
        
        # Sample 500 active projects for assignments
        active_projects = np.random.choice(projects, min(500, len(projects)), replace=False)
        
        for project in active_projects:
            # Determine team size (use project's team_size or default)
            team_size = int(project.get('team_size', np.random.randint(3, 10)))
            
            # Select employees for this project
            assigned_employees = np.random.choice(employees, min(team_size, len(employees)), replace=False)
            
            project_start = pd.to_datetime(project.get('start_date', datetime.now() - timedelta(days=60)))
            project_end = pd.to_datetime(project.get('end_date', datetime.now() + timedelta(days=90)))
            
            for emp in assigned_employees:
                # Determine allocation percentage
                # Some employees are on multiple projects (50-100%), others full-time (100%)
                if np.random.random() < 0.3:  # 30% are on multiple projects
                    allocation = np.random.choice([50, 60, 70, 80])
                else:
                    allocation = 100
                
                expected_hours = emp['max_hours_per_day'] * (allocation / 100.0)
                
                assignment = {
                    "project_id": project['id'],
                    "employee_id": emp['id'],
                    "allocation_percentage": allocation,
                    "expected_hours_per_day": round(expected_hours, 2),
                    "start_date": project_start.date().isoformat(),
                    "end_date": project_end.date().isoformat(),
                    "is_active": True,
                    "created_at": datetime.now().isoformat()
                }
                
                response = db.table("project_assignments").insert(assignment).execute()
                assignments.append(response.data[0])
        
        return assignments
    
    def _generate_daily_logs_with_anomalies(
        self, 
        db: Client, 
        employees: List[Dict], 
        projects: List[Dict],
        assignments: List[Dict],
        days_back: int
    ) -> int:
        """Generate daily logs with intentional anomalies for testing"""
        logs_created = 0
        
        # Create assignment lookup
        assignment_map = {}
        for assignment in assignments:
            emp_id = assignment['employee_id']
            if emp_id not in assignment_map:
                assignment_map[emp_id] = []
            assignment_map[emp_id].append(assignment)
        
        # Generate logs for each day
        for days_ago in range(days_back):
            log_date = datetime.now() - timedelta(days=days_ago)
            
            # Skip weekends with 80% probability
            if log_date.weekday() >= 5 and np.random.random() < 0.8:
                continue
            
            # Create logs for employees who have assignments
            for emp in employees:
                emp_assignments = assignment_map.get(emp['id'], [])
                if not emp_assignments:
                    continue
                
                # Get employee pattern
                pattern = emp.get('pattern', 'consistent')
                pattern_config = self.employee_patterns[pattern]
                
                # Determine if employee logs today
                if np.random.random() > pattern_config['reliability']:
                    # ANOMALY: Missing log (intentional)
                    continue
                
                # Determine how many projects to log for
                num_projects = min(len(emp_assignments), np.random.randint(1, 3))
                selected_assignments = np.random.choice(emp_assignments, num_projects, replace=False)
                
                for assignment in selected_assignments:
                    # Calculate expected hours
                    expected_hours = assignment['expected_hours_per_day']
                    
                    # Generate hours with pattern-based variance
                    variance = pattern_config['variance']
                    hours_logged = np.random.normal(expected_hours, expected_hours * variance)
                    
                    # Introduce specific anomalies
                    anomaly_type = self._introduce_anomaly(emp, log_date, days_ago)
                    
                    if anomaly_type == 'sudden_drop':
                        hours_logged *= 0.3  # ANOMALY: Sudden drop in hours
                    elif anomaly_type == 'overwork':
                        hours_logged *= 1.8  # ANOMALY: Overworking
                    elif anomaly_type == 'zero_hours':
                        hours_logged = 0  # ANOMALY: Zero hours logged
                    
                    # Ensure realistic bounds
                    hours_logged = max(0, min(14, hours_logged))
                    
                    # Calculate related metrics
                    completion_rate = self._calculate_completion_rate(hours_logged, expected_hours, pattern)
                    issues_reported = self._calculate_issues(hours_logged, pattern, anomaly_type)
                    
                    # Create daily log
                    daily_log = {
                        "project_id": assignment['project_id'],
                        "employee_id": emp['id'],
                        "date": log_date.date().isoformat(),
                        "hours_logged": round(hours_logged, 2),
                        "task_description": self._generate_task_description(emp['role']),
                        "task_category": np.random.choice(['development', 'testing', 'design', 'planning', 'documentation']),
                        "completion_percentage": round(completion_rate, 2),
                        "issues_reported": issues_reported,
                        "bugs_found": issues_reported if emp['role'] == 'tester' else max(0, issues_reported - 1),
                        "bugs_fixed": max(0, issues_reported - np.random.randint(0, 2)),
                        "story_points_completed": round(hours_logged / 2.0 * np.random.uniform(0.8, 1.2), 1),
                        "created_at": datetime.now().isoformat()
                    }
                    
                    try:
                        db.table("daily_logs").insert(daily_log).execute()
                        logs_created += 1
                    except Exception as e:
                        logger.warning(f"Failed to insert log: {e}")
                        continue
            
            # Log progress
            if days_ago % 15 == 0:
                logger.info(f"Generated logs for {days_ago} days ago... ({logs_created} logs created)")
        
        return logs_created
    
    def _introduce_anomaly(self, emp: Dict, log_date: datetime, days_ago: int) -> str:
        """Introduce specific anomalies based on employee and date"""
        # More anomalies for 'sporadic' pattern employees
        pattern = emp.get('pattern', 'consistent')
        
        if pattern == 'sporadic':
            anomaly_prob = 0.3
        elif pattern == 'inconsistent':
            anomaly_prob = 0.15
        else:
            anomaly_prob = 0.05
        
        if np.random.random() < anomaly_prob:
            return np.random.choice(['sudden_drop', 'overwork', 'zero_hours'], p=[0.5, 0.3, 0.2])
        
        return 'normal'
    
    def _calculate_completion_rate(self, hours: float, expected: float, pattern: str) -> float:
        """Calculate realistic completion rate"""
        base_rate = (hours / expected * 50) if expected > 0 else 50
        
        if pattern == 'consistent':
            rate = base_rate * np.random.uniform(0.9, 1.1)
        elif pattern == 'inconsistent':
            rate = base_rate * np.random.uniform(0.7, 1.0)
        else:
            rate = base_rate * np.random.uniform(0.5, 0.9)
        
        return max(5, min(100, rate))
    
    def _calculate_issues(self, hours: float, pattern: str, anomaly_type: str) -> int:
        """Calculate issues reported"""
        if anomaly_type == 'overwork':
            # Overworking leads to more issues
            base_issues = np.random.poisson(hours / 3)
        else:
            base_issues = np.random.poisson(hours / 5)
        
        if pattern == 'sporadic':
            base_issues += np.random.randint(0, 2)
        
        return max(0, base_issues)
    
    def _generate_task_description(self, role: str) -> str:
        """Generate realistic task descriptions"""
        tasks = {
            'developer': ['Feature implementation', 'Bug fixing', 'Code review', 'API development', 'Database optimization'],
            'tester': ['Test case execution', 'Bug reporting', 'Regression testing', 'Test automation', 'UAT support'],
            'designer': ['UI design', 'UX research', 'Mockup creation', 'Design review', 'Asset creation'],
            'devops': ['CI/CD pipeline', 'Infrastructure setup', 'Monitoring', 'Deployment', 'Security audit'],
            'manager': ['Sprint planning', 'Team standup', 'Client meeting', 'Resource planning', 'Risk assessment']
        }
        return np.random.choice(tasks.get(role, ['General project work']))
    
    def _generate_sprints(self, db: Client, projects: List[Dict]) -> int:
        """Generate sprint data for projects"""
        sprints_created = 0
        
        for project in projects:
            # Determine number of sprints (based on project duration)
            num_sprints = np.random.randint(4, 12)
            
            sprint_start = datetime.now() - timedelta(days=90)
            
            for sprint_num in range(1, num_sprints + 1):
                sprint_duration = 14  # 2 weeks
                sprint_end = sprint_start + timedelta(days=sprint_duration)
                
                planned_points = np.random.randint(20, 50)
                completion_rate = np.random.uniform(0.7, 1.0)
                completed_points = int(planned_points * completion_rate)
                velocity = completed_points / 2  # Per week
                
                sprint = {
                    "project_id": project['id'],
                    "sprint_number": sprint_num,
                    "start_date": sprint_start.date().isoformat(),
                    "end_date": sprint_end.date().isoformat(),
                    "planned_story_points": planned_points,
                    "completed_story_points": completed_points,
                    "velocity": round(velocity, 2),
                    "bugs_found": np.random.randint(0, 10),
                    "bugs_fixed": np.random.randint(0, 8),
                    "created_at": datetime.now().isoformat()
                }
                
                try:
                    db.table("sprints").insert(sprint).execute()
                    sprints_created += 1
                except Exception as e:
                    logger.warning(f"Failed to insert sprint: {e}")
                
                sprint_start = sprint_end + timedelta(days=2)
        
        return sprints_created


def generate_operational_sample_data(
    db: Client,
    num_employees: int = 50,
    days_back: int = 90
) -> Dict[str, Any]:
    """Convenience function to generate sample data"""
    generator = OperationalSampleDataGenerator()
    return generator.generate_complete_operational_data(db, num_employees, days_back)