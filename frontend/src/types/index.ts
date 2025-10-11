// ============================================================================
// BASE TYPES - Core entities used across the application
// ============================================================================

export interface Project {
  id: number
  project_id: number
  name: string
  description?: string
  project_type?: string
  project_manager?: string
  team_size?: number
  project_budget_usd?: number
  estimated_timeline_months?: number
  complexity_score?: number
  team_experience_level?: string
  risk_level?: string
  overall_risk_score?: number
  status?: string
  created_at?: string
  updated_at?: string
}

export interface Employee {
  id: number
  name: string
  employee_id?: string
  role?: string
  project_id?: number
  project_name?: string
}

// ============================================================================
// ANALYTICS OVERVIEW - Main dashboard metrics
// API: /api/v1/analytics/overview
// ============================================================================

export interface AnalyticsOverviewResponse {
  summary: {
    total_projects: number
    total_employees: number
    recent_activity_logs: number
    recent_anomalies: number
  }
  risk_distribution: {
    critical: number
    high: number
    medium: number
    low: number
    very_low: number
  }
  period: string
  generated_at: string
}

// ============================================================================
// RISK DASHBOARD - Comprehensive risk analysis
// API: /api/v1/analytics/risk-dashboard
// ============================================================================

export interface RiskDashboardResponse {
  summary: RiskDashboardSummary
  risk_overview: RiskOverview
  top_risk_projects: TopRiskProject[]
  risk_trends: RiskTrend[]
  recommendations: RiskRecommendation[]
}

export interface RiskDashboardSummary {
  total_projects: number
  avg_risk_score: number
  risk_distribution: {
    critical: number
    high: number
    medium: number
    low: number
    very_low: number
  }
  high_risk_projects: number
  critical_projects: number
  utilization_alerts: number
  cost_alerts: number
  recent_anomalies: number
}

export interface RiskOverview {
  risk_distribution: {
    critical: number
    high: number
    medium: number
    low: number
    very_low: number
  }
  component_averages: {
    schedule_risk: number
    budget_risk: number
    quality_risk: number
    resource_risk: number
    technical_risk: number
  }
  flagged_projects: {
    irregular_velocity: number
    inconsistent_logging: number
    overbudget: number
    high_bug_rate: number
  }
}

export interface TopRiskProject {
  project_id: number
  project_name: string
  risk_score: number
  risk_level: string
  schedule_risk: number
  budget_risk: number
  quality_risk: number
  resource_risk: number
  technical_risk: number
  key_metrics: {
    velocity_deviation: number
    logging_consistency: number
    budget_utilization: number
    team_utilization: number
    bug_density: number
  }
  flags: {
    irregular_velocity: boolean
    inconsistent_logging: boolean
    overbudget: boolean
    high_bug_rate: boolean
  }
}

export interface RiskTrend {
  date: string
  avg_risk_score: number
  high_risk_count: number
  critical_count: number
}

export interface RiskRecommendation {
  priority: string
  category: string
  project_id?: number
  project_name?: string
  finding: string
  recommendation: string
  estimated_impact?: string
}

// ============================================================================
// RISK DASHBOARD SPECIFIC ENDPOINTS
// ============================================================================

// API: /api/v1/risk-dashboard/overview
export interface RiskDashboardOverviewResponse {
  total_projects: number
  high_risk_count: number
  medium_risk_count: number
  low_risk_count: number
  average_risk_score: number
}

// API: /api/v1/risk-dashboard/statistics
export interface RiskStatisticsResponse {
  total_projects: number
  risk_distribution: Record<string, number>
  avg_risk_score: number
  component_breakdown: {
    schedule_risk: number
    budget_risk: number
    quality_risk: number
    resource_risk: number
    technical_risk: number
  }
}

// API: /api/v1/risk-dashboard/projects
export interface RiskDashboardProjectsResponse {
  projects: RiskDashboardProject[]
  total_count: number
}

export interface RiskDashboardProject {
  project_id: number
  project_name: string
  risk_score: number
  risk_level: string
  schedule_risk: number
  budget_risk: number
  quality_risk: number
  resource_risk: number
  technical_risk: number
}

// API: /api/v1/risk-dashboard/trends
export interface RiskTrendsResponse {
  trends: RiskTrend[]
  period_days: number
}

// API: /api/v1/risk-dashboard/flagged-projects
export interface FlaggedProjectsResponse {
  flagged_projects: FlaggedProject[]
  flag_summary: {
    irregular_velocity: number
    inconsistent_logging: number
    overbudget: number
    high_bug_rate: number
  }
}

export interface FlaggedProject {
  project_id: number
  project_name: string
  flags: {
    irregular_velocity: boolean
    inconsistent_logging: boolean
    overbudget: boolean
    high_bug_rate: boolean
  }
  risk_score: number
  risk_level: string
}

// ============================================================================
// AI INSIGHTS - AI-powered analysis and recommendations
// ============================================================================

// API: /api/v1/ai-insights/executive-summary
export interface AIExecutiveSummaryResponse {
  overview: {
    total_projects: number
    active_projects: number
    completed_projects: number
    high_risk_count: number
    high_risk_percentage: number
  }
  financial: {
    total_budget: number
    total_spend: number
    budget_utilization: number
    remaining_budget: number
  }
  key_findings: string[]
  generated_at: string
  analysis_method: string
  ai_insights: {
    full_text: string
  }
}

// API: /api/v1/ai-insights/portfolio-trends
export interface AIPortfolioTrendsResponse {
  total_projects: number
  risk_distribution: Record<string, number>
  project_type_distribution: Record<string, number>
  team_experience_distribution: Record<string, number>
  status_distribution: Record<string, number>
  averages: {
    complexity: number
    team_size: number
    budget: number
  }
  insights: {
    high_risk_percentage: number
    total_budget: number
    most_common_type: string
    most_common_experience: string
  }
  recommendations: AIRecommendation[]
  analysis_method: string
  ai_generated: boolean
  ai_error?: string
}

export interface AIRecommendation {
  priority: string
  category: string
  finding: string
  recommendation: string
}

// API: /api/v1/ai-insights/service-status
export interface AIServiceStatusResponse {
  ai_enabled: boolean
  service_available: boolean
  features: {
    portfolio_trends: string
    executive_summary: string
    risk_analysis: string
    recommendations: string
  }
  note: string
}

// ============================================================================
// PROJECTS - Project management and details
// ============================================================================

// API: /api/v1/projects/
export interface ProjectsListResponse {
  projects: Project[]
  total: number
}

// API: /api/v1/projects/csv-summary
export interface ProjectCSVSummaryResponse {
  total_rows: number
  total_projects: number
  status_breakdown: Record<string, number>
  risk_distribution: Record<string, number>
  total_budget: number
  avg_team_size: number
  avg_complexity: number
  date_range: {
    earliest: string
    latest: string
  }
}

// ============================================================================
// BUG TRACKER - Bug tracking and quality metrics
// ============================================================================

// API: /api/v1/bug-tracker/dashboard
export interface BugTrackerDashboardResponse {
  summary: {
    total_bugs: number
    open_bugs: number
    resolved_bugs: number
    critical_bugs: number
    avg_resolution_time_days: number
  }
  severity_distribution: Record<string, number>
  status_distribution: Record<string, number>
  priority_distribution: Record<string, number>
  resolution_trends: ResolutionTrend[]
  top_projects_by_bugs: TopProjectByBugs[]
}

export interface ResolutionTrend {
  date: string
  resolved: number
  reported: number
}

export interface TopProjectByBugs {
  project_id: number
  project_name: string
  total_bugs: number
  open_bugs: number
  critical_bugs: number
}

// API: /api/v1/bug-tracker/list
export interface BugTrackerListResponse {
  bugs: Bug[]
  total: number
  page: number
  per_page: number
  total_pages: number
}

export interface Bug {
  id: number
  bug_id: string
  project_id: number
  project_name?: string
  title: string
  description?: string
  severity: string
  priority: string
  status: string
  reported_by?: string
  assigned_to?: string
  reported_at: string
  resolved_at?: string
  resolution_time_days?: number
  tags?: string[]
}

// API: /api/v1/bug-tracker/quality-risks
export interface BugQualityRisksResponse {
  high_risk_projects: BugRiskProject[]
  overall_quality_score: number
  recommendations: string[]
}

export interface BugRiskProject {
  project_id: number
  project_name: string
  total_bugs: number
  critical_bugs: number
  bug_density: number
  quality_risk_score: number
  risk_level: string
}

// API: /api/v1/bug-tracker/metrics/resolution
export interface BugResolutionMetricsResponse {
  overall: {
    avg_resolution_time: number
    median_resolution_time: number
    resolution_rate: number
  }
  by_severity: Record<string, ResolutionMetrics>
  by_priority: Record<string, ResolutionMetrics>
  trends: ResolutionTrendMetrics[]
}

export interface ResolutionMetrics {
  avg_time: number
  count: number
}

export interface ResolutionTrendMetrics {
  period: string
  avg_resolution_time: number
  total_resolved: number
}

// ============================================================================
// RESOURCE UTILIZATION - Team and resource management
// ============================================================================

// API: /api/v1/resource-utilization/dashboard
export interface ResourceUtilizationDashboardResponse {
  summary: {
    total_employees: number
    avg_utilization: number
    over_utilized: number
    under_utilized: number
    optimal_utilization: number
  }
  utilization_distribution: {
    over_utilized: number
    optimal: number
    under_utilized: number
  }
  project_utilization: ProjectResourceUtilization[]
  team_breakdown: TeamBreakdown[]
}

export interface ProjectResourceUtilization {
  project_id: number
  project_name: string
  team_size: number
  avg_utilization: number
  status: string
  over_utilized_count: number
  under_utilized_count: number
}

export interface TeamBreakdown {
  experience_level: string
  count: number
  avg_utilization: number
}

// API: /api/v1/resource-utilization/alerts
export interface ResourceUtilizationAlertsResponse {
  alerts: ResourceAlert[]
  total_alerts: number
  critical_count: number
  warning_count: number
}

export interface ResourceAlert {
  alert_id: string
  type: string
  severity: string
  employee_id: number
  employee_name: string
  project_id?: number
  project_name?: string
  utilization_percentage: number
  message: string
  generated_at: string
}

// ============================================================================
// COST FORECASTING - Budget and spending analysis
// ============================================================================

// API: /api/v1/cost-forecasting/spending-trends
export interface CostSpendingTrendsResponse {
  trends: SpendingTrend[]
  total_budget: number
  total_spent: number
  projected_total: number
}

export interface SpendingTrend {
  period: string
  actual_spend: number
  projected_spend: number
  budget: number
}

// ============================================================================
// ANOMALIES - Anomaly detection and monitoring
// ============================================================================

// API: /api/v1/risks/anomalies/dashboard
export interface AnomaliesDashboardResponse {
  summary: {
    total_anomalies: number
    critical_anomalies: number
    unresolved_anomalies: number
    anomalies_last_24h: number
  }
  by_type: Record<string, number>
  by_severity: Record<string, number>
  recent_anomalies: Anomaly[]
  trends: AnomalyTrend[]
}

export interface Anomaly {
  id: number
  type: string
  severity: string
  description: string
  detected_at: string
  employee?: {
    id: number
    name: string
  }
  project?: {
    id: number | null
    name: string | null
  }
  is_resolved: boolean
  metadata: Record<string, unknown>
}

export interface AnomalyTrend {
  date: string
  count: number
  critical_count: number
}

// API: /api/v1/risks/anomalies/list
export interface AnomaliesListResponse {
  anomalies: Anomaly[]
  total: number
  page: number
  per_page: number
  total_pages: number
}

// ============================================================================
// SYSTEM HEALTH - Application health monitoring
// API: /health
// ============================================================================

export interface HealthResponse {
  status: string
  timestamp: string
  system_metrics: {
    cpu_percent: number
    memory_percent: number
    disk_percent: number
    process_count: number
    load_average: number[]
  }
  integrations: {
    supabase: string
    gemini_ai: string
    database_type: string
  }
}

// ============================================================================
// UTILITY TYPES
// ============================================================================

export interface ApiResponse<T> {
  data: T
  message?: string
  status: string
}

export interface PaginatedResponse<T> {
  data: T[]
  total: number
  page: number
  per_page: number
  total_pages: number
}

export type RiskLevel = 'critical' | 'high' | 'medium' | 'low' | 'very_low'
export type ProjectStatus = 'active' | 'on_hold' | 'completed' | 'planning'
export type SeverityLevel = 'critical' | 'high' | 'medium' | 'low'
export type AlertType = 'over_utilization' | 'under_utilization' | 'missing_logs' | 'budget_overrun'
