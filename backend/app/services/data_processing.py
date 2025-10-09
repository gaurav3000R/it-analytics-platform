"""
Data Extraction and Cleaning Module
Handles Kaizen logs, Jira API data, and internal records
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import json
import logging

logger = logging.getLogger(__name__)


class DataExtractor:
    """Extract data from various sources"""
    
    def __init__(self, jira_client=None):
        self.jira_client = jira_client
    
    def extract_kaizen_logs(self, file_path: str) -> pd.DataFrame:
        """
        Extract and parse Kaizen logs from CSV/JSON files
        
        Args:
            file_path: Path to Kaizen log file
            
        Returns:
            DataFrame with parsed Kaizen logs
        """
        try:
            if file_path.endswith('.csv'):
                df = pd.read_csv(file_path)
            elif file_path.endswith('.json'):
                df = pd.read_json(file_path)
            else:
                raise ValueError(f"Unsupported file format: {file_path}")
            
            logger.info(f"Extracted {len(df)} records from {file_path}")
            return df
        
        except Exception as e:
            logger.error(f"Error extracting Kaizen logs: {e}")
            raise
    
    def extract_from_jira(self, project_key: str, start_date: Optional[datetime] = None) -> pd.DataFrame:
        """
        Extract data from Jira API
        
        Args:
            project_key: Jira project key
            start_date: Start date for data extraction
            
        Returns:
            DataFrame with Jira issues
        """
        if not self.jira_client:
            logger.warning("Jira client not initialized")
            return pd.DataFrame()
        
        try:
            # Build JQL query
            jql = f"project = {project_key}"
            if start_date:
                jql += f" AND updated >= '{start_date.strftime('%Y-%m-%d')}'"
            
            # Fetch issues
            issues = self.jira_client.search_issues(jql, maxResults=1000)
            
            # Convert to DataFrame
            data = []
            for issue in issues:
                data.append({
                    'key': issue.key,
                    'summary': issue.fields.summary,
                    'description': issue.fields.description,
                    'status': issue.fields.status.name,
                    'priority': issue.fields.priority.name if issue.fields.priority else None,
                    'issue_type': issue.fields.issuetype.name,
                    'assignee': issue.fields.assignee.displayName if issue.fields.assignee else None,
                    'created': issue.fields.created,
                    'updated': issue.fields.updated,
                    'resolved': issue.fields.resolutiondate,
                    'story_points': getattr(issue.fields, 'customfield_10016', None),
                    'sprint': getattr(issue.fields, 'customfield_10020', None),
                })
            
            df = pd.DataFrame(data)
            logger.info(f"Extracted {len(df)} issues from Jira project {project_key}")
            return df
        
        except Exception as e:
            logger.error(f"Error extracting from Jira: {e}")
            raise


class DataCleaner:
    """Clean and preprocess data"""
    
    @staticmethod
    def handle_missing_values(df: pd.DataFrame, strategy: Dict[str, str] = None) -> pd.DataFrame:
        """
        Handle missing values in DataFrame
        
        Args:
            df: Input DataFrame
            strategy: Dictionary mapping column names to strategies (mean, median, mode, ffill, bfill, drop)
            
        Returns:
            Cleaned DataFrame
        """
        df_clean = df.copy()
        
        if strategy is None:
            strategy = {}
        
        for col in df_clean.columns:
            if df_clean[col].isnull().any():
                col_strategy = strategy.get(col, 'drop')
                
                if col_strategy == 'mean' and pd.api.types.is_numeric_dtype(df_clean[col]):
                    df_clean[col].fillna(df_clean[col].mean(), inplace=True)
                elif col_strategy == 'median' and pd.api.types.is_numeric_dtype(df_clean[col]):
                    df_clean[col].fillna(df_clean[col].median(), inplace=True)
                elif col_strategy == 'mode':
                    df_clean[col].fillna(df_clean[col].mode()[0], inplace=True)
                elif col_strategy == 'ffill':
                    df_clean[col].fillna(method='ffill', inplace=True)
                elif col_strategy == 'bfill':
                    df_clean[col].fillna(method='bfill', inplace=True)
                elif col_strategy == 'zero':
                    df_clean[col].fillna(0, inplace=True)
                elif col_strategy == 'drop':
                    df_clean.dropna(subset=[col], inplace=True)
        
        logger.info(f"Handled missing values. Rows: {len(df)} -> {len(df_clean)}")
        return df_clean
    
    @staticmethod
    def remove_duplicates(df: pd.DataFrame, subset: Optional[List[str]] = None) -> pd.DataFrame:
        """Remove duplicate rows"""
        df_clean = df.drop_duplicates(subset=subset, keep='first')
        logger.info(f"Removed {len(df) - len(df_clean)} duplicate rows")
        return df_clean
    
    @staticmethod
    def handle_outliers(df: pd.DataFrame, columns: List[str], method: str = 'iqr', threshold: float = 1.5) -> pd.DataFrame:
        """
        Handle outliers in numeric columns
        
        Args:
            df: Input DataFrame
            columns: Columns to check for outliers
            method: Method to detect outliers ('iqr' or 'zscore')
            threshold: Threshold for outlier detection
            
        Returns:
            DataFrame with outliers handled
        """
        df_clean = df.copy()
        
        for col in columns:
            if col not in df_clean.columns or not pd.api.types.is_numeric_dtype(df_clean[col]):
                continue
            
            if method == 'iqr':
                Q1 = df_clean[col].quantile(0.25)
                Q3 = df_clean[col].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - threshold * IQR
                upper_bound = Q3 + threshold * IQR
                
                # Cap outliers
                df_clean[col] = df_clean[col].clip(lower_bound, upper_bound)
            
            elif method == 'zscore':
                mean = df_clean[col].mean()
                std = df_clean[col].std()
                df_clean[col] = df_clean[col].clip(
                    mean - threshold * std,
                    mean + threshold * std
                )
        
        logger.info(f"Handled outliers in {len(columns)} columns")
        return df_clean
    
    @staticmethod
    def normalize_dates(df: pd.DataFrame, date_columns: List[str]) -> pd.DataFrame:
        """Normalize date columns to datetime format"""
        df_clean = df.copy()
        
        for col in date_columns:
            if col in df_clean.columns:
                df_clean[col] = pd.to_datetime(df_clean[col], errors='coerce')
        
        logger.info(f"Normalized {len(date_columns)} date columns")
        return df_clean
    
    @staticmethod
    def clean_text_fields(df: pd.DataFrame, text_columns: List[str]) -> pd.DataFrame:
        """Clean text fields"""
        df_clean = df.copy()
        
        for col in text_columns:
            if col in df_clean.columns:
                df_clean[col] = df_clean[col].astype(str).str.strip()
                df_clean[col] = df_clean[col].replace(['nan', 'None', ''], np.nan)
        
        logger.info(f"Cleaned {len(text_columns)} text columns")
        return df_clean


class FeatureEngineer:
    """Generate derived features for ML models"""
    
    @staticmethod
    def calculate_task_velocity(df: pd.DataFrame, group_by: str = 'sprint_id') -> pd.DataFrame:
        """
        Calculate task velocity per sprint/period
        
        Args:
            df: DataFrame with task data
            group_by: Column to group by (sprint_id, week, etc.)
            
        Returns:
            DataFrame with velocity metrics
        """
        if group_by not in df.columns:
            logger.warning(f"Column {group_by} not found in DataFrame")
            return df
        
        velocity_df = df.groupby(group_by).agg({
            'story_points': 'sum',
            'task_id': 'count',
            'completed_at': lambda x: x.notna().sum()
        }).reset_index()
        
        velocity_df.columns = [group_by, 'total_points', 'total_tasks', 'completed_tasks']
        velocity_df['velocity'] = velocity_df['total_points'] / velocity_df['total_tasks'].replace(0, 1)
        velocity_df['completion_rate'] = velocity_df['completed_tasks'] / velocity_df['total_tasks'].replace(0, 1)
        
        logger.info(f"Calculated velocity for {len(velocity_df)} groups")
        return velocity_df
    
    @staticmethod
    def calculate_utilization_rate(df: pd.DataFrame) -> pd.DataFrame:
        """Calculate resource utilization rate"""
        df_util = df.copy()
        
        if 'actual_hours' in df_util.columns and 'allocated_hours' in df_util.columns:
            df_util['utilization_rate'] = (
                df_util['actual_hours'] / df_util['allocated_hours'].replace(0, 1)
            ).clip(0, 2)  # Cap at 200% utilization
            
            df_util['is_overallocated'] = df_util['utilization_rate'] > 1.0
            df_util['is_underutilized'] = df_util['utilization_rate'] < 0.7
        
        logger.info("Calculated utilization rates")
        return df_util
    
    @staticmethod
    def calculate_bug_reopen_ratio(df: pd.DataFrame) -> pd.DataFrame:
        """Calculate bug reopen ratio"""
        bug_df = df[df['is_bug'] == True].copy() if 'is_bug' in df.columns else df.copy()
        
        if 'reopen_count' in bug_df.columns:
            bug_stats = bug_df.groupby('project_id').agg({
                'task_id': 'count',
                'reopen_count': 'sum'
            }).reset_index()
            
            bug_stats.columns = ['project_id', 'total_bugs', 'total_reopens']
            bug_stats['reopen_ratio'] = (
                bug_stats['total_reopens'] / bug_stats['total_bugs'].replace(0, 1)
            )
        
        logger.info("Calculated bug reopen ratios")
        return bug_stats
    
    @staticmethod
    def calculate_cycle_time(df: pd.DataFrame) -> pd.DataFrame:
        """Calculate task cycle time"""
        df_cycle = df.copy()
        
        if 'created_at' in df_cycle.columns and 'completed_at' in df_cycle.columns:
            df_cycle['created_at'] = pd.to_datetime(df_cycle['created_at'])
            df_cycle['completed_at'] = pd.to_datetime(df_cycle['completed_at'])
            
            df_cycle['cycle_time_days'] = (
                df_cycle['completed_at'] - df_cycle['created_at']
            ).dt.total_seconds() / 86400
            
            # Remove negative values
            df_cycle.loc[df_cycle['cycle_time_days'] < 0, 'cycle_time_days'] = np.nan
        
        logger.info("Calculated cycle times")
        return df_cycle
    
    @staticmethod
    def calculate_schedule_variance(df: pd.DataFrame) -> pd.DataFrame:
        """Calculate schedule variance (planned vs actual)"""
        df_var = df.copy()
        
        if 'planned_end_date' in df_var.columns and 'actual_end_date' in df_var.columns:
            df_var['planned_end_date'] = pd.to_datetime(df_var['planned_end_date'])
            df_var['actual_end_date'] = pd.to_datetime(df_var['actual_end_date'])
            
            df_var['schedule_variance_days'] = (
                df_var['actual_end_date'] - df_var['planned_end_date']
            ).dt.total_seconds() / 86400
            
            df_var['is_delayed'] = df_var['schedule_variance_days'] > 0
        
        logger.info("Calculated schedule variance")
        return df_var
    
    @staticmethod
    def calculate_cost_variance(df: pd.DataFrame) -> pd.DataFrame:
        """Calculate cost variance"""
        df_cost = df.copy()
        
        if 'planned_budget' in df_cost.columns and 'actual_cost' in df_cost.columns:
            df_cost['cost_variance'] = df_cost['actual_cost'] - df_cost['planned_budget']
            df_cost['cost_variance_percent'] = (
                df_cost['cost_variance'] / df_cost['planned_budget'].replace(0, 1) * 100
            )
            df_cost['is_over_budget'] = df_cost['cost_variance'] > 0
        
        logger.info("Calculated cost variance")
        return df_cost
    
    @staticmethod
    def create_time_based_features(df: pd.DataFrame, date_column: str = 'created_at') -> pd.DataFrame:
        """Create time-based features"""
        df_time = df.copy()
        
        if date_column in df_time.columns:
            df_time[date_column] = pd.to_datetime(df_time[date_column])
            
            df_time['day_of_week'] = df_time[date_column].dt.dayofweek
            df_time['week_of_year'] = df_time[date_column].dt.isocalendar().week
            df_time['month'] = df_time[date_column].dt.month
            df_time['quarter'] = df_time[date_column].dt.quarter
            df_time['is_weekend'] = df_time['day_of_week'].isin([5, 6])
        
        logger.info("Created time-based features")
        return df_time
    
    @staticmethod
    def create_lag_features(df: pd.DataFrame, columns: List[str], periods: List[int] = [1, 2, 3]) -> pd.DataFrame:
        """Create lag features for time series"""
        df_lag = df.copy()
        
        for col in columns:
            if col not in df_lag.columns:
                continue
            
            for period in periods:
                df_lag[f'{col}_lag_{period}'] = df_lag[col].shift(period)
        
        logger.info(f"Created lag features for {len(columns)} columns")
        return df_lag
    
    @staticmethod
    def create_rolling_features(df: pd.DataFrame, columns: List[str], windows: List[int] = [3, 7, 14]) -> pd.DataFrame:
        """Create rolling window features"""
        df_roll = df.copy()
        
        for col in columns:
            if col not in df_roll.columns or not pd.api.types.is_numeric_dtype(df_roll[col]):
                continue
            
            for window in windows:
                df_roll[f'{col}_rolling_mean_{window}'] = df_roll[col].rolling(window=window).mean()
                df_roll[f'{col}_rolling_std_{window}'] = df_roll[col].rolling(window=window).std()
        
        logger.info(f"Created rolling features for {len(columns)} columns")
        return df_roll


class DataPipeline:
    """Complete data processing pipeline"""
    
    def __init__(self, jira_client=None):
        self.extractor = DataExtractor(jira_client)
        self.cleaner = DataCleaner()
        self.feature_engineer = FeatureEngineer()
    
    def process_project_data(self, raw_data: pd.DataFrame) -> pd.DataFrame:
        """
        Complete pipeline for processing project data
        
        Args:
            raw_data: Raw project data
            
        Returns:
            Processed DataFrame with features
        """
        logger.info("Starting data processing pipeline")
        
        # Clean data
        df = self.cleaner.handle_missing_values(raw_data)
        df = self.cleaner.remove_duplicates(df)
        df = self.cleaner.normalize_dates(df, ['created_at', 'updated_at', 'completed_at', 'due_date'])
        
        # Engineer features
        df = self.feature_engineer.calculate_cycle_time(df)
        df = self.feature_engineer.create_time_based_features(df)
        
        if 'project_id' in df.columns:
            df = self.feature_engineer.calculate_schedule_variance(df)
            df = self.feature_engineer.calculate_cost_variance(df)
        
        logger.info(f"Data processing complete. Final shape: {df.shape}")
        return df
    
    def process_resource_data(self, raw_data: pd.DataFrame) -> pd.DataFrame:
        """Process resource utilization data"""
        logger.info("Processing resource data")
        
        df = self.cleaner.handle_missing_values(raw_data)
        df = self.feature_engineer.calculate_utilization_rate(df)
        
        logger.info(f"Resource data processing complete. Shape: {df.shape}")
        return df
    
    def process_task_data(self, raw_data: pd.DataFrame) -> pd.DataFrame:
        """Process task data"""
        logger.info("Processing task data")
        
        df = self.cleaner.handle_missing_values(raw_data)
        df = self.cleaner.normalize_dates(df, ['created_at', 'completed_at', 'due_date'])
        df = self.feature_engineer.calculate_cycle_time(df)
        df = self.feature_engineer.create_time_based_features(df)
        
        logger.info(f"Task data processing complete. Shape: {df.shape}")
        return df
