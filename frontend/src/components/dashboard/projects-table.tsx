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
                    ? 'bg-blue-500 text-white shadow-md'
                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
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
              <tr className="border-b border-gray-200">
                <th className="text-left py-3 px-4 text-gray-600 font-semibold">Project ID</th>
                <th className="text-left py-3 px-4 text-gray-600 font-semibold">Type</th>
                <th className="text-center py-3 px-4 text-gray-600 font-semibold">Team</th>
                <th className="text-center py-3 px-4 text-gray-600 font-semibold">Budget</th>
                <th className="text-center py-3 px-4 text-gray-600 font-semibold">Complexity</th>
                <th className="text-center py-3 px-4 text-gray-600 font-semibold">Risk</th>
                <th className="text-center py-3 px-4 text-gray-600 font-semibold">Actions</th>
              </tr>
            </thead>
            <tbody>
              {filteredProjects.map((project, index) => (
                <motion.tr
                  key={project.id}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.2, delay: index * 0.05 }}
                  className="border-b border-gray-100 hover:bg-gray-50 transition-colors"
                >
                  <td className="py-4 px-4">
                    <div className="font-medium text-blue-600">{project.project_id}</div>
                  </td>
                  <td className="py-4 px-4">
                    <Badge variant="secondary">{project.project_type}</Badge>
                  </td>
                  <td className="py-4 px-4 text-center">
                    <span className="font-medium text-gray-900">{project.team_size || 0}</span>
                  </td>
                  <td className="py-4 px-4 text-center text-gray-700">
                    ${((project.budget_usd || 0) / 1000).toFixed(0)}k
                  </td>
                  <td className="py-4 px-4 text-center">
                    <div className="flex items-center justify-center gap-2">
                      <div className="w-16 bg-gray-200 rounded-full h-2">
                        <div
                          className="bg-blue-600 h-2 rounded-full"
                          style={{ width: `${(project.complexity_score || 0) * 10}%` }}
                        />
                      </div>
                      <span className="text-xs text-gray-600">{project.complexity_score?.toFixed(1)}</span>
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
    Critical: 'bg-red-50 text-red-700 border-red-300',
    High: 'bg-orange-50 text-orange-700 border-orange-300',
    Medium: 'bg-yellow-50 text-yellow-700 border-yellow-300',
    Low: 'bg-green-50 text-green-700 border-green-300',
  }

  return (
    <Badge className={`${colors[level as keyof typeof colors] || colors.Medium} border font-semibold`}>
      {level}
    </Badge>
  )
}
