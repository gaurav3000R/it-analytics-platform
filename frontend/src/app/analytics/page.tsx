'use client'

import React from 'react'
import { useQuery } from '@tanstack/react-query'
import { DashboardLayout } from '@/components/layout/dashboard-layout'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { BarChart3, TrendingUp, Activity, PieChart, Download } from 'lucide-react'
import { motion } from 'framer-motion'
import { analyticsApi } from '@/services/api'
import { QUERY_KEYS } from '@/lib/constants'
import { AreaChart, Area, BarChart, Bar, PieChart as RePieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts'

export default function AnalyticsPage() {
  const { data: overview, isLoading } = useQuery({
    queryKey: QUERY_KEYS.ANALYTICS_OVERVIEW,
    queryFn: analyticsApi.getOverview,
  })

  const riskData = [
    { name: 'High', value: overview?.high_risk_projects || 0, color: '#ef4444' },
    { name: 'Medium', value: overview?.medium_risk_projects || 0, color: '#f59e0b' },
    { name: 'Low', value: overview?.low_risk_projects || 0, color: '#10b981' },
  ]

  const monthlyTrend = [
    { month: 'Jan', projects: 45, risks: 12, budget: 1.2 },
    { month: 'Feb', projects: 52, risks: 15, budget: 1.4 },
    { month: 'Mar', projects: 48, risks: 11, budget: 1.3 },
    { month: 'Apr', projects: 61, risks: 18, budget: 1.6 },
    { month: 'May', projects: 58, risks: 14, budget: 1.5 },
    { month: 'Jun', projects: 65, risks: 16, budget: 1.7 },
  ]

  if (isLoading) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center min-h-[60vh]">
          <div className="text-center space-y-4">
            <div className="w-16 h-16 border-4 border-purple-500 border-t-transparent rounded-full animate-spin mx-auto" />
            <p className="text-gray-400">Loading analytics...</p>
          </div>
        </div>
      </DashboardLayout>
    )
  }

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-4xl font-bold gradient-text mb-2">
              <BarChart3 className="inline h-10 w-10 mr-3" />
              Advanced Analytics
            </h1>
            <p className="text-gray-400">Comprehensive insights and metrics</p>
          </div>
          <Button><Download className="h-4 w-4 mr-2" />Export Report</Button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          {[
            { title: 'Total Projects', value: overview?.total_projects || 0, icon: Activity, color: 'from-blue-500 to-cyan-500' },
            { title: 'Team Members', value: overview?.total_employees || 0, icon: TrendingUp, color: 'from-purple-500 to-pink-500' },
            { title: 'Avg Risk Score', value: (overview?.avg_risk_score || 0).toFixed(1), icon: BarChart3, color: 'from-yellow-500 to-orange-500' },
            { title: 'Active Alerts', value: overview?.recent_anomalies?.length || 0, icon: PieChart, color: 'from-red-500 to-pink-500' },
          ].map((stat, i) => (
            <motion.div key={i} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.1 }}>
              <Card hover glow>
                <CardContent className="p-6">
                  <div className={`p-3 rounded-xl bg-gradient-to-br ${stat.color} bg-opacity-20 mb-4 inline-block`}>
                    <stat.icon className="h-6 w-6" />
                  </div>
                  <h3 className="text-gray-400 text-sm mb-1">{stat.title}</h3>
                  <p className="text-3xl font-bold">{stat.value}</p>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card hover>
            <CardHeader><CardTitle>Monthly Project Trends</CardTitle></CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <AreaChart data={monthlyTrend}>
                  <defs>
                    <linearGradient id="colorProjects" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#a855f7" stopOpacity={0.8}/>
                      <stop offset="95%" stopColor="#a855f7" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#ffffff10" />
                  <XAxis dataKey="month" stroke="#9ca3af" fontSize={12} />
                  <YAxis stroke="#9ca3af" fontSize={12} />
                  <Tooltip contentStyle={{ backgroundColor: 'rgba(30, 41, 59, 0.95)', border: '1px solid rgba(168, 85, 247, 0.3)', borderRadius: '8px' }} />
                  <Area type="monotone" dataKey="projects" stroke="#a855f7" fillOpacity={1} fill="url(#colorProjects)" />
                </AreaChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          <Card hover>
            <CardHeader><CardTitle>Risk Distribution</CardTitle></CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <RePieChart>
                  <Pie data={riskData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={90} label>
                    {riskData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip contentStyle={{ backgroundColor: 'rgba(30, 41, 59, 0.95)', border: '1px solid rgba(168, 85, 247, 0.3)', borderRadius: '8px' }} />
                  <Legend />
                </RePieChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </div>

        <Card hover>
          <CardHeader><CardTitle>Performance Metrics</CardTitle></CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={350}>
              <BarChart data={monthlyTrend}>
                <CartesianGrid strokeDasharray="3 3" stroke="#ffffff10" />
                <XAxis dataKey="month" stroke="#9ca3af" />
                <YAxis stroke="#9ca3af" />
                <Tooltip contentStyle={{ backgroundColor: 'rgba(30, 41, 59, 0.95)', border: '1px solid rgba(168, 85, 247, 0.3)', borderRadius: '8px' }} />
                <Legend />
                <Bar dataKey="projects" fill="#a855f7" name="Projects" radius={[8, 8, 0, 0]} />
                <Bar dataKey="risks" fill="#ef4444" name="High Risk" radius={[8, 8, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {[
            { title: 'System Health', score: '98%', status: 'Excellent', color: 'text-green-400' },
            { title: 'Data Quality', score: '95%', status: 'Very Good', color: 'text-blue-400' },
            { title: 'Prediction Accuracy', score: '87%', status: 'Good', color: 'text-purple-400' },
          ].map((metric, i) => (
            <Card key={i} hover glow>
              <CardContent className="p-6">
                <h3 className="text-gray-400 text-sm mb-2">{metric.title}</h3>
                <p className={`text-4xl font-bold mb-2 ${metric.color}`}>{metric.score}</p>
                <p className="text-sm text-gray-400">{metric.status}</p>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </DashboardLayout>
  )
}
