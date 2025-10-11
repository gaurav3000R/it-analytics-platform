'use client'

import React from 'react'
import { useQuery } from '@tanstack/react-query'
import { useParams } from 'next/navigation'
import { DashboardLayout } from '@/components/layout/dashboard-layout'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import {
  FolderKanban,
  AlertTriangle,
  Bug,
  DollarSign,
  Users,
  TrendingUp,
  Brain,
  Target,
  Calendar,
  Activity,
} from 'lucide-react'
import { motion } from 'framer-motion'
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from 'recharts'
import { projectsApi, risksApi, costApi, bugTrackerApi, aiInsightsApi } from '@/services/api'
import { QUERY_KEYS } from '@/lib/constants'

export default function ProjectDetailPage() {
  const params = useParams()
  const projectId = params.id as string

  const { data: project, isLoading } = useQuery({
    queryKey: QUERY_KEYS.PROJECT_BY_ID(projectId),
    queryFn: () => projectsApi.getById(projectId),
    enabled: !!projectId,
  })

  const { data: riskPrediction } = useQuery({
    queryKey: QUERY_KEYS.RISKS_PREDICT(projectId),
    queryFn: () => risksApi.predictRisk(projectId),
    enabled: !!projectId,
  })

  const { data: costForecast } = useQuery({
    queryKey: ['costForecast', projectId],
    queryFn: () => costApi.getForecast(project?.id?.toString() || ''),
    enabled: !!project?.id,
  })

  const { data: bugAnalysis } = useQuery({
    queryKey: ['bugAnalysis', projectId],
    queryFn: () => bugTrackerApi.analyzeProject(project?.id?.toString() || ''),
    enabled: !!project?.id,
  })

  const { data: aiInsights } = useQuery({
    queryKey: ['aiInsights', projectId],
    queryFn: () => aiInsightsApi.getProjectInsights(projectId),
    enabled: !!projectId,
  })

  const { data: projectAnomalies } = useQuery({
    queryKey: QUERY_KEYS.RISKS_ANOMALIES_PROJECT(project?.id?.toString() || ''),
    queryFn: () => risksApi.getAnomaliesByProject(project?.id?.toString() || ''),
    enabled: !!project?.id,
  })

  if (isLoading) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center min-h-[60vh]">
          <div className="text-center space-y-4">
            <div className="w-16 h-16 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto" />
            <p className="text-gray-400">Loading project data...</p>
          </div>
        </div>
      </DashboardLayout>
    )
  }

  if (!project) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center min-h-[60vh]">
          <div className="text-center">
            <FolderKanban className="h-16 w-16 text-gray-600 mx-auto mb-4" />
            <h2 className="text-2xl font-bold mb-2">Project Not Found</h2>
            <p className="text-gray-400">The project you're looking for doesn't exist.</p>
          </div>
        </div>
      </DashboardLayout>
    )
  }

  const riskScore = riskPrediction?.overall_risk_score || project?.risk_score || 0
  const riskLevel =
    riskScore > 70 ? 'High' : riskScore > 40 ? 'Medium' : 'Low'
  
  const riskColorBg =
    riskLevel === 'High' ? 'bg-red-50/80' :
    riskLevel === 'Medium' ? 'bg-amber-50/80' :
    'bg-green-50/80'
  
  const riskColorBorder =
    riskLevel === 'High' ? 'border-red-100' :
    riskLevel === 'Medium' ? 'border-amber-100' :
    'border-green-100'
  
  const riskColorText =
    riskLevel === 'High' ? 'text-red-600' :
    riskLevel === 'Medium' ? 'text-amber-600' :
    'text-green-600'

  const anomaliesCount = projectAnomalies?.total_anomalies || 0
  const bugsCount = bugAnalysis?.total_bugs || 0
  const budgetUtilization = costForecast?.current_status?.budget_utilization_percentage || 0

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Project Header */}
        <Card className="border-2 border-blue-100 bg-blue-50/30">
          <CardContent className="p-8">
            <div className="flex items-start justify-between">
              <div className="flex items-center gap-6">
                <div className="w-20 h-20 rounded-full bg-blue-100 border-2 border-blue-200 flex items-center justify-center">
                  <FolderKanban className="h-10 w-10 text-blue-600" />
                </div>
                <div>
                  <h1 className="text-4xl font-bold text-gray-900 mb-2">{project.name || project.project_id}</h1>
                  <div className="flex items-center gap-4 text-gray-600 mb-3">
                    <div className="flex items-center gap-2">
                      <Calendar className="h-4 w-4" />
                      <span>ID: {project.project_id}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <Target className="h-4 w-4" />
                      <span>{project.project_type || 'N/A'}</span>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <Badge
                      className={
                        riskLevel === 'High'
                          ? 'bg-red-100 text-red-700 border-red-200'
                          : riskLevel === 'Medium'
                          ? 'bg-amber-100 text-amber-700 border-amber-200'
                          : 'bg-green-100 text-green-700 border-green-200'
                      }
                    >
                      {riskLevel} Risk
                    </Badge>
                    {project.status && (
                      <Badge variant="secondary">{project.status}</Badge>
                    )}
                  </div>
                </div>
              </div>

              <div className="text-right">
                <p className="text-gray-600 text-sm mb-2 font-medium">Risk Score</p>
                <p className={`text-5xl font-bold ${riskColorText}`}>
                  {riskScore.toFixed(0)}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Key Metrics Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {[
            {
              title: 'Budget',
              value: `$${((project.budget_usd || 0) / 1000).toFixed(0)}k`,
              icon: DollarSign,
              bgColor: 'bg-green-50/80',
              borderColor: 'border-green-100',
              iconColor: 'text-green-600',
              description: `${budgetUtilization.toFixed(0)}% utilized`,
            },
            {
              title: 'Team Size',
              value: project.team_size || 0,
              icon: Users,
              bgColor: 'bg-blue-50/80',
              borderColor: 'border-blue-100',
              iconColor: 'text-blue-600',
              description: 'Team members',
            },
            {
              title: 'Active Bugs',
              value: bugsCount,
              icon: Bug,
              bgColor: 'bg-red-50/80',
              borderColor: 'border-red-100',
              iconColor: 'text-red-600',
              description: 'Open issues',
            },
            {
              title: 'Anomalies',
              value: anomaliesCount,
              icon: AlertTriangle,
              bgColor: 'bg-amber-50/80',
              borderColor: 'border-amber-100',
              iconColor: 'text-amber-600',
              description: 'Detected',
            },
          ].map((metric, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.1 }}
            >
              <Card hover glow>
                <CardContent className="p-6">
                  <div className={`p-3 rounded-xl ${metric.bgColor} border ${metric.borderColor} mb-4 inline-block`}>
                    <metric.icon className={`h-6 w-6 ${metric.iconColor}`} />
                  </div>
                  <h3 className="text-gray-600 text-sm mb-1 font-medium">{metric.title}</h3>
                  <p className="text-3xl font-bold text-gray-900 mb-1">{metric.value}</p>
                  <p className="text-xs text-gray-500">{metric.description}</p>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </div>

        {/* Project Details Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Project Information */}
          <Card hover>
            <CardHeader>
              <CardTitle>Project Information</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-gray-400 text-sm mb-1">Complexity Score</p>
                    <p className="text-xl font-bold">{project.complexity_score?.toFixed(1) || 'N/A'}</p>
                  </div>
                  <div>
                    <p className="text-gray-400 text-sm mb-1">Timeline</p>
                    <p className="text-xl font-bold">{project.timeline_months || 'N/A'} months</p>
                  </div>
                  <div>
                    <p className="text-gray-400 text-sm mb-1">Team Experience</p>
                    <p className="text-xl font-bold">{project.team_experience || 'N/A'}</p>
                  </div>
                  <div>
                    <p className="text-gray-400 text-sm mb-1">Methodology</p>
                    <p className="text-xl font-bold">{project.methodology || 'N/A'}</p>
                  </div>
                </div>

                {project.stakeholder_count && (
                  <div className="pt-4 border-t border-white/10">
                    <p className="text-gray-400 text-sm mb-1">Stakeholders</p>
                    <p className="text-lg font-semibold">{project.stakeholder_count} stakeholders</p>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>

          {/* Risk Analysis */}
          <Card hover className="border-orange-500/20">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <AlertTriangle className="h-5 w-5 text-orange-400" />
                Risk Analysis
              </CardTitle>
            </CardHeader>
            <CardContent>
              {riskPrediction && (
                <div className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    {Object.entries(riskPrediction.component_risks || {}).map(([key, value]: any, i) => (
                      <div key={i} className="p-3 rounded-lg bg-white/5">
                        <p className="text-gray-400 text-sm mb-1">
                          {key.replace('_risk', '').replace('_', ' ').toUpperCase()}
                        </p>
                        <p className="text-xl font-bold">{(value * 100).toFixed(0)}%</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Cost Forecast */}
        {costForecast && (
          <Card hover>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <DollarSign className="h-5 w-5 text-green-400" />
                Cost Forecast
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="p-4 rounded-lg bg-white/5">
                  <p className="text-gray-400 text-sm mb-1">Current Spend</p>
                  <p className="text-2xl font-bold">
                    ${((costForecast.current_status?.current_spend || 0) / 1000).toFixed(0)}k
                  </p>
                </div>
                <div className="p-4 rounded-lg bg-white/5">
                  <p className="text-gray-400 text-sm mb-1">Projected Cost</p>
                  <p className="text-2xl font-bold">
                    ${((costForecast.current_status?.projected_final_cost || 0) / 1000).toFixed(0)}k
                  </p>
                </div>
                <div className="p-4 rounded-lg bg-white/5">
                  <p className="text-gray-400 text-sm mb-1">Overrun Probability</p>
                  <p className="text-2xl font-bold text-red-400">
                    {((costForecast.overrun_analysis?.overrun_probability || 0) * 100).toFixed(0)}%
                  </p>
                </div>
                <div className="p-4 rounded-lg bg-white/5">
                  <p className="text-gray-400 text-sm mb-1">Days Remaining</p>
                  <p className="text-2xl font-bold">
                    {costForecast.current_status?.days_remaining || 'N/A'}
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* AI Insights */}
        {aiInsights?.ai_risk_analysis && (
          <Card hover className="border-purple-500/20 bg-purple-500/5">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Brain className="h-5 w-5 text-purple-400" />
                AI-Powered Insights
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div>
                  <h4 className="font-semibold mb-2 text-purple-400">Risk Analysis</h4>
                  <p className="text-sm text-gray-300 whitespace-pre-wrap">
                    {aiInsights.ai_risk_analysis}
                  </p>
                </div>
                {aiInsights.ai_recommendations && (
                  <div>
                    <h4 className="font-semibold mb-2 text-purple-400">Recommendations</h4>
                    <p className="text-sm text-gray-300 whitespace-pre-wrap">
                      {aiInsights.ai_recommendations}
                    </p>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Anomalies */}
        {projectAnomalies && anomaliesCount > 0 && (
          <Card hover className="border-red-500/20">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-red-400">
                <Activity className="h-5 w-5" />
                Project Anomalies ({anomaliesCount})
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {projectAnomalies.anomalies?.slice(0, 6).map((anomaly: any, i: number) => (
                  <div
                    key={i}
                    className={`p-4 rounded-lg border ${
                      anomaly.severity === 'critical'
                        ? 'bg-red-500/10 border-red-500/30'
                        : 'bg-yellow-500/10 border-yellow-500/30'
                    }`}
                  >
                    <div className="flex items-center justify-between mb-2">
                      <Badge
                        variant="secondary"
                        className={`text-xs ${
                          anomaly.severity === 'critical'
                            ? 'bg-red-500/20 text-red-400'
                            : 'bg-yellow-500/20 text-yellow-400'
                        }`}
                      >
                        {anomaly.severity}
                      </Badge>
                      <span className="text-xs text-gray-500">
                        {new Date(anomaly.detected_at).toLocaleDateString()}
                      </span>
                    </div>
                    <p className="text-sm line-clamp-2">{anomaly.description}</p>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </DashboardLayout>
  )
}
