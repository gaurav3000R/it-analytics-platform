# Completing the truncated ./backend/app/services/bug_tracker.py
# Adding missing implementation based on context

#===== ./backend/app/services/bug_tracker.py =====

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any
from collections import defaultdict
from sqlalchemy.orm import Session

from app.models import DailyLog  # FIXED
class BugTrackerService:
    def __init__(self):
        self.critical_reopen_threshold = 3  # Critical if bug reopened 3+ times
        self.quality_risk_threshold = 0.15  # 15% bug rate triggers quality risk
        
    def analyze_bug_patterns(self, db: Session, project_id: int = None, days_back: int = 30) -> Dict[str, Any]:
        """Analyze bug patterns and identify quality risks"""
        
        start_date = datetime.now() - timedelta(days=days_back)
        
        # Query bug data from daily logs
        query = db.query(DailyLog).filter(DailyLog.date >= start_date)
        if project_id:
            query = query.filter(DailyLog.project_id == project_id)
        
        logs = query.all()
        
        # Analyze patterns
        bug_patterns = self._analyze_bug_frequency_patterns(logs)
        quality_trends = self._calculate_quality_trends(logs)
        risk_indicators = self._identify_quality_risk_indicators(logs, bug_patterns)
        
        return {
            "bug_patterns": bug_patterns,
            "quality_trends": quality_trends,
            "risk_indicators": risk_indicators,
            "recommendations": self._generate_quality_recommendations(risk_indicators)
        }
    
    def _analyze_bug_frequency_patterns(self, logs: List[DailyLog]) -> Dict[str, Any]:
        """Analyze bug reporting frequency patterns"""
        
        daily_bugs = defaultdict(int)
        project_bugs = defaultdict(int)
        employee_bugs = defaultdict(int)
        
        for log in logs:
            date_key = log.date.strftime('%Y-%m-%d')
            daily_bugs[date_key] += log.issues_reported
            project_bugs[log.project_id] += log.issues_reported
            employee_bugs[log.employee_id] += log.issues_reported
        
        # Calculate statistics
        bug_counts = list(daily_bugs.values())
        avg_daily_bugs = np.mean(bug_counts) if bug_counts else 0
        bug_volatility = np.std(bug_counts) if len(bug_counts) > 1 else 0
        
        # Identify spike days
        threshold = avg_daily_bugs + 2 * bug_volatility
        spike_days = {date: count for date, count in daily_bugs.items() if count > threshold}
        
        return {
            "avg_daily_bugs": avg_daily_bugs,
            "bug_volatility": bug_volatility,
            "spike_days": spike_days,
            "total_bugs": sum(bug_counts),
            "projects_with_most_bugs": sorted(project_bugs.items(), key=lambda x: x[1], reverse=True)[:5]
        }
    
    def _calculate_quality_trends(self, logs: List[DailyLog]) -> Dict[str, Any]:
        """Calculate quality trend indicators"""
        
        if not logs:
            return {}
        
        # Group by week to see trends
        weekly_data = defaultdict(lambda: {'bugs': 0, 'hours': 0})
        
        for log in logs:
            week_key = log.date.strftime('%Y-W%U')
            weekly_data[week_key]['bugs'] += log.issues_reported
            weekly_data[week_key]['hours'] += log.hours_logged
        
        # Calculate bug rate per hour
        weekly_bug_rates = []
        for week_data in weekly_data.values():
            if week_data['hours'] > 0:
                rate = week_data['bugs'] / week_data['hours']
                weekly_bug_rates.append(rate)
        
        if len(weekly_bug_rates) < 2:
            return {"trend": "insufficient_data"}
        
        # Calculate trend
        x = np.arange(len(weekly_bug_rates))
        trend_slope = np.polyfit(x, weekly_bug_rates, 1)[0]
        
        current_rate = weekly_bug_rates[-1] if weekly_bug_rates else 0
        
        return {
            "current_bug_rate": current_rate,
            "trend_direction": "increasing" if trend_slope > 0.001 else "decreasing" if trend_slope < -0.001 else "stable",
            "trend_slope": trend_slope,
            "weekly_rates": weekly_bug_rates
        }
    
    def _identify_quality_risk_indicators(self, logs: List[DailyLog], patterns: Dict) -> List[Dict[str, Any]]:
        """Identify quality risk indicators"""
        
        risks = []
        
        # High bug rate risk
        if patterns['avg_daily_bugs'] > 5:
            risks.append({
                "type": "high_bug_rate",
                "severity": "high",
                "description": f"High average daily bug rate: {patterns['avg_daily_bugs']:.1f}",
                "recommendation": "Review testing processes and code quality standards"
            })
        
        # Bug volatility risk
        if patterns['bug_volatility'] > patterns['avg_daily_bugs']:
            risks.append({
                "type": "unstable_quality",
                "severity": "medium", 
                "description": "High volatility in bug reporting indicates inconsistent quality",
                "recommendation": "Implement more consistent testing and review processes"
            })
        
        # Spike pattern risk
        if len(patterns['spike_days']) > 3:
            risks.append({
                "type": "frequent_bug_spikes",
                "severity": "medium",
                "description": f"Frequent bug spikes detected: {len(patterns['spike_days'])} days",
                "recommendation": "Investigate root causes of bug spikes"
            })
        
        return risks
    
    def _generate_quality_recommendations(self, risk_indicators: List[Dict]) -> List[str]:
        """Generate quality improvement recommendations"""
        
        recommendations = []
        
        if any(risk['type'] == 'high_bug_rate' for risk in risk_indicators):
            recommendations.extend([
                "Implement additional code review checkpoints",
                "Increase automated testing coverage",
                "Conduct root cause analysis of common bugs"
            ])
        
        if any(risk['type'] == 'unstable_quality' for risk in risk_indicators):
            recommendations.extend([
                "Standardize testing procedures across team",
                "Implement quality gates in deployment pipeline"
            ])
        
        return recommendations