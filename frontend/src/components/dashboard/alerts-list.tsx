'use client'

import React from 'react'
import { motion } from 'framer-motion'
import { AlertTriangle, AlertCircle, Info, CheckCircle } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import type { Anomaly } from '@/types'
import { formatDistanceToNow } from 'date-fns'

interface AlertsListProps {
  alerts: Anomaly[]
}

export function AlertsList({ alerts }: AlertsListProps) {
  const getIcon = (severity: string) => {
    switch (severity.toLowerCase()) {
      case 'critical':
      case 'high':
        return <AlertTriangle className="h-5 w-5 text-red-500" />
      case 'medium':
        return <AlertCircle className="h-5 w-5 text-yellow-500" />
      case 'low':
        return <Info className="h-5 w-5 text-blue-500" />
      default:
        return <CheckCircle className="h-5 w-5 text-green-500" />
    }
  }

  const getVariant = (severity: string) => {
    switch (severity.toLowerCase()) {
      case 'critical':
      case 'high':
        return 'danger' as const
      case 'medium':
        return 'warning' as const
      case 'low':
        return 'info' as const
      default:
        return 'success' as const
    }
  }

  return (
    <Card hover>
      <CardHeader>
        <CardTitle>Recent Alerts</CardTitle>
      </CardHeader>
      <CardContent>
        {alerts && alerts.length > 0 ? (
          <div className="space-y-3">
            {alerts.slice(0, 5).map((alert, index) => (
              <motion.div
                key={alert.id}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.2, delay: index * 0.05 }}
                className="flex items-start gap-3 p-3 rounded-lg bg-gray-50 hover:bg-gray-100 transition-colors border border-gray-100"
              >
                <div className="mt-0.5">{getIcon(alert.severity)}</div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <Badge variant={getVariant(alert.severity)} className="text-xs">
                      {alert.severity}
                    </Badge>
                    <span className="text-xs text-gray-600">
                      {alert.anomaly_type}
                    </span>
                  </div>
                  <p className="text-sm text-gray-700">{alert.description}</p>
                  <p className="text-xs text-gray-500 mt-1">
                    {alert.detected_at
                      ? formatDistanceToNow(new Date(alert.detected_at), { addSuffix: true })
                      : 'Recently'}
                  </p>
                </div>
                {!alert.resolved && (
                  <div className="flex-shrink-0">
                    <div className="h-2 w-2 rounded-full bg-red-500 animate-pulse" />
                  </div>
                )}
              </motion.div>
            ))}
          </div>
        ) : (
          <div className="flex flex-col items-center justify-center py-12 text-gray-600">
            <CheckCircle className="h-12 w-12 mb-3 text-green-500" />
            <p className="text-sm font-medium">No active alerts</p>
            <p className="text-xs text-gray-500">All systems operational</p>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
