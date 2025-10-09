'use client'

import React from 'react'
import { DashboardLayout } from '@/components/layout/dashboard-layout'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Bug, AlertCircle, TrendingDown, Activity, BarChart3 } from 'lucide-react'
import { motion } from 'framer-motion'

export default function BugsPage() {
  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-4xl font-bold gradient-text mb-2">
              <Bug className="inline h-10 w-10 mr-3" />
              Bug Tracker
            </h1>
            <p className="text-gray-400">Monitor and analyze project bugs</p>
          </div>
          <Button><BarChart3 className="h-4 w-4 mr-2" />Analyze Portfolio</Button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          {[
            { title: 'Total Bugs', value: '342', icon: Bug, color: 'from-red-500 to-orange-500' },
            { title: 'Critical', value: '28', icon: AlertCircle, color: 'from-purple-500 to-pink-500' },
            { title: 'Bug Density', value: '2.3', icon: Activity, color: 'from-blue-500 to-cyan-500' },
            { title: 'Resolution Rate', value: '87%', icon: TrendingDown, color: 'from-green-500 to-emerald-500' },
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

        <Card hover>
          <CardHeader><CardTitle>Bug Analysis</CardTitle></CardHeader>
          <CardContent>
            <div className="text-center py-12 text-gray-400">
              <Bug className="h-16 w-16 mx-auto mb-4 text-gray-600" />
              <p>Bug tracking features coming soon</p>
              <p className="text-sm mt-2">Integrated bug analysis and resolution tracking</p>
            </div>
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  )
}
