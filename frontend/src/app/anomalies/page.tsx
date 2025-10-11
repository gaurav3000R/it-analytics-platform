'use client'

import React, { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { DashboardLayout } from '@/components/layout/dashboard-layout'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { AlertTriangle, Activity, TrendingUp, Users, RefreshCw } from 'lucide-react'
import { motion } from 'framer-motion'
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, BarChart, Bar, XAxis, YAxis, CartesianGrid } from 'recharts'
import { risksApi, projectsApi } from '@/services/api'
import { QUERY_KEYS } from '@/lib/constants'
import toast from 'react-hot-toast'
import type { Anomaly, Project } from '@/types'

interface EmployeeAnomalyItem {
  employee: string
  count: number
}

interface ProjectAnomalyItem {
  project: string
  count: number
}

export default function AnomaliesPage() {
  const [severityFilter, setSeverityFilter] = useState<string>('')
  const [typeFilter, setTypeFilter] = useState<string>('')
  const [projectFilter, setProjectFilter] = useState<string>('')

  const { data: anomaliesDashboard, isLoading, refetch } = useQuery({
    queryKey: QUERY_KEYS.RISKS_ANOMALIES_DASHBOARD,
    queryFn: risksApi.getAnomaliesDashboard,
  })

  const { data: anomaliesList, refetch: refetchList } = useQuery({
    queryKey: QUERY_KEYS.RISKS_ANOMALIES_LIST,
    queryFn: risksApi.getAnomaliesList,
  })

  const { data: projects } = useQuery({
    queryKey: QUERY_KEYS.PROJECTS,
    queryFn: projectsApi.getAll,
  })

  const handleDetectAnomalies = async () => {
    toast.promise(
      risksApi.detectAnomalies().then(() => {
        refetch()
        refetchList()
      }),
      {
        loading: 'Detecting anomalies...',
        success: (data) => `Detected ${data?.anomalies_detected || 0} anomalies!`,
        error: 'Failed to detect anomalies',
      }
    )
  }

  const handleRefresh = () => {
    toast.promise(
      Promise.all([refetch(), refetchList()]),
      {
        loading: 'Refreshing data...',
        success: 'Data refreshed!',
        error: 'Failed to refresh',
      }
    )
  }

  if (isLoading) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center min-h-[60vh]">
          <div className="text-center space-y-4">
            <div className="w-16 h-16 border-4 border-orange-500 border-t-transparent rounded-full animate-spin mx-auto" />
            <p className="text-gray-400">Loading anomaly data...</p>
          </div>
        </div>
      </DashboardLayout>
    )
  }

  const severityData = anomaliesDashboard?.by_severity || {}
  const typeData = anomaliesDashboard?.by_type || {}

  const severityChartData = Object.entries(severityData).map(([name, value]) => ({
    name: name.charAt(0).toUpperCase() + name.slice(1),
    value: value as number,
    color:
      name === 'critical' ? '#dc2626' :
      name === 'high' ? '#ef4444' :
      name === 'medium' ? '#f59e0b' : '#10b981'
  }))

  const typeChartData = Object.entries(typeData).map(([name, value]) => ({
    name: name.split('_').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' '),
    value: value as number,
  }))

  const filteredAnomalies = anomaliesList?.anomalies?.filter((a) => {
    if (severityFilter && a.severity !== severityFilter) return false
    if (typeFilter && a.type !== typeFilter) return false
    if (projectFilter && a.project?.id?.toString() !== projectFilter) return false
    return true
  }) || []

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-4xl font-bold gradient-text mb-2">
              <AlertTriangle className="inline h-10 w-10 mr-3" />
              Anomaly Detection
            </h1>
            <p className="text-gray-400">AI-powered anomaly detection in daily logs and activities</p>
          </div>
          <div className="flex gap-2">
            <Button onClick={handleRefresh} variant="outline">
              <RefreshCw className="h-4 w-4 mr-2" />Refresh
            </Button>
            <Button onClick={handleDetectAnomalies} className="bg-gradient-to-r from-orange-500 to-red-500">
              <Activity className="h-4 w-4 mr-2" />Detect Anomalies
            </Button>
          </div>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          {[
            {
              title: 'Total Anomalies',
              value: anomaliesDashboard?.total_anomalies || 0,
              icon: AlertTriangle,
              bgColor: 'bg-orange-50/80',
              borderColor: 'border-orange-100',
              iconColor: 'text-orange-600',
              description: `Last ${anomaliesDashboard?.period_days || 7} days`
            },
            {
              title: 'Critical',
              value: severityData?.critical || 0,
              icon: AlertTriangle,
              bgColor: 'bg-red-50/80',
              borderColor: 'border-red-100',
              iconColor: 'text-red-600',
              description: 'Immediate attention'
            },
            {
              title: 'Affected Employees',
              value: anomaliesDashboard?.summary?.affected_employees || 0,
              icon: Users,
              bgColor: 'bg-purple-50/80',
              borderColor: 'border-purple-100',
              iconColor: 'text-purple-600',
              description: 'Team members'
            },
            {
              title: 'Affected Projects',
              value: anomaliesDashboard?.summary?.affected_projects || 0,
              icon: TrendingUp,
              bgColor: 'bg-blue-50/80',
              borderColor: 'border-blue-100',
              iconColor: 'text-blue-600',
              description: 'Projects'
            },
          ].map((stat, i) => (
            <motion.div key={i} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.1 }}>
              <Card hover glow>
                <CardContent className="p-6">
                  <div className={`p-3 rounded-xl ${stat.bgColor} border ${stat.borderColor} mb-4 inline-block`}>
                    <stat.icon className={`h-6 w-6 ${stat.iconColor}`} />
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
          {/* Severity Distribution */}
          <Card hover>
            <CardHeader><CardTitle>Anomaly by Severity</CardTitle></CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={severityChartData}
                    dataKey="value"
                    nameKey="name"
                    cx="50%"
                    cy="50%"
                    outerRadius={100}
                    label={(entry) => `${entry.name}: ${entry.value}`}
                  >
                    {severityChartData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip contentStyle={{ backgroundColor: 'rgba(30, 41, 59, 0.95)', border: '1px solid rgba(251, 146, 60, 0.3)', borderRadius: '8px' }} />
                </PieChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          {/* Type Distribution */}
          <Card hover>
            <CardHeader><CardTitle>Anomaly by Type</CardTitle></CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={typeChartData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#30363d" />
                  <XAxis dataKey="name" stroke="#8b949e" angle={-45} textAnchor="end" height={100} />
                  <YAxis stroke="#8b949e" />
                  <Tooltip contentStyle={{ backgroundColor: 'rgba(30, 41, 59, 0.95)', border: '1px solid rgba(251, 146, 60, 0.3)', borderRadius: '8px' }} />
                  <Bar dataKey="value" fill="#f59e0b" radius={[8, 8, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </div>

        {/* Top Employees/Projects with Anomalies */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Top Employees */}
          <Card hover>
            <CardHeader><CardTitle>Top Employees with Anomalies</CardTitle></CardHeader>
            <CardContent>
              <div className="space-y-3">
                {anomaliesDashboard?.top_employees_with_anomalies?.slice(0, 8).map((item: EmployeeAnomalyItem, i: number) => (
                  <div key={i} className="flex items-center justify-between p-3 rounded-lg bg-white/5 hover:bg-white/10 transition-colors">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-full bg-gradient-to-br from-orange-500 to-red-500 flex items-center justify-center font-bold">
                        {item.employee?.charAt(0) || '?'}
                      </div>
                      <span className="font-medium">{item.employee}</span>
                    </div>
                    <Badge variant="secondary" className="bg-orange-500/20 text-orange-400">
                      {item.count} anomalies
                    </Badge>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Top Projects */}
          <Card hover>
            <CardHeader><CardTitle>Top Projects with Anomalies</CardTitle></CardHeader>
            <CardContent>
              <div className="space-y-3">
                {anomaliesDashboard?.top_projects_with_anomalies?.slice(0, 8).map((item: ProjectAnomalyItem, i: number) => (
                  <div key={i} className="flex items-center justify-between p-3 rounded-lg bg-white/5 hover:bg-white/10 transition-colors">
                    <span className="font-medium">{item.project}</span>
                    <Badge variant="secondary" className="bg-red-500/20 text-red-400">
                      {item.count} anomalies
                    </Badge>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Critical Anomalies */}
        <Card hover className="border-red-500/30">
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle className="text-red-400">Recent Critical Anomalies</CardTitle>
              <Badge className="bg-red-500/20 text-red-400">
                {anomaliesDashboard?.recent_critical_anomalies?.length || 0} Critical
              </Badge>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {anomaliesDashboard?.recent_critical_anomalies?.slice(0, 10).map((anomaly: Anomaly, i: number) => (
                <motion.div
                  key={anomaly.id}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: i * 0.05 }}
                  className="p-4 rounded-lg bg-red-500/10 border border-red-500/30"
                >
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <Badge variant="secondary" className="text-xs bg-red-500/20 text-red-400">
                          {anomaly.type}
                        </Badge>
                        <span className="text-sm text-gray-400">
                          {new Date(anomaly.detected_at).toLocaleDateString()}
                        </span>
                      </div>
                      <p className="text-sm font-medium mb-1">{anomaly.description}</p>
                      {anomaly.employee && (
                        <p className="text-xs text-gray-400">Employee: {anomaly.employee}</p>
                      )}
                      {anomaly.project && (
                        <p className="text-xs text-gray-400">Project: {anomaly.project}</p>
                      )}
                    </div>
                  </div>
                </motion.div>
              ))}
              {(!anomaliesDashboard?.recent_critical_anomalies || anomaliesDashboard.recent_critical_anomalies.length === 0) && (
                <p className="text-center text-gray-400 py-8">No critical anomalies detected</p>
              )}
            </div>
          </CardContent>
        </Card>

        {/* All Anomalies List with Filters */}
        <Card hover>
          <CardHeader>
            <div className="flex items-center justify-between flex-wrap gap-4">
              <CardTitle>All Anomalies ({filteredAnomalies.length})</CardTitle>
              <div className="flex gap-2 flex-wrap">
                <select
                  className="bg-white/5 border border-white/10 rounded px-3 py-1 text-sm"
                  value={severityFilter}
                  onChange={(e) => setSeverityFilter(e.target.value)}
                >
                  <option value="">All Severities</option>
                  <option value="critical">Critical</option>
                  <option value="high">High</option>
                  <option value="medium">Medium</option>
                  <option value="low">Low</option>
                </select>
                <select
                  className="bg-white/5 border border-white/10 rounded px-3 py-1 text-sm"
                  value={typeFilter}
                  onChange={(e) => setTypeFilter(e.target.value)}
                >
                  <option value="">All Types</option>
                  <option value="missing_logs">Missing Logs</option>
                  <option value="unusual_hours">Unusual Hours</option>
                  <option value="productivity_drop">Productivity Drop</option>
                  <option value="pattern_change">Pattern Change</option>
                </select>
                <select
                  className="bg-white/5 border border-white/10 rounded px-3 py-1 text-sm"
                  value={projectFilter}
                  onChange={(e) => setProjectFilter(e.target.value)}
                >
                  <option value="">All Projects</option>
                  {projects?.slice(0, 20).map((project: Project) => (
                    <option key={project.id} value={project.id}>
                      {project.project_id}
                    </option>
                  ))}
                </select>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {filteredAnomalies.slice(0, 30).map((anomaly: Anomaly, i: number) => (
                <div
                  key={i}
                  className={`p-4 rounded-lg border ${
                    anomaly.severity === 'critical'
                      ? 'bg-red-500/10 border-red-500/30'
                      : anomaly.severity === 'high'
                      ? 'bg-orange-500/10 border-orange-500/30'
                      : 'bg-yellow-500/10 border-yellow-500/30'
                  }`}
                >
                  <div className="flex items-center justify-between mb-2">
                    <Badge
                      variant="secondary"
                      className={`text-xs ${
                        anomaly.severity === 'critical'
                          ? 'bg-red-500/20 text-red-400'
                          : anomaly.severity === 'high'
                          ? 'bg-orange-500/20 text-orange-400'
                          : 'bg-yellow-500/20 text-yellow-400'
                      }`}
                    >
                      {anomaly.severity}
                    </Badge>
                    <Badge variant="outline" className="text-xs">
                      {anomaly.type}
                    </Badge>
                  </div>
                  <p className="text-sm mb-2 line-clamp-2">{anomaly.description}</p>
                  {anomaly.employee && (
                    <p className="text-xs text-gray-400 mb-1">
                      👤 {anomaly.employee.name}
                    </p>
                  )}
                  {anomaly.project && (
                    <p className="text-xs text-gray-400 mb-1">
                      📁 {anomaly.project.name}
                    </p>
                  )}
                  <p className="text-xs text-gray-500 mt-2">
                    {new Date(anomaly.detected_at).toLocaleDateString()}
                  </p>
                </div>
              ))}
            </div>
            {filteredAnomalies.length === 0 && (
              <p className="text-center text-gray-400 py-12">No anomalies found matching filters</p>
            )}
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  )
}
