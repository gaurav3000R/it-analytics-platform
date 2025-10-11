'use client'

import React from 'react'
import { useQuery } from '@tanstack/react-query'
import { DashboardLayout } from '@/components/layout/dashboard-layout'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Bug, AlertCircle, TrendingDown, Activity, BarChart3, RefreshCw, Target } from 'lucide-react'
import { motion } from 'framer-motion'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line, PieChart, Pie, Cell } from 'recharts'
import { bugTrackerApi, projectsApi } from '@/services/api'
import { QUERY_KEYS } from '@/lib/constants'
import toast from 'react-hot-toast'

export default function BugsPage() {
  const [selectedProjectId, setSelectedProjectId] = React.useState<string>('')

  const { data: bugDashboard, refetch } = useQuery({
    queryKey: QUERY_KEYS.BUG_DASHBOARD,
    queryFn: bugTrackerApi.getDashboard,
  })

  const { data: portfolioAnalysis } = useQuery({
    queryKey: QUERY_KEYS.BUG_PORTFOLIO,
    queryFn: bugTrackerApi.analyzePortfolio,
  })

  const { data: projects } = useQuery({
    queryKey: QUERY_KEYS.PROJECTS,
    queryFn: projectsApi.getAll,
  })

  const { data: projectAnalysis } = useQuery({
    queryKey: QUERY_KEYS.BUG_ANALYSIS(selectedProjectId),
    queryFn: () => bugTrackerApi.analyzeProject(selectedProjectId),
    enabled: !!selectedProjectId,
  })

  const handleRefresh = () => {
    toast.promise(refetch(), {
      loading: 'Refreshing bug data...',
      success: 'Bug data updated!',
      error: 'Failed to refresh',
    })
  }

  const totalBugs = portfolioAnalysis?.total_bugs || 0
  const projectsAnalyzed = portfolioAnalysis?.projects_analyzed || 0
  const avgBugsPerProject = projectsAnalyzed > 0 ? (totalBugs / projectsAnalyzed).toFixed(1) : '0'

  // Sample data for visualization (replace with real data when available)
  const bugTrendData = [
    { date: 'Week 1', open: 45, closed: 30, critical: 5 },
    { date: 'Week 2', open: 52, closed: 38, critical: 7 },
    { date: 'Week 3', open: 48, closed: 42, critical: 4 },
    { date: 'Week 4', open: 55, closed: 45, critical: 6 },
  ]

  const bugSeverityData = [
    { name: 'Critical', value: 28, color: '#dc2626' },
    { name: 'High', value: 85, color: '#ef4444' },
    { name: 'Medium', value: 142, color: '#f59e0b' },
    { name: 'Low', value: 87, color: '#10b981' },
  ]

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-4xl font-bold gradient-text mb-2">
              <Bug className="inline h-10 w-10 mr-3" />
              Bug Tracker Analytics
            </h1>
            <p className="text-gray-400">Monitor and analyze project bugs</p>
          </div>
          <Button onClick={handleRefresh}>
            <RefreshCw className="h-4 w-4 mr-2" />Refresh Data
          </Button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          {[
            { 
              title: 'Total Bugs', 
              value: totalBugs, 
              icon: Bug, 
              color: 'from-red-500 to-orange-500',
              description: `${projectsAnalyzed} projects`
            },
            { 
              title: 'Avg per Project', 
              value: avgBugsPerProject, 
              icon: Activity, 
              color: 'from-blue-500 to-cyan-500',
              description: 'Portfolio average'
            },
            { 
              title: 'Critical', 
              value: '28', 
              icon: AlertCircle, 
              color: 'from-purple-500 to-pink-500',
              description: 'Immediate attention'
            },
            { 
              title: 'Resolution Rate', 
              value: '87%', 
              icon: TrendingDown, 
              color: 'from-green-500 to-emerald-500',
              description: 'Last 30 days'
            },
          ].map((stat, i) => (
            <motion.div key={i} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.1 }}>
              <Card hover glow>
                <CardContent className="p-6">
                  <div className={`p-3 rounded-xl bg-gradient-to-br ${stat.color} bg-opacity-20 mb-4 inline-block`}>
                    <stat.icon className="h-6 w-6" />
                  </div>
                  <h3 className="text-gray-400 text-sm mb-1">{stat.title}</h3>
                  <p className="text-3xl font-bold mb-1">{stat.value}</p>
                  <p className="text-xs text-gray-500">{stat.description}</p>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </div>

        {/* Charts Row */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Bug Severity Distribution */}
          <Card hover>
            <CardHeader><CardTitle>Bug Severity Distribution</CardTitle></CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie 
                    data={bugSeverityData} 
                    dataKey="value" 
                    nameKey="name" 
                    cx="50%" 
                    cy="50%" 
                    outerRadius={100}
                    label={(entry) => `${entry.name}: ${entry.value}`}
                  >
                    {bugSeverityData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip contentStyle={{ backgroundColor: 'rgba(30, 41, 59, 0.95)', border: '1px solid rgba(59, 130, 246, 0.3)', borderRadius: '8px' }} />
                </PieChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          {/* Bug Trends */}
          <Card hover>
            <CardHeader><CardTitle>Bug Trends (Last 4 Weeks)</CardTitle></CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={bugTrendData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#30363d" />
                  <XAxis dataKey="date" stroke="#8b949e" />
                  <YAxis stroke="#8b949e" />
                  <Tooltip contentStyle={{ backgroundColor: 'rgba(30, 41, 59, 0.95)', border: '1px solid rgba(59, 130, 246, 0.3)', borderRadius: '8px' }} />
                  <Line type="monotone" dataKey="open" stroke="#ef4444" name="Open" strokeWidth={2} />
                  <Line type="monotone" dataKey="closed" stroke="#10b981" name="Closed" strokeWidth={2} />
                  <Line type="monotone" dataKey="critical" stroke="#dc2626" name="Critical" strokeWidth={2} />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </div>

        {/* Project Analysis */}
        <Card hover>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle>Project Bug Analysis</CardTitle>
              <div className="flex gap-2">
                <select
                  className="bg-white/5 border border-white/10 rounded px-3 py-1 text-sm"
                  value={selectedProjectId}
                  onChange={(e) => setSelectedProjectId(e.target.value)}
                >
                  <option value="">Select a project...</option>
                  {projects?.slice(0, 20).map((project) => (
                    <option key={project.id} value={project.id}>
                      {project.project_id}
                    </option>
                  ))}
                </select>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            {selectedProjectId && projectAnalysis ? (
              <div className="space-y-4">
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div className="p-4 rounded-lg bg-white/5">
                    <p className="text-gray-400 text-sm">Total Bugs</p>
                    <p className="text-2xl font-bold">{projectAnalysis.bug_patterns?.total_bugs || 0}</p>
                  </div>
                  <div className="p-4 rounded-lg bg-white/5">
                    <p className="text-gray-400 text-sm">Daily Average</p>
                    <p className="text-2xl font-bold">{projectAnalysis.bug_patterns?.avg_daily_bugs?.toFixed(1) || 0}</p>
                  </div>
                  <div className="p-4 rounded-lg bg-white/5">
                    <p className="text-gray-400 text-sm">Volatility</p>
                    <p className="text-2xl font-bold">{projectAnalysis.bug_patterns?.bug_volatility || 0}</p>
                  </div>
                  <div className="p-4 rounded-lg bg-white/5">
                    <p className="text-gray-400 text-sm">Trend</p>
                    <p className="text-2xl font-bold">{projectAnalysis.quality_trends?.trend || 'N/A'}</p>
                  </div>
                </div>

                {projectAnalysis?.recommendations && projectAnalysis.recommendations.length > 0 && (
                  <div>
                    <h4 className="font-semibold mb-2">Recommendations</h4>
                    <div className="space-y-2">
                      {projectAnalysis.recommendations.map((rec: string, i: number) => (
                        <div key={i} className="p-3 rounded-lg bg-blue-500/10 border border-blue-500/20 text-sm">
                          💡 {rec}
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="text-center py-12 text-gray-400">
                <Bug className="h-16 w-16 mx-auto mb-4 text-gray-600" />
                <p>Select a project to view detailed bug analysis</p>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Portfolio Summary */}
        {portfolioAnalysis && (
          <Card className="bg-purple-500/5 border-purple-500/20">
            <CardContent className="p-4">
              <div className="flex items-center gap-4 text-sm">
                <BarChart3 className="h-5 w-5 text-purple-400" />
                <span className="text-gray-400">
                  Portfolio: {portfolioAnalysis.total_bugs} bugs across {portfolioAnalysis.projects_analyzed} projects •
                  Average: {avgBugsPerProject} bugs per project
                </span>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </DashboardLayout>
  )
}
