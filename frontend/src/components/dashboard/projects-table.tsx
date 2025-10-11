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
  const [filter, setFilter] = React.useState<'all' | 'Critical' | 'High' | 'Medium' | 'Low'>('all')

  const filteredProjects = React.useMemo(() => {
    if (filter === 'all') return projects.slice(0, 10)
    return projects
      .filter((p) => p.risk_level === filter)
      .slice(0, 10)
  }, [projects, filter])

  return (
    <Card hover>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle>Recent Projects</CardTitle>
          <div className="flex gap-2">
            {['all', 'Critical', 'High', 'Medium', 'Low'].map((f) => (
              <button
                key={f}
                onClick={() => setFilter(f as typeof filter)}
                className={`px-3 py-1 rounded-lg text-sm font-medium transition-all ${
                  filter === f
                    ? 'bg-blue-500 text-white shadow-lg shadow-blue-500/30'
                    : 'bg-white/[0.03] text-gray-400 hover:bg-white/[0.06]'
                }`}
              >
                {f}
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
                <th className="text-left py-3 px-4 text-gray-400 font-semibold">Project ID</th>
                <th className="text-left py-3 px-4 text-gray-400 font-semibold">Type</th>
                <th className="text-center py-3 px-4 text-gray-400 font-semibold">Team</th>
                <th className="text-center py-3 px-4 text-gray-400 font-semibold">Budget</th>
                <th className="text-center py-3 px-4 text-gray-400 font-semibold">Complexity</th>
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
                    <div className="font-medium text-blue-400">{project.project_id}</div>
                  </td>
                  <td className="py-4 px-4">
                    <Badge variant="secondary">{project.project_type}</Badge>
                  </td>
                  <td className="py-4 px-4 text-center">
                    <span className="font-medium">{project.team_size || 0}</span>
                  </td>
                  <td className="py-4 px-4 text-center text-gray-300">
                    ${((project.budget_usd || 0) / 1000).toFixed(0)}k
                  </td>
                  <td className="py-4 px-4 text-center">
                    <div className="flex items-center justify-center gap-2">
                      <div className="w-16 bg-gray-700 rounded-full h-2">
                        <div
                          className="bg-gradient-to-r from-blue-500 to-cyan-500 h-2 rounded-full"
                          style={{ width: `${(project.complexity_score || 0) * 10}%` }}
                        />
                      </div>
                      <span className="text-xs text-gray-400">{project.complexity_score?.toFixed(1)}</span>
                    </div>
                  </td>
                  <td className="py-4 px-4 text-center">
                    <RiskBadge level={project.risk_level} />
                  </td>
                  <td className="py-4 px-4 text-center">
                    <Link href={`/projects/${project.project_id}`}>
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

function RiskBadge({ level }: { level: string }) {
  const colors = {
    Critical: 'bg-red-500/20 text-red-400 border-red-500/50',
    High: 'bg-orange-500/20 text-orange-400 border-orange-500/50',
    Medium: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/50',
    Low: 'bg-green-500/20 text-green-400 border-green-500/50',
  }

  return (
    <Badge className={`${colors[level as keyof typeof colors] || colors.Medium} border font-semibold`}>
      {level}
    </Badge>
  )
}
