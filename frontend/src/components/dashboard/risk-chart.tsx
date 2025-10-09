'use client'

import React from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Area, AreaChart } from 'recharts'
import type { TrendingRisk } from '@/types'

interface RiskChartProps {
  data: TrendingRisk[]
}

export function RiskChart({ data }: RiskChartProps) {
  const chartData = data.map((item, index) => ({
    name: item.project_name?.slice(0, 15) || `Project ${index + 1}`,
    risk: item.risk_score || 0,
    change: item.change_percentage || 0,
  }))

  return (
    <Card hover>
      <CardHeader>
        <CardTitle>Risk Trends</CardTitle>
      </CardHeader>
      <CardContent>
        {chartData.length > 0 ? (
          <ResponsiveContainer width="100%" height={300}>
            <AreaChart data={chartData}>
              <defs>
                <linearGradient id="colorRisk" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="hsl(var(--color-primary))" stopOpacity={0.8} />
                  <stop offset="95%" stopColor="hsl(var(--color-primary))" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" className="stroke-white/10" />
              <XAxis
                dataKey="name"
                className="stroke-gray-400"
                fontSize={12}
                tickLine={false}
              />
              <YAxis className="stroke-gray-400" fontSize={12} tickLine={false} />
              <Tooltip
                contentStyle={{
                  backgroundColor: 'hsl(var(--color-card))',
                  border: '1px solid hsl(var(--color-border))',
                  borderRadius: '8px',
                }}
              />
              <Area
                type="monotone"
                dataKey="risk"
                className="stroke-primary"
                strokeWidth={2}
                fillOpacity={1}
                fill="url(#colorRisk)"
              />
            </AreaChart>
          </ResponsiveContainer>
        ) : (
          <div className="flex items-center justify-center h-[300px] text-gray-400">
            No trending risk data available
          </div>
        )}
      </CardContent>
    </Card>
  )
}
