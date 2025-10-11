import { apiClient } from './api-client'
import { API_ENDPOINTS } from '@/lib/constants'
import type {
  Project,
  ProjectsListResponse,
  ProjectCSVSummaryResponse,
  AnalyticsOverviewResponse,
  RiskDashboardResponse,
  RiskDashboardOverviewResponse,
  RiskStatisticsResponse,
  RiskDashboardProjectsResponse,
  RiskTrendsResponse,
  FlaggedProjectsResponse,
  AIExecutiveSummaryResponse,
  AIPortfolioTrendsResponse,
  AIServiceStatusResponse,
  BugTrackerDashboardResponse,
  BugTrackerListResponse,
  BugQualityRisksResponse,
  BugResolutionMetricsResponse,
  ResourceUtilizationDashboardResponse,
  ResourceUtilizationAlertsResponse,
  CostSpendingTrendsResponse,
  AnomaliesDashboardResponse,
  AnomaliesListResponse,
  HealthResponse,
} from '@/types'

export const projectsApi = {
  getAll: () => apiClient.get<Project[]>(API_ENDPOINTS.PROJECTS),
  getById: (id: string) => apiClient.get<Project>(API_ENDPOINTS.PROJECT_BY_ID(id)),
  uploadCsv: (file: File, onProgress?: (progress: number) => void) =>
    apiClient.uploadFile<{ message: string; projects_loaded: number }>(
      API_ENDPOINTS.UPLOAD_CSV,
      file,
      onProgress
    ),
  loadDefaultCsv: () =>
    apiClient.post<{ message: string; projects_loaded: number }>(API_ENDPOINTS.LOAD_DEFAULT_CSV),
  generateSampleData: (count: number = 100) =>
    apiClient.post<{ message: string; projects_generated: number }>(
      API_ENDPOINTS.GENERATE_SAMPLE_DATA,
      { count }
    ),
  getCsvSummary: () =>
    apiClient.get<ProjectCSVSummaryResponse>(API_ENDPOINTS.CSV_SUMMARY),
}

export const analyticsApi = {
  getOverview: () => apiClient.get<AnalyticsOverviewResponse>(API_ENDPOINTS.ANALYTICS_OVERVIEW),
  getRiskDashboard: () => apiClient.get<RiskDashboardResponse>(API_ENDPOINTS.RISK_DASHBOARD),
}

export const riskDashboardApi = {
  getOverview: () => apiClient.get<RiskDashboardOverviewResponse>(API_ENDPOINTS.RISK_DASHBOARD_OVERVIEW),
  getStatistics: () => apiClient.get<RiskStatisticsResponse>(API_ENDPOINTS.RISK_DASHBOARD_STATISTICS),
  getProjects: () => apiClient.get<RiskDashboardProjectsResponse>(API_ENDPOINTS.RISK_DASHBOARD_PROJECTS),
  getTrends: (days?: number) => apiClient.get<RiskTrendsResponse>(`${API_ENDPOINTS.RISK_DASHBOARD_TRENDS}${days ? `?days=${days}` : ''}`),
  getFlaggedProjects: () => apiClient.get<FlaggedProjectsResponse>(API_ENDPOINTS.RISK_DASHBOARD_FLAGGED_PROJECTS),
}

export const risksApi = {
  trainModel: () => apiClient.post<{ message: string; accuracy: number }>(API_ENDPOINTS.RISKS_TRAIN_MODEL),
  predictRisk: (projectId: string) =>
    apiClient.get<{ project_id: string; risk_score: number; risk_factors: Record<string, unknown> }>(
      API_ENDPOINTS.RISKS_PREDICT(projectId)
    ),
  getDashboard: () => apiClient.get<{ total_projects: number; high_risk_projects: number; medium_risk_projects: number; low_risk_projects: number; projects: Project[] }>(API_ENDPOINTS.RISKS_DASHBOARD),
  detectAnomalies: () => apiClient.post<{ message: string; anomalies_detected: number }>(API_ENDPOINTS.RISKS_DETECT_ANOMALIES),
  getAnomaliesByProject: (projectId: string) =>
    apiClient.get<AnomaliesListResponse>(API_ENDPOINTS.RISKS_ANOMALIES_PROJECT(projectId)),
  getAnomaliesByEmployee: (employeeId: string) =>
    apiClient.get<AnomaliesListResponse>(API_ENDPOINTS.RISKS_ANOMALIES_EMPLOYEE(employeeId)),
  getAnomaliesDashboard: () => apiClient.get<AnomaliesDashboardResponse>(API_ENDPOINTS.RISKS_ANOMALIES_DASHBOARD),
  getAnomaliesList: () => apiClient.get<AnomaliesListResponse>(API_ENDPOINTS.RISKS_ANOMALIES_LIST),
}

export const aiInsightsApi = {
  getExecutiveSummary: () =>
    apiClient.get<AIExecutiveSummaryResponse>(API_ENDPOINTS.AI_EXECUTIVE_SUMMARY),
  getPortfolioTrends: () =>
    apiClient.get<AIPortfolioTrendsResponse>(API_ENDPOINTS.AI_PORTFOLIO_TRENDS),
  getServiceStatus: () =>
    apiClient.get<AIServiceStatusResponse>(API_ENDPOINTS.AI_SERVICE_STATUS),
  getProjectInsights: (projectId: string) =>
    apiClient.get<Record<string, unknown>>(API_ENDPOINTS.AI_PROJECT_INSIGHTS(projectId)),
  getDashboard: () => apiClient.get<Record<string, unknown>>(API_ENDPOINTS.AI_DASHBOARD),
}

export const bugTrackerApi = {
  getDashboard: () => apiClient.get<BugTrackerDashboardResponse>(API_ENDPOINTS.BUG_DASHBOARD),
  getList: (page?: number, perPage?: number) => {
    const params = new URLSearchParams()
    if (page) params.append('page', page.toString())
    if (perPage) params.append('per_page', perPage.toString())
    const query = params.toString()
    return apiClient.get<BugTrackerListResponse>(`${API_ENDPOINTS.BUG_LIST}${query ? `?${query}` : ''}`)
  },
  getQualityRisks: () => apiClient.get<BugQualityRisksResponse>(API_ENDPOINTS.BUG_QUALITY_RISKS),
  getResolutionMetrics: () => apiClient.get<BugResolutionMetricsResponse>(API_ENDPOINTS.BUG_RESOLUTION_METRICS),
}

export const resourceApi = {
  getDashboard: () => apiClient.get<ResourceUtilizationDashboardResponse>(API_ENDPOINTS.RESOURCE_DASHBOARD),
  getAlerts: () => apiClient.get<ResourceUtilizationAlertsResponse>(API_ENDPOINTS.RESOURCE_ALERTS),
  acknowledgeAlert: (alertId: string) =>
    apiClient.post<{ message: string }>(API_ENDPOINTS.RESOURCE_ALERT_ACKNOWLEDGE(alertId)),
  getEmployee: (employeeId: string) =>
    apiClient.get<Record<string, unknown>>(API_ENDPOINTS.RESOURCE_EMPLOYEE(employeeId)),
  getOverbookingReport: () => apiClient.get<Record<string, unknown>>(API_ENDPOINTS.RESOURCE_OVERBOOKING_REPORT),
}

export const costApi = {
  getSpendingTrends: (projectId?: string) => {
    const endpoint = projectId 
      ? `${API_ENDPOINTS.COST_SPENDING_TRENDS}/${projectId}`
      : API_ENDPOINTS.COST_SPENDING_TRENDS
    return apiClient.get<CostSpendingTrendsResponse>(endpoint)
  },
  getForecastHistory: (projectId: string) =>
    apiClient.get<Record<string, unknown>>(API_ENDPOINTS.COST_FORECAST_HISTORY(projectId)),
}

export const healthApi = {
  getHealth: () => apiClient.get<HealthResponse>(API_ENDPOINTS.HEALTH),
}

export const mlApi = {
  getHealth: () => apiClient.get<Record<string, unknown>>(API_ENDPOINTS.ML_HEALTH),
  getModelInfo: () => apiClient.get<Record<string, unknown>>(API_ENDPOINTS.ML_MODEL_INFO),
  predict: (data: Record<string, unknown>) => apiClient.post<Record<string, unknown>>(API_ENDPOINTS.ML_PREDICT, data),
  predictBatch: (data: Record<string, unknown>) => apiClient.post<Record<string, unknown>>(API_ENDPOINTS.ML_PREDICT_BATCH, data),
  analyze: (data: Record<string, unknown>) => apiClient.post<Record<string, unknown>>(API_ENDPOINTS.ML_ANALYZE, data),
}
