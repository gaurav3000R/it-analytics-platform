# backend/app/services/anomaly_detection.py

import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from typing import Dict, List, Any, Optional, Tuple
import logging
from datetime import datetime, timedelta
from supabase import Client
from collections import defaultdict

logger = logging.getLogger(__name__)

class AnomalyDetectionService:
    def __init__(self):
        self.isolation_forest = IsolationForest(
            contamination=0.15,
            random_state=42,
            n_estimators=100
        )
        self.scaler = StandardScaler()
        
        # Thresholds for different anomaly types
        self.MISSING_LOG_THRESHOLD = 0.3  # 30% missing logs
        self.HOURS_DEVIATION_FACTOR = 2.5  # Standard deviations
        self.CONSISTENCY_THRESHOLD = 0.6  # 60% logging consistency
        self.WEEKEND_WORK_THRESHOLD = 0.2  # 20% weekend work is unusual

    def detect_daily_log_anomalies(
        self, 
        db: Client, 
        days_back: int = 30,
        project_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Comprehensive anomaly detection in daily logs
        Detects: missing logs, unusual hours, productivity issues, inconsistent patterns
        """
        logger.info(f"Detecting anomalies in daily logs for last {days_back} days...")
        
        # Get daily logs
        start_date = (datetime.now() - timedelta(days=days_back)).date().isoformat()
        
        query = db.table("daily_logs").select(
            "*, projects(name, risk_level), employees(name, role, max_hours_per_day)"
        ).gte("date", start_date)
        
        if project_id:
            query = query.eq("project_id", project_id)
        
        logs_response = query.execute()
        logs = logs_response.data
        
        if len(logs) < 10:
            logger.warning("Insufficient data for anomaly detection")
            return []
        
        # Convert to DataFrame
        df = self._prepare_logs_dataframe(logs)
        
        # Get all employees and projects for context
        employees = self._get_all_employees(db)
        projects = self._get_all_projects(db)
        
        anomalies = []
        
        # 1. Detect missing logs
        missing_anomalies = self._detect_missing_logs_enhanced(
            db, df, employees, days_back
        )
        anomalies.extend(missing_anomalies)
        
        # 2. Detect unusual working hours
        hours_anomalies = self._detect_hours_anomalies_enhanced(df, employees)
        anomalies.extend(hours_anomalies)
        
        # 3. Detect productivity anomalies using ML
        productivity_anomalies = self._detect_productivity_anomalies_ml(df)
        anomalies.extend(productivity_anomalies)
        
        # 4. Detect inconsistent logging patterns
        consistency_anomalies = self._detect_logging_consistency(df, employees, days_back)
        anomalies.extend(consistency_anomalies)
        
        # 5. Detect unusual weekend work patterns
        weekend_anomalies = self._detect_weekend_anomalies(df, employees)
        anomalies.extend(weekend_anomalies)
        
        # 6. Detect sudden pattern changes
        pattern_anomalies = self._detect_pattern_changes(df, employees)
        anomalies.extend(pattern_anomalies)
        
        # 7. Detect project-specific anomalies
        project_anomalies = self._detect_project_anomalies(df, projects)
        anomalies.extend(project_anomalies)
        
        # Save anomalies to database
        self._save_anomalies(db, anomalies)
        
        # Update anomaly summaries
        self._update_anomaly_summaries(db, anomalies)
        
        logger.info(f"Detected {len(anomalies)} anomalies across {len(set(a.get('employee_id') for a in anomalies if a.get('employee_id')))} employees")
        
        return anomalies

    def _prepare_logs_dataframe(self, logs: List[Dict]) -> pd.DataFrame:
        """Prepare logs data for analysis"""
        df_data = []
        
        for log in logs:
            df_data.append({
                'log_id': log['id'],
                'project_id': log['project_id'],
                'employee_id': log['employee_id'],
                'date': pd.to_datetime(log['date']),
                'hours_logged': log['hours_logged'],
                'completion_percentage': log.get('completion_percentage', 0),
                'issues_reported': log.get('issues_reported', 0),
                'bugs_found': log.get('bugs_found', 0),
                'story_points': log.get('story_points_completed', 0),
                'project_name': log.get('projects', {}).get('name', 'Unknown') if log.get('projects') else 'Unknown',
                'project_risk': log.get('projects', {}).get('risk_level', 'Unknown') if log.get('projects') else 'Unknown',
                'employee_name': log.get('employees', {}).get('name', 'Unknown') if log.get('employees') else 'Unknown',
                'employee_role': log.get('employees', {}).get('role', 'Unknown') if log.get('employees') else 'Unknown',
                'employee_max_hours': log.get('employees', {}).get('max_hours_per_day', 8) if log.get('employees') else 8
            })
        
        df = pd.DataFrame(df_data)
        df['day_of_week'] = df['date'].dt.dayofweek
        df['is_weekend'] = df['day_of_week'].isin([5, 6])
        df['week_number'] = df['date'].dt.isocalendar().week
        df['month'] = df['date'].dt.month
        
        return df

    def _get_all_employees(self, db: Client) -> List[Dict]:
        """Get all active employees"""
        response = db.table("employees").select("*").eq("is_active", True).execute()
        return response.data

    def _get_all_projects(self, db: Client) -> List[Dict]:
        """Get all projects"""
        response = db.table("projects").select("id, name, risk_level").execute()
        return response.data

    def _detect_missing_logs_enhanced(
        self, 
        db: Client,
        df: pd.DataFrame, 
        employees: List[Dict], 
        days_back: int
    ) -> List[Dict[str, Any]]:
        """Detect employees with missing or inconsistent log entries"""
        anomalies = []
        
        start_date = datetime.now() - timedelta(days=days_back)
        working_days = np.busday_count(
            start_date.date(),
            datetime.now().date()
        )
        
        for employee in employees:
            emp_id = employee['id']
            emp_logs = df[df['employee_id'] == emp_id]
            
            # Count unique logging days
            unique_days = emp_logs['date'].nunique()
            
            # Calculate expected logs (accounting for weekends)
            expected_logs = working_days
            missing_percentage = (expected_logs - unique_days) / expected_logs if expected_logs > 0 else 0
            
            if missing_percentage > self.MISSING_LOG_THRESHOLD:
                severity = 'critical' if missing_percentage > 0.7 else 'high' if missing_percentage > 0.5 else 'medium'
                
                # Check if employee has recent activity
                recent_logs = emp_logs[emp_logs['date'] >= (datetime.now() - timedelta(days=7))]
                days_since_last_log = (datetime.now() - emp_logs['date'].max()).days if len(emp_logs) > 0 else days_back
                
                anomalies.append({
                    'project_id': None,
                    'employee_id': emp_id,
                    'anomaly_type': 'missing_logs',
                    'severity': severity,
                    'description': f"{employee['name']} missing {missing_percentage*100:.1f}% of expected logs ({unique_days}/{expected_logs} days)",
                    'anomaly_data': {
                        'employee_name': employee['name'],
                        'employee_role': employee['role'],
                        'missing_percentage': float(missing_percentage),
                        'expected_logs': int(expected_logs),
                        'actual_logs': int(unique_days),
                        'days_since_last_log': int(days_since_last_log),
                        'period_days': days_back,
                        'recent_activity': len(recent_logs) > 0
                    }
                })
        
        return anomalies

    def _detect_hours_anomalies_enhanced(
        self, 
        df: pd.DataFrame, 
        employees: List[Dict]
    ) -> List[Dict[str, Any]]:
        """Detect unusual working hours patterns with context"""
        anomalies = []
        
        for employee in employees:
            emp_id = employee['id']
            emp_logs = df[df['employee_id'] == emp_id].copy()
            
            if len(emp_logs) < 5:
                continue
            
            # Calculate employee's typical pattern
            avg_hours = emp_logs['hours_logged'].mean()
            std_hours = emp_logs['hours_logged'].std()
            max_allowed = employee.get('max_hours_per_day', 8)
            
            if std_hours == 0 or pd.isna(std_hours):
                continue
            
            # Detect significant deviations
            threshold_low = max(0, avg_hours - self.HOURS_DEVIATION_FACTOR * std_hours)
            threshold_high = avg_hours + self.HOURS_DEVIATION_FACTOR * std_hours
            
            unusual_days = emp_logs[
                (emp_logs['hours_logged'] < threshold_low) |
                (emp_logs['hours_logged'] > threshold_high)
            ]
            
            # Focus on most recent unusual days
            recent_unusual = unusual_days.nlargest(5, 'date')
            
            for _, row in recent_unusual.iterrows():
                hours = row['hours_logged']
                
                # Determine anomaly type and severity
                if hours > max_allowed * 1.5:
                    anomaly_type = 'extreme_overwork'
                    severity = 'critical'
                elif hours > threshold_high:
                    anomaly_type = 'hours_overwork'
                    severity = 'high' if hours > max_allowed * 1.2 else 'medium'
                elif hours < 2:
                    anomaly_type = 'minimal_hours'
                    severity = 'high'
                else:
                    anomaly_type = 'hours_underwork'
                    severity = 'medium'
                
                anomalies.append({
                    'project_id': int(row['project_id']),
                    'employee_id': emp_id,
                    'anomaly_type': anomaly_type,
                    'severity': severity,
                    'description': f"{employee['name']} logged {hours:.1f} hours on {row['date'].date()} (typical: {avg_hours:.1f}±{std_hours:.1f})",
                    'anomaly_data': {
                        'employee_name': employee['name'],
                        'employee_role': employee['role'],
                        'logged_hours': float(hours),
                        'typical_hours': float(avg_hours),
                        'std_deviation': float(std_hours),
                        'max_allowed_hours': float(max_allowed),
                        'date': row['date'].date().isoformat(),
                        'project_name': row['project_name'],
                        'deviation_factor': float(abs(hours - avg_hours) / std_hours) if std_hours > 0 else 0
                    }
                })
        
        return anomalies

    def _detect_productivity_anomalies_ml(self, df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Use ML to detect unusual productivity patterns"""
        anomalies = []
        
        if len(df) < 20:
            return anomalies
        
        # Prepare features for anomaly detection
        feature_cols = ['hours_logged', 'completion_percentage', 'issues_reported', 'story_points']
        features = df[feature_cols].fillna(0)
        
        # Add derived features
        features['efficiency'] = features['completion_percentage'] / (features['hours_logged'] + 1)
        features['issue_rate'] = features['issues_reported'] / (features['hours_logged'] + 1)
        
        try:
            # Scale features
            features_scaled = self.scaler.fit_transform(features)
            
            # Detect anomalies
            outlier_labels = self.isolation_forest.fit_predict(features_scaled)
            anomaly_scores = self.isolation_forest.score_samples(features_scaled)
            
            # Add to dataframe
            df['is_anomaly'] = outlier_labels == -1
            df['anomaly_score'] = -anomaly_scores  # Convert to positive score
            
            # Process detected anomalies (top anomalies only)
            anomalous_logs = df[df['is_anomaly']].nlargest(20, 'anomaly_score')
            
            for _, row in anomalous_logs.iterrows():
                score = row['anomaly_score']
                
                # Determine severity
                if score > 0.6:
                    severity = 'critical'
                elif score > 0.45:
                    severity = 'high'
                else:
                    severity = 'medium'
                
                # Classify specific anomaly type
                anomaly_type = self._classify_productivity_anomaly(row)
                
                anomalies.append({
                    'project_id': int(row['project_id']),
                    'employee_id': int(row['employee_id']),
                    'anomaly_type': anomaly_type,
                    'severity': severity,
                    'description': f"{row['employee_name']}: {anomaly_type.replace('_', ' ').title()} detected (score: {score:.2f})",
                    'anomaly_data': {
                        'employee_name': row['employee_name'],
                        'employee_role': row['employee_role'],
                        'project_name': row['project_name'],
                        'anomaly_score': float(score),
                        'hours_logged': float(row['hours_logged']),
                        'completion_percentage': float(row['completion_percentage']),
                        'issues_reported': int(row['issues_reported']),
                        'story_points': float(row['story_points']),
                        'date': row['date'].date().isoformat(),
                        'efficiency': float(row['completion_percentage'] / (row['hours_logged'] + 1))
                    }
                })
        
        except Exception as e:
            logger.error(f"ML anomaly detection failed: {e}")
        
        return anomalies

    def _classify_productivity_anomaly(self, row: pd.Series) -> str:
        """Classify specific type of productivity anomaly"""
        hours = row['hours_logged']
        completion = row['completion_percentage']
        issues = row['issues_reported']
        
        if hours > 10 and completion < 30:
            return 'low_efficiency'
        elif hours < 4 and completion > 80:
            return 'suspiciously_high_productivity'
        elif issues > 5:
            return 'high_issue_rate'
        elif hours > 8 and issues > 3:
            return 'quality_concerns'
        elif completion < 20:
            return 'low_progress'
        else:
            return 'unusual_productivity_pattern'

    def _detect_logging_consistency(
        self, 
        df: pd.DataFrame, 
        employees: List[Dict],
        days_back: int
    ) -> List[Dict[str, Any]]:
        """Detect inconsistent logging patterns"""
        anomalies = []
        
        for employee in employees:
            emp_id = employee['id']
            emp_logs = df[df['employee_id'] == emp_id].copy()
            
            if len(emp_logs) < 5:
                continue
            
            # Calculate weekly consistency
            emp_logs['week'] = emp_logs['date'].dt.isocalendar().week
            weekly_logs = emp_logs.groupby('week').size()
            
            # Expected logs per week (5 working days)
            expected_weekly = 5
            consistency_rate = (weekly_logs >= expected_weekly * self.CONSISTENCY_THRESHOLD).sum() / len(weekly_logs)
            
            if consistency_rate < self.CONSISTENCY_THRESHOLD:
                # Calculate gaps between logs
                emp_logs_sorted = emp_logs.sort_values('date')
                date_diffs = emp_logs_sorted['date'].diff().dt.days
                max_gap = date_diffs.max() if len(date_diffs) > 0 else 0
                avg_gap = date_diffs.mean() if len(date_diffs) > 0 else 0
                
                severity = 'high' if consistency_rate < 0.4 else 'medium'
                
                anomalies.append({
                    'project_id': None,
                    'employee_id': emp_id,
                    'anomaly_type': 'inconsistent_logging',
                    'severity': severity,
                    'description': f"{employee['name']} has inconsistent logging pattern ({consistency_rate*100:.1f}% consistency)",
                    'anomaly_data': {
                        'employee_name': employee['name'],
                        'employee_role': employee['role'],
                        'consistency_rate': float(consistency_rate),
                        'max_gap_days': float(max_gap) if not pd.isna(max_gap) else 0,
                        'avg_gap_days': float(avg_gap) if not pd.isna(avg_gap) else 0,
                        'total_weeks': int(len(weekly_logs)),
                        'weeks_below_threshold': int((weekly_logs < expected_weekly * self.CONSISTENCY_THRESHOLD).sum())
                    }
                })
        
        return anomalies

    def _detect_weekend_anomalies(
        self, 
        df: pd.DataFrame, 
        employees: List[Dict]
    ) -> List[Dict[str, Any]]:
        """Detect unusual weekend work patterns"""
        anomalies = []
        
        weekend_logs = df[df['is_weekend'] == True]
        
        if len(weekend_logs) == 0:
            return anomalies
        
        for employee in employees:
            emp_id = employee['id']
            emp_weekend_logs = weekend_logs[weekend_logs['employee_id'] == emp_id]
            emp_all_logs = df[df['employee_id'] == emp_id]
            
            if len(emp_all_logs) == 0:
                continue
            
            weekend_work_ratio = len(emp_weekend_logs) / len(emp_all_logs)
            
            if weekend_work_ratio > self.WEEKEND_WORK_THRESHOLD:
                total_weekend_hours = emp_weekend_logs['hours_logged'].sum()
                avg_weekend_hours = emp_weekend_logs['hours_logged'].mean()
                
                severity = 'high' if weekend_work_ratio > 0.3 else 'medium'
                
                anomalies.append({
                    'project_id': None,
                    'employee_id': emp_id,
                    'anomaly_type': 'excessive_weekend_work',
                    'severity': severity,
                    'description': f"{employee['name']} working {weekend_work_ratio*100:.1f}% of time on weekends",
                    'anomaly_data': {
                        'employee_name': employee['name'],
                        'employee_role': employee['role'],
                        'weekend_work_ratio': float(weekend_work_ratio),
                        'total_weekend_hours': float(total_weekend_hours),
                        'avg_weekend_hours': float(avg_weekend_hours),
                        'weekend_days_worked': int(len(emp_weekend_logs)),
                        'total_days_worked': int(len(emp_all_logs))
                    }
                })
        
        return anomalies

    def _detect_pattern_changes(
        self, 
        df: pd.DataFrame, 
        employees: List[Dict]
    ) -> List[Dict[str, Any]]:
        """Detect sudden changes in work patterns"""
        anomalies = []
        
        for employee in employees:
            emp_id = employee['id']
            emp_logs = df[df['employee_id'] == emp_id].copy()
            
            if len(emp_logs) < 14:  # Need at least 2 weeks
                continue
            
            # Sort by date
            emp_logs = emp_logs.sort_values('date')
            
            # Split into recent and historical
            split_point = len(emp_logs) // 2
            historical = emp_logs.iloc[:split_point]
            recent = emp_logs.iloc[split_point:]
            
            # Compare patterns
            hist_avg_hours = historical['hours_logged'].mean()
            recent_avg_hours = recent['hours_logged'].mean()
            
            hist_avg_completion = historical['completion_percentage'].mean()
            recent_avg_completion = recent['completion_percentage'].mean()
            
            # Detect significant changes
            hours_change = abs(recent_avg_hours - hist_avg_hours) / hist_avg_hours if hist_avg_hours > 0 else 0
            completion_change = abs(recent_avg_completion - hist_avg_completion) / hist_avg_completion if hist_avg_completion > 0 else 0
            
            if hours_change > 0.4 or completion_change > 0.4:
                severity = 'high' if hours_change > 0.6 or completion_change > 0.6 else 'medium'
                
                anomalies.append({
                    'project_id': None,
                    'employee_id': emp_id,
                    'anomaly_type': 'sudden_pattern_change',
                    'severity': severity,
                    'description': f"{employee['name']} work pattern changed significantly: hours {hours_change*100:.1f}%, completion {completion_change*100:.1f}%",
                    'anomaly_data': {
                        'employee_name': employee['name'],
                        'employee_role': employee['role'],
                        'historical_avg_hours': float(hist_avg_hours),
                        'recent_avg_hours': float(recent_avg_hours),
                        'hours_change_percentage': float(hours_change * 100),
                        'historical_avg_completion': float(hist_avg_completion),
                        'recent_avg_completion': float(recent_avg_completion),
                        'completion_change_percentage': float(completion_change * 100)
                    }
                })
        
        return anomalies

    def _detect_project_anomalies(
        self, 
        df: pd.DataFrame, 
        projects: List[Dict]
    ) -> List[Dict[str, Any]]:
        """Detect project-specific anomalies"""
        anomalies = []
        
        for project in projects:
            proj_id = project['id']
            proj_logs = df[df['project_id'] == proj_id]
            
            if len(proj_logs) < 5:
                continue
            
            # Detect issue spikes
            daily_issues = proj_logs.groupby(proj_logs['date'].dt.date)['issues_reported'].sum()
            
            if len(daily_issues) < 2:
                continue
            
            mean_issues = daily_issues.mean()
            std_issues = daily_issues.std()
            
            if std_issues == 0 or pd.isna(std_issues):
                continue
            
            threshold = mean_issues + 2 * std_issues
            spike_days = daily_issues[daily_issues > threshold]
            
            if len(spike_days) > 0:
                for date, issue_count in spike_days.items():
                    severity = 'critical' if issue_count > threshold * 1.5 else 'high'
                    
                    anomalies.append({
                        'project_id': proj_id,
                        'employee_id': None,
                        'anomaly_type': 'project_issue_spike',
                        'severity': severity,
                        'description': f"Project {project['name']}: Issue spike on {date} - {issue_count} issues (typical: {mean_issues:.1f})",
                        'anomaly_data': {
                            'project_name': project['name'],
                            'project_risk_level': project.get('risk_level', 'Unknown'),
                            'issue_count': int(issue_count),
                            'typical_count': float(mean_issues),
                            'threshold': float(threshold),
                            'date': date.isoformat()
                        }
                    })
        
        return anomalies

    def _save_anomalies(self, db: Client, anomalies: List[Dict[str, Any]]):
        """Save detected anomalies to database"""
        current_date = datetime.now().date().isoformat()
        saved_count = 0
        
        for anomaly_data in anomalies:
            try:
                # Check for duplicate
                query = db.table("anomalies").select("id").eq(
                    "anomaly_type", anomaly_data['anomaly_type']
                )
                
                if anomaly_data.get('project_id'):
                    query = query.eq("project_id", anomaly_data['project_id'])
                if anomaly_data.get('employee_id'):
                    query = query.eq("employee_id", anomaly_data['employee_id'])
                
                query = query.gte("detected_at", current_date)
                existing = query.execute()
                
                if not existing.data:
                    anomaly = {
                        "project_id": anomaly_data.get('project_id'),
                        "employee_id": anomaly_data.get('employee_id'),
                        "anomaly_type": anomaly_data['anomaly_type'],
                        "severity": anomaly_data['severity'],
                        "description": anomaly_data['description'],
                        "anomaly_data": anomaly_data['anomaly_data'],
                        "detected_at": datetime.now().isoformat(),
                        "is_resolved": False
                    }
                    db.table("anomalies").insert(anomaly).execute()
                    saved_count += 1
            except Exception as e:
                logger.warning(f"Failed to save anomaly: {e}")
        
        logger.info(f"Saved {saved_count} new anomalies to database")

    def _update_anomaly_summaries(self, db: Client, anomalies: List[Dict[str, Any]]):
        """Update anomaly summary table for quick dashboard access"""
        try:
            summary_date = datetime.now().date().isoformat()
            
            # Group by employee
            employee_summaries = defaultdict(lambda: {'critical': 0, 'high': 0, 'medium': 0, 'low': 0, 'types': []})
            
            for anomaly in anomalies:
                emp_id = anomaly.get('employee_id')
                if emp_id:
                    severity = anomaly['severity']
                    employee_summaries[emp_id][severity] += 1
                    employee_summaries[emp_id]['types'].append(anomaly['anomaly_type'])
            
            # Save summaries
            for emp_id, summary in employee_summaries.items():
                total = sum([summary['critical'], summary['high'], summary['medium'], summary['low']])
                
                summary_record = {
                    'employee_id': emp_id,
                    'summary_date': summary_date,
                    'total_anomalies': total,
                    'critical_count': summary['critical'],
                    'high_count': summary['high'],
                    'medium_count': summary['medium'],
                    'low_count': summary['low'],
                    'anomaly_types': list(set(summary['types'])),
                    'updated_at': datetime.now().isoformat()
                }
                
                # Upsert
                db.table("anomaly_summary").upsert(summary_record).execute()
        
        except Exception as e:
            logger.error(f"Failed to update anomaly summaries: {e}")

    def get_project_anomaly_summary(
        self, 
        db: Client, 
        project_id: int, 
        days_back: int = 7
    ) -> Dict[str, Any]:
        """Get anomaly summary for a specific project"""
        start_date = (datetime.now() - timedelta(days=days_back)).date().isoformat()
        
        anomalies_response = db.table("anomalies").select(
            "*"
        ).eq("project_id", project_id).gte("detected_at", start_date).execute()
        
        anomalies = anomalies_response.data
        
        summary = {
            'project_id': project_id,
            'period_days': days_back,
            'total_anomalies': len(anomalies),
            'by_severity': {'critical': 0, 'high': 0, 'medium': 0, 'low': 0},
            'by_type': {},
            'recent_anomalies': [],
            'affected_employees': set()
        }
        
        for anomaly in anomalies:
            # Count by severity
            severity = anomaly.get('severity', 'medium')
            summary['by_severity'][severity] = summary['by_severity'].get(severity, 0) + 1
            
            # Count by type
            anom_type = anomaly['anomaly_type']
            summary['by_type'][anom_type] = summary['by_type'].get(anom_type, 0) + 1
            
            # Track affected employees
            if anomaly.get('employee_id'):
                summary['affected_employees'].add(anomaly['employee_id'])
            
            # Add to recent list
            summary['recent_anomalies'].append({
                'id': anomaly['id'],
                'type': anom_type,
                'severity': severity,
                'description': anomaly['description'],
                'detected_at': anomaly['detected_at'],
                'is_resolved': anomaly['is_resolved'],
                'anomaly_data': anomaly.get('anomaly_data', {})
            })
        
        # Convert set to count
        summary['affected_employees'] = len(summary['affected_employees'])
        
        # Sort recent anomalies
        summary['recent_anomalies'] = sorted(
            summary['recent_anomalies'],
            key=lambda x: x['detected_at'],
            reverse=True
        )[:10]
        
        return summary

    def get_employee_anomaly_summary(
        self, 
        db: Client, 
        employee_id: int, 
        days_back: int = 30
    ) -> Dict[str, Any]:
        """Get anomaly summary for a specific employee"""
        start_date = (datetime.now() - timedelta(days=days_back)).date().isoformat()
        
        anomalies_response = db.table("anomalies").select(
            "*"
        ).eq("employee_id", employee_id).gte("detected_at", start_date).execute()
        
        anomalies = anomalies_response.data
        
        # Get employee info
        employee_response = db.table("employees").select("*").eq("id", employee_id).single().execute()
        employee = employee_response.data
        
        summary = {
            'employee_id': employee_id,
            'employee_name': employee.get('name', 'Unknown'),
            'employee_role': employee.get('role', 'Unknown'),
            'period_days': days_back,
            'total_anomalies': len(anomalies),
            'by_severity': {'critical': 0, 'high': 0, 'medium': 0, 'low': 0},
            'by_type': {},
            'recent_anomalies': [],
            'trends': {}
        }
        
        for anomaly in anomalies:
            severity = anomaly.get('severity', 'medium')
            summary['by_severity'][severity] = summary['by_severity'].get(severity, 0) + 1
            
            anom_type = anomaly['anomaly_type']
            summary['by_type'][anom_type] = summary['by_type'].get(anom_type, 0) + 1
            
            summary['recent_anomalies'].append({
                'id': anomaly['id'],
                'type': anom_type,
                'severity': severity,
                'description': anomaly['description'],
                'detected_at': anomaly['detected_at'],
                'is_resolved': anomaly['is_resolved'],
                'project_id': anomaly.get('project_id'),
                'anomaly_data': anomaly.get('anomaly_data', {})
            })
        
        # Calculate trends
        if len(anomalies) > 0:
            # Group by week
            anomaly_dates = pd.to_datetime([a['detected_at'] for a in anomalies])
            weekly_counts = anomaly_dates.groupby(anomaly_dates.dt.isocalendar().week).size()
            
            summary['trends'] = {
                'weekly_average': float(weekly_counts.mean()) if len(weekly_counts) > 0 else 0,
                'trend_direction': 'increasing' if len(weekly_counts) > 1 and weekly_counts.iloc[-1] > weekly_counts.iloc[0] else 'stable'
            }
        
        # Sort recent anomalies
        summary['recent_anomalies'] = sorted(
            summary['recent_anomalies'],
            key=lambda x: x['detected_at'],
            reverse=True
        )[:15]
        
        return summary