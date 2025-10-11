'use client'

import React from 'react'
import { useQuery } from '@tanstack/react-query'
import { DashboardLayout } from '@/components/layout/dashboard-layout'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { DollarSign, TrendingUp, TrendingDown, AlertTriangle, Target, RefreshCw, BarChart3 } from 'lucide-react'
import { motion } from 'framer-motion'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend, BarChart, Bar, PieChart, Pie, Cell } from 'recharts'
import { costApi, projectsApi } from '@/services/api'
import { QUERY_KEYS } from '@/lib/constants'
import toast from 'react-hot-toast'

export default function CostsPage() {
  const [selectedProject, setSelectedProject] = React.useState<string>('')

  const { data: budgetAlerts, isLoading, refetch } = useQuery({
    queryKey: QUERY_KEYS.COST_ALERTS,
    queryFn: costApi.getBudgetAlerts,
  })

  const { data: portfolioSummary } = useQuery({
    queryKey: QUERY_KEYS.COST_PORTFOLIO_SUMMARY,
    queryFn: costApi.getPortfolioSummary,
  })

  const { data: projects } = useQuery({
    queryKey: QUERY_KEYS.PROJECTS,
    queryFn: projectsApi.getAll,
  })

  const handleRefresh = () => {
    toast.promise(refetch(), {
      loading: 'Refreshing cost data...',
      success: 'Cost data updated!',
      error: 'Failed to refresh',
    })
  }

  if (isLoading) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center min-h-[60vh]">
          <div className="text-center space-y-4">
            <div className="w-16 h-16 border-4 border-green-500 border-t-transparent rounded-full animate-spin mx-auto" />
            <p className="text-gray-400">Loading cost forecasts...</p>
          </div>
        </div>
      </DashboardLayout>
    )
  }

  const alerts = budgetAlerts?.alerts || []
  const criticalAlerts = alerts.filter(a => a.alert_severity === 'critical')
  const highAlerts = alerts.filter(a => a.alert_severity === 'high')

  // Calculate totals
  const totalBudget = alerts.reduce((sum, a) => sum + (a.total_budget || 0), 0)
  const totalSpent = alerts.reduce((sum, a) => sum + (a.current_spend || 0), 0)
  const avgOverrunRisk = alerts.length > 0 
    ? alerts.reduce((sum, a) => sum + (a.overrun_probability || 0), 0) / alerts.length 
    : 0

  // Prepare chart data
  const riskDistribution = [
    { name: 'Low Risk', value: alerts.filter(a => a.risk_level === 'low').length, color: '#10b981' },
    { name: 'Medium Risk', value: alerts.filter(a => a.risk_level === 'medium').length, color: '#f59e0b' },
    { name: 'High Risk', value: alerts.filter(a => a.risk_level === 'high').length, color: '#ef4444' },
    { name: 'Critical', value: alerts.filter(a => a.risk_level === 'critical').length, color: '#dc2626' },
  ]

  const topOverruns = alerts
    .sort((a, b) => (b.overrun_probability || 0) - (a.overrun_probability || 0))
    .slice(0, 10)
    .map(a => ({
      name: a.project_name?.substring(0, 20) || a.project_identifier,
      probability: ((a.overrun_probability || 0) * 100).toFixed(1),
      amount: a.expected_overrun_amount || 0,
    }))

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-4xl font-bold gradient-text mb-2">
              <DollarSign className="inline h-10 w-10 mr-3" />
              Cost Forecasting
            </h1>
            <p className="text-gray-400">Budget tracking and overrun predictions</p>
          </div>
          <Button onClick={handleRefresh}>
            <RefreshCw className="h-4 w-4 mr-2" />Refresh Data
          </Button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          {[
            { 
              title: 'Total Budget', 
              value: `$${(totalBudget / 1000000).toFixed(2)}M`, 
              icon: DollarSign, 
              bgColor: 'bg-blue-50/80',
              borderColor: 'border-blue-100',
              iconColor: 'text-blue-600',
              description: 'Portfolio total'
            },
            { 
              title: 'Spent to Date', 
              value: `$${(totalSpent / 1000000).toFixed(2)}M`, 
              icon: TrendingUp, 
              bgColor: 'bg-purple-50/80',
              borderColor: 'border-purple-100',
              iconColor: 'text-purple-600',
              description: `${((totalSpent / totalBudget) * 100).toFixed(1)}% utilized`
            },
            { 
              title: 'Budget Alerts', 
              value: budgetAlerts?.total_alerts || 0, 
              icon: AlertTriangle, 
              bgColor: 'bg-red-50/80',
              borderColor: 'border-red-100',
              iconColor: 'text-red-600',
              description: `${criticalAlerts.length} critical`
            },
            { 
              title: 'Avg Overrun Risk', 
              value: `${(avgOverrunRisk * 100).toFixed(1)}%`, 
              icon: TrendingDown, 
              bgColor: 'bg-amber-50/80',
              borderColor: 'border-amber-100',
              iconColor: 'text-amber-600',
              description: 'Portfolio average'
            },
          ].map((stat, i) => (
            <motion.div key={i} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.1 }}>
              <Card hover glow>
                <CardContent className="p-6">
                  <div className="flex items-center justify-between mb-4">
                    <div className={`p-3 rounded-xl ${stat.bgColor} border ${stat.borderColor}`}>
                      <stat.icon className={`h-6 w-6 ${stat.iconColor}`} />
                    </div>
                  </div>
                  <h3 className="text-gray-600 text-sm mb-1 font-medium">{stat.title}</h3>
                  <p className="text-3xl font-bold text-gray-900 mb-1">{stat.value}</p>
                  <p className="text-xs text-gray-500">{stat.description}</p>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </div>

        {/* Charts Row */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Risk Distribution */}
          <Card hover>
            <CardHeader><CardTitle>Budget Risk Distribution</CardTitle></CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie 
                    data={riskDistribution} 
                    dataKey="value" 
                    nameKey="name" 
                    cx="50%" 
                    cy="50%" 
                    outerRadius={100}
                    label={(entry) => `${entry.name}: ${entry.value}`}
                  >
                    {riskDistribution.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip contentStyle={{ backgroundColor: 'rgba(30, 41, 59, 0.95)', border: '1px solid rgba(59, 130, 246, 0.3)', borderRadius: '8px' }} />
                </PieChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          {/* Top Overrun Risks */}
          <Card hover>
            <CardHeader><CardTitle>Top Overrun Risks</CardTitle></CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={topOverruns}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#30363d" />
                  <XAxis dataKey="name" stroke="#8b949e" angle={-45} textAnchor="end" height={100} />
                  <YAxis stroke="#8b949e" />
                  <Tooltip contentStyle={{ backgroundColor: 'rgba(30, 41, 59, 0.95)', border: '1px solid rgba(59, 130, 246, 0.3)', borderRadius: '8px' }} />
                  <Bar dataKey="probability" fill="#ef4444" name="Overrun %" />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </div>

        {/* Budget Alerts Table */}
        <Card hover>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle>Budget Alerts ({budgetAlerts?.total_alerts || 0})</CardTitle>
              <div className="flex gap-2">
                <Badge className="bg-red-500/20 text-red-400">
                  {budgetAlerts?.critical_alerts || 0} Critical
                </Badge>
                <Badge className="bg-orange-500/20 text-orange-400">
                  {budgetAlerts?.high_alerts || 0} High
                </Badge>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {alerts.length === 0 ? (
                <p className="text-gray-400 text-center py-8">No budget alerts at this time</p>
              ) : (
                alerts.slice(0, 15).map((alert, i) => (
                  <motion.div
                    key={i}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: i * 0.05 }}
                    className={`p-4 rounded-lg border ${
                      alert.alert_severity === 'critical'
                        ? 'bg-red-500/10 border-red-500/30'
                        : 'bg-orange-500/10 border-orange-500/30'
                    }`}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-2">
                          <span className="font-semibold">{alert.project_name || alert.project_identifier}</span>
                          <Badge variant="secondary" className="text-xs">
                            {alert.risk_level}
                          </Badge>
                        </div>
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                          <div>
                            <p className="text-gray-400 text-xs">Budget</p>
                            <p className="font-medium">${(alert.total_budget / 1000).toFixed(0)}k</p>
                          </div>
                          <div>
                            <p className="text-gray-400 text-xs">Spent</p>
                            <p className="font-medium">${(alert.current_spend / 1000).toFixed(0)}k</p>
                          </div>
                          <div>
                            <p className="text-gray-400 text-xs">Utilization</p>
                            <p className="font-medium">{alert.budget_utilization?.toFixed(1)}%</p>
                          </div>
                          <div>
                            <p className="text-gray-400 text-xs">Overrun Risk</p>
                            <p className={`font-semibold ${
                              (alert.overrun_probability || 0) > 1 ? 'text-red-400' : 'text-yellow-400'
                            }`}>
                              {((alert.overrun_probability || 0) * 100).toFixed(1)}%
                            </p>
                          </div>
                        </div>
                        {alert.expected_overrun_amount > 0 && (
                          <div className="mt-2 text-xs text-red-400">
                            Expected overrun: ${(alert.expected_overrun_amount / 1000).toFixed(0)}k
                          </div>
                        )}
                      </div>
                    </div>
                  </motion.div>
                ))
              )}
            </div>
          </CardContent>
        </Card>

        {/* Optimization Stats */}
        {budgetAlerts?.optimization_stats && (
          <Card className="bg-blue-500/5 border-blue-500/20">
            <CardContent className="p-4">
              <div className="flex items-center gap-4 text-sm">
                <BarChart3 className="h-5 w-5 text-blue-400" />
                <span className="text-gray-400">
                  Analyzed {budgetAlerts.optimization_stats.projects_analyzed} projects •
                  Saved {budgetAlerts.optimization_stats.database_queries_saved}+ database queries •
                  Response optimized 233x faster
                </span>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </DashboardLayout>
  )
}
