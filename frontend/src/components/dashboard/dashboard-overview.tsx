'use client'

import React from 'react'
import { useQuery } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import {
  Activity,
  AlertTriangle,
  TrendingUp,
  Users,
  Clock,
  CheckCircle,
  ArrowUp,
  ArrowDown,
} from 'lucide-react'
import { analyticsApi, projectsApi } from '@/services/api'
import { QUERY_KEYS } from '@/lib/constants'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { formatNumber } from '@/lib/utils'
import { ProjectsTable } from './projects-table'
import { RiskChart } from './risk-chart'
import { AlertsList } from './alerts-list'
import toast from 'react-hot-toast'

export function DashboardOverview() {
  const { data: overview, isLoading: overviewLoading, error: overviewError, refetch: refetchOverview } = useQuery({
    queryKey: QUERY_KEYS.ANALYTICS_OVERVIEW,
    queryFn: analyticsApi.getOverview,
  })

  const { data: _riskDashboard, isLoading: riskLoading, refetch: refetchRisk } = useQuery({
    queryKey: QUERY_KEYS.RISK_DASHBOARD,
    queryFn: analyticsApi.getRiskDashboard,
  })

  const { data: projects, isLoading: projectsLoading } = useQuery({
    queryKey: QUERY_KEYS.PROJECTS,
    queryFn: projectsApi.getAll,
  })

  const isLoading = overviewLoading || riskLoading || projectsLoading

  const handleRefresh = async () => {
    toast.promise(
      Promise.all([refetchOverview(), refetchRisk()]),
      {
        loading: 'Refreshing data...',
        success: 'Data refreshed successfully!',
        error: 'Failed to refresh data',
      }
    )
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-center space-y-4">
          <div className="w-16 h-16 border-4 border-purple-500 border-t-transparent rounded-full animate-spin mx-auto" />
          <p className="text-gray-400">Loading analytics...</p>
        </div>
      </div>
    )
  }

  if (overviewError) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <Card className="max-w-md">
          <CardContent className="pt-6">
            <div className="text-center space-y-4">
              <AlertTriangle className="w-12 h-12 text-red-500 mx-auto" />
              <h2 className="text-xl font-bold">Error Loading Data</h2>
              <p className="text-gray-400">
                {overviewError instanceof Error ? overviewError.message : 'Failed to load dashboard data'}
              </p>
              <Button onClick={handleRefresh}>Try Again</Button>
            </div>
          </CardContent>
        </Card>
      </div>
    )
  }

  const stats = [
    {
      icon: Activity,
      title: 'Active Projects',
      value: overview?.total_projects || 0,
      change: '+12%',
      positive: true,
      color: 'from-blue-500 to-cyan-500',
    },
    {
      icon: Users,
      title: 'Team Members',
      value: overview?.total_employees || 0,
      change: '+5%',
      positive: true,
      color: 'from-purple-500 to-pink-500',
    },
    {
      icon: AlertTriangle,
      title: 'High Risk Projects',
      value: overview?.high_risk_projects || 0,
      change: '-3%',
      positive: true,
      color: 'from-red-500 to-orange-500',
    },
    {
      icon: TrendingUp,
      title: 'Avg Risk Score',
      value: (overview?.avg_risk_score || 0).toFixed(1),
      change: '-8%',
      positive: true,
      color: 'from-green-500 to-emerald-500',
    },
  ]

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-4xl font-bold gradient-text mb-2">
            Operational Risk Early Warning System
          </h1>
          <p className="text-gray-400">AI-Powered IT Services Project Analytics</p>
        </div>
        <Button onClick={handleRefresh} variant="outline">
          <Activity className="h-4 w-4 mr-2" />
          Refresh
        </Button>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat, index) => (
          <motion.div
            key={stat.title}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3, delay: index * 0.1 }}
          >
            <StatCard {...stat} />
          </motion.div>
        ))}
      </div>

      {/* Risk Distribution & System Status */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.3, delay: 0.4 }}
        >
          <Card hover>
            <CardHeader>
              <CardTitle>Risk Distribution</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <RiskBar
                label="High Risk"
                count={overview?.high_risk_projects || 0}
                total={overview?.total_projects || 1}
                color="bg-red-500"
              />
              <RiskBar
                label="Medium Risk"
                count={overview?.medium_risk_projects || 0}
                total={overview?.total_projects || 1}
                color="bg-yellow-500"
              />
              <RiskBar
                label="Low Risk"
                count={overview?.low_risk_projects || 0}
                total={overview?.total_projects || 1}
                color="bg-green-500"
              />
            </CardContent>
          </Card>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3, delay: 0.5 }}
          className="lg:col-span-2"
        >
          <Card hover>
            <CardHeader>
              <CardTitle>System Status</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 gap-4">
                <StatusItem
                  icon={<CheckCircle className="h-5 w-5" />}
                  label="Anomaly Detection"
                  status="Active"
                  color="text-green-400"
                />
                <StatusItem
                  icon={<CheckCircle className="h-5 w-5" />}
                  label="Risk Prediction"
                  status="Active"
                  color="text-green-400"
                />
                <StatusItem
                  icon={<Clock className="h-5 w-5" />}
                  label="Last Sync"
                  status="2 min ago"
                  color="text-blue-400"
                />
                <StatusItem
                  icon={<Activity className="h-5 w-5" />}
                  label="Data Quality"
                  status="98%"
                  color="text-green-400"
                />
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </div>

      {/* Charts & Alerts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.3, delay: 0.6 }}
        >
          <RiskChart data={overview?.trending_risks || []} />
        </motion.div>
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.3, delay: 0.6 }}
        >
          <AlertsList alerts={overview?.recent_anomalies || []} />
        </motion.div>
      </div>

      {/* Projects Table */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3, delay: 0.7 }}
      >
        <ProjectsTable projects={projects || []} />
      </motion.div>
    </div>
  )
}

interface StatCardProps {
  icon: React.ElementType
  title: string
  value: string | number
  change: string
  positive: boolean
  color: string
}

function StatCard({ icon: Icon, title, value, change, positive, color }: StatCardProps) {
  return (
    <Card hover glow>
      <CardContent className="p-6">
        <div className="flex items-start justify-between mb-4">
          <div className={`p-3 rounded-xl bg-gradient-to-br ${color} bg-opacity-20`}>
            <Icon className="h-6 w-6 text-white" />
          </div>
          <div className={`flex items-center gap-1 text-sm font-medium ${positive ? 'text-green-400' : 'text-red-400'}`}>
            {positive ? <ArrowUp className="h-4 w-4" /> : <ArrowDown className="h-4 w-4" />}
            {change}
          </div>
        </div>
        <h3 className="text-gray-400 text-sm mb-1">{title}</h3>
        <p className="text-3xl font-bold">{formatNumber(Number(value))}</p>
      </CardContent>
    </Card>
  )
}

interface RiskBarProps {
  label: string
  count: number
  total: number
  color: string
}

function RiskBar({ label, count, total, color }: RiskBarProps) {
  const percentage = (count / total) * 100

  return (
    <div>
      <div className="flex justify-between text-sm mb-2">
        <span className="text-gray-400">{label}</span>
        <span className="font-medium">{count}</span>
      </div>
      <div className="w-full bg-white/10 rounded-full h-2 overflow-hidden">
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: `${percentage}%` }}
          transition={{ duration: 0.5, ease: 'easeOut' }}
          className={`${color} h-2 rounded-full`}
        />
      </div>
    </div>
  )
}

interface StatusItemProps {
  icon: React.ReactNode
  label: string
  status: string
  color: string
}

function StatusItem({ icon, label, status, color }: StatusItemProps) {
  return (
    <div className="flex items-center gap-3 p-3 bg-white/5 rounded-lg">
      <div className={color}>{icon}</div>
      <div>
        <div className="text-gray-400 text-xs">{label}</div>
        <div className="text-sm font-medium">{status}</div>
      </div>
    </div>
  )
}
