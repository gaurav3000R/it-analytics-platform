# Implementing the placeholder ./backend/app/services/resource_utilization.py

#===== ./backend/app/services/resource_utilization.py =====

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any
from sqlalchemy.orm import Session
from sqlalchemy import func  # Add if missing for queries

from app.models.employee import Employee
from app.models import DailyLog  # FIXED

# ... (rest unchanged)

class ResourceUtilizationService:
    def __init__(self):
        self.underutilization_threshold = 0.6  # 60% of expected hours
        self.overutilization_threshold = 1.3   # 130% of expected hours
        
    def analyze_team_utilization(self, db: Session, days_back: int = 14) -> Dict[str, Any]:
        """Analyze team utilization and generate alerts"""
        
        start_date = datetime.now() - timedelta(days=days_back)
        
        # Get employee utilization data
        utilization_data = db.query(
            Employee.id,
            Employee.name,
            Employee.role,
            Employee.max_hours_per_day,
            func.avg(DailyLog.hours_logged).label('avg_daily_hours'),
            func.sum(DailyLog.hours_logged).label('total_hours'),
            func.count(func.distinct(func.date(DailyLog.date))).label('active_days')
        ).join(DailyLog).filter(
            DailyLog.date >= start_date,
            Employee.is_active == True
        ).group_by(Employee.id).all()
        
        alerts = []
        utilization_summary = []
        
        for emp_data in utilization_data:
            expected_daily_hours = emp_data.max_hours_per_day
            actual_avg_hours = emp_data.avg_daily_hours or 0
            utilization_rate = actual_avg_hours / expected_daily_hours if expected_daily_hours > 0 else 0
            
            # Generate alerts
            if utilization_rate < self.underutilization_threshold:
                alerts.append({
                    "type": "underutilization",
                    "employee_id": emp_data.id,
                    "employee_name": emp_data.name,
                    "severity": "high" if utilization_rate < 0.4 else "medium",
                    "utilization_rate": utilization_rate,
                    "message": f"{emp_data.name} is underutilized at {utilization_rate:.1%}"
                })
            
            elif utilization_rate > self.overutilization_threshold:
                alerts.append({
                    "type": "overutilization",
                    "employee_id": emp_data.id,
                    "employee_name": emp_data.name,
                    "severity": "high" if utilization_rate > 1.5 else "medium",
                    "utilization_rate": utilization_rate,
                    "message": f"{emp_data.name} is overworked at {utilization_rate:.1%}"
                })
            
            utilization_summary.append({
                "employee_id": emp_data.id,
                "name": emp_data.name,
                "role": emp_data.role,
                "utilization_rate": utilization_rate,
                "avg_daily_hours": actual_avg_hours,
                "expected_hours": expected_daily_hours,
                "total_hours": emp_data.total_hours,
                "active_days": emp_data.active_days
            })
        
        return {
            "alerts": alerts,
            "utilization_summary": sorted(utilization_summary, 
                                        key=lambda x: x['utilization_rate'], reverse=True),
            "period_days": days_back,
            "summary_stats": self._calculate_utilization_stats(utilization_summary)
        }
    
    def _calculate_utilization_stats(self, utilization_data: List[Dict]) -> Dict[str, Any]:
        """Calculate summary statistics"""
        if not utilization_data:
            return {}
        
        rates = [emp['utilization_rate'] for emp in utilization_data]
        
        return {
            "avg_utilization": np.mean(rates),
            "median_utilization": np.median(rates),
            "underutilized_count": len([r for r in rates if r < self.underutilization_threshold]),
            "overutilized_count": len([r for r in rates if r > self.overutilization_threshold]),
            "optimal_count": len([r for r in rates if self.underutilization_threshold <= r <= self.overutilization_threshold])
        }
        
    def get_rebalancing_suggestions(self, db: Session) -> List[Dict[str, Any]]:
        """Generate resource rebalancing suggestions"""
        utilization_data = self.analyze_team_utilization(db)
        
        suggestions = []
        underutilized = [emp for emp in utilization_data['utilization_summary'] 
                        if emp['utilization_rate'] < self.underutilization_threshold]
        overutilized = [emp for emp in utilization_data['utilization_summary'] 
                       if emp['utilization_rate'] > self.overutilization_threshold]
        
        for over_emp in overutilized:
            for under_emp in underutilized:
                if over_emp['role'] == under_emp['role']:  # Same role match
                    suggestions.append({
                        "type": "workload_redistribution",
                        "from_employee": over_emp['name'],
                        "to_employee": under_emp['name'],
                        "role": over_emp['role'],
                        "potential_hours_transfer": min(
                            (over_emp['utilization_rate'] - 1.0) * over_emp['expected_hours'],
                            (1.0 - under_emp['utilization_rate']) * under_emp['expected_hours']
                        )
                    })
        
        return suggestions