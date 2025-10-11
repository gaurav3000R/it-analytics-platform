'use client'

import React from 'react'
import { useQuery } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import { DashboardLayout } from '@/components/layout/dashboard-layout'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import {
  FolderKanban,
  Upload,
  Download,
  Plus,
  Search,
  Filter,
  Eye,
  Edit,
  Trash2,
  Calendar,
  Users,
  DollarSign,
  Clock,
  TrendingUp,
} from 'lucide-react'
import { projectsApi } from '@/services/api'
import { QUERY_KEYS } from '@/lib/constants'
import { getRiskLevel, formatCurrency } from '@/lib/utils'
import toast from 'react-hot-toast'
import Link from 'next/link'

export default function ProjectsPage() {
  const [searchQuery, setSearchQuery] = React.useState('')
  const [filterRisk, setFilterRisk] = React.useState<string>('all')
  const [filterStatus, setFilterStatus] = React.useState<string>('all')

  const { data: projects, isLoading, error, refetch } = useQuery({
    queryKey: QUERY_KEYS.PROJECTS,
    queryFn: projectsApi.getAll,
  })

  const handleLoadDefaultData = async () => {
    toast.promise(
      projectsApi.loadDefaultCsv(),
      {
        loading: 'Loading default dataset...',
        success: (data) => {
          refetch()
          return `Loaded ${data.projects_loaded} projects successfully!`
        },
        error: 'Failed to load default data',
      }
    )
  }

  const handleGenerateSampleData = async () => {
    toast.promise(
      projectsApi.generateSampleData(50),
      {
        loading: 'Generating sample data...',
        success: (data) => {
          refetch()
          return `Generated ${data.projects_generated} sample projects!`
        },
        error: 'Failed to generate sample data',
      }
    )
  }

  const filteredProjects = React.useMemo(() => {
    if (!projects) return []
    
    return projects.filter((project) => {
      const matchesSearch = project.name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
                          project.project_manager?.toLowerCase().includes(searchQuery.toLowerCase())
      const matchesRisk = filterRisk === 'all' || getRiskLevel(project.risk_score || 0) === filterRisk
      const matchesStatus = filterStatus === 'all' || project.status === filterStatus
      
      return matchesSearch && matchesRisk && matchesStatus
    })
  }, [projects, searchQuery, filterRisk, filterStatus])

  const stats = React.useMemo(() => {
    if (!projects) return { total: 0, active: 0, completed: 0, totalBudget: 0 }
    
    return {
      total: projects.length,
      active: projects.filter(p => p.status === 'active').length,
      completed: projects.filter(p => p.status === 'completed').length,
      totalBudget: projects.reduce((sum, p) => sum + (p.project_budget_usd || p.budget || 0), 0),
    }
  }, [projects])

  if (isLoading) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center min-h-[60vh]">
          <div className="text-center space-y-4">
            <div className="w-16 h-16 border-4 border-purple-500 border-t-transparent rounded-full animate-spin mx-auto" />
            <p className="text-gray-400">Loading projects...</p>
          </div>
        </div>
      </DashboardLayout>
    )
  }

  if (error) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center min-h-[60vh]">
          <Card className="max-w-md">
            <CardContent className="pt-6 text-center space-y-4">
              <FolderKanban className="w-12 h-12 text-red-500 mx-auto" />
              <h2 className="text-xl font-bold">Error Loading Projects</h2>
              <p className="text-gray-400">
                {error instanceof Error ? error.message : 'Failed to load projects'}
              </p>
              <Button onClick={() => refetch()}>Try Again</Button>
            </CardContent>
          </Card>
        </div>
      </DashboardLayout>
    )
  }

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-4xl font-bold gradient-text mb-2">Projects</h1>
            <p className="text-gray-400">Manage and monitor all your IT projects</p>
          </div>
          <div className="flex gap-3">
            <Button variant="outline" onClick={handleLoadDefaultData}>
              <Download className="h-4 w-4 mr-2" />
              Load Default Data
            </Button>
            <Button variant="outline" onClick={handleGenerateSampleData}>
              <Plus className="h-4 w-4 mr-2" />
              Generate Samples
            </Button>
            <Button>
              <Upload className="h-4 w-4 mr-2" />
              Upload CSV
            </Button>
          </div>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
            <Card hover glow>
              <CardContent className="p-6">
                <div className="flex items-center justify-between mb-4">
                  <div className="p-3 rounded-xl bg-blue-50/80 border border-blue-100">
                    <FolderKanban className="h-6 w-6 text-blue-600" />
                  </div>
                </div>
                <h3 className="text-gray-600 text-sm mb-1 font-medium">Total Projects</h3>
                <p className="text-3xl font-bold text-gray-900">{stats.total}</p>
              </CardContent>
            </Card>
          </motion.div>

          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
            <Card hover glow>
              <CardContent className="p-6">
                <div className="flex items-center justify-between mb-4">
                  <div className="p-3 rounded-xl bg-green-50/80 border border-green-100">
                    <TrendingUp className="h-6 w-6 text-green-600" />
                  </div>
                </div>
                <h3 className="text-gray-600 text-sm mb-1 font-medium">Active Projects</h3>
                <p className="text-3xl font-bold text-gray-900">{stats.active}</p>
              </CardContent>
            </Card>
          </motion.div>

          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
            <Card hover glow>
              <CardContent className="p-6">
                <div className="flex items-center justify-between mb-4">
                  <div className="p-3 rounded-xl bg-purple-50/80 border border-purple-100">
                    <Clock className="h-6 w-6 text-purple-600" />
                  </div>
                </div>
                <h3 className="text-gray-600 text-sm mb-1 font-medium">Completed</h3>
                <p className="text-3xl font-bold text-gray-900">{stats.completed}</p>
              </CardContent>
            </Card>
          </motion.div>

          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
            <Card hover glow>
              <CardContent className="p-6">
                <div className="flex items-center justify-between mb-4">
                  <div className="p-3 rounded-xl bg-amber-50/80 border border-amber-100">
                    <DollarSign className="h-6 w-6 text-amber-600" />
                  </div>
                </div>
                <h3 className="text-gray-600 text-sm mb-1 font-medium">Total Budget</h3>
                <p className="text-3xl font-bold text-gray-900">{formatCurrency(stats.totalBudget)}</p>
              </CardContent>
            </Card>
          </motion.div>
        </div>

        {/* Filters */}
        <Card>
          <CardContent className="p-6">
            <div className="flex flex-col md:flex-row gap-4">
              <div className="flex-1 relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search projects..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="input-field pl-10 w-full"
                />
              </div>
              
              <select
                value={filterRisk}
                onChange={(e) => setFilterRisk(e.target.value)}
                className="input-field w-full md:w-48"
              >
                <option value="all">All Risk Levels</option>
                <option value="low">Low Risk</option>
                <option value="medium">Medium Risk</option>
                <option value="high">High Risk</option>
              </select>

              <select
                value={filterStatus}
                onChange={(e) => setFilterStatus(e.target.value)}
                className="input-field w-full md:w-48"
              >
                <option value="all">All Statuses</option>
                <option value="active">Active</option>
                <option value="completed">Completed</option>
                <option value="on-hold">On Hold</option>
              </select>
            </div>
          </CardContent>
        </Card>

        {/* Projects Table */}
        <Card hover>
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              <span>All Projects ({filteredProjects.length})</span>
              <Button variant="ghost" size="sm" onClick={() => refetch()}>
                <Filter className="h-4 w-4 mr-2" />
                Refresh
              </Button>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-white/10">
                    <th className="text-left py-3 px-4 text-gray-400 font-semibold">Project</th>
                    <th className="text-left py-3 px-4 text-gray-400 font-semibold">Manager</th>
                    <th className="text-center py-3 px-4 text-gray-400 font-semibold">Team</th>
                    <th className="text-center py-3 px-4 text-gray-400 font-semibold">Budget</th>
                    <th className="text-center py-3 px-4 text-gray-400 font-semibold">Timeline</th>
                    <th className="text-center py-3 px-4 text-gray-400 font-semibold">Status</th>
                    <th className="text-center py-3 px-4 text-gray-400 font-semibold">Risk</th>
                    <th className="text-center py-3 px-4 text-gray-400 font-semibold">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredProjects.map((project, index) => (
                    <motion.tr
                      key={project.id}
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      transition={{ delay: index * 0.05 }}
                      className="border-b border-white/5 hover:bg-white/5 transition-colors"
                    >
                      <td className="py-4 px-4">
                        <div>
                          <div className="font-medium">{project.name}</div>
                          <div className="text-gray-400 text-sm truncate max-w-xs">
                            {project.project_type || 'N/A'}
                          </div>
                        </div>
                      </td>
                      <td className="py-4 px-4 text-gray-300">{project.project_manager || 'N/A'}</td>
                      <td className="py-4 px-4 text-center">
                        <div className="flex items-center justify-center gap-1">
                          <Users className="h-4 w-4 text-gray-400" />
                          <span className="font-medium">{project.team_size || 0}</span>
                        </div>
                      </td>
                      <td className="py-4 px-4 text-center text-gray-300">
                        {formatCurrency(project.project_budget_usd || project.budget || 0)}
                      </td>
                      <td className="py-4 px-4 text-center">
                        <div className="flex items-center justify-center gap-1">
                          <Calendar className="h-4 w-4 text-gray-400" />
                          <span className="text-sm">{project.estimated_timeline_months || 0}m</span>
                        </div>
                      </td>
                      <td className="py-4 px-4 text-center">
                        <Badge variant={project.status === 'active' ? 'success' : 'secondary'}>
                          {project.status || 'unknown'}
                        </Badge>
                      </td>
                      <td className="py-4 px-4 text-center">
                        <RiskBadge score={project.risk_score || 0} />
                      </td>
                      <td className="py-4 px-4 text-center">
                        <div className="flex items-center justify-center gap-2">
                          <Link href={`/projects/${project.id}`}>
                            <Button variant="ghost" size="sm">
                              <Eye className="h-4 w-4" />
                            </Button>
                          </Link>
                          <Button variant="ghost" size="sm">
                            <Edit className="h-4 w-4" />
                          </Button>
                          <Button variant="ghost" size="sm">
                            <Trash2 className="h-4 w-4 text-red-400" />
                          </Button>
                        </div>
                      </td>
                    </motion.tr>
                  ))}
                </tbody>
              </table>

              {filteredProjects.length === 0 && (
                <div className="text-center py-12">
                  <FolderKanban className="h-12 w-12 text-gray-600 mx-auto mb-4" />
                  <p className="text-gray-400 mb-4">No projects found</p>
                  <Button onClick={handleLoadDefaultData}>
                    Load Default Data
                  </Button>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  )
}

function RiskBadge({ score }: { score: number }) {
  const level = getRiskLevel(score)
  const variant = level === 'high' ? 'danger' : level === 'medium' ? 'warning' : 'success'

  return (
    <Badge variant={variant} className="font-bold">
      {score.toFixed(0)}
    </Badge>
  )
}
