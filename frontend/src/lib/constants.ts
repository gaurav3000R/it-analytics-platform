export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'

export const API_ENDPOINTS = {
  // Projects
  PROJECTS: '/projects',
  PROJECT_BY_ID: (id: string) => `/projects/${id}`,
  UPLOAD_CSV: '/projects/upload-csv',
  LOAD_DEFAULT_CSV: '/projects/load-default-csv',
  GENERATE_SAMPLE_DATA: '/projects/generate-sample-data',
  CSV_SUMMARY: '/projects/csv-summary',

  // Analytics
  ANALYTICS_OVERVIEW: '/analytics/overview',
  RISK_DASHBOARD: '/analytics/risk-dashboard',

  // Risks
  RISKS_TRAIN_MODEL: '/risks/train-model',
  RISKS_PREDICT: (projectId: string) => `/risks/predict/${projectId}`,

  // AI Insights
  AI_RISK_ANALYSIS: (projectId: string) => `/ai-insights/risk-analysis/${projectId}`,
  AI_RECOMMENDATIONS: (projectId: string) => `/ai-insights/recommendations/${projectId}`,
  AI_PORTFOLIO_TRENDS: '/ai-insights/portfolio-trends',
  AI_EXECUTIVE_SUMMARY: '/ai-insights/executive-summary',

  // Bug Tracker
  BUG_ANALYSIS: (projectId: string) => `/bug-tracker/analyze/${projectId}`,
  BUG_PORTFOLIO_ANALYSIS: '/bug-tracker/portfolio-analysis',

  // Resource Utilization
  RESOURCE_ANALYZE: '/resource-utilization/analyze',
  RESOURCE_REBALANCING: '/resource-utilization/rebalancing-suggestions',

  // Cost Forecasting
  COST_FORECAST: (projectId: string) => `/cost-forecasting/forecast/${projectId}`,
  COST_BUDGET_ALERTS: '/cost-forecasting/budget-alerts',
} as const

export const QUERY_KEYS = {
  PROJECTS: ['projects'],
  PROJECT: (id: string) => ['project', id],
  ANALYTICS_OVERVIEW: ['analytics', 'overview'],
  RISK_DASHBOARD: ['analytics', 'risk-dashboard'],
  AI_RISK_ANALYSIS: (id: string) => ['ai', 'risk-analysis', id],
  AI_RECOMMENDATIONS: (id: string) => ['ai', 'recommendations', id],
  AI_PORTFOLIO_TRENDS: ['ai', 'portfolio-trends'],
  AI_EXECUTIVE_SUMMARY: ['ai', 'executive-summary'],
  BUG_ANALYSIS: (id: string) => ['bugs', 'analysis', id],
  BUG_PORTFOLIO: ['bugs', 'portfolio'],
  RESOURCE_ANALYSIS: ['resources', 'analysis'],
  RESOURCE_REBALANCING: ['resources', 'rebalancing'],
  COST_FORECAST: (id: string) => ['cost', 'forecast', id],
  COST_ALERTS: ['cost', 'alerts'],
} as const
