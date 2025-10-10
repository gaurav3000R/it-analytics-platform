#backend/app/services/anomaly_detection.py

import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from typing import Dict, List, Any, Optional
import logging
from datetime import datetime, timedelta
from supabase import Client

from app.database import connect_db

logger = logging.getLogger(__name__)

class AnomalyDetectionService:
    def __init__(self):
        self.isolation_forest = IsolationForest(contamination=0.1, random_state=42)
        self.scaler = StandardScaler()

    def detect_daily_log_anomalies(self, db: Client, days_back: int = 30) -> List[Dict[str, Any]]:
        """Detect anomalies in daily logs"""
        logger.info(f"Detecting anomalies in daily logs for last {days_back} days...")

        # Get daily logs from last N days
        start_date = (datetime.now() - timedelta(days=days_back)).isoformat()
        logs_response = db.table("daily_logs").select("*").gte("date", start_date).gt("hours_logged", 0).execute()
        logs = logs_response.data

        if len(logs) < 10:  # Need minimum data for anomaly detection
            logger.warning("Insufficient data for anomaly detection")
            return []

        # Convert to DataFrame
        df = pd.DataFrame([
            {
                'log_id': log['id'],
                'project_id': log['project_id'],
                'employee_id': log['employee_id'],
                'date': pd.to_datetime(log['date']),
                'hours_logged': log['hours_logged'],
                'completion_percentage': log['completion_percentage'],
                'issues_reported': log['issues_reported'],
                'day_of_week': pd.to_datetime(log['date']).weekday(),
                'hour_of_day': pd.to_datetime(log['date']).hour
            }
            for log in logs
        ])

        anomalies = []

        # 1. Detect unusual working hours anomalies
        hours_anomalies = self._detect_hours_anomalies(df, db)
        anomalies.extend(hours_anomalies)

        # 2. Detect missing log patterns
        missing_log_anomalies = self._detect_missing_logs(db, days_back)
        anomalies.extend(missing_log_anomalies)

        # 3. Detect productivity anomalies
        productivity_anomalies = self._detect_productivity_anomalies(df, db)
        anomalies.extend(productivity_anomalies)

        # 4. Detect unusual issue reporting patterns
        issue_anomalies = self._detect_issue_anomalies(df, db)
        anomalies.extend(issue_anomalies)

        # Save detected anomalies to database
        self._save_anomalies(db, anomalies)

        logger.info(f"Detected {len(anomalies)} anomalies")
        return anomalies

    def _detect_hours_anomalies(self, df: pd.DataFrame, db: Client) -> List[Dict[str, Any]]:
        """Detect unusual working hours patterns"""
        anomalies = []

        # Group by employee and analyze their hour patterns
        for employee_id in df['employee_id'].unique():
            employee_df = df[df['employee_id'] == employee_id].copy()

            if len(employee_df) < 5:  # Need minimum data
                continue

            # Calculate employee's typical working pattern
            avg_hours = employee_df['hours_logged'].mean()
            std_hours = employee_df['hours_logged'].std()

            # Detect significant deviations (more than 2 standard deviations)
            threshold_low = max(0, avg_hours - 2 * std_hours)
            threshold_high = avg_hours + 2 * std_hours

            unusual_days = employee_df[
                (employee_df['hours_logged'] < threshold_low) |
                (employee_df['hours_logged'] > threshold_high)
            ]

            for _, row in unusual_days.iterrows():
                severity = 'high' if row['hours_logged'] < 2 or row['hours_logged'] > 12 else 'medium'
                anomaly_type = 'hours_overwork' if row['hours_logged'] > threshold_high else 'hours_underwork'

                anomalies.append({
                    'project_id': int(row['project_id']),
                    'employee_id': int(row['employee_id']),
                    'anomaly_type': anomaly_type,
                    'severity': severity,
                    'description': f"Employee logged {row['hours_logged']:.1f} hours (typical: {avg_hours:.1f}±{std_hours:.1f})",
                    'anomaly_data': {
                        'logged_hours': row['hours_logged'],
                        'typical_hours': avg_hours,
                        'date': row['date'].isoformat()
                    }
                })

        return anomalies

    def _detect_missing_logs(self, db: Client, days_back: int) -> List[Dict[str, Any]]:
        """Detect employees who haven't logged hours recently"""
        anomalies = []

        # Get all active employees
        employees_response = db.table("employees").select("id").eq("is_active", True).execute()
        active_employees = employees_response.data

        start_date = (datetime.now() - timedelta(days=days_back)).isoformat()

        for employee in active_employees:
            # Check if employee has logged any hours in the period
            recent_logs_response = db.table("daily_logs").select("id").eq("employee_id", employee["id"]).gte("date", start_date).execute()
            recent_logs = len(recent_logs_response.data)

            expected_logs = days_back  # Assuming daily logging
            missing_percentage = (expected_logs - recent_logs) / expected_logs

            if missing_percentage > 0.3:  # More than 30% missing logs
                severity = 'critical' if missing_percentage > 0.7 else 'high'

                anomalies.append({
                    'project_id': None,
                    'employee_id': employee["id"],
                    'anomaly_type': 'missing_logs',
                    'severity': severity,
                    'description': f"Employee missing {missing_percentage*100:.1f}% of expected log entries",
                    'anomaly_data': {
                        'missing_percentage': missing_percentage,
                        'expected_logs': expected_logs,
                        'actual_logs': recent_logs,
                        'period_days': days_back
                    }
                })

        return anomalies

    def _detect_productivity_anomalies(self, df: pd.DataFrame, db: Client) -> List[Dict[str, Any]]:
        """Detect productivity anomalies using isolation forest"""
        anomalies = []

        # Prepare features for anomaly detection
        features = df[['hours_logged', 'completion_percentage', 'issues_reported']].fillna(0)

        if len(features) < 10:
            return anomalies

        # Scale features
        features_scaled = self.scaler.fit_transform(features)

        # Detect anomalies
        outlier_labels = self.isolation_forest.fit_predict(features_scaled)
        anomaly_scores = self.isolation_forest.score_samples(features_scaled)

        # Mark outliers
        df['is_anomaly'] = outlier_labels == -1
        df['anomaly_score'] = anomaly_scores

        # Process detected anomalies
        anomalous_logs = df[df['is_anomaly']].copy()

        for _, row in anomalous_logs.iterrows():
            # Determine severity based on anomaly score
            score = abs(row['anomaly_score'])
            if score > 0.6:
                severity = 'critical'
            elif score > 0.4:
                severity = 'high'
            else:
                severity = 'medium'

            # Determine specific anomaly type
            anomaly_type = self._classify_productivity_anomaly(row)

            anomalies.append({
                'project_id': int(row['project_id']),
                'employee_id': int(row['employee_id']),
                'anomaly_type': anomaly_type,
                'severity': severity,
                'description': f"Unusual productivity pattern detected (score: {score:.3f})",
                'anomaly_data': {
                    'anomaly_score': score,
                    'hours_logged': row['hours_logged'],
                    'completion_percentage': row['completion_percentage'],
                    'issues_reported': row['issues_reported'],
                    'date': row['date'].isoformat()
                }
            })

        return anomalies

    def _classify_productivity_anomaly(self, row: pd.Series) -> str:
        """Classify the type of productivity anomaly"""
        if row['hours_logged'] > 10 and row['completion_percentage'] < 30:
            return 'low_efficiency'
        elif row['hours_logged'] < 4 and row['completion_percentage'] > 80:
            return 'suspiciously_high_productivity'
        elif row['issues_reported'] > 5:
            return 'high_issue_rate'
        else:
            return 'general_productivity_anomaly'

    def _detect_issue_anomalies(self, df: pd.DataFrame, db: Client) -> List[Dict[str, Any]]:
        """Detect unusual patterns in issue reporting"""
        anomalies = []

        # Analyze issue patterns by project
        for project_id in df['project_id'].unique():
            project_df = df[df['project_id'] == project_id].copy()

            if len(project_df) < 5:
                continue

            # Calculate daily issue rate
            daily_issues = project_df.groupby(project_df['date'].dt.date)['issues_reported'].sum()

            # Detect spikes in issue reporting
            mean_issues = daily_issues.mean()
            std_issues = daily_issues.std()

            if std_issues == 0:  # No variation
                continue

            threshold = mean_issues + 2 * std_issues

            spike_days = daily_issues[daily_issues > threshold]

            for date, issue_count in spike_days.items():
                anomalies.append({
                    'project_id': int(project_id),
                    'employee_id': None,
                    'anomaly_type': 'issue_spike',
                    'severity': 'high' if issue_count > threshold * 1.5 else 'medium',
                    'description': f"Unusual spike in issues reported: {issue_count} (typical: {mean_issues:.1f})",
                    'anomaly_data': {
                        'issue_count': int(issue_count),
                        'typical_count': mean_issues,
                        'date': date.isoformat()
                    }
                })

        return anomalies

    def _save_anomalies(self, db: Client, anomalies: List[Dict[str, Any]]):
        """Save detected anomalies to database"""
        current_date = datetime.now().date().isoformat()
        for anomaly_data in anomalies:
            # Check if similar anomaly already exists (avoid duplicates)
            query = db.table("anomalies").select("id").eq("anomaly_type", anomaly_data['anomaly_type'])
            if anomaly_data.get('project_id'):
                query = query.eq("project_id", anomaly_data['project_id'])
            if anomaly_data.get('employee_id'):
                query = query.eq("employee_id", anomaly_data['employee_id'])
            query = query.filter("detected_at", "gte", current_date)
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

    def get_project_anomaly_summary(self, db: Client, project_id: int, days_back: int = 7) -> Dict[str, Any]:
        """Get anomaly summary for a specific project"""
        start_date = (datetime.now() - timedelta(days=days_back)).isoformat()
        anomalies_response = db.table("anomalies").select("*").eq("project_id", project_id).gte("detected_at", start_date).execute()
        anomalies = anomalies_response.data

        # Group by severity and type
        summary = {
            'total_anomalies': len(anomalies),
            'by_severity': {},
            'by_type': {},
            'recent_anomalies': []
        }

        for anomaly in anomalies:
            # Count by severity
            summary['by_severity'][anomaly['severity']] = summary['by_severity'].get(anomaly['severity'], 0) + 1

            # Count by type
            summary['by_type'][anomaly['anomaly_type']] = summary['by_type'].get(anomaly['anomaly_type'], 0) + 1

            # Add to recent list
            summary['recent_anomalies'].append({
                'id': anomaly['id'],
                'type': anomaly['anomaly_type'],
                'severity': anomaly['severity'],
                'description': anomaly['description'],
                'detected_at': anomaly['detected_at'],
                'is_resolved': anomaly['is_resolved']
            })

        # Sort recent anomalies by detection time
        summary['recent_anomalies'] = sorted(
            summary['recent_anomalies'],
            key=lambda x: x['detected_at'],
            reverse=True
        )[:10]  # Top 10 most recent

        return summary