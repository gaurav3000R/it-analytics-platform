// Base types
export interface Project {
  id: string
  project_id: string
  name: string
  description?: string
  project_type?: string
  project_manager?: string
  team_size?: number
  project_budget_usd?: number
  budget?: number
  estimated_timeline_months?: number
  complexity_score?: number
  team_experience_level?: string
  risk_level?: string
  risk_score?: number
  status?: string
  created_at?: string
  updated_at?: string
  ai_risk_analysis?: string
  ai_recommendations?: string
  ai_insights_updated_at?: string
}

export interface RiskScore {
  id: string
  project_id: string
  overall_risk_score: number
  schedule_risk: number
  budget_risk: number
  resource_risk: number
  technical_risk: number
  date: string
  predicted_at: string
}

export interface Anomaly {
  id: string
  project_id: string
  anomaly_type: string
  severity: string
  description: string
  metric_value: number
  expected_range: string
  detected_at: string
  resolved: boolean
}

export interface Alert {
  id: string
  project_id: string
  alert_type: string
  severity: string
  message: string
  triggered_at: string
  acknowledged: boolean
  resolved: boolean
}

// Dashboard types
export interface AnalyticsOverview {
  total_projects: number
  total_employees: number
  total_budget: number
  avg_team_size: number
  avg_risk_score: number
  high_risk_projects: number
  medium_risk_projects: number
  low_risk_projects: number
  recent_anomalies: Anomaly[]
  utilization_alerts: Alert[]
  cost_alerts: Alert[]
  trending_risks: TrendingRisk[]
}

export interface RiskDashboard {
  total_projects: number
  high_risk_count: number
  medium_risk_count: number
  low_risk_count: number
  average_risk_score: number
  risk_distribution: RiskDistribution
  recent_predictions: RiskScore[]
  top_risk_projects: Project[]
}

export interface RiskDistribution {
  high: number
  medium: number
  low: number
}

export interface TrendingRisk {
  project_id: string
  project_name: string
  risk_score: number
  trend: 'up' | 'down' | 'stable'
  change_percentage: number
}

// AI Insights types
export interface AIRiskAnalysis {
  project_id: string
  analysis: {
    full_text: string
    risk_factors?: string[]
    mitigation_strategies?: string[]
  }
  raw_analysis: string
  generated_at: string
}

export interface AIRecommendations {
  project_id: string
  recommendations: string[]
  raw_recommendations: string
  generated_at: string
}

export interface AIPortfolioTrends {
  analysis: {
    full_text: string
  }
  raw_analysis: string
  generated_at: string
}

export interface AIExecutiveSummary {
  summary: {
    full_text: string
  }
  raw_summary: string
  generated_at: string
}

// Bug Analysis types
export interface BugAnalysis {
  project_id: string
  total_bugs: number
  critical_bugs: number
  bug_density: number
  resolution_rate: number
  avg_resolution_time: number
  bug_trends: BugTrend[]
}

export interface BugTrend {
  date: string
  count: number
  severity: string
}

// Resource Utilization types
export interface ResourceAnalysis {
  total_resources: number
  avg_utilization: number
  over_utilized_count: number
  under_utilized_count: number
  utilization_by_project: ProjectUtilization[]
}

export interface ProjectUtilization {
  project_id: string
  project_name: string
  utilization_percentage: number
  team_size: number
  status: 'optimal' | 'over' | 'under'
}

export interface RebalancingSuggestion {
  from_project_id: string
  to_project_id: string
  resource_count: number
  reason: string
  impact_score: number
}

// Cost Forecasting types
export interface CostForecast {
  project_id: string
  current_budget: number
  projected_cost: number
  overrun_probability: number
  estimated_overrun_amount: number
  confidence_level: number
  forecast_date: string
}

export interface BudgetAlert {
  project_id: string
  project_name: string
  alert_type: string
  severity: string
  current_spend: number
  budget: number
  variance_percentage: number
  message: string
}

// API Response types
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
