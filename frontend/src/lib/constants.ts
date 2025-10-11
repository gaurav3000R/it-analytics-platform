export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export const API_ENDPOINTS = {
  // Projects
  PROJECTS: '/api/v1/projects/',
  PROJECT_BY_ID: (id: string) => `/api/v1/projects/${id}`,
  UPLOAD_CSV: '/api/v1/projects/upload-csv',
  LOAD_DEFAULT_CSV: '/api/v1/projects/load-default-csv',
  GENERATE_SAMPLE_DATA: '/api/v1/projects/generate-sample-data',
  CSV_SUMMARY: '/api/v1/projects/csv-summary',

  // Analytics
  ANALYTICS_OVERVIEW: '/api/v1/analytics/overview',
  RISK_DASHBOARD: '/api/v1/analytics/risk-dashboard',

  // Risk Dashboard
  RISK_DASHBOARD_OVERVIEW: '/api/v1/risk-dashboard/overview',
  RISK_DASHBOARD_STATISTICS: '/api/v1/risk-dashboard/statistics',
  RISK_DASHBOARD_PROJECTS: '/api/v1/risk-dashboard/projects',
  RISK_DASHBOARD_TRENDS: '/api/v1/risk-dashboard/trends',
  RISK_DASHBOARD_FLAGGED_PROJECTS: '/api/v1/risk-dashboard/flagged-projects',

  // Risks
  RISKS_TRAIN_MODEL: '/api/v1/risks/train-model',
  RISKS_PREDICT: (projectId: string) => `/api/v1/risks/predict/${projectId}`,
  RISKS_DASHBOARD: '/api/v1/risks/dashboard',
  RISKS_DETECT_ANOMALIES: '/api/v1/risks/anomalies/detect',
  RISKS_ANOMALIES_PROJECT: (projectId: string) => `/api/v1/risks/anomalies/project/${projectId}`,
  RISKS_ANOMALIES_EMPLOYEE: (employeeId: string) => `/api/v1/risks/anomalies/employee/${employeeId}`,
  RISKS_ANOMALIES_DASHBOARD: '/api/v1/risks/anomalies/dashboard',
  RISKS_ANOMALIES_LIST: '/api/v1/risks/anomalies/list',

  // AI Insights
  AI_RISK_ANALYSIS: (projectId: string) => `/api/v1/ai-insights/risk-analysis/${projectId}`,
  AI_RECOMMENDATIONS: (projectId: string) => `/api/v1/ai-insights/recommendations/${projectId}`,
  AI_PORTFOLIO_TRENDS: '/api/v1/ai-insights/portfolio-trends',
  AI_EXECUTIVE_SUMMARY: '/api/v1/ai-insights/executive-summary',
  AI_SERVICE_STATUS: '/api/v1/ai-insights/service-status',
  AI_PROJECT_INSIGHTS: (projectId: string) => `/api/v1/ai-insights/project/${projectId}/insights`,
  AI_DASHBOARD: '/api/v1/ai-insights/dashboard',

  // Bug Tracker
  BUG_ANALYSIS: (projectId: string) => `/api/v1/bug-tracker/analyze/${projectId}`,
  BUG_PORTFOLIO_ANALYSIS: '/api/v1/bug-tracker/portfolio-analysis',
  BUG_DASHBOARD: '/api/v1/bug-tracker/dashboard',
  BUG_LIST: '/api/v1/bug-tracker/list',
  BUG_QUALITY_RISKS: '/api/v1/bug-tracker/quality-risks',
  BUG_RESOLUTION_METRICS: '/api/v1/bug-tracker/metrics/resolution',

  // Resource Utilization
  RESOURCE_ANALYZE: '/api/v1/resource-utilization/analyze',
  RESOURCE_REBALANCING: '/api/v1/resource-utilization/rebalancing-suggestions',
  RESOURCE_EMPLOYEE: (employeeId: string) => `/api/v1/resource-utilization/employee/${employeeId}`,
  RESOURCE_ALERTS: '/api/v1/resource-utilization/alerts',
  RESOURCE_ALERT_ACKNOWLEDGE: (alertId: string) => `/api/v1/resource-utilization/alerts/${alertId}/acknowledge`,
  RESOURCE_DASHBOARD: '/api/v1/resource-utilization/dashboard',
  RESOURCE_OVERBOOKING_REPORT: '/api/v1/resource-utilization/overbooking-report',

  // Cost Forecasting
  COST_FORECAST: (projectId: string) => `/api/v1/cost-forecasting/forecast/${projectId}`,
  COST_BUDGET_ALERTS: '/api/v1/cost-forecasting/budget-alerts',
  COST_PORTFOLIO_SUMMARY: '/api/v1/cost-forecasting/portfolio-summary',
  COST_FORECAST_HISTORY: (projectId: string) => `/api/v1/cost-forecasting/forecast-history/${projectId}`,
  COST_SPENDING_TRENDS: '/api/v1/cost-forecasting/spending-trends',

  // Health
  HEALTH: '/health',

  // ML Predictions
  ML_HEALTH: '/api/v1/ml-predictions/health',
  ML_MODEL_INFO: '/api/v1/ml-predictions/model/info',
  ML_PREDICT: '/api/v1/ml-predictions/predict',
  ML_PREDICT_BATCH: '/api/v1/ml-predictions/predict/batch',
  ML_ANALYZE: '/api/v1/ml-predictions/analyze',
} as const

export const QUERY_KEYS = {
  // Projects
  PROJECTS: ['projects'],
  PROJECT: (id: string) => ['project', id],
  PROJECT_BY_ID: (id: string) => ['project', id],

  // Analytics
  ANALYTICS_OVERVIEW: ['analytics', 'overview'],
  RISK_DASHBOARD: ['analytics', 'risk-dashboard'],

  // Risks
  RISKS_DASHBOARD: ['risks', 'dashboard'],
  RISKS_PREDICT: (id: string) => ['risks', 'predict', id],
  RISKS_ANOMALIES_DASHBOARD: ['risks', 'anomalies', 'dashboard'],
  RISKS_ANOMALIES_LIST: ['risks', 'anomalies', 'list'],
  RISKS_ANOMALIES_PROJECT: (id: string) => ['risks', 'anomalies', 'project', id],
  RISKS_ANOMALIES_EMPLOYEE: (id: string) => ['risks', 'anomalies', 'employee', id],

  // AI Insights
  AI_RISK_ANALYSIS: (id: string) => ['ai', 'risk-analysis', id],
  AI_RECOMMENDATIONS: (id: string) => ['ai', 'recommendations', id],
  AI_PORTFOLIO_TRENDS: ['ai', 'portfolio-trends'],
  AI_EXECUTIVE_SUMMARY: ['ai', 'executive-summary'],
  AI_PROJECT_INSIGHTS: (id: string) => ['ai', 'project-insights', id],
  AI_DASHBOARD: ['ai', 'dashboard'],

  // Bug Tracker
  BUG_ANALYSIS: (id: string) => ['bugs', 'analysis', id],
  BUG_PORTFOLIO: ['bugs', 'portfolio'],
  BUG_DASHBOARD: ['bugs', 'dashboard'],

  // Resource Utilization
  RESOURCE_ANALYSIS: ['resources', 'analysis'],
  RESOURCE_ANALYZE: ['resources', 'analyze'],
  RESOURCE_REBALANCING: ['resources', 'rebalancing'],
  RESOURCE_EMPLOYEE: (id: string) => ['resources', 'employee', id],
  RESOURCE_ALERTS: ['resources', 'alerts'],
  RESOURCE_DASHBOARD: ['resources', 'dashboard'],
  RESOURCE_OVERBOOKING_REPORT: ['resources', 'overbooking'],

  // Cost Forecasting
  COST_FORECAST: (id: string) => ['cost', 'forecast', id],
  COST_ALERTS: ['cost', 'alerts'],
  COST_PORTFOLIO_SUMMARY: ['cost', 'portfolio-summary'],
  COST_FORECAST_HISTORY: (id: string) => ['cost', 'forecast-history', id],
  COST_SPENDING_TRENDS: (id: string) => ['cost', 'spending-trends', id],

  // ML Predictions
  ML_HEALTH: ['ml', 'health'],
  ML_MODEL_INFO: ['ml', 'model-info'],
} as const
