"""
Sample Data Generator for Cost Forecasting
Generates realistic daily logs and employee data for existing projects
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List
from supabase import Client
import logging
import uuid

logger = logging.getLogger(__name__)

class CostSampleDataGenerator:
    
    def __init__(self, db: Client):
        self.db = db
        
    def generate_sample_data_for_projects(self, num_employees: int = 50, days_back: int = 90):
        """
        Generate sample employees and daily logs for existing projects
        
        Args:
            num_employees: Number of sample employees to create
            days_back: Number of days of historical data to generate
        """
        logger.info(f"Generating sample data: {num_employees} employees, {days_back} days of logs")
        
        # Step 1: Create sample employees
        employees = self._create_sample_employees(num_employees)
        logger.info(f"✅ Created {len(employees)} employees")
        
        # Step 2: Get existing projects
        projects = self._get_existing_projects()
        logger.info(f"📊 Found {len(projects)} projects")
        
        if not projects:
            logger.error("No projects found. Please load project data first.")
            return
        
        # Step 3: Generate daily logs for projects
        self._generate_daily_logs(projects, employees, days_back)
        logger.info(f"✅ Generated daily logs for {days_back} days")
        
        # Step 4: Update project dates and current spend
        self._update_project_dates_and_spend(projects, days_back)
        logger.info("✅ Updated project dates and spending")
        
        logger.info("🎉 Sample data generation complete!")
    
    def _create_sample_employees(self, num_employees: int) -> List[Dict]:
        """Create sample employees with realistic profiles"""
        roles = ['Developer', 'Senior Developer', 'QA Engineer', 'DevOps Engineer', 
                'Designer', 'Business Analyst', 'Project Manager', 'Tech Lead']
        
        skill_levels = ['Junior', 'Mid', 'Senior', 'Expert']
        
        # Hourly rate ranges by role
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
        
        for i in range(num_employees):
            role = np.random.choice(roles)
            skill_level = np.random.choice(skill_levels, p=[0.2, 0.4, 0.3, 0.1])
            
            # Calculate hourly rate
            base_min, base_max = rate_ranges[role]
            
            if skill_level == 'Junior':
                hourly_rate = np.random.uniform(base_min * 0.7, base_min * 1.0)
            elif skill_level == 'Mid':
                hourly_rate = np.random.uniform(base_min * 0.9, base_max * 0.7)
            elif skill_level == 'Senior':
                hourly_rate = np.random.uniform(base_max * 0.6, base_max * 0.9)
            else:  # Expert
                hourly_rate = np.random.uniform(base_max * 0.8, base_max * 1.2)
            
            employee = {
                'name': f"Employee_{i+1:03d}",
                'email': f"employee{i+1:03d}_{uuid.uuid4().hex[:6]}@company.com",
                'role': role,
                'skill_level': skill_level,
                'hourly_rate': round(hourly_rate, 2),
                'max_hours_per_day': 8.0,
                'is_active': True,
                'hire_date': (datetime.now() - timedelta(days=np.random.randint(180, 1000))).date().isoformat(),
                'created_at': datetime.now().isoformat()
            }
            
            try:
                result = self.db.table('employees').insert(employee).execute()
                employee['id'] = result.data[0]['id']
                employees.append(employee)
            except Exception as e:
                logger.error(f"Error creating employee: {e}")
        
        return employees
    
    def _get_existing_projects(self) -> List[Dict]:
        """Get all existing projects from database"""
        try:
            response = self.db.table('projects').select(
                'id, project_id, name, project_budget_usd, team_size, complexity_score, risk_level'
            ).execute()
            return response.data
        except Exception as e:
            logger.error(f"Error fetching projects: {e}")
            return []
    
    def _generate_daily_logs(self, projects: List[Dict], employees: List[Dict], days_back: int):
        """Generate realistic daily logs for projects"""
        start_date = datetime.now() - timedelta(days=days_back)
        
        # Assign employees to projects
        project_teams = self._assign_employees_to_projects(projects, employees)
        
        logs_batch = []
        batch_size = 100
        
        for project in projects:
            project_id = project['id']
            team = project_teams.get(project_id, [])
            
            if not team:
                continue
            
            # Determine project characteristics that affect costs
            complexity = float(project.get('complexity_score', 5))
            risk_level = project.get('risk_level', 'Medium')
            
            # Risk level affects spending patterns
            risk_multipliers = {
                'Low': (0.8, 1.0),
                'Medium': (0.9, 1.2),
                'High': (1.1, 1.5),
                'Very High': (1.3, 1.8)
            }
            
            risk_min, risk_max = risk_multipliers.get(risk_level, (0.9, 1.2))
            
            # Generate logs for each day
            for day_offset in range(days_back):
                log_date = (start_date + timedelta(days=day_offset)).date()
                
                # Skip some weekends (but not all - some teams work weekends)
                if log_date.weekday() >= 5 and np.random.random() > 0.2:
                    continue
                
                # Each team member logs hours
                for employee in team:
                    # Probability of logging (some days people are sick, on leave, etc.)
                    if np.random.random() > 0.85:
                        continue
                    
                    # Base hours with variation
                    base_hours = np.random.normal(7, 1.5)
                    
                    # Apply risk and complexity multipliers
                    risk_factor = np.random.uniform(risk_min, risk_max)
                    complexity_factor = 1 + (complexity - 5) * 0.05
                    
                    hours = base_hours * risk_factor * complexity_factor
                    
                    # Weekend hours are typically lower
                    if log_date.weekday() >= 5:
                        hours *= 0.4
                    
                    # Clamp hours to reasonable range
                    hours = max(0.5, min(14, hours))
                    
                    # Completion and issues vary by role and project phase
                    completion_pct = np.random.uniform(40, 95)
                    
                    # Higher complexity = more bugs
                    bugs_found = np.random.poisson(complexity * 0.3)
                    bugs_fixed = int(bugs_found * np.random.uniform(0.5, 1.0))
                    
                    log_entry = {
                        'project_id': project_id,
                        'employee_id': employee['id'],
                        'date': log_date.isoformat(),
                        'hours_logged': round(hours, 2),
                        'tasks_completed': np.random.randint(1, 5),
                        'bugs_found': bugs_found,
                        'bugs_fixed': bugs_fixed,
                        'story_points_completed': round(np.random.uniform(0.5, 3.0), 1),
                        'code_quality_score': round(np.random.uniform(6.5, 9.5), 1),
                        'created_at': datetime.now().isoformat()
                    }
                    
                    logs_batch.append(log_entry)
                    
                    # Insert in batches
                    if len(logs_batch) >= batch_size:
                        try:
                            self.db.table('daily_logs').insert(logs_batch).execute()
                            logger.info(f"Inserted batch of {len(logs_batch)} logs")
                            logs_batch = []
                        except Exception as e:
                            logger.error(f"Error inserting logs batch: {e}")
                            logs_batch = []
        
        # Insert remaining logs
        if logs_batch:
            try:
                self.db.table('daily_logs').insert(logs_batch).execute()
                logger.info(f"Inserted final batch of {len(logs_batch)} logs")
            except Exception as e:
                logger.error(f"Error inserting final logs batch: {e}")
    
    def _assign_employees_to_projects(self, projects: List[Dict], employees: List[Dict]) -> Dict[int, List[Dict]]:
        """Assign employees to projects based on team size"""
        project_teams = {}
        
        available_employees = employees.copy()
        np.random.shuffle(available_employees)
        
        employee_idx = 0
        
        for project in projects:
            # Convert team_size to int and handle None/null values
            team_size = project.get('team_size')
            if team_size is None:
                team_size = 5
            else:
                team_size = int(float(team_size))  # Convert float to int
            
            team_size = max(2, min(team_size, 15))  # Reasonable team size
            
            # Assign employees to project
            team = []
            for _ in range(team_size):
                if employee_idx >= len(available_employees):
                    employee_idx = 0  # Reuse employees (they can work on multiple projects)
                
                team.append(available_employees[employee_idx])
                employee_idx += 1
            
            project_teams[project['id']] = team
        
        return project_teams
    
    def _update_project_dates_and_spend(self, projects: List[Dict], days_back: int):
        """Update project start/end dates and calculate current spend"""
        
        for project in projects:
            project_id = project['id']
            
            # Set realistic start and end dates
            start_date = datetime.now() - timedelta(days=days_back)
            
            # End date based on estimated timeline (from CSV)
            # Handle potential None or float values
            estimated_months = project.get('estimated_timeline_months')
            if estimated_months is None:
                estimated_months = np.random.randint(6, 18)
            else:
                estimated_months = int(float(estimated_months))
            
            estimated_months = max(3, min(estimated_months, 36))  # Clamp to reasonable range
            end_date = start_date + timedelta(days=estimated_months * 30)
            
            # Calculate current spend from daily logs
            try:
                logs_response = self.db.table('daily_logs').select(
                    'hours_logged, employee_id'
                ).eq('project_id', project_id).execute()
                
                logs = logs_response.data
                
                if logs:
                    # Get employee rates
                    employee_ids = list(set(log['employee_id'] for log in logs))
                    employees_response = self.db.table('employees').select(
                        'id, hourly_rate'
                    ).in_('id', employee_ids).execute()
                    
                    employee_rates = {
                        emp['id']: float(emp.get('hourly_rate', 75.0)) 
                        for emp in employees_response.data
                    }
                    
                    # Calculate total spend
                    total_spend = sum(
                        float(log['hours_logged']) * employee_rates.get(log['employee_id'], 75.0)
                        for log in logs
                    )
                else:
                    total_spend = 0
                
                # Update project
                update_data = {
                    'start_date': start_date.date().isoformat(),
                    'end_date': end_date.date().isoformat(),
                    'current_spend': round(total_spend, 2),
                    'status': 'active',
                    'name': project.get('name') or f"Project {project['project_id']}",
                    'updated_at': datetime.now().isoformat()
                }
                
                self.db.table('projects').update(update_data).eq('id', project_id).execute()
                
            except Exception as e:
                logger.error(f"Error updating project {project_id}: {e}")


def generate_sample_cost_data(db: Client, num_employees: int = 50, days_back: int = 90):
    """
    Main function to generate sample data for cost forecasting
    
    Args:
        db: Supabase client
        num_employees: Number of employees to create
        days_back: Days of historical data to generate
    """
    generator = CostSampleDataGenerator(db)
    generator.generate_sample_data_for_projects(num_employees, days_back)