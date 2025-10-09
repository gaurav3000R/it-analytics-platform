"""
Sample Data Generator for Testing and Development
Generates realistic project, task, and resource data
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import json
from pathlib import Path


class SampleDataGenerator:
    """Generate sample data for testing the risk prediction system"""
    
    def __init__(self, seed=42):
        np.random.seed(seed)
        random.seed(seed)
        self.output_dir = Path("./data/raw/sample")
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_projects(self, n_projects=10) -> pd.DataFrame:
        """Generate sample project data"""
        statuses = ['planning', 'in_progress', 'at_risk', 'delayed', 'completed']
        
        projects = []
        for i in range(1, n_projects + 1):
            start_date = datetime.now() - timedelta(days=random.randint(90, 365))
            planned_duration = random.randint(60, 180)
            actual_duration = planned_duration + random.randint(-30, 60)
            
            projects.append({
                'project_id': i,
                'project_name': f'Project {chr(64+i)}',
                'status': random.choice(statuses),
                'start_date': start_date,
                'planned_end_date': start_date + timedelta(days=planned_duration),
                'actual_end_date': start_date + timedelta(days=actual_duration) if random.random() > 0.5 else None,
                'planned_budget': random.uniform(100000, 500000),
                'actual_cost': random.uniform(90000, 550000),
                'team_size': random.randint(5, 20),
                'manager_id': random.randint(1, 5)
            })
        
        df = pd.DataFrame(projects)
        df.to_csv(self.output_dir / 'projects.csv', index=False)
        print(f"Generated {len(df)} projects")
        return df
    
    def generate_sprints(self, project_ids, sprints_per_project=6) -> pd.DataFrame:
        """Generate sample sprint data"""
        sprints = []
        sprint_id = 1
        
        for project_id in project_ids:
            start_date = datetime.now() - timedelta(days=180)
            
            for sprint_num in range(1, sprints_per_project + 1):
                sprint_start = start_date + timedelta(days=(sprint_num - 1) * 14)
                sprint_end = sprint_start + timedelta(days=14)
                
                planned_points = random.randint(30, 60)
                completed_points = int(planned_points * random.uniform(0.6, 1.0))
                
                sprints.append({
                    'sprint_id': sprint_id,
                    'project_id': project_id,
                    'sprint_number': sprint_num,
                    'sprint_name': f'Sprint {sprint_num}',
                    'start_date': sprint_start,
                    'end_date': sprint_end,
                    'planned_points': planned_points,
                    'completed_points': completed_points,
                    'velocity': completed_points / 14  # Points per day
                })
                sprint_id += 1
        
        df = pd.DataFrame(sprints)
        df.to_csv(self.output_dir / 'sprints.csv', index=False)
        print(f"Generated {len(df)} sprints")
        return df
    
    def generate_tasks(self, project_ids, sprint_ids, n_tasks=500) -> pd.DataFrame:
        """Generate sample task data"""
        task_types = ['feature', 'bug', 'tech_debt', 'documentation']
        statuses = ['todo', 'in_progress', 'in_review', 'completed', 'blocked']
        priorities = ['low', 'medium', 'high', 'critical']
        
        tasks = []
        for i in range(1, n_tasks + 1):
            is_bug = random.random() < 0.2
            task_type = 'bug' if is_bug else random.choice(task_types)
            
            created_at = datetime.now() - timedelta(days=random.randint(1, 180))
            estimated_hours = random.uniform(2, 40)
            actual_hours = estimated_hours * random.uniform(0.7, 1.5)
            
            status = random.choice(statuses)
            completed_at = created_at + timedelta(hours=actual_hours) if status == 'completed' else None
            
            tasks.append({
                'task_id': i,
                'project_id': random.choice(project_ids),
                'sprint_id': random.choice(sprint_ids) if random.random() > 0.2 else None,
                'title': f'Task {i}: {task_type.capitalize()}',
                'task_type': task_type,
                'status': status,
                'priority': random.choice(priorities),
                'is_bug': is_bug,
                'bug_severity': random.choice(['low', 'medium', 'high', 'critical']) if is_bug else None,
                'reopen_count': random.randint(0, 3) if is_bug else 0,
                'estimated_hours': estimated_hours,
                'actual_hours': actual_hours if status == 'completed' else 0,
                'story_points': random.randint(1, 13),
                'assignee_id': random.randint(1, 20),
                'created_at': created_at,
                'completed_at': completed_at,
                'is_blocked': status == 'blocked',
                'has_dependencies': random.random() < 0.3
            })
        
        df = pd.DataFrame(tasks)
        df.to_csv(self.output_dir / 'tasks.csv', index=False)
        print(f"Generated {len(df)} tasks")
        return df
    
    def generate_project_metrics(self, project_ids, days=90) -> pd.DataFrame:
        """Generate daily/weekly project metrics"""
        metrics = []
        
        for project_id in project_ids:
            start_date = datetime.now() - timedelta(days=days)
            
            # Initial values
            velocity = random.uniform(20, 40)
            completion_rate = random.uniform(0.6, 0.9)
            
            for day in range(0, days, 7):  # Weekly metrics
                metric_date = start_date + timedelta(days=day)
                
                # Add some trend and randomness
                velocity += random.uniform(-5, 5)
                velocity = max(10, min(50, velocity))
                
                completion_rate += random.uniform(-0.1, 0.1)
                completion_rate = max(0.3, min(1.0, completion_rate))
                
                total_tasks = random.randint(20, 50)
                completed_tasks = int(total_tasks * completion_rate)
                
                metrics.append({
                    'project_id': project_id,
                    'metric_date': metric_date,
                    'sprint_velocity': velocity,
                    'avg_velocity_last_3_sprints': velocity * random.uniform(0.9, 1.1),
                    'velocity_trend': random.choice(['improving', 'declining', 'stable']),
                    'total_tasks': total_tasks,
                    'completed_tasks': completed_tasks,
                    'in_progress_tasks': random.randint(5, 15),
                    'blocked_tasks': random.randint(0, 5),
                    'completion_rate': completion_rate,
                    'total_bugs': random.randint(5, 20),
                    'open_bugs': random.randint(2, 10),
                    'closed_bugs': random.randint(3, 15),
                    'bug_reopen_rate': random.uniform(0, 0.3),
                    'team_size': random.randint(5, 20),
                    'avg_utilization_rate': random.uniform(0.6, 1.2),
                    'over_allocated_resources': random.randint(0, 3),
                    'avg_task_cycle_time': random.uniform(2, 10),
                    'avg_time_to_resolve_bug': random.uniform(1, 15),
                    'days_behind_schedule': random.randint(-5, 20),
                    'budget_variance_percent': random.uniform(-10, 30)
                })
        
        df = pd.DataFrame(metrics)
        df.to_csv(self.output_dir / 'project_metrics.csv', index=False)
        print(f"Generated {len(df)} metric records")
        return df
    
    def generate_resource_utilization(self, project_ids, n_resources=20, weeks=12) -> pd.DataFrame:
        """Generate resource utilization data"""
        resources = []
        
        for resource_id in range(1, n_resources + 1):
            project_id = random.choice(project_ids)
            start_date = datetime.now() - timedelta(weeks=weeks)
            
            for week in range(weeks):
                week_start = start_date + timedelta(weeks=week)
                
                allocated_hours = 40
                actual_hours = random.uniform(20, 60)
                utilization_rate = actual_hours / allocated_hours
                
                tasks_assigned = random.randint(3, 15)
                tasks_completed = int(tasks_assigned * random.uniform(0.5, 1.0))
                
                resources.append({
                    'user_id': resource_id,
                    'project_id': project_id,
                    'week_start_date': week_start,
                    'allocated_hours': allocated_hours,
                    'actual_hours': actual_hours,
                    'utilization_rate': utilization_rate,
                    'tasks_assigned': tasks_assigned,
                    'tasks_completed': tasks_completed,
                    'avg_task_completion_time': random.uniform(1, 5),
                    'bugs_created': random.randint(0, 3),
                    'code_review_comments': random.randint(0, 10),
                    'is_overallocated': utilization_rate > 1.0,
                    'is_underutilized': utilization_rate < 0.7
                })
        
        df = pd.DataFrame(resources)
        df.to_csv(self.output_dir / 'resource_utilization.csv', index=False)
        print(f"Generated {len(df)} resource utilization records")
        return df
    
    def generate_kaizen_logs(self, project_ids, n_logs=100) -> pd.DataFrame:
        """Generate sample Kaizen logs"""
        log_types = ['meeting', 'improvement', 'issue', 'decision', 'retrospective']
        categories = ['process', 'quality', 'communication', 'tooling', 'planning']
        
        logs = []
        for i in range(1, n_logs + 1):
            log_date = datetime.now() - timedelta(days=random.randint(1, 90))
            
            logs.append({
                'log_id': i,
                'project_id': random.choice(project_ids),
                'log_date': log_date,
                'log_type': random.choice(log_types),
                'category': random.choice(categories),
                'title': f'Kaizen Log {i}',
                'description': f'Description for kaizen log entry {i}',
                'participants': json.dumps([random.randint(1, 20) for _ in range(random.randint(3, 8))]),
                'action_items': json.dumps([f'Action {j}' for j in range(random.randint(1, 5))]),
                'impact': random.choice(['low', 'medium', 'high']),
                'status': random.choice(['open', 'in_progress', 'completed'])
            })
        
        df = pd.DataFrame(logs)
        df.to_csv(self.output_dir / 'kaizen_logs.csv', index=False)
        print(f"Generated {len(df)} Kaizen logs")
        return df
    
    def generate_all(self):
        """Generate all sample datasets"""
        print("=" * 50)
        print("Generating Sample Data for IT Analytics Platform")
        print("=" * 50)
        
        # Generate projects
        projects_df = self.generate_projects(n_projects=10)
        project_ids = projects_df['project_id'].tolist()
        
        # Generate sprints
        sprints_df = self.generate_sprints(project_ids, sprints_per_project=6)
        sprint_ids = sprints_df['sprint_id'].tolist()
        
        # Generate tasks
        self.generate_tasks(project_ids, sprint_ids, n_tasks=500)
        
        # Generate metrics
        self.generate_project_metrics(project_ids, days=90)
        
        # Generate resource utilization
        self.generate_resource_utilization(project_ids, n_resources=20, weeks=12)
        
        # Generate Kaizen logs
        self.generate_kaizen_logs(project_ids, n_logs=100)
        
        print("=" * 50)
        print(f"All sample data generated in: {self.output_dir}")
        print("=" * 50)
        
        return {
            'projects': len(project_ids),
            'sprints': len(sprint_ids),
            'output_directory': str(self.output_dir)
        }


if __name__ == "__main__":
    generator = SampleDataGenerator()
    result = generator.generate_all()
    print("\nSummary:")
    print(f"- Projects: {result['projects']}")
    print(f"- Sprints: {result['sprints']}")
    print(f"- Data location: {result['output_directory']}")
