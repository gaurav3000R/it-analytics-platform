'use client'

import React from 'react'
import { useQuery } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import { DashboardLayout } from '@/components/layout/dashboard-layout'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import {
  AlertTriangle,
  TrendingUp,
  Activity,
  Shield,
  RefreshCw,
  Target,
  BarChart3,
  AlertCircle,
  TrendingDown,
  CheckCircle,
} from 'lucide-react'
import { risksApi, projectsApi } from '@/services/api'
import { QUERY_KEYS } from '@/lib/constants'
import toast from 'react-hot-toast'
import { 
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
  LineChart,
  Line,
  Legend
} from 'recharts'

export default function RisksPage() {
  const { data: riskDashboard, isLoading, refetch } = useQuery({
    queryKey: QUERY_KEYS.RISKS_DASHBOARD,
    queryFn: risksApi.getDashboard,
  })

  const { data: projects } = useQuery({
    queryKey: QUERY_KEYS.PROJECTS,
    queryFn: projectsApi.getAll,
  })

  const { data: anomaliesList } = useQuery({
    queryKey: QUERY_KEYS.RISKS_ANOMALIES_LIST,
    queryFn: risksApi.getAnomaliesList,
  })

  const handleTrainModel = async () => {
    toast.promise(
      risksApi.trainModel().then(() => refetch()),
      {
        loading: 'Training risk prediction model...',
        success: (data: any) => `Model trained! R²: ${data?.metrics?.test_r2?.toFixed(3) || 'N/A'}`,
        error: 'Failed to train model',
      }
    )
  }

  const handleDetectAnomalies = async () => {
    toast.promise(
      risksApi.detectAnomalies().then(() => refetch()),
      {
        loading: 'Detecting anomalies...',
        success: 'Anomaly detection complete!',
        error: 'Failed to detect anomalies',
      }
    )
  }

  if (isLoading) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center min-h-[60vh]">
          <div className="text-center space-y-4">
            <div className="w-16 h-16 border-4 border-purple-500 border-t-transparent rounded-full animate-spin mx-auto" />
            <p className="text-gray-400">Loading risk analysis...</p>
          </div>
        </div>
      </DashboardLayout>
    )
  }

  const riskDistribution = [
    { name: 'Low Risk', value: riskDashboard?.low_risk_count || 0, color: '#10b981' },
    { name: 'Medium Risk', value: riskDashboard?.medium_risk_count || 0, color: '#f59e0b' },
    { name: 'High Risk', value: riskDashboard?.high_risk_count || 0, color: '#ef4444' },
  ]

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-4xl font-bold gradient-text mb-2">Risk Analysis</h1>
            <p className="text-gray-400">ML-powered risk prediction and monitoring</p>
          </div>
          <Button onClick={handleTrainModel}>
            <Shield className="h-4 w-4 mr-2" />
            Train ML Model
          </Button>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
            <Card hover className="glow-red">
              <CardContent className="p-6">
                <div className="flex items-center justify-between mb-4">
                  <div className="p-3 rounded-xl bg-red-500/20">
                    <AlertTriangle className="h-6 w-6 text-red-400" />
                  </div>
                  <TrendingUp className="h-5 w-5 text-red-400" />
                </div>
                <h3 className="text-gray-400 text-sm mb-1">High Risk</h3>
                <p className="text-3xl font-bold text-red-400">{riskDashboard?.high_risk_count || 0}</p>
              </CardContent>
            </Card>
          </motion.div>

          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
            <Card hover className="glow">
              <CardContent className="p-6">
                <div className="flex items-center justify-between mb-4">
                  <div className="p-3 rounded-xl bg-yellow-500/20">
                    <AlertCircle className="h-6 w-6 text-yellow-400" />
                  </div>
                </div>
                <h3 className="text-gray-400 text-sm mb-1">Medium Risk</h3>
                <p className="text-3xl font-bold text-yellow-400">{riskDashboard?.medium_risk_count || 0}</p>
              </CardContent>
            </Card>
          </motion.div>

          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
            <Card hover className="glow-green">
              <CardContent className="p-6">
                <div className="flex items-center justify-between mb-4">
                  <div className="p-3 rounded-xl bg-green-500/20">
                    <CheckCircle className="h-6 w-6 text-green-400" />
                  </div>
                  <TrendingDown className="h-5 w-5 text-green-400" />
                </div>
                <h3 className="text-gray-400 text-sm mb-1">Low Risk</h3>
                <p className="text-3xl font-bold text-green-400">{riskDashboard?.low_risk_count || 0}</p>
              </CardContent>
            </Card>
          </motion.div>

          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
            <Card hover glow>
              <CardContent className="p-6">
                <div className="flex items-center justify-between mb-4">
                  <div className="p-3 rounded-xl bg-purple-500/20">
                    <Activity className="h-6 w-6 text-purple-400" />
                  </div>
                </div>
                <h3 className="text-gray-400 text-sm mb-1">Avg Risk Score</h3>
                <p className="text-3xl font-bold">{(riskDashboard?.average_risk_score || 0).toFixed(1)}</p>
              </CardContent>
            </Card>
          </motion.div>
        </div>

        {/* Charts */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card hover>
            <CardHeader>
              <CardTitle>Risk Distribution</CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={riskDistribution}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#ffffff10" />
                  <XAxis dataKey="name" stroke="#9ca3af" fontSize={12} />
                  <YAxis stroke="#9ca3af" fontSize={12} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: 'rgba(30, 41, 59, 0.95)',
                      border: '1px solid rgba(168, 85, 247, 0.3)',
                      borderRadius: '8px',
                      color: '#fff',
                    }}
                  />
                  <Bar dataKey="value" fill="#a855f7" radius={[8, 8, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          <Card hover>
            <CardHeader>
              <CardTitle>Top Risk Projects</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {riskDashboard?.top_risk_projects?.slice(0, 5).map((project, index: number) => (
                  <motion.div
                    key={project.id}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.1 }}
                    className="flex items-center justify-between p-4 rounded-lg bg-white/5 hover:bg-white/10 transition-colors"
                  >
                    <div className="flex-1">
                      <div className="font-medium">{project.name}</div>
                      <div className="text-sm text-gray-400">{project.project_manager}</div>
                    </div>
                    <Badge variant={getRiskLevel(project.risk_score || 0) === 'high' ? 'danger' : 'warning'}>
                      {project.risk_score?.toFixed(0)}
                    </Badge>
                  </motion.div>
                )) || (
                  <div className="text-center py-8 text-gray-400">
                    No risk data available
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Risk Factors */}
        <Card hover>
          <CardHeader>
            <CardTitle>Common Risk Factors</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <RiskFactorCard
                icon={<AlertTriangle className="h-5 w-5" />}
                title="High Complexity"
                description="Projects with complexity score > 7"
                count={15}
                color="text-red-400"
              />
              <RiskFactorCard
                icon={<Activity className="h-5 w-5" />}
                title="Low Experience"
                description="Teams with < 2 years experience"
                count={12}
                color="text-yellow-400"
              />
              <RiskFactorCard
                icon={<TrendingUp className="h-5 w-5" />}
                title="Budget Overrun"
                description="Projects exceeding budget by > 10%"
                count={8}
                color="text-orange-400"
              />
            </div>
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  )
}

function RiskFactorCard({ icon, title, description, count, color }: {
  icon: React.ReactNode
  title: string
  description: string
  count: number
  color: string
}) {
  return (
    <div className="p-4 rounded-lg bg-white/5 border border-white/10">
      <div className={`flex items-center gap-3 mb-3 ${color}`}>
        {icon}
        <span className="font-semibold">{title}</span>
      </div>
      <p className="text-sm text-gray-400 mb-2">{description}</p>
      <p className="text-2xl font-bold">{count} projects</p>
    </div>
  )
}
