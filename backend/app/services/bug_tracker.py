# backend/app/services/bug_tracker.py

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from collections import defaultdict
from supabase import Client
import logging

logger = logging.getLogger(__name__)

class BugTrackerService:
    def __init__(self):
        # Thresholds for quality risk detection
        self.critical_reopen_threshold = 3
        self.quality_risk_threshold = 0.15  # 15% bug rate
        self.high_severity_threshold = 0.25  # 25% high/critical bugs
        self.slow_resolution_threshold = 72  # 72 hours
        
    def analyze_bug_patterns(
        self, 
        db: Client, 
        project_id: Optional[int] = None, 
        days_back: int = 30
    ) -> Dict[str, Any]:
        """
        Comprehensive bug pattern analysis
        """
        logger.info(f"Analyzing bug patterns for project {project_id or 'ALL'}, last {days_back} days")
        
        start_date = (datetime.now() - timedelta(days=days_back)).isoformat()
        
        # Get bugs
        query = db.table("bugs").select("*")
        if project_id:
            query = query.eq("project_id", project_id)
        query = query.gte("reported_at", start_date)
        
        bugs_response = query.execute()
        bugs = bugs_response.data
        
        if not bugs:
            return {
                "message": "No bugs found for analysis",
                "period_days": days_back,
                "total_bugs": 0
            }
        
        # Convert to DataFrame for analysis
        df = pd.DataFrame(bugs)
        
        # Perform analyses
        frequency_analysis = self._analyze_frequency_patterns(df, days_back)
        severity_analysis = self._analyze_severity_distribution(df)
        resolution_analysis = self._analyze_resolution_metrics(df)
        reopen_analysis = self._analyze_reopen_patterns(df)
        quality_risks = self._identify_quality_risks(df, frequency_analysis, resolution_analysis)
        trend_analysis = self._analyze_trends(df, days_back)
        team_analysis = self._analyze_team_performance(df)
        
        return {
            "period_days": days_back,
            "total_bugs": len(bugs),
            "frequency_patterns": frequency_analysis,
            "severity_distribution": severity_analysis,
            "resolution_metrics": resolution_analysis,
            "reopen_patterns": reopen_analysis,
            "quality_risks": quality_risks,
            "trends": trend_analysis,
            "team_performance": team_analysis,
            "recommendations": self._generate_recommendations(quality_risks, resolution_analysis)
        }
    
    def _analyze_frequency_patterns(self, df: pd.DataFrame, days_back: int) -> Dict[str, Any]:
        """Analyze bug reporting frequency"""
        df['reported_date'] = pd.to_datetime(df['reported_at']).dt.date
        
        # Daily bug counts
        daily_bugs = df.groupby('reported_date').size()
        
        # Calculate statistics
        avg_daily = daily_bugs.mean()
        std_daily = daily_bugs.std()
        
        # Identify spike days (> 2 std dev from mean)
        spike_threshold = avg_daily + 2 * std_daily
        spike_days = daily_bugs[daily_bugs > spike_threshold]
        
        # By project
        by_project = df.groupby('project_id').size().to_dict()
        
        # By bug type
        by_type = df['bug_type'].value_counts().to_dict() if 'bug_type' in df.columns else {}
        
        return {
            "avg_daily_bugs": float(avg_daily),
            "std_daily_bugs": float(std_daily),
            "max_daily_bugs": int(daily_bugs.max()) if len(daily_bugs) > 0 else 0,
            "spike_days": {str(k): int(v) for k, v in spike_days.items()},
            "spike_count": len(spike_days),
            "bugs_by_project": by_project,
            "bugs_by_type": by_type,
            "total_bugs": len(df)
        }
    
    def _analyze_severity_distribution(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze bug severity distribution"""
        severity_counts = df['severity'].value_counts().to_dict()
        
        total = len(df)
        severity_percentages = {
            sev: (count / total * 100) if total > 0 else 0
            for sev, count in severity_counts.items()
        }
        
        # Calculate high severity percentage
        high_severity_count = severity_counts.get('critical', 0) + severity_counts.get('high', 0)
        high_severity_percentage = (high_severity_count / total * 100) if total > 0 else 0
        
        # Average severity by project
        severity_map = {'critical': 4, 'high': 3, 'medium': 2, 'low': 1}
        df['severity_score'] = df['severity'].map(severity_map)
        
        by_project = {}
        if 'project_id' in df.columns:
            project_severity = df.groupby('project_id').agg({
                'severity_score': 'mean',
                'severity': lambda x: x.value_counts().to_dict()
            })
            by_project = project_severity.to_dict()
        
        return {
            "severity_counts": severity_counts,
            "severity_percentages": severity_percentages,
            "high_severity_percentage": float(high_severity_percentage),
            "high_severity_count": int(high_severity_count),
            "is_high_severity_risk": high_severity_percentage > self.high_severity_threshold * 100,
            "by_project": by_project
        }
    
    def _analyze_resolution_metrics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze bug resolution metrics"""
        # Filter resolved/closed bugs
        resolved_bugs = df[df['status'].isin(['resolved', 'closed'])]
        
        if len(resolved_bugs) == 0:
            return {
                "avg_resolution_time_hours": 0,
                "median_resolution_time_hours": 0,
                "slow_resolution_count": 0,
                "resolution_rate": 0,
                "by_severity": {}
            }
        
        # Calculate resolution time
        resolved_bugs['resolution_time'] = resolved_bugs['resolution_time_hours'].fillna(0)
        
        avg_resolution = float(resolved_bugs['resolution_time'].mean())
        median_resolution = float(resolved_bugs['resolution_time'].median())
        
        # Count slow resolutions
        slow_resolutions = len(resolved_bugs[resolved_bugs['resolution_time'] > self.slow_resolution_threshold])
        
        # Resolution rate
        resolution_rate = (len(resolved_bugs) / len(df) * 100) if len(df) > 0 else 0
        
        # By severity
        by_severity = resolved_bugs.groupby('severity')['resolution_time'].agg(['mean', 'median', 'count']).to_dict()
        
        # By priority
        by_priority = resolved_bugs.groupby('priority')['resolution_time'].agg(['mean', 'count']).to_dict() if 'priority' in resolved_bugs.columns else {}
        
        return {
            "avg_resolution_time_hours": avg_resolution,
            "median_resolution_time_hours": median_resolution,
            "slow_resolution_count": int(slow_resolutions),
            "slow_resolution_percentage": float(slow_resolutions / len(resolved_bugs) * 100) if len(resolved_bugs) > 0 else 0,
            "resolution_rate": float(resolution_rate),
            "total_resolved": len(resolved_bugs),
            "by_severity": by_severity,
            "by_priority": by_priority
        }
    
    def _analyze_reopen_patterns(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze bug reopen patterns"""
        reopened_bugs = df[df['reopen_count'] > 0]
        
        if len(reopened_bugs) == 0:
            return {
                "total_reopened": 0,
                "reopen_rate": 0,
                "chronic_reopens": []
            }
        
        # Chronic reopens (>= threshold)
        chronic = reopened_bugs[reopened_bugs['reopen_count'] >= self.critical_reopen_threshold]
        
        chronic_list = []
        for _, bug in chronic.iterrows():
            chronic_list.append({
                "bug_id": bug['bug_id'],
                "title": bug.get('title', ''),
                "reopen_count": int(bug['reopen_count']),
                "severity": bug['severity'],
                "status": bug['status']
            })
        
        # Reopen rate by severity
        by_severity = reopened_bugs.groupby('severity').agg({
            'reopen_count': ['count', 'mean', 'max']
        }).to_dict()
        
        return {
            "total_reopened": len(reopened_bugs),
            "reopen_rate": float(len(reopened_bugs) / len(df) * 100) if len(df) > 0 else 0,
            "chronic_reopens": chronic_list,
            "chronic_count": len(chronic),
            "avg_reopen_count": float(reopened_bugs['reopen_count'].mean()),
            "max_reopen_count": int(reopened_bugs['reopen_count'].max()),
            "by_severity": by_severity
        }
    
    def _identify_quality_risks(
        self, 
        df: pd.DataFrame, 
        frequency: Dict, 
        resolution: Dict
    ) -> List[Dict[str, Any]]:
        """Identify quality risks based on bug patterns"""
        risks = []
        
        # High bug rate risk
        if frequency['avg_daily_bugs'] > 5:
            risks.append({
                "type": "high_bug_rate",
                "severity": "high" if frequency['avg_daily_bugs'] > 10 else "medium",
                "description": f"High average daily bug rate: {frequency['avg_daily_bugs']:.1f}",
                "metric_value": frequency['avg_daily_bugs'],
                "threshold": 5.0,
                "recommendation": "Review testing processes and code quality standards"
            })
        
        # Frequent spikes risk
        if frequency['spike_count'] > 3:
            risks.append({
                "type": "frequent_bug_spikes",
                "severity": "medium",
                "description": f"Frequent bug spikes detected: {frequency['spike_count']} days",
                "metric_value": frequency['spike_count'],
                "threshold": 3,
                "recommendation": "Investigate root causes of bug spikes, possibly related to deployments"
            })
        
        # Slow resolution risk
        if resolution['slow_resolution_percentage'] > 30:
            risks.append({
                "type": "slow_resolution",
                "severity": "high",
                "description": f"{resolution['slow_resolution_percentage']:.1f}% of bugs take > {self.slow_resolution_threshold}h to resolve",
                "metric_value": resolution['slow_resolution_percentage'],
                "threshold": 30.0,
                "recommendation": "Improve bug triage process and allocate more resources to bug fixing"
            })
        
        # Low resolution rate
        if resolution['resolution_rate'] < 60:
            risks.append({
                "type": "low_resolution_rate",
                "severity": "high" if resolution['resolution_rate'] < 40 else "medium",
                "description": f"Only {resolution['resolution_rate']:.1f}% of bugs are resolved",
                "metric_value": resolution['resolution_rate'],
                "threshold": 60.0,
                "recommendation": "Prioritize bug resolution and reduce backlog"
            })
        
        # High reopen rate
        reopened = df[df['reopen_count'] > 0]
        reopen_rate = (len(reopened) / len(df) * 100) if len(df) > 0 else 0
        if reopen_rate > 15:
            risks.append({
                "type": "high_reopen_rate",
                "severity": "high",
                "description": f"{reopen_rate:.1f}% of bugs are reopened",
                "metric_value": reopen_rate,
                "threshold": 15.0,
                "recommendation": "Improve testing before marking bugs as resolved"
            })
        
        return risks
    
    def _analyze_trends(self, df: pd.DataFrame, days_back: int) -> Dict[str, Any]:
        """Analyze bug trends over time"""
        df['week'] = pd.to_datetime(df['reported_at']).dt.isocalendar().week
        
        weekly_counts = df.groupby('week').size()
        
        if len(weekly_counts) < 2:
            return {"trend": "insufficient_data"}
        
        # Calculate trend
        x = np.arange(len(weekly_counts))
        trend_slope = np.polyfit(x, weekly_counts.values, 1)[0]
        
        trend_direction = "increasing" if trend_slope > 0.5 else "decreasing" if trend_slope < -0.5 else "stable"
        
        # Recent vs historical comparison
        midpoint = len(df) // 2
        recent_bugs = df.iloc[midpoint:]
        historical_bugs = df.iloc[:midpoint]
        
        recent_avg = len(recent_bugs) / (days_back / 2) if days_back > 0 else 0
        historical_avg = len(historical_bugs) / (days_back / 2) if days_back > 0 else 0
        
        change_percentage = ((recent_avg - historical_avg) / historical_avg * 100) if historical_avg > 0 else 0
        
        return {
            "trend_direction": trend_direction,
            "trend_slope": float(trend_slope),
            "weekly_counts": weekly_counts.to_dict(),
            "recent_avg_daily": float(recent_avg),
            "historical_avg_daily": float(historical_avg),
            "change_percentage": float(change_percentage)
        }
    
    def _analyze_team_performance(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze team performance on bug resolution"""
        if 'assigned_to' not in df.columns:
            return {}
        
        # Bugs by assignee
        assigned_bugs = df[df['assigned_to'].notna()]
        
        if len(assigned_bugs) == 0:
            return {"message": "No assigned bugs to analyze"}
        
        by_assignee = assigned_bugs.groupby('assigned_to').agg({
            'id': 'count',
            'status': lambda x: (x.isin(['resolved', 'closed']).sum() / len(x) * 100) if len(x) > 0 else 0,
            'resolution_time_hours': 'mean'
        }).rename(columns={
            'id': 'total_assigned',
            'status': 'resolution_rate',
            'resolution_time_hours': 'avg_resolution_time'
        })
        
        # Top performers
        top_resolvers = by_assignee.nlargest(5, 'resolution_rate').to_dict()
        
        # Needs support
        needs_support = by_assignee[by_assignee['resolution_rate'] < 50].to_dict() if len(by_assignee) > 0 else {}
        
        return {
            "by_assignee": by_assignee.to_dict(),
            "top_performers": top_resolvers,
            "needs_support": needs_support
        }
    
    def _generate_recommendations(
        self, 
        risks: List[Dict], 
        resolution: Dict
    ) -> List[Dict[str, str]]:
        """Generate actionable recommendations"""
        recommendations = []
        
        if any(r['type'] == 'high_bug_rate' for r in risks):
            recommendations.append({
                "priority": "high",
                "category": "quality_assurance",
                "action": "Implement stricter code review process and increase test coverage",
                "rationale": "High bug rate indicates quality issues in development process"
            })
        
        if any(r['type'] == 'slow_resolution' for r in risks):
            recommendations.append({
                "priority": "high",
                "category": "resource_allocation",
                "action": "Allocate dedicated resources for bug fixing and reduce WIP",
                "rationale": f"Average resolution time exceeds acceptable threshold"
            })
        
        if any(r['type'] == 'high_reopen_rate' for r in risks):
            recommendations.append({
                "priority": "high",
                "category": "testing",
                "action": "Improve verification testing before closing bugs",
                "rationale": "High reopen rate suggests incomplete bug fixes"
            })
        
        if resolution['resolution_rate'] < 60:
            recommendations.append({
                "priority": "medium",
                "category": "backlog_management",
                "action": "Conduct bug triage session and prioritize critical fixes",
                "rationale": "Low resolution rate indicates growing bug backlog"
            })
        
        if any(r['type'] == 'frequent_bug_spikes' for r in risks):
            recommendations.append({
                "priority": "medium",
                "category": "process_improvement",
                "action": "Correlate bug spikes with deployments and improve CI/CD",
                "rationale": "Frequent spikes suggest deployment or integration issues"
            })
        
        return recommendations
    
    def get_bug_details(self, db: Client, bug_id: str) -> Dict[str, Any]:
        """Get detailed information about a specific bug"""
        bug_response = db.table("bugs").select("*").eq("bug_id", bug_id).single().execute()
        bug = bug_response.data
        
        if not bug:
            raise ValueError(f"Bug {bug_id} not found")
        
        # Get comments/history
        comments_response = db.table("bug_comments").select(
            "*, employees(name, role)"
        ).eq("bug_id", bug['id']).order("created_at").execute()
        
        comments = comments_response.data
        
        return {
            "bug": bug,
            "history": comments,
            "metrics": {
                "age_hours": (datetime.now() - pd.to_datetime(bug['reported_at'])).total_seconds() / 3600,
                "is_overdue": bug['status'] not in ['resolved', 'closed'] and 
                             bug.get('resolution_time_hours', 0) > self.slow_resolution_threshold,
                "reopen_count": bug.get('reopen_count', 0)
            }
        }