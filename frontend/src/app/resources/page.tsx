'use client'

import React from 'react'
import { useQuery } from '@tanstack/react-query'
import { DashboardLayout } from '@/components/layout/dashboard-layout'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Users, TrendingUp, Activity, AlertTriangle, RefreshCw, Clock } from 'lucide-react'
import { motion } from 'framer-motion'
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip, BarChart, Bar, XAxis, YAxis, CartesianGrid } from 'recharts'
import { resourceApi } from '@/services/api'
import { QUERY_KEYS } from '@/lib/constants'
import toast from 'react-hot-toast'

export default function ResourcesPage() {
  const { data: resourceData, isLoading, refetch } = useQuery({
    queryKey: QUERY_KEYS.RESOURCE_ANALYZE,
    queryFn: resourceApi.analyze,
  })

  const handleRefresh = async () => {
    toast.promise(refetch(), {
      loading: 'Refreshing resource data...',
      success: 'Data refreshed successfully!',
      error: 'Failed to refresh data',
    })
  }

  if (isLoading) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center min-h-[60vh]">
          <div className="text-center space-y-4">
            <div className="w-16 h-16 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto" />
            <p className="text-gray-400">Loading resource data...</p>
          </div>
        </div>
      </DashboardLayout>
    )
  }

  const utilizationData = [
    { name: 'Optimal', value: resourceData?.summary_stats?.optimal_count || 0, color: '#10b981' },
    { name: 'Over-utilized', value: resourceData?.summary_stats?.overutilized_count || 0, color: '#ef4444' },
    { name: 'Critical', value: resourceData?.summary_stats?.critically_overutilized || 0, color: '#dc2626' },
  ]

  const criticalAlerts = resourceData?.alerts?.filter(a => a.severity === 'critical').slice(0, 10) || []

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-4xl font-bold gradient-text mb-2">
              <Users className="inline h-10 w-10 mr-3" />
              Resource Management
            </h1>
            <p className="text-gray-400">Monitor team utilization and capacity - {resourceData?.period_days} days analysis</p>
          </div>
          <Button onClick={handleRefresh}>
            <RefreshCw className="h-4 w-4 mr-2" />Refresh Data
          </Button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          {[
            { 
              title: 'Total Employees', 
              value: resourceData?.total_employees || 0, 
              icon: Users, 
              bgColor: 'bg-blue-50/80',
              borderColor: 'border-blue-100',
              iconColor: 'text-blue-600',
              description: 'Active team members'
            },
            { 
              title: 'Avg Utilization', 
              value: `${((resourceData?.summary_stats?.avg_utilization || 0) * 100).toFixed(0)}%`, 
              icon: Activity, 
              bgColor: 'bg-purple-50/80',
              borderColor: 'border-purple-100',
              iconColor: 'text-purple-600',
              description: 'Team average'
            },
            { 
              title: 'Critical Alerts', 
              value: resourceData?.summary_stats?.critically_overutilized || 0, 
              icon: AlertTriangle, 
              bgColor: 'bg-red-50/80',
              borderColor: 'border-red-100',
              iconColor: 'text-red-600',
              description: 'Needs immediate action'
            },
            { 
              title: 'Optimal Resources', 
              value: resourceData?.summary_stats?.optimal_count || 0, 
              icon: TrendingUp, 
              bgColor: 'bg-green-50/80',
              borderColor: 'border-green-100',
              iconColor: 'text-green-600',
              description: 'Well balanced'
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

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card hover>
            <CardHeader><CardTitle>Resource Utilization</CardTitle></CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie data={utilizationData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={80} label>
                    {utilizationData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip contentStyle={{ backgroundColor: 'rgba(30, 41, 59, 0.95)', border: '1px solid rgba(168, 85, 247, 0.3)', borderRadius: '8px' }} />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          <Card hover>
            <CardHeader>
              <CardTitle>Critical Alerts - Immediate Action Required</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3 max-h-[400px] overflow-y-auto">
                {criticalAlerts.length === 0 ? (
                  <p className="text-gray-400 text-center py-4">No critical alerts</p>
                ) : (
                  criticalAlerts.map((alert, i) => (
                    <motion.div
                      key={i}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: i * 0.05 }}
                      className="p-4 rounded-lg bg-red-500/10 border border-red-500/30"
                    >
                      <div className="flex items-start justify-between mb-2">
                        <div>
                          <span className="font-semibold text-red-400">{alert.employee_name}</span>
                          <Badge variant="secondary" className="ml-2 text-xs">{alert.employee_role}</Badge>
                        </div>
                        <Badge className="bg-red-500/20 text-red-400 border-red-500">
                          {alert.severity}
                        </Badge>
                      </div>
                      <div className="flex items-center gap-2 mb-2">
                        <Clock className="h-4 w-4 text-gray-400" />
                        <span className="text-sm">
                          {alert.avg_daily_hours?.toFixed(1)}h / {alert.expected_hours}h daily
                          <span className="text-red-400 ml-2 font-semibold">
                            ({(alert.utilization_rate * 100).toFixed(0)}%)
                          </span>
                        </span>
                      </div>
                      <p className="text-sm text-gray-300 mb-2">{alert.message}</p>
                      <p className="text-xs text-gray-400 bg-white/5 p-2 rounded">
                        💡 {alert.recommendation}
                      </p>
                    </motion.div>
                  ))
                )}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* All Alerts Section */}
        <Card hover>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle>All Resource Alerts ({resourceData?.alerts?.length || 0})</CardTitle>
              <div className="flex gap-2">
                {['all', 'critical', 'high', 'medium'].map((severity) => (
                  <Badge
                    key={severity}
                    variant="secondary"
                    className="cursor-pointer hover:bg-blue-500/20"
                  >
                    {severity}
                  </Badge>
                ))}
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {resourceData?.alerts?.slice(0, 12).map((alert, i) => (
                <div
                  key={i}
                  className={`p-4 rounded-lg border ${
                    alert.severity === 'critical'
                      ? 'bg-red-500/10 border-red-500/30'
                      : 'bg-yellow-500/10 border-yellow-500/30'
                  }`}
                >
                  <div className="flex items-center justify-between mb-2">
                    <span className="font-medium text-sm">{alert.employee_name}</span>
                    <Badge
                      variant="secondary"
                      className={`text-xs ${
                        alert.severity === 'critical' ? 'bg-red-500/20 text-red-400' : 'bg-yellow-500/20 text-yellow-400'
                      }`}
                    >
                      {alert.type}
                    </Badge>
                  </div>
                  <p className="text-xs text-gray-400 mb-1">{alert.employee_role}</p>
                  {alert.utilization_rate && (
                    <div className="mt-2">
                      <div className="w-full bg-gray-700 rounded-full h-2">
                        <div
                          className={`h-2 rounded-full ${
                            alert.severity === 'critical' ? 'bg-red-500' : 'bg-yellow-500'
                          }`}
                          style={{ width: `${Math.min(alert.utilization_rate * 100, 100)}%` }}
                        />
                      </div>
                      <p className="text-xs text-gray-500 mt-1">
                        {(alert.utilization_rate * 100).toFixed(0)}% utilized
                      </p>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  )
}
