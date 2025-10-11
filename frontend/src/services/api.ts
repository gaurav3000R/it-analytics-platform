import { apiClient } from './api-client'
import { API_ENDPOINTS } from '@/lib/constants'
import type {
  Project,
  AnalyticsOverview,
  RiskDashboard,
  AIRiskAnalysis,
  AIRecommendations,
  AIPortfolioTrends,
  AIExecutiveSummary,
  BugAnalysis,
  ResourceAnalysis,
  RebalancingSuggestion,
  CostForecast,
  BudgetAlert,
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
    apiClient.get<{ total_rows: number; columns: string[] }>(API_ENDPOINTS.CSV_SUMMARY),
}

export const analyticsApi = {
  getOverview: () => apiClient.get<AnalyticsOverview>(API_ENDPOINTS.ANALYTICS_OVERVIEW),
  getRiskDashboard: () => apiClient.get<RiskDashboard>(API_ENDPOINTS.RISK_DASHBOARD),
}

export const risksApi = {
  trainModel: () => apiClient.post<{ message: string; accuracy: number }>(API_ENDPOINTS.RISKS_TRAIN_MODEL),
  predictRisk: (projectId: string) =>
    apiClient.get<{ project_id: string; risk_score: number; risk_factors: Record<string, unknown> }>(
      API_ENDPOINTS.RISKS_PREDICT(projectId)
    ),
  getDashboard: () => apiClient.get<RiskDashboard>(API_ENDPOINTS.RISKS_DASHBOARD),
  detectAnomalies: () => apiClient.post<any>(API_ENDPOINTS.RISKS_DETECT_ANOMALIES),
  getAnomaliesByProject: (projectId: string) =>
    apiClient.get<any>(API_ENDPOINTS.RISKS_ANOMALIES_PROJECT(projectId)),
  getAnomaliesByEmployee: (employeeId: string) =>
    apiClient.get<any>(API_ENDPOINTS.RISKS_ANOMALIES_EMPLOYEE(employeeId)),
  getAnomaliesDashboard: () => apiClient.get<any>(API_ENDPOINTS.RISKS_ANOMALIES_DASHBOARD),
  getAnomaliesList: () => apiClient.get<any>(API_ENDPOINTS.RISKS_ANOMALIES_LIST),
}

export const aiInsightsApi = {
  getRiskAnalysis: (projectId: string) =>
    apiClient.post<AIRiskAnalysis>(API_ENDPOINTS.AI_RISK_ANALYSIS(projectId)),
  getRecommendations: (projectId: string) =>
    apiClient.post<AIRecommendations>(API_ENDPOINTS.AI_RECOMMENDATIONS(projectId)),
  getPortfolioTrends: () =>
    apiClient.get<AIPortfolioTrends>(API_ENDPOINTS.AI_PORTFOLIO_TRENDS),
  getExecutiveSummary: () =>
    apiClient.get<AIExecutiveSummary>(API_ENDPOINTS.AI_EXECUTIVE_SUMMARY),
  getProjectInsights: (projectId: string) =>
    apiClient.get<any>(API_ENDPOINTS.AI_PROJECT_INSIGHTS(projectId)),
  getDashboard: () => apiClient.get<any>(API_ENDPOINTS.AI_DASHBOARD),
}

export const bugTrackerApi = {
  analyzeProject: (projectId: string) =>
    apiClient.get<BugAnalysis>(API_ENDPOINTS.BUG_ANALYSIS(projectId)),
  analyzePortfolio: () =>
    apiClient.get<{ total_bugs: number; projects_analyzed: number; summary: Record<string, unknown> }>(
      API_ENDPOINTS.BUG_PORTFOLIO_ANALYSIS
    ),
  getDashboard: () => apiClient.get<any>(API_ENDPOINTS.BUG_DASHBOARD),
}

export const resourceApi = {
  analyze: () => apiClient.get<ResourceAnalysis>(API_ENDPOINTS.RESOURCE_ANALYZE),
  getRebalancingSuggestions: () =>
    apiClient.get<{ suggestions: RebalancingSuggestion[]; total_suggestions: number }>(
      API_ENDPOINTS.RESOURCE_REBALANCING
    ),
  getEmployee: (employeeId: string) =>
    apiClient.get<any>(API_ENDPOINTS.RESOURCE_EMPLOYEE(employeeId)),
  getAlerts: () => apiClient.get<any>(API_ENDPOINTS.RESOURCE_ALERTS),
  acknowledgeAlert: (alertId: string) =>
    apiClient.post<any>(API_ENDPOINTS.RESOURCE_ALERT_ACKNOWLEDGE(alertId)),
  getDashboard: () => apiClient.get<any>(API_ENDPOINTS.RESOURCE_DASHBOARD),
  getOverbookingReport: () => apiClient.get<any>(API_ENDPOINTS.RESOURCE_OVERBOOKING_REPORT),
}

export const costApi = {
  getForecast: (projectId: string) =>
    apiClient.get<CostForecast>(API_ENDPOINTS.COST_FORECAST(projectId)),

  getBudgetAlerts: () =>
    apiClient.get<{ alerts: BudgetAlert[]; total_alerts: number }>(
      API_ENDPOINTS.COST_BUDGET_ALERTS
    ),
  getPortfolioSummary: () => apiClient.get<any>(API_ENDPOINTS.COST_PORTFOLIO_SUMMARY),
  getForecastHistory: (projectId: string) =>
    apiClient.get<any>(API_ENDPOINTS.COST_FORECAST_HISTORY(projectId)),
  getSpendingTrends: (projectId: string) =>
    apiClient.get<any>(API_ENDPOINTS.COST_SPENDING_TRENDS(projectId)),
}

export const mlApi = {
  getHealth: () => apiClient.get<any>(API_ENDPOINTS.ML_HEALTH),
  getModelInfo: () => apiClient.get<any>(API_ENDPOINTS.ML_MODEL_INFO),
  predict: (data: any) => apiClient.post<any>(API_ENDPOINTS.ML_PREDICT, data),
  predictBatch: (data: any) => apiClient.post<any>(API_ENDPOINTS.ML_PREDICT_BATCH, data),
  analyze: (data: any) => apiClient.post<any>(API_ENDPOINTS.ML_ANALYZE, data),
}
