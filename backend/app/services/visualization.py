"""
Exploratory Data Analysis and Visualization Module
"""
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)


class DataVisualizer:
    """Generate visualizations for risk analysis"""
    
    @staticmethod
    def create_velocity_trend_chart(df: pd.DataFrame, group_by: str = 'sprint') -> Dict[str, Any]:
        """Create sprint velocity trend visualization"""
        fig = go.Figure()
        
        if group_by in df.columns and 'velocity' in df.columns:
            fig.add_trace(go.Scatter(
                x=df[group_by],
                y=df['velocity'],
                mode='lines+markers',
                name='Velocity',
                line=dict(color='#3b82f6', width=2),
                marker=dict(size=8)
            ))
            
            # Add moving average
            if len(df) >= 3:
                df['velocity_ma'] = df['velocity'].rolling(window=3).mean()
                fig.add_trace(go.Scatter(
                    x=df[group_by],
                    y=df['velocity_ma'],
                    mode='lines',
                    name='3-Sprint MA',
                    line=dict(color='#10b981', width=2, dash='dash')
                ))
        
        fig.update_layout(
            title='Sprint Velocity Trend',
            xaxis_title='Sprint',
            yaxis_title='Story Points',
            template='plotly_white',
            hovermode='x unified'
        )
        
        return fig.to_dict()
    
    @staticmethod
    def create_resource_utilization_heatmap(df: pd.DataFrame) -> Dict[str, Any]:
        """Create resource utilization heatmap"""
        if 'user_id' not in df.columns or 'week_start_date' not in df.columns:
            return {}
        
        # Pivot data for heatmap
        heatmap_data = df.pivot_table(
            values='utilization_rate',
            index='user_id',
            columns='week_start_date',
            aggfunc='mean'
        )
        
        fig = go.Figure(data=go.Heatmap(
            z=heatmap_data.values,
            x=heatmap_data.columns.astype(str),
            y=heatmap_data.index.astype(str),
            colorscale='RdYlGn',
            zmid=0.8,
            text=np.round(heatmap_data.values, 2),
            texttemplate='%{text}',
            textfont={"size": 10},
            colorbar=dict(title="Utilization Rate")
        ))
        
        fig.update_layout(
            title='Resource Utilization Over Time',
            xaxis_title='Week',
            yaxis_title='Resource',
            template='plotly_white'
        )
        
        return fig.to_dict()
    
    @staticmethod
    def create_bug_analysis_chart(df: pd.DataFrame) -> Dict[str, Any]:
        """Create bug analysis visualization"""
        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=('Bug Creation Trend', 'Bug Reopen Rate'),
            specs=[[{'type': 'scatter'}, {'type': 'bar'}]]
        )
        
        if 'created_at' in df.columns and 'is_bug' in df.columns:
            bug_df = df[df['is_bug'] == True].copy()
            bug_df['created_date'] = pd.to_datetime(bug_df['created_at']).dt.date
            bug_counts = bug_df.groupby('created_date').size().reset_index(name='count')
            
            fig.add_trace(
                go.Scatter(
                    x=bug_counts['created_date'],
                    y=bug_counts['count'],
                    mode='lines+markers',
                    name='Bugs Created',
                    line=dict(color='#ef4444')
                ),
                row=1, col=1
            )
        
        if 'project_id' in df.columns and 'reopen_count' in df.columns:
            reopen_stats = df.groupby('project_id').agg({
                'reopen_count': 'mean'
            }).reset_index()
            
            fig.add_trace(
                go.Bar(
                    x=reopen_stats['project_id'].astype(str),
                    y=reopen_stats['reopen_count'],
                    name='Avg Reopens',
                    marker_color='#f59e0b'
                ),
                row=1, col=2
            )
        
        fig.update_layout(
            title_text='Bug Analysis Dashboard',
            showlegend=True,
            template='plotly_white'
        )
        
        return fig.to_dict()
    
    @staticmethod
    def create_risk_score_gauge(risk_score: float, risk_level: str) -> Dict[str, Any]:
        """Create risk score gauge chart"""
        color_map = {
            'low': '#10b981',
            'medium': '#f59e0b',
            'high': '#ef4444',
            'critical': '#991b1b'
        }
        
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=risk_score,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': f"Risk Score - {risk_level.upper()}"},
            delta={'reference': 50},
            gauge={
                'axis': {'range': [None, 100]},
                'bar': {'color': color_map.get(risk_level.lower(), '#6b7280')},
                'steps': [
                    {'range': [0, 25], 'color': '#d1fae5'},
                    {'range': [25, 50], 'color': '#fef3c7'},
                    {'range': [50, 75], 'color': '#fecaca'},
                    {'range': [75, 100], 'color': '#fee2e2'}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 75
                }
            }
        ))
        
        fig.update_layout(
            template='plotly_white',
            height=300
        )
        
        return fig.to_dict()
    
    @staticmethod
    def create_project_timeline(df: pd.DataFrame) -> Dict[str, Any]:
        """Create project timeline Gantt chart"""
        if not all(col in df.columns for col in ['project_name', 'start_date', 'end_date']):
            return {}
        
        df_timeline = df.copy()
        df_timeline['start_date'] = pd.to_datetime(df_timeline['start_date'])
        df_timeline['end_date'] = pd.to_datetime(df_timeline['end_date'])
        
        fig = px.timeline(
            df_timeline,
            x_start='start_date',
            x_end='end_date',
            y='project_name',
            color='status',
            title='Project Timeline'
        )
        
        fig.update_layout(
            xaxis_title='Date',
            yaxis_title='Project',
            template='plotly_white'
        )
        
        return fig.to_dict()
    
    @staticmethod
    def create_correlation_heatmap(df: pd.DataFrame, features: List[str]) -> Dict[str, Any]:
        """Create correlation heatmap for risk factors"""
        available_features = [f for f in features if f in df.columns]
        
        if len(available_features) < 2:
            return {}
        
        corr_matrix = df[available_features].corr()
        
        fig = go.Figure(data=go.Heatmap(
            z=corr_matrix.values,
            x=corr_matrix.columns,
            y=corr_matrix.columns,
            colorscale='RdBu',
            zmid=0,
            text=np.round(corr_matrix.values, 2),
            texttemplate='%{text}',
            textfont={"size": 10},
            colorbar=dict(title="Correlation")
        ))
        
        fig.update_layout(
            title='Risk Factors Correlation Matrix',
            template='plotly_white',
            width=800,
            height=800
        )
        
        return fig.to_dict()
    
    @staticmethod
    def create_cost_variance_chart(df: pd.DataFrame) -> Dict[str, Any]:
        """Create cost variance visualization"""
        if not all(col in df.columns for col in ['project_name', 'planned_budget', 'actual_cost']):
            return {}
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            name='Planned Budget',
            x=df['project_name'],
            y=df['planned_budget'],
            marker_color='#3b82f6'
        ))
        
        fig.add_trace(go.Bar(
            name='Actual Cost',
            x=df['project_name'],
            y=df['actual_cost'],
            marker_color='#ef4444'
        ))
        
        fig.update_layout(
            title='Cost: Planned vs Actual',
            xaxis_title='Project',
            yaxis_title='Cost ($)',
            barmode='group',
            template='plotly_white'
        )
        
        return fig.to_dict()
    
    @staticmethod
    def create_anomaly_scatter(df: pd.DataFrame) -> Dict[str, Any]:
        """Create anomaly detection scatter plot"""
        if not all(col in df.columns for col in ['anomaly_score', 'utilization_rate', 'is_bottleneck']):
            return {}
        
        fig = px.scatter(
            df,
            x='utilization_rate',
            y='anomaly_score',
            color='is_bottleneck',
            size='tasks_assigned' if 'tasks_assigned' in df.columns else None,
            hover_data=['user_id'] if 'user_id' in df.columns else None,
            title='Resource Anomaly Detection',
            color_discrete_map={True: '#ef4444', False: '#10b981'}
        )
        
        fig.update_layout(
            xaxis_title='Utilization Rate',
            yaxis_title='Anomaly Score',
            template='plotly_white'
        )
        
        return fig.to_dict()


class EDAAnalyzer:
    """Perform Exploratory Data Analysis"""
    
    @staticmethod
    def generate_summary_statistics(df: pd.DataFrame) -> Dict[str, Any]:
        """Generate summary statistics"""
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        summary = {
            'total_records': len(df),
            'numeric_columns': len(numeric_cols),
            'missing_values': df.isnull().sum().to_dict(),
            'statistics': {}
        }
        
        for col in numeric_cols:
            summary['statistics'][col] = {
                'mean': float(df[col].mean()) if not df[col].isna().all() else None,
                'median': float(df[col].median()) if not df[col].isna().all() else None,
                'std': float(df[col].std()) if not df[col].isna().all() else None,
                'min': float(df[col].min()) if not df[col].isna().all() else None,
                'max': float(df[col].max()) if not df[col].isna().all() else None,
                'q25': float(df[col].quantile(0.25)) if not df[col].isna().all() else None,
                'q75': float(df[col].quantile(0.75)) if not df[col].isna().all() else None
            }
        
        return summary
    
    @staticmethod
    def analyze_risk_trends(df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze risk trends over time"""
        analysis = {
            'velocity_trend': 'stable',
            'bug_trend': 'stable',
            'utilization_trend': 'stable',
            'risk_indicators': []
        }
        
        # Analyze velocity trend
        if 'velocity' in df.columns and len(df) >= 3:
            recent_velocity = df['velocity'].tail(3).mean()
            older_velocity = df['velocity'].head(3).mean()
            
            if recent_velocity < older_velocity * 0.9:
                analysis['velocity_trend'] = 'declining'
                analysis['risk_indicators'].append('Velocity declining')
            elif recent_velocity > older_velocity * 1.1:
                analysis['velocity_trend'] = 'improving'
        
        # Analyze bug trend
        if 'total_bugs' in df.columns and len(df) >= 3:
            recent_bugs = df['total_bugs'].tail(3).mean()
            older_bugs = df['total_bugs'].head(3).mean()
            
            if recent_bugs > older_bugs * 1.2:
                analysis['bug_trend'] = 'increasing'
                analysis['risk_indicators'].append('Bug rate increasing')
        
        # Analyze utilization
        if 'avg_utilization_rate' in df.columns:
            avg_util = df['avg_utilization_rate'].mean()
            
            if avg_util > 1.0:
                analysis['utilization_trend'] = 'over-allocated'
                analysis['risk_indicators'].append('Team over-allocated')
            elif avg_util < 0.7:
                analysis['utilization_trend'] = 'under-utilized'
                analysis['risk_indicators'].append('Team under-utilized')
        
        return analysis
    
    @staticmethod
    def identify_correlations(df: pd.DataFrame, target: str, threshold: float = 0.3) -> List[Dict[str, Any]]:
        """Identify strong correlations with target variable"""
        if target not in df.columns:
            return []
        
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        correlations = []
        
        for col in numeric_cols:
            if col != target:
                corr = df[target].corr(df[col])
                if abs(corr) >= threshold:
                    correlations.append({
                        'feature': col,
                        'correlation': float(corr),
                        'strength': 'strong' if abs(corr) >= 0.7 else 'moderate'
                    })
        
        correlations.sort(key=lambda x: abs(x['correlation']), reverse=True)
        return correlations
    
    @staticmethod
    def detect_data_quality_issues(df: pd.DataFrame) -> Dict[str, Any]:
        """Detect data quality issues"""
        issues = {
            'missing_values': {},
            'duplicates': 0,
            'outliers': {},
            'data_types': {}
        }
        
        # Missing values
        missing = df.isnull().sum()
        issues['missing_values'] = {
            col: int(count) for col, count in missing.items() if count > 0
        }
        
        # Duplicates
        issues['duplicates'] = int(df.duplicated().sum())
        
        # Outliers (using IQR method)
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            outliers = ((df[col] < (Q1 - 1.5 * IQR)) | (df[col] > (Q3 + 1.5 * IQR))).sum()
            if outliers > 0:
                issues['outliers'][col] = int(outliers)
        
        # Data types
        issues['data_types'] = {col: str(dtype) for col, dtype in df.dtypes.items()}
        
        return issues
    
    @staticmethod
    def generate_insights(df: pd.DataFrame, project_type: str = 'project_metrics') -> List[str]:
        """Generate actionable insights from data"""
        insights = []
        
        if project_type == 'project_metrics':
            # Check completion rate
            if 'completion_rate' in df.columns:
                avg_completion = df['completion_rate'].mean()
                if avg_completion < 0.7:
                    insights.append(f"Low average completion rate ({avg_completion:.1%}). Consider reviewing task complexity and resource allocation.")
            
            # Check velocity
            if 'sprint_velocity' in df.columns and len(df) >= 2:
                velocity_change = df['sprint_velocity'].pct_change().mean()
                if velocity_change < -0.1:
                    insights.append(f"Velocity declining by {abs(velocity_change):.1%} on average. Team may be facing impediments.")
            
            # Check bug rate
            if 'bug_reopen_rate' in df.columns:
                avg_reopen = df['bug_reopen_rate'].mean()
                if avg_reopen > 0.15:
                    insights.append(f"High bug reopen rate ({avg_reopen:.1%}). Quality assurance processes may need improvement.")
            
            # Check blocked tasks
            if 'blocked_tasks' in df.columns:
                avg_blocked = df['blocked_tasks'].mean()
                if avg_blocked > 3:
                    insights.append(f"Average of {avg_blocked:.1f} blocked tasks. Review dependency management and remove blockers.")
        
        elif project_type == 'resource_utilization':
            # Check utilization
            if 'utilization_rate' in df.columns:
                over_allocated = (df['utilization_rate'] > 1.0).sum()
                under_utilized = (df['utilization_rate'] < 0.7).sum()
                
                if over_allocated > len(df) * 0.2:
                    insights.append(f"{over_allocated} resources are over-allocated. Risk of burnout and quality issues.")
                
                if under_utilized > len(df) * 0.3:
                    insights.append(f"{under_utilized} resources are under-utilized. Optimize resource allocation.")
        
        return insights
