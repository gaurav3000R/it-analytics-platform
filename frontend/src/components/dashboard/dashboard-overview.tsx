'use client'

import React from 'react'
import { useQuery } from '@tanstack/react-query'
import Link from 'next/link'
import {
  FolderKanban,
  AlertTriangle,
  Users,
  TrendingUp,
  Activity,
} from 'lucide-react'
import { analyticsApi, projectsApi } from '@/services/api'
import { QUERY_KEYS } from '@/lib/constants'
import { ButtonFuturistic } from '@/components/ui/button-futuristic'
import { MetricCardFuturistic } from './metric-card-futuristic'
import { ProjectCardFuturistic } from './project-card-futuristic'
import { GlassCard } from '@/components/ui/glass-card'
import { RiskChart } from './risk-chart'
import { AlertsList } from './alerts-list'
import { useRouter } from 'next/navigation'
import type { AnalyticsOverviewResponse, RiskDashboardResponse } from '@/types'

export function DashboardOverview() {
  const router = useRouter()
  
  const { data: overview, isLoading: overviewLoading } = useQuery({
    queryKey: QUERY_KEYS.ANALYTICS_OVERVIEW,
    queryFn: analyticsApi.getOverview,
  })

  const { data: riskDashboard, isLoading: riskLoading } = useQuery({
    queryKey: QUERY_KEYS.RISK_DASHBOARD,
    queryFn: analyticsApi.getRiskDashboard,
  })

  const { data: projects, isLoading: projectsLoading } = useQuery({
    queryKey: QUERY_KEYS.PROJECTS,
    queryFn: projectsApi.getAll,
  })

  const isLoading = overviewLoading || projectsLoading || riskLoading
  
  // Extract data from API responses - no static values
  const totalProjects = overview?.summary?.total_projects || 0
  const totalEmployees = overview?.summary?.total_employees || 0
  const recentActivityLogs = overview?.summary?.recent_activity_logs || 0
  const recentAnomalies = overview?.summary?.recent_anomalies || 0
  
  // Risk metrics from risk dashboard
  const highRiskProjects = riskDashboard?.summary?.high_risk_projects || 0
  const criticalProjects = riskDashboard?.summary?.critical_projects || 0
  const avgRiskScore = riskDashboard?.summary?.avg_risk_score || 0
  
  // Risk distribution
  const riskDistribution = overview?.risk_distribution || {
    critical: 0,
    high: 0,
    medium: 0,
    low: 0,
    very_low: 0,
  }

  if (isLoading) {
    return <DashboardSkeleton />
  }

  return (
    <div className="space-y-8">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-5xl font-bold bg-gradient-to-r from-cyan-600 via-purple-600 to-pink-600 bg-clip-text text-transparent mb-3 tracking-tight">
            Dashboard Overview
          </h1>
          <p className="text-lg text-gray-600 leading-relaxed">
            Real-time insights and analytics for your IT portfolio • {overview?.period || 'Last 30 days'}
          </p>
        </div>
        
        <ButtonFuturistic variant="primary" size="md">
          <TrendingUp className="w-5 h-5 mr-2" />
          <span className="font-semibold">Generate Report</span>
        </ButtonFuturistic>
      </div>
      
      {/* Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <MetricCardFuturistic
          title="Total Projects"
          value={totalProjects}
          icon={<FolderKanban className="w-5 h-5" />}
          color="cyan"
          loading={isLoading}
        />
        <MetricCardFuturistic
          title="High Risk Projects"
          value={highRiskProjects}
          subtitle={criticalProjects > 0 ? `${criticalProjects} Critical` : undefined}
          icon={<AlertTriangle className="w-5 h-5" />}
          color="pink"
          loading={isLoading}
        />
        <MetricCardFuturistic
          title="Team Members"
          value={totalEmployees}
          icon={<Users className="w-5 h-5" />}
          color="purple"
          loading={isLoading}
        />
        <MetricCardFuturistic
          title="Recent Activity"
          value={recentActivityLogs}
          subtitle={`${recentAnomalies} Anomalies`}
          icon={<Activity className="w-5 h-5" />}
          color="green"
          loading={isLoading}
        />
      </div>

      {/* Risk Distribution Overview */}
      {(riskDistribution.critical > 0 || riskDistribution.high > 0 || riskDistribution.medium > 0) && (
        <GlassCard hover={false}>
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-2xl font-bold text-gray-900 tracking-tight">Risk Distribution</h3>
            <span className="text-sm text-gray-500">Avg Risk Score: {avgRiskScore.toFixed(1)}</span>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
            {riskDistribution.critical > 0 && (
              <div className="text-center p-4 rounded-xl bg-red-50 border border-red-200">
                <div className="text-3xl font-bold text-red-600">{riskDistribution.critical}</div>
                <div className="text-sm font-medium text-red-700 mt-1">Critical</div>
              </div>
            )}
            {riskDistribution.high > 0 && (
              <div className="text-center p-4 rounded-xl bg-orange-50 border border-orange-200">
                <div className="text-3xl font-bold text-orange-600">{riskDistribution.high}</div>
                <div className="text-sm font-medium text-orange-700 mt-1">High</div>
              </div>
            )}
            {riskDistribution.medium > 0 && (
              <div className="text-center p-4 rounded-xl bg-yellow-50 border border-yellow-200">
                <div className="text-3xl font-bold text-yellow-600">{riskDistribution.medium}</div>
                <div className="text-sm font-medium text-yellow-700 mt-1">Medium</div>
              </div>
            )}
            {riskDistribution.low > 0 && (
              <div className="text-center p-4 rounded-xl bg-blue-50 border border-blue-200">
                <div className="text-3xl font-bold text-blue-600">{riskDistribution.low}</div>
                <div className="text-sm font-medium text-blue-700 mt-1">Low</div>
              </div>
            )}
            {riskDistribution.very_low > 0 && (
              <div className="text-center p-4 rounded-xl bg-green-50 border border-green-200">
                <div className="text-3xl font-bold text-green-600">{riskDistribution.very_low}</div>
                <div className="text-sm font-medium text-green-700 mt-1">Very Low</div>
              </div>
            )}
          </div>
        </GlassCard>
      )}
      
      {/* Projects Grid */}
      <div>
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-3xl font-bold text-gray-900 tracking-tight">
            Active Projects
            {projects && projects.length > 0 && (
              <span className="text-lg font-normal text-gray-500 ml-3">({projects.length} total)</span>
            )}
          </h2>
          <Link
            href="/projects"
            className="text-cyan-600 hover:text-cyan-700 transition-colors text-base font-semibold flex items-center gap-2"
          >
            View All <span className="text-lg">→</span>
          </Link>
        </div>
        
        {projects && projects.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {projects.slice(0, 6).map((project) => (
              <ProjectCardFuturistic
                key={project.id}
                project={project}
                onClick={() => router.push(`/projects/${project.id}`)}
              />
            ))}
          </div>
        ) : (
          <GlassCard>
            <div className="text-center py-12">
              <FolderKanban className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-xl font-semibold text-gray-900 mb-2">No Projects Found</h3>
              <p className="text-base text-gray-600 mb-4">Get started by creating your first project</p>
              <ButtonFuturistic variant="primary" size="sm">
                <span className="font-semibold">Create Project</span>
              </ButtonFuturistic>
            </div>
          </GlassCard>
        )}
      </div>
      
      {/* Charts & Alerts */}
      {(riskDashboard?.risk_trends || riskDashboard?.top_risk_projects) && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {riskDashboard?.risk_trends && riskDashboard.risk_trends.length > 0 && (
            <div>
              <RiskChart data={riskDashboard.risk_trends} />
            </div>
          )}
          {riskDashboard?.top_risk_projects && riskDashboard.top_risk_projects.length > 0 && (
            <div>
              <GlassCard hover={false}>
                <h3 className="text-2xl font-bold text-gray-900 mb-6 tracking-tight">Top Risk Projects</h3>
                <div className="space-y-3">
                  {riskDashboard.top_risk_projects.slice(0, 5).map((project) => (
                    <div 
                      key={project.project_id}
                      onClick={() => router.push(`/projects/${project.project_id}`)}
                      className="flex items-center justify-between p-4 rounded-lg hover:bg-gray-50 transition-colors cursor-pointer border border-gray-100"
                    >
                      <div className="flex-1">
                        <p className="text-gray-900 text-sm font-semibold">{project.project_name}</p>
                        <p className="text-gray-500 text-xs mt-1">
                          Risk Score: {project.risk_score.toFixed(1)} • {project.risk_level}
                        </p>
                      </div>
                      <div className={`px-3 py-1 rounded-full text-xs font-medium ${
                        project.risk_level === 'critical' ? 'bg-red-100 text-red-700' :
                        project.risk_level === 'high' ? 'bg-orange-100 text-orange-700' :
                        'bg-yellow-100 text-yellow-700'
                      }`}>
                        {project.risk_level}
                      </div>
                    </div>
                  ))}
                </div>
              </GlassCard>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

const DashboardSkeleton = () => (
  <div className="space-y-8 animate-pulse">
    <div className="h-20 bg-gray-100 rounded-2xl" />
    <div className="grid grid-cols-4 gap-6">
      {[1, 2, 3, 4].map((i) => (
        <div key={i} className="h-32 bg-gray-100 rounded-2xl" />
      ))}
    </div>
    <div className="h-96 bg-gray-100 rounded-2xl" />
  </div>
)
