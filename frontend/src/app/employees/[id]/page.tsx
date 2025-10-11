'use client'

import React from 'react'
import { useQuery } from '@tanstack/react-query'
import { useParams } from 'next/navigation'
import { DashboardLayout } from '@/components/layout/dashboard-layout'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import {
  User,
  Activity,
  AlertTriangle,
  Clock,
  TrendingUp,
  TrendingDown,
  BarChart3,
  Target,
  Calendar,
  Briefcase,
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
  AreaChart,
  Area,
} from 'recharts'
import { resourceApi, risksApi } from '@/services/api'
import { QUERY_KEYS } from '@/lib/constants'

export default function EmployeeDetailPage() {
  const params = useParams()
  const employeeId = params.id as string

  const { data: employeeData, isLoading } = useQuery({
    queryKey: QUERY_KEYS.RESOURCE_EMPLOYEE(employeeId),
    queryFn: () => resourceApi.getEmployee(employeeId),
    enabled: !!employeeId,
  })

  const { data: employeeAnomalies } = useQuery({
    queryKey: QUERY_KEYS.RISKS_ANOMALIES_EMPLOYEE(employeeId),
    queryFn: () => risksApi.getAnomaliesByEmployee(employeeId),
    enabled: !!employeeId,
  })

  if (isLoading) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center min-h-[60vh]">
          <div className="text-center space-y-4">
            <div className="w-16 h-16 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto" />
            <p className="text-gray-400">Loading employee data...</p>
          </div>
        </div>
      </DashboardLayout>
    )
  }

  const employee = employeeData?.employee || {}
  const utilization = employeeData?.utilization || {}
  const projects = employeeData?.projects || []
  const workload = employeeData?.workload || []
  const anomalies = employeeAnomalies?.anomalies || []

  // Prepare chart data
  const workloadData = workload.map((w: any) => ({
    date: new Date(w.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
    hours: w.hours_logged,
    expected: w.expected_hours || 8,
  }))

  const projectDistribution = projects.map((p: any) => ({
    name: p.project_name?.substring(0, 15) || p.project_id,
    hours: p.total_hours,
  }))

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Employee Header */}
        <Card className="border-2 border-blue-100 bg-blue-50/30">
          <CardContent className="p-8">
            <div className="flex items-start justify-between">
              <div className="flex items-center gap-6">
                <div className="w-24 h-24 rounded-full bg-blue-100 border-2 border-blue-200 flex items-center justify-center">
                  <User className="h-12 w-12 text-blue-600" />
                </div>
                <div>
                  <h1 className="text-4xl font-bold text-gray-900 mb-2">{employee.name || `Employee ${employeeId}`}</h1>
                  <div className="flex items-center gap-4 text-gray-600">
                    <div className="flex items-center gap-2">
                      <Briefcase className="h-4 w-4" />
                      <span>{employee.role || 'N/A'}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <Calendar className="h-4 w-4" />
                      <span>ID: {employeeId}</span>
                    </div>
                  </div>
                  <div className="flex items-center gap-2 mt-3">
                    <Badge
                      className={
                        utilization.status === 'optimal'
                          ? 'bg-green-100 text-green-700 border-green-200'
                          : utilization.status === 'overutilized'
                            ? 'bg-red-100 text-red-700 border-red-200'
                            : 'bg-amber-100 text-amber-700 border-amber-200'
                      }
                    >
                      {utilization.status || 'Unknown'}
                    </Badge>
                    {employee.hourly_rate && (
                      <Badge variant="secondary">${employee.hourly_rate}/hr</Badge>
                    )}
                  </div>
                </div>
              </div>

              <div className="text-right">
                <p className="text-gray-600 text-sm mb-2 font-medium">Utilization Rate</p>
                <p className="text-5xl font-bold text-blue-600">
                  {((utilization.utilization_rate || 0) * 100).toFixed(0)}%
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          {[
            {
              title: 'Active Projects',
              value: projects.length,
              icon: Target,
              bgColor: 'bg-blue-50/80',
              borderColor: 'border-blue-100',
              iconColor: 'text-blue-600',
              description: 'Currently assigned',
            },
            {
              title: 'Avg Daily Hours',
              value: (utilization.avg_daily_hours || 0).toFixed(1),
              icon: Clock,
              bgColor: 'bg-purple-50/80',
              borderColor: 'border-purple-100',
              iconColor: 'text-purple-600',
              description: `Expected: ${utilization.expected_hours || 8}h`,
            },
            {
              title: 'Total Hours (30d)',
              value: (utilization.total_hours_30d || 0).toFixed(0),
              icon: Activity,
              bgColor: 'bg-green-50/80',
              borderColor: 'border-green-100',
              iconColor: 'text-green-600',
              description: 'Last 30 days',
            },
            {
              title: 'Anomalies',
              value: anomalies.length,
              icon: AlertTriangle,
              bgColor: 'bg-red-50/80',
              borderColor: 'border-red-100',
              iconColor: 'text-red-600',
              description: 'Detected issues',
            },
          ].map((stat, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.1 }}
            >
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
          {/* Workload Trend */}
          <Card hover>
            <CardHeader>
              <CardTitle>Workload Trend (Last 30 Days)</CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <AreaChart data={workloadData}>
                  <defs>
                    <linearGradient id="hoursGradient" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.8} />
                      <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#30363d" />
                  <XAxis dataKey="date" stroke="#8b949e" />
                  <YAxis stroke="#8b949e" />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: 'rgba(30, 41, 59, 0.95)',
                      border: '1px solid rgba(59, 130, 246, 0.3)',
                      borderRadius: '8px',
                    }}
                  />
                  <Area
                    type="monotone"
                    dataKey="hours"
                    stroke="#3b82f6"
                    fillOpacity={1}
                    fill="url(#hoursGradient)"
                    name="Hours Logged"
                  />
                  <Line type="monotone" dataKey="expected" stroke="#ef4444" strokeDasharray="5 5" name="Expected" />
                </AreaChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          {/* Project Distribution */}
          <Card hover>
            <CardHeader>
              <CardTitle>Time Distribution by Project</CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={projectDistribution}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#30363d" />
                  <XAxis dataKey="name" stroke="#8b949e" angle={-45} textAnchor="end" height={100} />
                  <YAxis stroke="#8b949e" />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: 'rgba(30, 41, 59, 0.95)',
                      border: '1px solid rgba(59, 130, 246, 0.3)',
                      borderRadius: '8px',
                    }}
                  />
                  <Bar dataKey="hours" fill="#06b6d4" radius={[8, 8, 0, 0]} name="Hours" />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </div>

        {/* Active Projects */}
        <Card hover>
          <CardHeader>
            <CardTitle>Projects ({projects.length})</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {projects.length === 0 ? (
                <p className="text-gray-400 text-center py-8">No active projects</p>
              ) : (
                projects.slice(0, 10).map((project: any, i: number) => (
                  <motion.div
                    key={i}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: i * 0.05 }}
                    className="p-4 rounded-lg bg-white/5 border border-white/10 hover:border-blue-500/30 transition-colors"
                  >
                    <div className="flex items-center justify-between">
                      <div>
                        <h4 className="font-semibold mb-1">{project.project_name || project.project_id}</h4>
                        <div className="flex items-center gap-4 text-sm text-gray-400">
                          <span>Role: {project.role || 'Team Member'}</span>
                          <span>Allocation: {(project.allocation * 100).toFixed(0)}%</span>
                        </div>
                      </div>
                      <div className="text-right">
                        <p className="text-2xl font-bold text-blue-400">{project.total_hours.toFixed(0)}h</p>
                        <p className="text-xs text-gray-500">Total logged</p>
                      </div>
                    </div>
                  </motion.div>
                ))
              )}
            </div>
          </CardContent>
        </Card>

        {/* Anomalies */}
        {anomalies.length > 0 && (
          <Card hover className="border-red-500/20 bg-red-500/5">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-red-400">
                <AlertTriangle className="h-5 w-5" />
                Detected Anomalies ({anomalies.length})
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {anomalies.map((anomaly: any, i: number) => (
                  <motion.div
                    key={i}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: i * 0.05 }}
                    className="p-4 rounded-lg bg-red-500/10 border border-red-500/30"
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-2">
                          <Badge className="bg-red-500/20 text-red-400 border-red-500">
                            {anomaly.severity || 'warning'}
                          </Badge>
                          <span className="text-sm text-gray-400">
                            {new Date(anomaly.detected_at).toLocaleDateString()}
                          </span>
                        </div>
                        <p className="text-sm mb-1">{anomaly.description || 'Anomaly detected'}</p>
                        {anomaly.recommendation && (
                          <p className="text-xs text-gray-400 mt-2">💡 {anomaly.recommendation}</p>
                        )}
                      </div>
                    </div>
                  </motion.div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Recommendations */}
        {utilization.status === 'overutilized' && (
          <Card className="border-yellow-500/20 bg-yellow-500/5">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-yellow-400">
                <TrendingDown className="h-5 w-5" />
                Workload Optimization Recommendations
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <div className="p-3 rounded-lg bg-yellow-500/10 border border-yellow-500/20 text-sm">
                  💡 Reduce daily workload by {((utilization.utilization_rate - 1) * 100).toFixed(0)}% to reach
                  optimal utilization
                </div>
                <div className="p-3 rounded-lg bg-yellow-500/10 border border-yellow-500/20 text-sm">
                  💡 Consider redistributing {Math.ceil(projects.length * 0.2)} project(s) to other team members
                </div>
                <div className="p-3 rounded-lg bg-yellow-500/10 border border-yellow-500/20 text-sm">
                  💡 Schedule regular breaks and monitor for burnout signs
                </div>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </DashboardLayout>
  )
}
