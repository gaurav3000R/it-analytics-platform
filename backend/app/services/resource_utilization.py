# backend/app/services/resource_utilization.py (FIXED)

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from supabase import Client
import logging

logger = logging.getLogger(__name__)

def convert_numpy_types(obj):
    """Convert NumPy types to native Python types for JSON serialization"""
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, dict):
        return {key: convert_numpy_types(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_types(item) for item in obj]
    return obj

class ResourceUtilizationService:
    def __init__(self):
        # Utilization thresholds
        self.UNDERUTIL_THRESHOLD = 0.6  # 60% utilization
        self.OVERUTIL_THRESHOLD = 1.3   # 130% utilization
        self.CRITICAL_UNDERUTIL = 0.4   # 40% - critical underutilization
        self.CRITICAL_OVERUTIL = 1.5    # 150% - critical overutilization
        
        # Overbooking thresholds
        self.MAX_ALLOCATION = 100  # 100% total allocation
        self.WARN_ALLOCATION = 90  # 90% allocation warning
        
    def analyze_team_utilization(
        self, 
        db: Client, 
        days_back: int = 14
    ) -> Dict[str, Any]:
        """
        Comprehensive team utilization analysis
        Returns: alerts, utilization metrics, recommendations
        """
        logger.info(f"Analyzing team utilization for last {days_back} days")
        
        start_date = (datetime.now() - timedelta(days=days_back)).date().isoformat()
        
        # Get all active employees
        employees_response = db.table("employees").select("*").eq("is_active", True).execute()
        employees = employees_response.data
        
        if not employees:
            return self._empty_utilization_response(days_back)
        
        # Get daily logs for the period
        logs_response = db.table("daily_logs").select(
            "*, projects(name, risk_level)"
        ).gte("date", start_date).execute()
        logs = logs_response.data
        
        # Get project assignments
        assignments_response = db.table("project_assignments").select(
            "*, projects(name)"
        ).eq("is_active", True).execute()
        assignments = assignments_response.data
        
        # Analyze each employee
        utilization_data = []
        alerts = []
        
        for employee in employees:
            emp_analysis = self._analyze_employee_utilization(
                employee, logs, assignments, days_back, start_date
            )
            
            utilization_data.append(emp_analysis['summary'])
            alerts.extend(emp_analysis['alerts'])
        
        # Calculate aggregate statistics
        summary_stats = self._calculate_utilization_stats(utilization_data)
        
        # Generate rebalancing suggestions
        rebalancing = self._generate_rebalancing_suggestions(utilization_data, assignments)
        
        # Save alerts to database
        self._save_utilization_alerts(db, alerts, days_back)
        
        result = {
            "period_days": int(days_back),
            "total_employees": int(len(employees)),
            "alerts": sorted(alerts, key=lambda x: self._severity_order(x['severity']), reverse=True),
            "utilization_summary": sorted(
                utilization_data, 
                key=lambda x: x['utilization_rate'], 
                reverse=True
            ),
            "summary_stats": summary_stats,
            "rebalancing_suggestions": rebalancing,
            "generated_at": datetime.now().isoformat()
        }
        
        # Convert all NumPy types to native Python types
        return convert_numpy_types(result)
    
    def _analyze_employee_utilization(
        self,
        employee: Dict,
        all_logs: List[Dict],
        all_assignments: List[Dict],
        days_back: int,
        start_date: str
    ) -> Dict[str, Any]:
        """Analyze utilization for a single employee"""
        emp_id = employee['id']
        
        # Filter logs for this employee
        emp_logs = [log for log in all_logs if log['employee_id'] == emp_id]
        emp_assignments = [assign for assign in all_assignments if assign['employee_id'] == emp_id]
        
        # Calculate metrics
        if len(emp_logs) == 0:
            return self._empty_employee_analysis(employee, emp_assignments)
        
        # Convert to DataFrame for easier analysis
        df = pd.DataFrame(emp_logs)
        df['date'] = pd.to_datetime(df['date'])
        
        # Calculate working days
        unique_dates = int(df['date'].nunique())
        working_days = int(np.busday_count(
            pd.to_datetime(start_date).date(),
            datetime.now().date()
        ))
        
        # Calculate hours metrics
        total_hours = float(df['hours_logged'].sum())
        avg_daily_hours = float(total_hours / unique_dates if unique_dates > 0 else 0)
        max_hours_per_day = float(employee['max_hours_per_day'])
        expected_daily_hours = float(self._calculate_expected_hours(emp_assignments, max_hours_per_day))
        
        # Calculate utilization rate
        utilization_rate = float(avg_daily_hours / expected_daily_hours if expected_daily_hours > 0 else 0)
        
        # Calculate allocation metrics
        total_allocation = float(sum(a['allocation_percentage'] for a in emp_assignments))
        
        # Project distribution
        project_distribution = df.groupby('project_id').agg({
            'hours_logged': 'sum',
            'date': 'nunique'
        }).reset_index()
        
        project_details = []
        for _, proj in project_distribution.iterrows():
            proj_logs = [log for log in emp_logs if log['project_id'] == proj['project_id']]
            proj_name = proj_logs[0].get('projects', {}).get('name', 'Unknown') if proj_logs else 'Unknown'
            
            project_details.append({
                'project_id': int(proj['project_id']),
                'project_name': str(proj_name),
                'hours_logged': float(proj['hours_logged']),
                'days_worked': int(proj['date']),
                'avg_daily_hours': float(proj['hours_logged'] / proj['date']) if int(proj['date']) > 0 else 0.0
            })
        
        # Identify issues and create alerts
        alerts = []
        issues = []
        
        # Check underutilization
        if utilization_rate < self.UNDERUTIL_THRESHOLD:
            severity = 'critical' if utilization_rate < self.CRITICAL_UNDERUTIL else 'high' if utilization_rate < 0.5 else 'medium'
            alerts.append({
                'type': 'underutilization',
                'employee_id': int(emp_id),
                'employee_name': str(employee['name']),
                'employee_role': str(employee['role']),
                'severity': str(severity),
                'utilization_rate': float(utilization_rate),
                'avg_daily_hours': float(avg_daily_hours),
                'expected_hours': float(expected_daily_hours),
                'message': f"{employee['name']} is underutilized at {utilization_rate:.1%} ({avg_daily_hours:.1f}h/{expected_daily_hours:.1f}h per day)",
                'recommendation': str(self._get_underutilization_recommendation(utilization_rate, emp_assignments))
            })
            issues.append('underutilized')
        
        # Check overutilization
        elif utilization_rate > self.OVERUTIL_THRESHOLD:
            severity = 'critical' if utilization_rate > self.CRITICAL_OVERUTIL else 'high'
            alerts.append({
                'type': 'overutilization',
                'employee_id': int(emp_id),
                'employee_name': str(employee['name']),
                'employee_role': str(employee['role']),
                'severity': str(severity),
                'utilization_rate': float(utilization_rate),
                'avg_daily_hours': float(avg_daily_hours),
                'expected_hours': float(expected_daily_hours),
                'message': f"{employee['name']} is overworked at {utilization_rate:.1%} ({avg_daily_hours:.1f}h/{expected_daily_hours:.1f}h per day)",
                'recommendation': str(self._get_overutilization_recommendation(utilization_rate, emp_assignments))
            })
            issues.append('overutilized')
        
        # Check overbooking (multiple projects exceeding 100%)
        if total_allocation > 100:
            severity = 'high' if total_allocation > 120 else 'medium'
            alerts.append({
                'type': 'overbooked',
                'employee_id': int(emp_id),
                'employee_name': str(employee['name']),
                'employee_role': str(employee['role']),
                'severity': str(severity),
                'total_allocation': float(total_allocation),
                'num_projects': int(len(emp_assignments)),
                'message': f"{employee['name']} is overbooked at {total_allocation}% across {len(emp_assignments)} projects",
                'recommendation': f"Reduce allocation or redistribute {total_allocation - 100}% to other team members"
            })
            issues.append('overbooked')
        
        # Check inconsistent logging
        logging_consistency = float(unique_dates / working_days if working_days > 0 else 0)
        if logging_consistency < 0.6:
            alerts.append({
                'type': 'inconsistent_logging',
                'employee_id': int(emp_id),
                'employee_name': str(employee['name']),
                'employee_role': str(employee['role']),
                'severity': 'medium',
                'logging_consistency': float(logging_consistency),
                'days_logged': int(unique_dates),
                'expected_days': int(working_days),
                'message': f"{employee['name']} has inconsistent logging: {unique_dates}/{working_days} days",
                'recommendation': "Encourage daily time logging for accurate resource tracking"
            })
            issues.append('inconsistent_logging')
        
        # Build summary
        summary = {
            'employee_id': int(emp_id),
            'employee_name': str(employee['name']),
            'employee_role': str(employee['role']),
            'max_hours_per_day': float(max_hours_per_day),
            'utilization_rate': float(utilization_rate),
            'avg_daily_hours': float(avg_daily_hours),
            'expected_hours': float(expected_daily_hours),
            'total_hours': float(total_hours),
            'days_worked': int(unique_dates),
            'working_days': int(working_days),
            'logging_consistency': float(logging_consistency),
            'total_allocation': float(total_allocation),
            'num_projects': int(len(emp_assignments)),
            'project_distribution': project_details,
            'status': str(self._determine_utilization_status(utilization_rate)),
            'issues': issues,
            'health_score': float(self._calculate_health_score(utilization_rate, logging_consistency, total_allocation))
        }
        
        return {
            'summary': summary,
            'alerts': alerts
        }
    
    def _calculate_expected_hours(self, assignments: List[Dict], max_hours: float) -> float:
        """Calculate expected daily hours based on assignments"""
        if not assignments:
            return max_hours
        
        # Sum up all allocations and calculate expected hours
        total_allocation = sum(a['allocation_percentage'] for a in assignments)
        # Cap at 100% for expected hours calculation
        effective_allocation = min(total_allocation, 100)
        
        return max_hours * (effective_allocation / 100)
    
    def _empty_employee_analysis(self, employee: Dict, assignments: List[Dict]) -> Dict[str, Any]:
        """Return empty analysis for employee with no logs"""
        alerts = [{
            'type': 'no_activity',
            'employee_id': int(employee['id']),
            'employee_name': str(employee['name']),
            'employee_role': str(employee['role']),
            'severity': 'critical',
            'message': f"{employee['name']} has no logged hours in the period",
            'recommendation': "Check if employee is active or has access to time logging system"
        }]
        
        summary = {
            'employee_id': int(employee['id']),
            'employee_name': str(employee['name']),
            'employee_role': str(employee['role']),
            'max_hours_per_day': float(employee['max_hours_per_day']),
            'utilization_rate': 0.0,
            'avg_daily_hours': 0.0,
            'expected_hours': float(employee['max_hours_per_day']),
            'total_hours': 0.0,
            'days_worked': 0,
            'working_days': 0,
            'logging_consistency': 0.0,
            'total_allocation': float(sum(a['allocation_percentage'] for a in assignments)),
            'num_projects': int(len(assignments)),
            'project_distribution': [],
            'status': 'no_activity',
            'issues': ['no_activity'],
            'health_score': 0.0
        }
        
        return {'summary': summary, 'alerts': alerts}
    
    def _determine_utilization_status(self, rate: float) -> str:
        """Determine utilization status"""
        if rate < self.CRITICAL_UNDERUTIL:
            return 'critically_underutilized'
        elif rate < self.UNDERUTIL_THRESHOLD:
            return 'underutilized'
        elif rate > self.CRITICAL_OVERUTIL:
            return 'critically_overutilized'
        elif rate > self.OVERUTIL_THRESHOLD:
            return 'overutilized'
        else:
            return 'optimal'
    
    def _calculate_health_score(self, utilization: float, consistency: float, allocation: float) -> float:
        """Calculate overall health score (0-100)"""
        # Optimal utilization score (peaks at 0.9-1.0)
        if 0.8 <= utilization <= 1.1:
            util_score = 100
        elif utilization < 0.8:
            util_score = max(0, utilization / 0.8 * 100)
        else:
            util_score = max(0, 100 - (utilization - 1.1) * 50)
        
        # Consistency score
        consistency_score = consistency * 100
        
        # Allocation score (penalize over 100%)
        if allocation <= 100:
            alloc_score = 100
        else:
            alloc_score = max(0, 100 - (allocation - 100))
        
        # Weighted average
        health_score = (util_score * 0.5 + consistency_score * 0.3 + alloc_score * 0.2)
        
        return round(health_score, 1)
    
    def _get_underutilization_recommendation(self, rate: float, assignments: List[Dict]) -> str:
        """Get recommendation for underutilized employee"""
        if len(assignments) == 0:
            return "Assign to active projects to improve utilization"
        elif len(assignments) == 1:
            return "Consider assigning to additional projects or increasing current project allocation"
        else:
            return "Review project workload distribution and ensure adequate task assignment"
    
    def _get_overutilization_recommendation(self, rate: float, assignments: List[Dict]) -> str:
        """Get recommendation for overutilized employee"""
        if rate > 1.5:
            return "URGENT: Immediately reduce workload by 30-40% to prevent burnout"
        elif len(assignments) > 2:
            return "Reduce number of concurrent projects or decrease allocation percentages"
        else:
            return "Reassign some tasks to other team members or extend deadlines"
    
    def _calculate_utilization_stats(self, utilization_data: List[Dict]) -> Dict[str, Any]:
        """Calculate aggregate statistics"""
        if not utilization_data:
            return {}
        
        rates = [emp['utilization_rate'] for emp in utilization_data]
        hours = [emp['avg_daily_hours'] for emp in utilization_data]
        
        return {
            'avg_utilization': float(np.mean(rates)),
            'median_utilization': float(np.median(rates)),
            'min_utilization': float(np.min(rates)),
            'max_utilization': float(np.max(rates)),
            'std_utilization': float(np.std(rates)),
            'avg_daily_hours': float(np.mean(hours)),
            'total_team_hours': float(sum(emp['total_hours'] for emp in utilization_data)),
            'underutilized_count': int(len([r for r in rates if r < self.UNDERUTIL_THRESHOLD])),
            'overutilized_count': int(len([r for r in rates if r > self.OVERUTIL_THRESHOLD])),
            'optimal_count': int(len([r for r in rates if self.UNDERUTIL_THRESHOLD <= r <= self.OVERUTIL_THRESHOLD])),
            'critically_underutilized': int(len([r for r in rates if r < self.CRITICAL_UNDERUTIL])),
            'critically_overutilized': int(len([r for r in rates if r > self.CRITICAL_OVERUTIL])),
            'avg_health_score': float(np.mean([emp['health_score'] for emp in utilization_data]))
        }
    
    def _generate_rebalancing_suggestions(
        self, 
        utilization_data: List[Dict],
        assignments: List[Dict]
    ) -> List[Dict[str, Any]]:
        """Generate intelligent rebalancing suggestions"""
        suggestions = []
        
        # Identify underutilized and overutilized employees
        underutilized = [emp for emp in utilization_data 
                        if emp['utilization_rate'] < self.UNDERUTIL_THRESHOLD]
        overutilized = [emp for emp in utilization_data 
                       if emp['utilization_rate'] > self.OVERUTIL_THRESHOLD]
        
        # Match by role for workload transfer
        for over_emp in overutilized:
            for under_emp in underutilized:
                if over_emp['employee_role'] == under_emp['employee_role']:
                    # Calculate potential transfer
                    over_capacity = (over_emp['utilization_rate'] - 1.0) * over_emp['expected_hours']
                    under_capacity = (1.0 - under_emp['utilization_rate']) * under_emp['expected_hours']
                    transfer_hours = min(over_capacity, under_capacity)
                    
                    if transfer_hours > 1.0:  # Only suggest if meaningful
                        # Find common projects
                        over_projects = set(p['project_id'] for p in over_emp['project_distribution'])
                        under_projects = set(p['project_id'] for p in under_emp['project_distribution'])
                        common_projects = over_projects & under_projects
                        
                        suggestion = {
                            'type': 'workload_redistribution',
                            'from_employee': {
                                'id': int(over_emp['employee_id']),
                                'name': str(over_emp['employee_name']),
                                'current_utilization': float(over_emp['utilization_rate'])
                            },
                            'to_employee': {
                                'id': int(under_emp['employee_id']),
                                'name': str(under_emp['employee_name']),
                                'current_utilization': float(under_emp['utilization_rate'])
                            },
                            'role': str(over_emp['employee_role']),
                            'suggested_hours_transfer': float(round(transfer_hours, 1)),
                            'common_projects': int(len(common_projects)),
                            'priority': 'high' if over_emp['utilization_rate'] > 1.5 else 'medium',
                            'expected_impact': {
                                'from_new_utilization': float(round(over_emp['utilization_rate'] - (transfer_hours / over_emp['expected_hours']), 2)),
                                'to_new_utilization': float(round(under_emp['utilization_rate'] + (transfer_hours / under_emp['expected_hours']), 2))
                            }
                        }
                        suggestions.append(suggestion)
        
        # Suggest project reassignment for overbooked employees
        overbooked = [emp for emp in utilization_data if emp['total_allocation'] > 100]
        for emp in overbooked:
            if emp['num_projects'] > 1:
                suggestions.append({
                    'type': 'reduce_concurrent_projects',
                    'employee': {
                        'id': int(emp['employee_id']),
                        'name': str(emp['employee_name']),
                        'total_allocation': float(emp['total_allocation'])
                    },
                    'current_projects': int(emp['num_projects']),
                    'suggested_reduction': int(min(2, emp['num_projects'] - 1)),
                    'priority': 'high' if emp['total_allocation'] > 120 else 'medium',
                    'recommendation': f"Reduce from {emp['num_projects']} to {max(1, emp['num_projects'] - 1)} concurrent projects"
                })
        
        # Suggest new assignments for highly underutilized
        critically_under = [emp for emp in utilization_data 
                           if emp['utilization_rate'] < self.CRITICAL_UNDERUTIL]
        for emp in critically_under:
            suggestions.append({
                'type': 'increase_workload',
                'employee': {
                    'id': int(emp['employee_id']),
                    'name': str(emp['employee_name']),
                    'role': str(emp['employee_role']),
                    'current_utilization': float(emp['utilization_rate'])
                },
                'available_capacity': float(round((1.0 - emp['utilization_rate']) * emp['expected_hours'], 1)),
                'priority': 'high',
                'recommendation': f"Assign additional work to utilize {(1.0 - emp['utilization_rate'])*100:.0f}% available capacity"
            })
        
        # Sort by priority
        priority_order = {'high': 0, 'medium': 1, 'low': 2}
        suggestions.sort(key=lambda x: priority_order.get(x.get('priority', 'low'), 2))
        
        return suggestions
    
    def _severity_order(self, severity: str) -> int:
        """Return numeric order for severity sorting"""
        order = {'critical': 4, 'high': 3, 'medium': 2, 'low': 1}
        return order.get(severity, 0)
    
    def _save_utilization_alerts(self, db: Client, alerts: List[Dict], days_back: int):
        """Save utilization alerts to database"""
        period_end = datetime.now().date()
        period_start = (datetime.now() - timedelta(days=days_back)).date()
        
        saved_count = 0
        for alert in alerts:
            try:
                alert_record = {
                    'employee_id': int(alert['employee_id']),
                    'alert_type': str(alert['type']),
                    'severity': str(alert['severity']),
                    'utilization_rate': float(alert.get('utilization_rate', 0)),
                    'avg_daily_hours': float(alert.get('avg_daily_hours', 0)),
                    'expected_hours': float(alert.get('expected_hours', 0)),
                    'period_start_date': period_start.isoformat(),
                    'period_end_date': period_end.isoformat(),
                    'alert_message': str(alert['message']),
                    'is_acknowledged': False,
                    'created_at': datetime.now().isoformat()
                }
                
                db.table("resource_utilization_alerts").insert(alert_record).execute()
                saved_count += 1
            except Exception as e:
                logger.warning(f"Failed to save utilization alert: {e}")
        
        logger.info(f"Saved {saved_count} utilization alerts to database")
    
    def _empty_utilization_response(self, days_back: int) -> Dict[str, Any]:
        """Return empty response structure"""
        return {
            "period_days": int(days_back),
            "total_employees": 0,
            "alerts": [],
            "utilization_summary": [],
            "summary_stats": {},
            "rebalancing_suggestions": [],
            "generated_at": datetime.now().isoformat(),
            "message": "No employee data available"
        }
    
    def get_employee_utilization_detail(
        self, 
        db: Client, 
        employee_id: int,
        days_back: int = 30
    ) -> Dict[str, Any]:
        """Get detailed utilization analysis for specific employee"""
        start_date = (datetime.now() - timedelta(days=days_back)).date().isoformat()
        
        # Get employee
        employee_response = db.table("employees").select("*").eq("id", employee_id).single().execute()
        employee = employee_response.data
        
        # Get logs
        logs_response = db.table("daily_logs").select(
            "*, projects(name, risk_level)"
        ).eq("employee_id", employee_id).gte("date", start_date).execute()
        logs = logs_response.data
        
        # Get assignments
        assignments_response = db.table("project_assignments").select(
            "*, projects(name)"
        ).eq("employee_id", employee_id).eq("is_active", True).execute()
        assignments = assignments_response.data
        
        # Analyze
        analysis = self._analyze_employee_utilization(
            employee, logs, assignments, days_back, start_date
        )
        
        # Add time series data
        if logs:
            df = pd.DataFrame(logs)
            df['date'] = pd.to_datetime(df['date'])
            df = df.sort_values('date')
            
            time_series = []
            for _, row in df.iterrows():
                time_series.append({
                    'date': row['date'].date().isoformat(),
                    'hours_logged': float(row['hours_logged']),
                    'completion_percentage': float(row.get('completion_percentage', 0)),
                    'issues_reported': int(row.get('issues_reported', 0)),
                    'project_name': str(row.get('projects', {}).get('name', 'Unknown') if row.get('projects') else 'Unknown')
                })
            
            analysis['time_series'] = time_series
        
        return convert_numpy_types(analysis)
    
    def get_rebalancing_suggestions(self, db: Client) -> List[Dict[str, Any]]:
        """Get resource rebalancing suggestions"""
        analysis = self.analyze_team_utilization(db, days_back=14)
        return analysis['rebalancing_suggestions']