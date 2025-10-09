'use client'

import React from 'react'
import { DashboardLayout } from '@/components/layout/dashboard-layout'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Users, TrendingUp, Activity, AlertTriangle, RefreshCw } from 'lucide-react'
import { motion } from 'framer-motion'
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts'

export default function ResourcesPage() {
  const utilizationData = [
    { name: 'Optimal', value: 65, fill: 'hsl(var(--color-success))' },
    { name: 'Over-utilized', value: 20, fill: 'hsl(var(--color-destructive))' },
    { name: 'Under-utilized', value: 15, fill: 'hsl(var(--color-warning))' },
  ]

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-4xl font-bold gradient-text mb-2">
              <Users className="inline h-10 w-10 mr-3" />
              Resource Management
            </h1>
            <p className="text-gray-400">Monitor team utilization and capacity</p>
          </div>
          <Button><RefreshCw className="h-4 w-4 mr-2" />Rebalance Resources</Button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          {[
            { title: 'Total Resources', value: '248', icon: Users, color: 'from-blue-500 to-cyan-500' },
            { title: 'Avg Utilization', value: '78%', icon: Activity, color: 'from-purple-500 to-pink-500' },
            { title: 'Over-utilized', value: '24', icon: AlertTriangle, color: 'from-red-500 to-orange-500' },
            { title: 'Efficiency Score', value: '8.5', icon: TrendingUp, color: 'from-green-500 to-emerald-500' },
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
            <CardHeader><CardTitle>Resource Utilization</CardTitle></CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie data={utilizationData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={80} label>
                    {utilizationData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.fill} />
                    ))}
                  </Pie>
                  <Tooltip contentStyle={{ backgroundColor: 'hsl(var(--color-card))', border: '1px solid hsl(var(--color-border))', borderRadius: '8px' }} />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          <Card hover>
            <CardHeader><CardTitle>Rebalancing Suggestions</CardTitle></CardHeader>
            <CardContent>
              <div className="space-y-3">
                {[
                  { from: 'Project Alpha', to: 'Project Beta', count: 3, reason: 'Reduce overutilization' },
                  { from: 'Project Gamma', to: 'Project Delta', count: 2, reason: 'Balance workload' },
                  { from: 'Project Epsilon', to: 'Project Zeta', count: 4, reason: 'Optimize capacity' },
                ].map((suggestion, i) => (
                  <div key={i} className="p-4 rounded-lg bg-white/5 border border-white/10">
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-medium">{suggestion.count} resources</span>
                      <Button size="sm" variant="ghost">Apply</Button>
                    </div>
                    <p className="text-sm text-gray-400">
                      <span className="text-blue-400">{suggestion.from}</span> → <span className="text-green-400">{suggestion.to}</span>
                    </p>
                    <p className="text-xs text-gray-500 mt-1">{suggestion.reason}</p>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </DashboardLayout>
  )
}
