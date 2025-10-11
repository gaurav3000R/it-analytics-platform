'use client'

import React from 'react'
import { useQuery } from '@tanstack/react-query'
import Link from 'next/link'
import {
  FolderKanban,
  AlertTriangle,
  DollarSign,
  Users,
  TrendingUp,
} from 'lucide-react'
import { analyticsApi, projectsApi } from '@/services/api'
import { QUERY_KEYS } from '@/lib/constants'
import { ButtonFuturistic } from '@/components/ui/button-futuristic'
import { MetricCardFuturistic } from './metric-card-futuristic'
import { ProjectCardFuturistic } from './project-card-futuristic'
import { GlassCard } from '@/components/ui/glass-card'
import { cn } from '@/lib/utils'
import { RiskChart } from './risk-chart'
import { AlertsList } from './alerts-list'
import { useRouter } from 'next/navigation'

export function DashboardOverview() {
  const router = useRouter()
  const { data: overview, isLoading: overviewLoading } = useQuery({
    queryKey: QUERY_KEYS.ANALYTICS_OVERVIEW,
    queryFn: analyticsApi.getOverview,
  })

  const { data: projects, isLoading: projectsLoading } = useQuery({
    queryKey: QUERY_KEYS.PROJECTS,
    queryFn: projectsApi.getAll,
  })

  const isLoading = overviewLoading || projectsLoading
  
  // Sample data for metrics
  const totalProjects = projects?.length || overview?.summary?.total_projects || 0
  const highRiskProjects = overview?.high_risk_projects || 0
  const totalBudget = overview?.summary?.total_budget || 0
  const totalTeamMembers = overview?.summary?.total_employees || 0

  if (isLoading) {
    return <DashboardSkeleton />
  }

  return (
    <div className="space-y-8">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-4xl font-bold bg-gradient-to-r from-cyan-600 via-purple-600 to-pink-600 bg-clip-text text-transparent mb-2">
            Dashboard Overview
          </h1>
          <p className="text-gray-600">
            Real-time insights and analytics for your IT portfolio
          </p>
        </div>
        
        <ButtonFuturistic variant="primary" size="md">
          <TrendingUp className="w-5 h-5 mr-2" />
          Generate Report
        </ButtonFuturistic>
      </div>
      
      {/* Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <MetricCardFuturistic
          title="Total Projects"
          value={totalProjects}
          change={12.5}
          icon={<FolderKanban className="w-5 h-5" />}
          color="cyan"
          loading={isLoading}
        />
        <MetricCardFuturistic
          title="High Risk Projects"
          value={highRiskProjects}
          change={-8.3}
          icon={<AlertTriangle className="w-5 h-5" />}
          color="pink"
          loading={isLoading}
        />
        <MetricCardFuturistic
          title="Total Budget"
          value={`$${(totalBudget / 1000000).toFixed(1)}M`}
          change={15.7}
          icon={<DollarSign className="w-5 h-5" />}
          color="purple"
          loading={isLoading}
        />
        <MetricCardFuturistic
          title="Team Members"
          value={totalTeamMembers}
          change={5.2}
          icon={<Users className="w-5 h-5" />}
          color="green"
          loading={isLoading}
        />
      </div>
      
      {/* Projects Grid */}
      <div>
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold text-gray-900">Active Projects</h2>
          <Link
            href="/projects"
            className="text-cyan-600 hover:text-cyan-700 transition-colors text-sm font-medium"
          >
            View All →
          </Link>
        </div>
        
        {projects && projects.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {projects.slice(0, 6).map((project: any) => (
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
              <h3 className="text-lg font-semibold text-gray-900 mb-2">No Projects Found</h3>
              <p className="text-gray-600 text-sm mb-4">Get started by creating your first project</p>
              <ButtonFuturistic variant="primary" size="sm">
                Create Project
              </ButtonFuturistic>
            </div>
          </GlassCard>
        )}
      </div>
      
      {/* Charts & Alerts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div>
          <RiskChart data={overview?.trending_risks || []} />
        </div>
        <div>
          <AlertsList alerts={overview?.recent_anomalies || []} />
        </div>
      </div>
      
      {/* Recent Activity */}
      <GlassCard hover={false}>
        <h3 className="text-xl font-bold text-gray-900 mb-4">Recent Activity</h3>
        <div className="space-y-3">
          {[1, 2, 3].map((i) => (
            <div key={i} className="flex items-center gap-4 p-3 rounded-lg hover:bg-gray-50 transition-colors">
              <div className="w-2 h-2 rounded-full bg-cyan-500 animate-pulse" />
              <div className="flex-1">
                <p className="text-gray-900 text-sm">Project {i} updated</p>
                <p className="text-gray-500 text-xs">{i * 2} minutes ago</p>
              </div>
            </div>
          ))}
        </div>
      </GlassCard>
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
