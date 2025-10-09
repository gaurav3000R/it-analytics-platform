'use client'

import React from 'react'
import { DashboardLayout } from '@/components/layout/dashboard-layout'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { DollarSign, TrendingUp, TrendingDown, AlertTriangle, Target } from 'lucide-react'
import { motion } from 'framer-motion'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts'

export default function CostsPage() {
  const forecastData = [
    { month: 'Jan', budget: 100000, actual: 95000, forecast: 98000 },
    { month: 'Feb', budget: 100000, actual: 102000, forecast: 105000 },
    { month: 'Mar', budget: 100000, actual: 98000, forecast: 101000 },
    { month: 'Apr', budget: 100000, actual: 110000, forecast: 115000 },
    { month: 'May', budget: 100000, actual: 105000, forecast: 108000 },
    { month: 'Jun', budget: 100000, actual: 0, forecast: 112000 },
  ]

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-4xl font-bold gradient-text mb-2">
              <DollarSign className="inline h-10 w-10 mr-3" />
              Cost Forecasting
            </h1>
            <p className="text-gray-400">Budget tracking and overrun predictions</p>
          </div>
          <Button><Target className="h-4 w-4 mr-2" />View Forecasts</Button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          {[
            { title: 'Total Budget', value: '$2.4M', icon: DollarSign, color: 'from-blue-500 to-cyan-500', trend: '+12%' },
            { title: 'Spent to Date', value: '$1.8M', icon: TrendingUp, color: 'from-purple-500 to-pink-500', trend: '+8%' },
            { title: 'Budget Alerts', value: '5', icon: AlertTriangle, color: 'from-red-500 to-orange-500', trend: '-2' },
            { title: 'Overrun Risk', value: '15%', icon: TrendingDown, color: 'from-yellow-500 to-amber-500', trend: '-3%' },
          ].map((stat, i) => (
            <motion.div key={i} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.1 }}>
              <Card hover glow>
                <CardContent className="p-6">
                  <div className="flex items-center justify-between mb-4">
                    <div className={`p-3 rounded-xl bg-gradient-to-br ${stat.color} bg-opacity-20`}>
                      <stat.icon className="h-6 w-6" />
                    </div>
                    <span className="text-sm text-green-400 font-medium">{stat.trend}</span>
                  </div>
                  <h3 className="text-gray-400 text-sm mb-1">{stat.title}</h3>
                  <p className="text-3xl font-bold">{stat.value}</p>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </div>

        <Card hover>
          <CardHeader><CardTitle>Budget vs Actual vs Forecast</CardTitle></CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={350}>
              <LineChart data={forecastData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#ffffff10" />
                <XAxis dataKey="month" stroke="#9ca3af" />
                <YAxis stroke="#9ca3af" />
                <Tooltip contentStyle={{ backgroundColor: 'rgba(30, 41, 59, 0.95)', border: '1px solid rgba(168, 85, 247, 0.3)', borderRadius: '8px' }} />
                <Legend />
                <Line type="monotone" dataKey="budget" stroke="#3b82f6" strokeWidth={2} name="Budget" />
                <Line type="monotone" dataKey="actual" stroke="#10b981" strokeWidth={2} name="Actual" />
                <Line type="monotone" dataKey="forecast" stroke="#a855f7" strokeWidth={2} strokeDasharray="5 5" name="Forecast" />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <Card hover>
          <CardHeader><CardTitle>Budget Alerts</CardTitle></CardHeader>
          <CardContent>
            <div className="space-y-3">
              {[
                { project: 'Project Alpha', variance: '+15%', severity: 'high', amount: '$150K' },
                { project: 'Project Beta', variance: '+8%', severity: 'medium', amount: '$80K' },
                { project: 'Project Gamma', variance: '+12%', severity: 'high', amount: '$120K' },
                { project: 'Project Delta', variance: '+5%', severity: 'low', amount: '$50K' },
              ].map((alert, i) => (
                <div key={i} className="p-4 rounded-lg bg-white/5 border border-white/10 flex items-center justify-between">
                  <div className="flex-1">
                    <div className="font-medium mb-1">{alert.project}</div>
                    <div className="text-sm text-gray-400">Budget variance: <span className="text-red-400 font-semibold">{alert.variance}</span></div>
                  </div>
                  <div className="flex items-center gap-3">
                    <span className="text-xl font-bold text-red-400">{alert.amount}</span>
                    <Badge variant={alert.severity === 'high' ? 'danger' : alert.severity === 'medium' ? 'warning' : 'info'}>
                      {alert.severity}
                    </Badge>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  )
}
