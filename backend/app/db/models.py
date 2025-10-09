"""
Database Models for IT Analytics Platform - Risk Early Warning System
"""
from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel, Relationship
from enum import Enum


class ProjectStatus(str, Enum):
    """Project status enumeration"""
    PLANNING = "planning"
    IN_PROGRESS = "in_progress"
    AT_RISK = "at_risk"
    DELAYED = "delayed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class RiskLevel(str, Enum):
    """Risk level enumeration"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TaskPriority(str, Enum):
    """Task priority enumeration"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TaskStatus(str, Enum):
    """Task status enumeration"""
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    IN_REVIEW = "in_review"
    BLOCKED = "blocked"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


# Base Models
class TimestampModel(SQLModel):
    """Base model with timestamps"""
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# User Models
class User(TimestampModel, table=True):
    """User model"""
    __tablename__ = "users"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    username: str = Field(unique=True, index=True)
    full_name: str
    hashed_password: str
    is_active: bool = Field(default=True)
    is_superuser: bool = Field(default=False)
    role: str = Field(default="developer")  # developer, manager, admin
    
    # Skills and experience
    skills: Optional[str] = Field(default=None)  # JSON string
    experience_years: Optional[float] = Field(default=0.0)
    department: Optional[str] = Field(default=None)
    
    # Relationships
    assigned_tasks: list["Task"] = Relationship(back_populates="assignee")
    managed_projects: list["Project"] = Relationship(back_populates="manager")


# Project Models
class Project(TimestampModel, table=True):
    """Project model"""
    __tablename__ = "projects"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    description: Optional[str] = Field(default=None)
    status: ProjectStatus = Field(default=ProjectStatus.PLANNING)
    
    # Dates
    start_date: Optional[datetime] = Field(default=None)
    planned_end_date: Optional[datetime] = Field(default=None)
    actual_end_date: Optional[datetime] = Field(default=None)
    
    # Budget and resources
    planned_budget: Optional[float] = Field(default=0.0)
    actual_cost: Optional[float] = Field(default=0.0)
    allocated_resources: Optional[int] = Field(default=0)
    
    # Risk metrics
    risk_score: Optional[float] = Field(default=0.0)
    risk_level: Optional[RiskLevel] = Field(default=RiskLevel.LOW)
    delay_probability: Optional[float] = Field(default=0.0)
    cost_overrun_probability: Optional[float] = Field(default=0.0)
    
    # Foreign keys
    manager_id: Optional[int] = Field(default=None, foreign_key="users.id")
    
    # Relationships
    manager: Optional[User] = Relationship(back_populates="managed_projects")
    tasks: list["Task"] = Relationship(back_populates="project")
    sprints: list["Sprint"] = Relationship(back_populates="project")
    project_metrics: list["ProjectMetrics"] = Relationship(back_populates="project")


# Sprint Models
class Sprint(TimestampModel, table=True):
    """Sprint model"""
    __tablename__ = "sprints"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    sprint_number: int
    
    # Dates
    start_date: datetime
    end_date: datetime
    
    # Metrics
    planned_points: Optional[int] = Field(default=0)
    completed_points: Optional[int] = Field(default=0)
    velocity: Optional[float] = Field(default=0.0)
    
    # Foreign keys
    project_id: int = Field(foreign_key="projects.id")
    
    # Relationships
    project: Optional[Project] = Relationship(back_populates="sprints")
    tasks: list["Task"] = Relationship(back_populates="sprint")


# Task Models
class Task(TimestampModel, table=True):
    """Task model"""
    __tablename__ = "tasks"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(index=True)
    description: Optional[str] = Field(default=None)
    task_type: str = Field(default="feature")  # feature, bug, tech_debt, etc.
    status: TaskStatus = Field(default=TaskStatus.TODO)
    priority: TaskPriority = Field(default=TaskPriority.MEDIUM)
    
    # Time tracking
    estimated_hours: Optional[float] = Field(default=0.0)
    actual_hours: Optional[float] = Field(default=0.0)
    story_points: Optional[int] = Field(default=0)
    
    # Dates
    due_date: Optional[datetime] = Field(default=None)
    completed_at: Optional[datetime] = Field(default=None)
    
    # Bug tracking
    is_bug: bool = Field(default=False)
    bug_severity: Optional[str] = Field(default=None)
    reopen_count: int = Field(default=0)
    
    # Risk indicators
    is_blocked: bool = Field(default=False)
    has_dependencies: bool = Field(default=False)
    
    # Foreign keys
    project_id: int = Field(foreign_key="projects.id")
    sprint_id: Optional[int] = Field(default=None, foreign_key="sprints.id")
    assignee_id: Optional[int] = Field(default=None, foreign_key="users.id")
    
    # Relationships
    project: Optional[Project] = Relationship(back_populates="tasks")
    sprint: Optional[Sprint] = Relationship(back_populates="tasks")
    assignee: Optional[User] = Relationship(back_populates="assigned_tasks")


# Metrics Models
class ProjectMetrics(TimestampModel, table=True):
    """Daily/Weekly project metrics"""
    __tablename__ = "project_metrics"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    project_id: int = Field(foreign_key="projects.id")
    metric_date: datetime = Field(index=True)
    
    # Velocity metrics
    sprint_velocity: Optional[float] = Field(default=0.0)
    avg_velocity_last_3_sprints: Optional[float] = Field(default=0.0)
    velocity_trend: Optional[str] = Field(default="stable")  # improving, declining, stable
    
    # Task metrics
    total_tasks: int = Field(default=0)
    completed_tasks: int = Field(default=0)
    in_progress_tasks: int = Field(default=0)
    blocked_tasks: int = Field(default=0)
    completion_rate: Optional[float] = Field(default=0.0)
    
    # Bug metrics
    total_bugs: int = Field(default=0)
    open_bugs: int = Field(default=0)
    closed_bugs: int = Field(default=0)
    bug_reopen_rate: Optional[float] = Field(default=0.0)
    
    # Resource metrics
    team_size: int = Field(default=0)
    avg_utilization_rate: Optional[float] = Field(default=0.0)
    over_allocated_resources: int = Field(default=0)
    
    # Time metrics
    avg_task_cycle_time: Optional[float] = Field(default=0.0)
    avg_time_to_resolve_bug: Optional[float] = Field(default=0.0)
    
    # Risk indicators
    days_behind_schedule: Optional[int] = Field(default=0)
    budget_variance_percent: Optional[float] = Field(default=0.0)
    
    # Relationships
    project: Optional[Project] = Relationship(back_populates="project_metrics")


class ResourceUtilization(TimestampModel, table=True):
    """Resource utilization tracking"""
    __tablename__ = "resource_utilization"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    project_id: int = Field(foreign_key="projects.id")
    week_start_date: datetime = Field(index=True)
    
    # Utilization metrics
    allocated_hours: float = Field(default=40.0)
    actual_hours: float = Field(default=0.0)
    utilization_rate: float = Field(default=0.0)
    
    # Task metrics
    tasks_assigned: int = Field(default=0)
    tasks_completed: int = Field(default=0)
    avg_task_completion_time: Optional[float] = Field(default=0.0)
    
    # Quality metrics
    bugs_created: int = Field(default=0)
    code_review_comments: int = Field(default=0)
    
    # Risk flags
    is_overallocated: bool = Field(default=False)
    is_underutilized: bool = Field(default=False)


# ML Models Output Storage
class RiskPrediction(TimestampModel, table=True):
    """ML model predictions for risks"""
    __tablename__ = "risk_predictions"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    project_id: int = Field(foreign_key="projects.id")
    prediction_date: datetime = Field(default_factory=datetime.utcnow, index=True)
    
    # Delay predictions
    delay_risk_score: float = Field(default=0.0)
    predicted_delay_days: Optional[int] = Field(default=0)
    delay_confidence: float = Field(default=0.0)
    
    # Cost predictions
    cost_overrun_risk_score: float = Field(default=0.0)
    predicted_cost_overrun_percent: Optional[float] = Field(default=0.0)
    cost_confidence: float = Field(default=0.0)
    
    # Resource predictions
    resource_bottleneck_risk: float = Field(default=0.0)
    predicted_bottleneck_resources: Optional[str] = Field(default=None)  # JSON
    
    # Overall risk
    overall_risk_score: float = Field(default=0.0)
    risk_level: RiskLevel = Field(default=RiskLevel.LOW)
    
    # Model metadata
    model_version: str = Field(default="1.0")
    model_type: str = Field(default="ensemble")
    features_used: Optional[str] = Field(default=None)  # JSON


class AnomalyDetection(TimestampModel, table=True):
    """Anomaly detection results"""
    __tablename__ = "anomaly_detections"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    project_id: Optional[int] = Field(default=None, foreign_key="projects.id")
    user_id: Optional[int] = Field(default=None, foreign_key="users.id")
    detection_date: datetime = Field(default_factory=datetime.utcnow, index=True)
    
    # Anomaly details
    anomaly_type: str  # velocity_drop, spike_in_bugs, resource_overload, etc.
    severity: RiskLevel
    anomaly_score: float
    
    # Context
    metric_name: str
    expected_value: float
    actual_value: float
    deviation_percent: float
    
    # Description
    description: str
    recommended_action: Optional[str] = Field(default=None)
    
    # Status
    is_acknowledged: bool = Field(default=False)
    is_resolved: bool = Field(default=False)
    resolved_at: Optional[datetime] = Field(default=None)


# Kaizen Log Integration
class KaizenLog(TimestampModel, table=True):
    """Kaizen logs from external sources"""
    __tablename__ = "kaizen_logs"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    project_id: Optional[int] = Field(default=None, foreign_key="projects.id")
    log_date: datetime = Field(index=True)
    
    # Log details
    log_type: str  # meeting, improvement, issue, decision
    category: str
    title: str
    description: str
    
    # Participants
    participants: Optional[str] = Field(default=None)  # JSON
    
    # Outcomes
    action_items: Optional[str] = Field(default=None)  # JSON
    impact: Optional[str] = Field(default=None)
    
    # Status
    status: str = Field(default="open")
    
    # Raw data
    raw_data: Optional[str] = Field(default=None)  # JSON


# Jira Integration
class JiraSync(TimestampModel, table=True):
    """Jira synchronization tracking"""
    __tablename__ = "jira_sync"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    project_id: int = Field(foreign_key="projects.id")
    jira_project_key: str
    
    # Sync details
    last_sync_at: datetime
    sync_status: str = Field(default="success")
    records_synced: int = Field(default=0)
    
    # Errors
    error_message: Optional[str] = Field(default=None)
    
    # Configuration
    sync_config: Optional[str] = Field(default=None)  # JSON


# Dashboard Configuration
class DashboardConfig(TimestampModel, table=True):
    """User dashboard configurations"""
    __tablename__ = "dashboard_configs"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", unique=True)
    
    # Layout configuration
    layout: str  # JSON configuration for dashboard layout
    theme: str = Field(default="light")
    
    # Widget preferences
    visible_widgets: str  # JSON array of widget IDs
    widget_settings: Optional[str] = Field(default=None)  # JSON
    
    # Filters
    default_filters: Optional[str] = Field(default=None)  # JSON
    
    # Notifications
    notification_preferences: Optional[str] = Field(default=None)  # JSON
