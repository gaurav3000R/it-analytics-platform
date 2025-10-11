'use client'

import React from 'react'
import { GlassCard } from '@/components/ui/glass-card'
import { XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Area, AreaChart, Legend } from 'recharts'
import type { RiskTrend } from '@/types'

interface RiskChartProps {
  data: RiskTrend[]
}

export function RiskChart({ data }: RiskChartProps) {
  const chartData = data.map((item) => ({
    date: new Date(item.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
    avgRisk: Math.round(item.avg_risk_score * 10) / 10,
    highRisk: item.high_risk_count,
    critical: item.critical_count,
  }))

  return (
    <GlassCard hover={false}>
      <h3 className="text-2xl font-bold text-gray-900 mb-6 tracking-tight">Risk Trends Over Time</h3>
      {chartData.length > 0 ? (
        <ResponsiveContainer width="100%" height={320}>
          <AreaChart data={chartData}>
            <defs>
              <linearGradient id="colorAvgRisk" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.8} />
                <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0.1} />
              </linearGradient>
              <linearGradient id="colorHighRisk" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#f59e0b" stopOpacity={0.6} />
                <stop offset="95%" stopColor="#f59e0b" stopOpacity={0.05} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" opacity={0.5} />
            <XAxis
              dataKey="date"
              stroke="#6b7280"
              fontSize={12}
              tickLine={false}
              axisLine={false}
            />
            <YAxis 
              stroke="#6b7280" 
              fontSize={12} 
              tickLine={false}
              axisLine={false}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: 'rgba(255, 255, 255, 0.98)',
                border: '1px solid #e5e7eb',
                borderRadius: '12px',
                color: '#1f2937',
                boxShadow: '0 10px 25px -5px rgb(0 0 0 / 0.1)',
                padding: '12px',
              }}
              labelStyle={{ 
                color: '#1f2937',
                fontWeight: 600,
                marginBottom: '4px'
              }}
            />
            <Legend 
              wrapperStyle={{
                paddingTop: '20px',
                fontSize: '14px',
                fontWeight: 500
              }}
            />
            <Area
              type="monotone"
              dataKey="avgRisk"
              name="Avg Risk Score"
              stroke="#8b5cf6"
              strokeWidth={3}
              fillOpacity={1}
              fill="url(#colorAvgRisk)"
            />
            <Area
              type="monotone"
              dataKey="highRisk"
              name="High Risk Count"
              stroke="#f59e0b"
              strokeWidth={2}
              fillOpacity={1}
              fill="url(#colorHighRisk)"
            />
          </AreaChart>
        </ResponsiveContainer>
      ) : (
        <div className="flex items-center justify-center h-[320px] text-gray-500">
          <div className="text-center">
            <p className="text-lg font-medium">No risk trend data available</p>
            <p className="text-sm mt-2">Data will appear as your projects are analyzed</p>
          </div>
        </div>
      )}
    </GlassCard>
  )
}
