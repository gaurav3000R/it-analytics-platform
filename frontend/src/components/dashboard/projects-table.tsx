'use client'

import React from 'react'
import { motion } from 'framer-motion'
import { Eye, TrendingUp, TrendingDown } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import type { Project } from '@/types'
import { getRiskLevel } from '@/lib/utils'
import Link from 'next/link'

interface ProjectsTableProps {
  projects: Project[]
}

export function ProjectsTable({ projects }: ProjectsTableProps) {
  const [filter, setFilter] = React.useState<'all' | 'high' | 'medium' | 'low'>('all')

  const filteredProjects = React.useMemo(() => {
    if (filter === 'all') return projects.slice(0, 10)
    return projects
      .filter((p) => getRiskLevel(p.risk_score || 0) === filter)
      .slice(0, 10)
  }, [projects, filter])

  return (
    <Card hover>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle>Project Risk Overview</CardTitle>
          <div className="flex gap-2">
            {['all', 'high', 'medium', 'low'].map((f) => (
              <button
                key={f}
                onClick={() => setFilter(f as typeof filter)}
                className={`px-3 py-1 rounded-lg text-sm font-medium transition-all ${
                  filter === f
                    ? 'bg-blue-500 text-white shadow-lg shadow-blue-500/30'
                    : 'bg-white/[0.03] text-gray-400 hover:bg-white/[0.06]'
                }`}
              >
                {f.charAt(0).toUpperCase() + f.slice(1)}
              </button>
            ))}
          </div>
        </div>
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
                <th className="text-center py-3 px-4 text-gray-400 font-semibold">Status</th>
                <th className="text-center py-3 px-4 text-gray-400 font-semibold">Risk</th>
                <th className="text-center py-3 px-4 text-gray-400 font-semibold">Actions</th>
              </tr>
            </thead>
            <tbody>
              {filteredProjects.map((project, index) => (
                <motion.tr
                  key={project.id}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.2, delay: index * 0.05 }}
                  className="border-b border-white/5 hover:bg-white/5 transition-colors"
                >
                  <td className="py-4 px-4">
                    <div>
                      <div className="font-medium">{project.name}</div>
                      <div className="text-gray-400 text-sm truncate max-w-xs">
                        {project.description || 'No description'}
                      </div>
                    </div>
                  </td>
                  <td className="py-4 px-4 text-gray-300">{project.project_manager || 'N/A'}</td>
                  <td className="py-4 px-4 text-center">
                    <span className="font-medium">{project.team_size || 0}</span>
                  </td>
                  <td className="py-4 px-4 text-center text-gray-300">
                    ${((project.project_budget_usd || project.budget || 0) / 1000).toFixed(0)}k
                  </td>
                  <td className="py-4 px-4 text-center">
                    <Badge
                      variant={
                        project.status === 'active' ? 'success' : 'secondary'
                      }
                    >
                      {project.status || 'unknown'}
                    </Badge>
                  </td>
                  <td className="py-4 px-4 text-center">
                    <RiskBadge score={project.risk_score || 0} />
                  </td>
                  <td className="py-4 px-4 text-center">
                    <Link href={`/projects/${project.id}`}>
                      <Button variant="ghost" size="sm">
                        <Eye className="h-4 w-4" />
                      </Button>
                    </Link>
                  </td>
                </motion.tr>
              ))}
            </tbody>
          </table>
        </div>
      </CardContent>
    </Card>
  )
}

function RiskBadge({ score }: { score: number }) {
  const level = getRiskLevel(score)
  const variant = level === 'high' ? 'danger' : level === 'medium' ? 'warning' : 'success'

  return (
    <div className="flex items-center justify-center gap-2">
      <Badge variant={variant} className="font-bold">
        {score.toFixed(0)}
      </Badge>
      {level === 'high' && <TrendingUp className="h-4 w-4 text-red-400" />}
      {level === 'low' && <TrendingDown className="h-4 w-4 text-green-400" />}
    </div>
  )
}
