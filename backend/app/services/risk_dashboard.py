# backend/app/services/risk_dashboard.py

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from supabase import Client
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
import asyncio

logger = logging.getLogger(__name__)

class RiskDashboardService:
    """
    Optimized service for calculating and managing risk dashboard data
    Uses batch processing and parallel computation for performance
    """
    
    def __init__(self):
        self.risk_thresholds = {
            'critical': 80,
            'high': 65,
            'medium': 45,
            'low': 25
        }
        
        # Cache for frequently accessed data
        self._employees_cache = None
        self._cache_timestamp = None
        self._cache_ttl = 300  # 5 minutes
    
    def calculate_risk_dashboard_summary(
        self, 
        db: Client,
        project_ids: Optional[List[int]] = None,
        force_recalculation: bool = False
    ) -> Dict[str, Any]:
        """
        Calculate comprehensive risk dashboard summary
        Uses parallel processing for performance
        """
        try:
            logger.info(f"Calculating risk dashboard summary for {len(project_ids) if project_ids else 'all'} projects")
            
            # Get projects with filters
            projects = self._fetch_projects_batch(db, project_ids)
            
            if not projects:
                return self._empty_dashboard_response()
            
            # Check if we need recalculation
            if not force_recalculation:
                existing_summaries = self._fetch_existing_summaries(db, [p['id'] for p in projects])
                recent_summaries = [
                    s for s in existing_summaries 
                    if self._is_summary_recent(s, hours=4)
                ]
                
                if len(recent_summaries) == len(projects):
                    logger.info("Using cached risk summaries")
                    return self._build_dashboard_from_summaries(recent_summaries, projects)
            
            # Batch fetch all required data
            logger.info("Fetching batch data for risk calculation...")
            batch_data = self._fetch_batch_data(db, projects)
            
            # Calculate risks in parallel
            logger.info("Calculating risks in parallel...")
            risk_summaries = self._calculate_risks_parallel(projects, batch_data)
            
            # Save to database
            logger.info("Saving risk summaries to database...")
            self._save_risk_summaries(db, risk_summaries)
            
            # Build dashboard response
            dashboard = self._build_dashboard_response(risk_summaries, projects)
            
            logger.info(f"Dashboard calculation complete: {len(risk_summaries)} projects analyzed")
            return dashboard
            
        except Exception as e:
            logger.error(f"Error calculating risk dashboard: {e}")
            raise
    
    def _fetch_projects_batch(
        self, 
        db: Client, 
        project_ids: Optional[List[int]] = None
    ) -> List[Dict]:
        """Fetch projects with optimized query"""
        query = db.table("projects").select(
            "id, project_id, name, status, project_budget_usd, current_spend, "
            "team_size, complexity_score, risk_level, start_date, end_date, "
            "estimated_timeline_months"
        )
        
        if project_ids:
            query = query.in_("id", project_ids)
        else:
            # Only active projects by default
            query = query.eq("status", "active")
        
        # Limit to prevent timeout
        query = query.limit(1000)
        
        response = query.execute()
        return response.data
    
    def _fetch_existing_summaries(
        self, 
        db: Client, 
        project_ids: List[int]
    ) -> List[Dict]:
        """Fetch existing risk summaries"""
        try:
            response = db.table("risk_dashboard_summary").select("*").in_(
                "project_id", project_ids
            ).execute()
            return response.data
        except Exception as e:
            logger.warning(f"Could not fetch existing summaries: {e}")
            return []
    
    def _is_summary_recent(self, summary: Dict, hours: int = 4) -> bool:
        """Check if summary is recent enough"""
        if not summary.get('last_calculated_at'):
            return False
        
        last_calc = pd.to_datetime(summary['last_calculated_at'])
        age = datetime.now() - last_calc.replace(tzinfo=None)
        return age < timedelta(hours=hours)
    
    def _fetch_batch_data(self, db: Client, projects: List[Dict]) -> Dict[str, Any]:
        """
        Fetch all required data in batch queries
        Returns organized data structure for risk calculation
        """
        project_ids = [p['id'] for p in projects]
        cutoff_date = (datetime.now() - timedelta(days=30)).date().isoformat()
        
        batch_data = {
            'daily_logs': {},
            'sprints': {},
            'bugs': {},
            'assignments': {},
            'employees': {}
        }
        
        try:
            # Fetch daily logs (last 30 days)
            logger.info("Fetching daily logs...")
            logs_response = db.table("daily_logs").select(
                "project_id, employee_id, date, hours_logged, completion_percentage, "
                "issues_reported, story_points_completed"
            ).in_("project_id", project_ids).gte("date", cutoff_date).execute()
            
            # Group by project
            for log in logs_response.data:
                pid = log['project_id']
                if pid not in batch_data['daily_logs']:
                    batch_data['daily_logs'][pid] = []
                batch_data['daily_logs'][pid].append(log)
            
            # Fetch sprints (last 5 per project)
            logger.info("Fetching sprints...")
            sprints_response = db.table("sprints").select(
                "project_id, sprint_number, velocity, completed_story_points, "
                "planned_story_points, start_date, end_date"
            ).in_("project_id", project_ids).order(
                "start_date", desc=True
            ).execute()
            
            # Group by project and take last 5
            sprint_groups = {}
            for sprint in sprints_response.data:
                pid = sprint['project_id']
                if pid not in sprint_groups:
                    sprint_groups[pid] = []
                sprint_groups[pid].append(sprint)
            
            for pid, sprints in sprint_groups.items():
                batch_data['sprints'][pid] = sorted(
                    sprints, 
                    key=lambda x: x['start_date'], 
                    reverse=True
                )[:5]
            
            # Fetch bugs (last 30 days)
            logger.info("Fetching bugs...")
            bugs_response = db.table("bugs").select(
                "project_id, severity, status, reported_at, resolution_time_hours"
            ).in_("project_id", project_ids).gte("reported_at", cutoff_date).execute()
            
            for bug in bugs_response.data:
                pid = bug['project_id']
                if pid not in batch_data['bugs']:
                    batch_data['bugs'][pid] = []
                batch_data['bugs'][pid].append(bug)
            
            # Fetch assignments
            logger.info("Fetching assignments...")
            assignments_response = db.table("project_assignments").select(
                "project_id, employee_id, allocation_percentage, expected_hours_per_day"
            ).in_("project_id", project_ids).eq("is_active", True).execute()
            
            for assignment in assignments_response.data:
                pid = assignment['project_id']
                if pid not in batch_data['assignments']:
                    batch_data['assignments'][pid] = []
                batch_data['assignments'][pid].append(assignment)
            
            # Fetch employees (cache)
            if not self._employees_cache or self._is_cache_expired():
                logger.info("Fetching employees...")
                employees_response = db.table("employees").select(
                    "id, hourly_rate, max_hours_per_day, skill_level"
                ).eq("is_active", True).execute()
                
                self._employees_cache = {
                    emp['id']: emp for emp in employees_response.data
                }
                self._cache_timestamp = datetime.now()
            
            batch_data['employees'] = self._employees_cache
            
            logger.info("Batch data fetching complete")
            return batch_data
            
        except Exception as e:
            logger.error(f"Error fetching batch data: {e}")
            raise
    
    def _is_cache_expired(self) -> bool:
        """Check if employee cache is expired"""
        if not self._cache_timestamp:
            return True
        return (datetime.now() - self._cache_timestamp).seconds > self._cache_ttl
    
    def _calculate_risks_parallel(
        self, 
        projects: List[Dict], 
        batch_data: Dict[str, Any]
    ) -> List[Dict]:
        """
        Calculate risks for all projects in parallel
        Uses ThreadPoolExecutor for CPU-bound calculations
        """
        risk_summaries = []
        
        # Use thread pool for parallel processing
        max_workers = min(10, len(projects))
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_project = {
                executor.submit(
                    self._calculate_project_risk, 
                    project, 
                    batch_data
                ): project for project in projects
            }
            
            for future in as_completed(future_to_project):
                try:
                    risk_summary = future.result()
                    if risk_summary:
                        risk_summaries.append(risk_summary)
                except Exception as e:
                    project = future_to_project[future]
                    logger.error(f"Error calculating risk for project {project['id']}: {e}")
        
        return risk_summaries
    
    def _calculate_project_risk(
        self, 
        project: Dict, 
        batch_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Calculate comprehensive risk for a single project
        """
        project_id = project['id']
        
        # Get project-specific data
        logs = batch_data['daily_logs'].get(project_id, [])
        sprints = batch_data['sprints'].get(project_id, [])
        bugs = batch_data['bugs'].get(project_id, [])
        assignments = batch_data['assignments'].get(project_id, [])
        employees = batch_data['employees']
        
        # Calculate component risks
        schedule_risk = self._calculate_schedule_risk(project, logs, sprints)
        budget_risk = self._calculate_budget_risk(project, logs, employees)
        quality_risk = self._calculate_quality_risk(bugs, logs)
        resource_risk = self._calculate_resource_risk(logs, assignments, employees)
        technical_risk = self._calculate_technical_risk(project, logs, sprints)
        
        # Calculate overall risk (weighted average)
        overall_risk = (
            schedule_risk * 0.25 +
            budget_risk * 0.25 +
            quality_risk * 0.20 +
            resource_risk * 0.15 +
            technical_risk * 0.15
        )
        
        # Determine risk level
        risk_level = self._determine_risk_level(overall_risk)
        
        # Calculate key metrics
        metrics = self._calculate_key_metrics(
            project, logs, sprints, bugs, assignments
        )
        
        # Identify risk factors
        risk_factors = self._identify_risk_factors(
            schedule_risk, budget_risk, quality_risk,
            resource_risk, technical_risk, metrics
        )
        
        return {
            'project_id': project_id,
            'overall_risk_score': float(overall_risk),
            'risk_level': risk_level,
            'schedule_risk': float(schedule_risk),
            'budget_risk': float(budget_risk),
            'quality_risk': float(quality_risk),
            'resource_risk': float(resource_risk),
            'technical_risk': float(technical_risk),
            'sprint_velocity_deviation': float(metrics['velocity_deviation']),
            'logging_consistency_score': float(metrics['logging_consistency']),
            'budget_utilization': float(metrics['budget_utilization']),
            'team_utilization_avg': float(metrics['team_utilization']),
            'bug_density': float(metrics['bug_density']),
            'delayed_tasks_count': int(metrics['delayed_tasks']),
            'irregular_velocity_flag': risk_factors['irregular_velocity'],
            'inconsistent_logging_flag': risk_factors['inconsistent_logging'],
            'overbudget_flag': risk_factors['overbudget'],
            'high_bug_rate_flag': risk_factors['high_bug_rate'],
            'last_calculated_at': datetime.now().isoformat(),
            'calculation_version': '1.0'
        }
    
    def _calculate_schedule_risk(
        self, 
        project: Dict, 
        logs: List[Dict], 
        sprints: List[Dict]
    ) -> float:
        """Calculate schedule risk based on velocity and completion trends"""
        risk = 50.0  # Base risk
        
        # Sprint velocity analysis
        if sprints and len(sprints) >= 3:
            velocities = [s['velocity'] for s in sprints if s.get('velocity')]
            if velocities:
                velocity_std = np.std(velocities)
                velocity_mean = np.mean(velocities)
                
                if velocity_mean > 0:
                    cv = velocity_std / velocity_mean
                    # High coefficient of variation = higher risk
                    risk += min(cv * 100, 30)
                
                # Declining trend
                if len(velocities) >= 3:
                    recent_avg = np.mean(velocities[:2])
                    historical_avg = np.mean(velocities[2:])
                    if historical_avg > 0 and recent_avg < historical_avg * 0.8:
                        risk += 20
        
        # Timeline progress vs completion
        if project.get('start_date') and project.get('end_date'):
            start = pd.to_datetime(project['start_date'])
            end = pd.to_datetime(project['end_date'])
            now = pd.Timestamp.now()
            
            if now < end:
                timeline_progress = (now - start) / (end - start)
                
                # Estimate completion from logs
                if logs:
                    avg_completion = np.mean([l.get('completion_percentage', 50) for l in logs])
                    completion_ratio = avg_completion / 100.0
                    
                    # Behind schedule
                    if timeline_progress > completion_ratio + 0.15:
                        risk += 25
        
        return min(100, max(0, risk))
    
    def _calculate_budget_risk(
        self, 
        project: Dict, 
        logs: List[Dict], 
        employees: Dict[int, Dict]
    ) -> float:
        """Calculate budget risk based on spending trends"""
        risk = 50.0
        
        budget = project.get('project_budget_usd', 0)
        current_spend = project.get('current_spend', 0)
        
        if budget > 0:
            utilization = (current_spend / budget) * 100
            
            # Over budget
            if utilization > 100:
                risk += 40
            elif utilization > 85:
                risk += 25
            elif utilization > 70:
                risk += 10
            
            # Calculate burn rate from logs
            if logs:
                total_hours = sum(l.get('hours_logged', 0) for l in logs)
                # Estimate cost
                employee_costs = {}
                for log in logs:
                    emp_id = log.get('employee_id')
                    if emp_id in employees:
                        rate = employees[emp_id].get('hourly_rate', 75)
                        hours = log.get('hours_logged', 0)
                        employee_costs[emp_id] = employee_costs.get(emp_id, 0) + (hours * rate)
                
                recent_cost = sum(employee_costs.values())
                
                # Check if burn rate is accelerating
                if budget > 0 and current_spend > 0:
                    days_elapsed = 30  # Last 30 days
                    projected_monthly = recent_cost
                    
                    # Estimate project duration
                    if project.get('start_date') and project.get('end_date'):
                        start = pd.to_datetime(project['start_date'])
                        end = pd.to_datetime(project['end_date'])
                        total_months = (end - start).days / 30
                        
                        if total_months > 0:
                            projected_total = projected_monthly * total_months
                            if projected_total > budget * 1.2:
                                risk += 20
        
        return min(100, max(0, risk))
    
    def _calculate_quality_risk(
        self, 
        bugs: List[Dict], 
        logs: List[Dict]
    ) -> float:
        """Calculate quality risk based on bug metrics"""
        risk = 50.0
        
        if not logs:
            return risk
        
        # Bug density
        total_hours = sum(l.get('hours_logged', 0) for l in logs)
        if total_hours > 0:
            bug_density = len(bugs) / (total_hours / 100)  # Bugs per 100 hours
            if bug_density > 2:
                risk += 25
            elif bug_density > 1:
                risk += 15
        
        # High severity bugs
        high_severity = [b for b in bugs if b.get('severity') in ['critical', 'high']]
        if len(bugs) > 0:
            high_severity_ratio = len(high_severity) / len(bugs)
            if high_severity_ratio > 0.3:
                risk += 20
        
        # Unresolved bugs
        open_bugs = [b for b in bugs if b.get('status') not in ['resolved', 'closed']]
        if len(bugs) > 0:
            open_ratio = len(open_bugs) / len(bugs)
            if open_ratio > 0.5:
                risk += 15
        
        return min(100, max(0, risk))
    
    def _calculate_resource_risk(
        self, 
        logs: List[Dict], 
        assignments: List[Dict],
        employees: Dict[int, Dict]
    ) -> float:
        """Calculate resource risk based on utilization"""
        risk = 50.0
        
        if not logs or not assignments:
            return risk
        
        # Calculate utilization by employee
        employee_hours = {}
        for log in logs:
            emp_id = log.get('employee_id')
            employee_hours[emp_id] = employee_hours.get(emp_id, 0) + log.get('hours_logged', 0)
        
        # Calculate expected hours
        days = 30
        utilization_rates = []
        
        for assignment in assignments:
            emp_id = assignment['employee_id']
            expected_daily = assignment.get('expected_hours_per_day', 8)
            expected_total = expected_daily * days
            
            actual = employee_hours.get(emp_id, 0)
            if expected_total > 0:
                util_rate = actual / expected_total
                utilization_rates.append(util_rate)
        
        if utilization_rates:
            avg_util = np.mean(utilization_rates)
            
            # Underutilization
            if avg_util < 0.6:
                risk += 20
            # Overutilization
            elif avg_util > 1.3:
                risk += 25
            
            # High variance in utilization
            util_std = np.std(utilization_rates)
            if util_std > 0.3:
                risk += 15
        
        return min(100, max(0, risk))
    
    def _calculate_technical_risk(
        self, 
        project: Dict, 
        logs: List[Dict], 
        sprints: List[Dict]
    ) -> float:
        """Calculate technical risk based on complexity and issues"""
        risk = 50.0
        
        # Complexity factor
        complexity = project.get('complexity_score', 5)
        if complexity > 7:
            risk += 20
        elif complexity > 5:
            risk += 10
        
        # Issue density from logs
        if logs:
            total_issues = sum(l.get('issues_reported', 0) for l in logs)
            total_hours = sum(l.get('hours_logged', 0) for l in logs)
            
            if total_hours > 0:
                issue_rate = total_issues / (total_hours / 10)
                if issue_rate > 2:
                    risk += 15
        
        return min(100, max(0, risk))
    
    def _calculate_key_metrics(
        self,
        project: Dict,
        logs: List[Dict],
        sprints: List[Dict],
        bugs: List[Dict],
        assignments: List[Dict]
    ) -> Dict[str, float]:
        """Calculate key metrics for dashboard"""
        metrics = {
            'velocity_deviation': 0.0,
            'logging_consistency': 0.0,
            'budget_utilization': 0.0,
            'team_utilization': 0.0,
            'bug_density': 0.0,
            'delayed_tasks': 0
        }
        
        # Velocity deviation
        if sprints and len(sprints) >= 3:
            velocities = [s['velocity'] for s in sprints if s.get('velocity')]
            if velocities:
                metrics['velocity_deviation'] = np.std(velocities) / np.mean(velocities) if np.mean(velocities) > 0 else 0
        
        # Logging consistency
        if logs:
            unique_dates = len(set(l['date'] for l in logs))
            expected_days = 30
            metrics['logging_consistency'] = unique_dates / expected_days
        
        # Budget utilization
        budget = project.get('project_budget_usd', 0)
        if budget > 0:
            metrics['budget_utilization'] = (project.get('current_spend', 0) / budget) * 100
        
        # Team utilization
        if logs and assignments:
            total_hours = sum(l.get('hours_logged', 0) for l in logs)
            expected_hours = sum(a.get('expected_hours_per_day', 8) * 30 for a in assignments)
            if expected_hours > 0:
                metrics['team_utilization'] = (total_hours / expected_hours) * 100
        
        # Bug density
        if logs:
            total_hours = sum(l.get('hours_logged', 0) for l in logs)
            if total_hours > 0:
                metrics['bug_density'] = len(bugs) / (total_hours / 100)
        
        # Delayed tasks (from completion percentage)
        if logs:
            low_completion = [l for l in logs if l.get('completion_percentage', 100) < 70]
            metrics['delayed_tasks'] = len(low_completion)
        
        return metrics
    
    def _identify_risk_factors(
        self,
        schedule_risk: float,
        budget_risk: float,
        quality_risk: float,
        resource_risk: float,
        technical_risk: float,
        metrics: Dict[str, float]
    ) -> Dict[str, bool]:
        """Identify specific risk factors as flags"""
        return {
            'irregular_velocity': metrics['velocity_deviation'] > 0.3,
            'inconsistent_logging': metrics['logging_consistency'] < 0.7,
            'overbudget': metrics['budget_utilization'] > 100,
            'high_bug_rate': metrics['bug_density'] > 1.5
        }
    
    def _determine_risk_level(self, risk_score: float) -> str:
        """Determine risk level from score"""
        if risk_score >= self.risk_thresholds['critical']:
            return 'critical'
        elif risk_score >= self.risk_thresholds['high']:
            return 'high'
        elif risk_score >= self.risk_thresholds['medium']:
            return 'medium'
        elif risk_score >= self.risk_thresholds['low']:
            return 'low'
        return 'very_low'
    
    def _save_risk_summaries(self, db: Client, summaries: List[Dict]):
        """Save risk summaries to database"""
        if not summaries:
            return
        
        def serialize_bools(data: Dict) -> Dict:
            """Convert boolean values to JSON-compatible format"""
            serialized = data.copy()
            bool_fields = [
                'irregular_velocity_flag',
                'inconsistent_logging_flag',
                'overbudget_flag',
                'high_bug_rate_flag'
            ]
            for field in bool_fields:
                if field in serialized:
                    serialized[field] = bool(serialized[field])  # Ensure it's a bool
            return serialized

        try:
            batch_size = 100
            for i in range(0, len(summaries), batch_size):
                batch = summaries[i:i+batch_size]
                serialized_batch = [serialize_bools(summary) for summary in batch]
                logger.debug(f"Upserting batch: {serialized_batch}")  # Optional: for debugging
                db.table("risk_dashboard_summary").upsert(serialized_batch).execute()
            logger.info(f"Saved {len(summaries)} risk summaries")
        except Exception as e:
            logger.error(f"Error saving risk summaries: {e}")
            raise
    
    def _build_dashboard_response(self, summaries: List[Dict], projects: List[Dict]) -> Dict[str, Any]:
        """Build final dashboard response"""
        # Create project lookup
        project_lookup = {p['id']: p for p in projects}
        
        # Risk distribution
        risk_distribution = {
            'critical': 0,
            'high': 0,
            'medium': 0,
            'low': 0,
            'very_low': 0
        }
        
        # Aggregate metrics
        total_score = 0
        component_scores = {
            'schedule': 0,
            'budget': 0,
            'quality': 0,
            'resource': 0,
            'technical': 0
        }
        
        # Projects with flags
        flagged_projects = {
            'irregular_velocity': [],
            'inconsistent_logging': [],
            'overbudget': [],
            'high_bug_rate': []
        }
        
        # Process summaries
        project_risks = []
        for summary in summaries:
            # Convert numpy.bool to Python bool for flag fields
            summary = summary.copy()  # Avoid modifying original data
            bool_fields = [
                'irregular_velocity_flag',
                'inconsistent_logging_flag',
                'overbudget_flag',
                'high_bug_rate_flag'
            ]
            for field in bool_fields:
                if field in summary:
                    summary[field] = bool(summary[field])  # Convert numpy.bool to Python bool
            
            risk_level = summary['risk_level']
            risk_distribution[risk_level] += 1
            
            total_score += summary['overall_risk_score']
            component_scores['schedule'] += summary['schedule_risk']
            component_scores['budget'] += summary['budget_risk']
            component_scores['quality'] += summary['quality_risk']
            component_scores['resource'] += summary['resource_risk']
            component_scores['technical'] += summary['technical_risk']
            
            # Check flags
            proj = project_lookup.get(summary['project_id'])
            if proj:
                project_info = {
                    'project_id': proj['id'],
                    'project_name': proj.get('name', f"Project {proj['project_id']}"),
                    'risk_score': summary['overall_risk_score'],
                    'risk_level': risk_level
                }
                
                if summary['irregular_velocity_flag']:
                    flagged_projects['irregular_velocity'].append(project_info)
                if summary['inconsistent_logging_flag']:
                    flagged_projects['inconsistent_logging'].append(project_info)
                if summary['overbudget_flag']:
                    flagged_projects['overbudget'].append(project_info)
                if summary['high_bug_rate_flag']:
                    flagged_projects['high_bug_rate'].append(project_info)
                
                # Add to project risks list
                project_risks.append({
                    **project_info,
                    'schedule_risk': summary['schedule_risk'],
                    'budget_risk': summary['budget_risk'],
                    'quality_risk': summary['quality_risk'],
                    'resource_risk': summary['resource_risk'],
                    'technical_risk': summary['technical_risk'],
                    'key_metrics': {
                        'velocity_deviation': summary['sprint_velocity_deviation'],
                        'logging_consistency': summary['logging_consistency_score'],
                        'budget_utilization': summary['budget_utilization'],
                        'team_utilization': summary['team_utilization_avg'],
                        'bug_density': summary['bug_density']
                    },
                    'flags': {
                        'irregular_velocity': summary['irregular_velocity_flag'],
                        'inconsistent_logging': summary['inconsistent_logging_flag'],
                        'overbudget': summary['overbudget_flag'],
                        'high_bug_rate': summary['high_bug_rate_flag']
                    },
                    'delayed_tasks_count': summary['delayed_tasks_count']
                })
        
        # Calculate averages
        num_projects = len(summaries)
        avg_risk_score = total_score / num_projects if num_projects > 0 else 0
        
        for key in component_scores:
            component_scores[key] = component_scores[key] / num_projects if num_projects > 0 else 0
        
        # Sort project risks by score
        project_risks.sort(key=lambda x: x['risk_score'], reverse=True)
        
        return {
            'summary': {
                'total_projects': num_projects,
                'avg_risk_score': round(avg_risk_score, 2),
                'risk_distribution': risk_distribution,
                'high_risk_projects': risk_distribution['critical'] + risk_distribution['high'],
                'critical_projects': risk_distribution['critical']
            },
            'component_averages': {
                'schedule_risk': round(component_scores['schedule'], 2),
                'budget_risk': round(component_scores['budget'], 2),
                'quality_risk': round(component_scores['quality'], 2),
                'resource_risk': round(component_scores['resource'], 2),
                'technical_risk': round(component_scores['technical'], 2)
            },
            'flagged_projects': {
                'irregular_velocity': len(flagged_projects['irregular_velocity']),
                'inconsistent_logging': len(flagged_projects['inconsistent_logging']),
                'overbudget': len(flagged_projects['overbudget']),
                'high_bug_rate': len(flagged_projects['high_bug_rate'])
            },
            'top_risk_projects': project_risks[:20],  # Top 20 highest risk
            'flagged_details': {
                'irregular_velocity': flagged_projects['irregular_velocity'][:10],
                'inconsistent_logging': flagged_projects['inconsistent_logging'][:10],
                'overbudget': flagged_projects['overbudget'][:10],
                'high_bug_rate': flagged_projects['high_bug_rate'][:10]
            },
            'generated_at': datetime.now().isoformat(),
            'calculation_version': '1.0'
        }
    
    def _build_dashboard_from_summaries(
        self, 
        summaries: List[Dict], 
        projects: List[Dict]
    ) -> Dict[str, Any]:
        """Build dashboard from cached summaries"""
        return self._build_dashboard_response(summaries, projects)
    
    def _empty_dashboard_response(self) -> Dict[str, Any]:
        """Return empty dashboard response"""
        return {
            'summary': {
                'total_projects': 0,
                'avg_risk_score': 0,
                'risk_distribution': {
                    'critical': 0,
                    'high': 0,
                    'medium': 0,
                    'low': 0,
                    'very_low': 0
                },
                'high_risk_projects': 0,
                'critical_projects': 0
            },
            'component_averages': {
                'schedule_risk': 0,
                'budget_risk': 0,
                'quality_risk': 0,
                'resource_risk': 0,
                'technical_risk': 0
            },
            'flagged_projects': {
                'irregular_velocity': 0,
                'inconsistent_logging': 0,
                'overbudget': 0,
                'high_bug_rate': 0
            },
            'top_risk_projects': [],
            'flagged_details': {
                'irregular_velocity': [],
                'inconsistent_logging': [],
                'overbudget': [],
                'high_bug_rate': []
            },
            'generated_at': datetime.now().isoformat(),
            'message': 'No projects found'
        }
    
    def get_paginated_project_risks(
        self,
        db: Client,
        page: int = 1,
        page_size: int = 50,
        risk_level: Optional[str] = None,
        sort_by: str = 'risk_score',
        order: str = 'desc'
    ) -> Dict[str, Any]:
        """
        Get paginated project risks with filtering and sorting
        """
        try:
            # Build query
            query = db.table("risk_dashboard_summary").select(
                "*, projects(id, project_id, name, status)"
            )
            
            # Filter by risk level
            if risk_level:
                query = query.eq("risk_level", risk_level)
            
            # Count total
            count_response = query.execute()
            total_count = len(count_response.data)
            
            # Apply sorting
            query = query.order(sort_by, desc=(order == 'desc'))
            
            # Apply pagination
            offset = (page - 1) * page_size
            query = query.range(offset, offset + page_size - 1)
            
            response = query.execute()
            summaries = response.data
            
            # Format response
            projects = []
            for summary in summaries:
                proj_data = summary.get('projects', {})
                projects.append({
                    'project_id': summary['project_id'],
                    'project_name': proj_data.get('name', 'Unknown'),
                    'project_identifier': proj_data.get('project_id', ''),
                    'status': proj_data.get('status', 'unknown'),
                    'overall_risk_score': summary['overall_risk_score'],
                    'risk_level': summary['risk_level'],
                    'component_risks': {
                        'schedule': summary['schedule_risk'],
                        'budget': summary['budget_risk'],
                        'quality': summary['quality_risk'],
                        'resource': summary['resource_risk'],
                        'technical': summary['technical_risk']
                    },
                    'key_metrics': {
                        'velocity_deviation': summary['sprint_velocity_deviation'],
                        'logging_consistency': summary['logging_consistency_score'],
                        'budget_utilization': summary['budget_utilization'],
                        'team_utilization': summary['team_utilization_avg'],
                        'bug_density': summary['bug_density']
                    },
                    'flags': {
                        'irregular_velocity': summary['irregular_velocity_flag'],
                        'inconsistent_logging': summary['inconsistent_logging_flag'],
                        'overbudget': summary['overbudget_flag'],
                        'high_bug_rate': summary['high_bug_rate_flag']
                    },
                    'delayed_tasks_count': summary['delayed_tasks_count'],
                    'last_updated': summary['last_calculated_at']
                })
            
            return {
                'projects': projects,
                'pagination': {
                    'page': page,
                    'page_size': page_size,
                    'total_count': total_count,
                    'total_pages': (total_count + page_size - 1) // page_size,
                    'has_next': offset + page_size < total_count,
                    'has_prev': page > 1
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting paginated risks: {e}")
            raise
    
    def get_project_risk_detail(
        self,
        db: Client,
        project_id: int,
        force_recalculation: bool = False
    ) -> Dict[str, Any]:
        """
        Get detailed risk information for a specific project
        """
        try:
            # Check cache first
            if not force_recalculation:
                summary_response = db.table("risk_dashboard_summary").select(
                    "*"
                ).eq("project_id", project_id).execute()
                
                if summary_response.data and self._is_summary_recent(summary_response.data[0], hours=4):
                    summary = summary_response.data[0]
                    
                    # Get project details
                    project_response = db.table("projects").select("*").eq("id", project_id).single().execute()
                    project = project_response.data
                    
                    return self._format_project_detail(summary, project)
            
            # Recalculate if needed
            project_response = db.table("projects").select("*").eq("id", project_id).single().execute()
            project = project_response.data
            
            if not project:
                raise ValueError(f"Project {project_id} not found")
            
            # Fetch batch data for this project
            batch_data = self._fetch_batch_data(db, [project])
            
            # Calculate risk
            summary = self._calculate_project_risk(project, batch_data)
            
            # Save to database
            db.table("risk_dashboard_summary").upsert(summary).execute()
            
            return self._format_project_detail(summary, project)
            
        except Exception as e:
            logger.error(f"Error getting project risk detail: {e}")
            raise
    
    def _format_project_detail(self, summary: Dict, project: Dict) -> Dict[str, Any]:
        """Format detailed project risk information"""
        return {
            'project': {
                'id': project['id'],
                'project_id': project['project_id'],
                'name': project.get('name', 'Unknown'),
                'status': project.get('status', 'unknown'),
                'budget': project.get('project_budget_usd'),
                'current_spend': project.get('current_spend'),
                'team_size': project.get('team_size'),
                'complexity': project.get('complexity_score'),
                'start_date': project.get('start_date'),
                'end_date': project.get('end_date')
            },
            'risk_assessment': {
                'overall_risk_score': summary['overall_risk_score'],
                'risk_level': summary['risk_level'],
                'component_risks': {
                    'schedule': {
                        'score': summary['schedule_risk'],
                        'level': self._determine_risk_level(summary['schedule_risk'])
                    },
                    'budget': {
                        'score': summary['budget_risk'],
                        'level': self._determine_risk_level(summary['budget_risk'])
                    },
                    'quality': {
                        'score': summary['quality_risk'],
                        'level': self._determine_risk_level(summary['quality_risk'])
                    },
                    'resource': {
                        'score': summary['resource_risk'],
                        'level': self._determine_risk_level(summary['resource_risk'])
                    },
                    'technical': {
                        'score': summary['technical_risk'],
                        'level': self._determine_risk_level(summary['technical_risk'])
                    }
                }
            },
            'key_metrics': {
                'sprint_velocity_deviation': summary['sprint_velocity_deviation'],
                'logging_consistency_score': summary['logging_consistency_score'],
                'budget_utilization': summary['budget_utilization'],
                'team_utilization_avg': summary['team_utilization_avg'],
                'bug_density': summary['bug_density'],
                'delayed_tasks_count': summary['delayed_tasks_count']
            },
            'risk_flags': {
                'irregular_velocity': summary['irregular_velocity_flag'],
                'inconsistent_logging': summary['inconsistent_logging_flag'],
                'overbudget': summary['overbudget_flag'],
                'high_bug_rate': summary['high_bug_rate_flag']
            },
            'metadata': {
                'last_calculated': summary['last_calculated_at'],
                'calculation_version': summary.get('calculation_version', '1.0')
            }
        }