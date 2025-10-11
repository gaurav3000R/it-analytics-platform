'use client'

import React from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import {
  LayoutDashboard,
  FolderKanban,
  AlertTriangle,
  Brain,
  Bug,
  Users,
  DollarSign,
  BarChart3,
  Settings,
  ChevronLeft,
  ChevronRight,
  Activity,
  Zap,
} from 'lucide-react'
import { cn } from '@/lib/utils'
import { useSidebarStore } from '@/store'

const navigation = [
  { name: 'Dashboard', href: '/', icon: LayoutDashboard },
  { name: 'Projects', href: '/projects', icon: FolderKanban },
  { name: 'Analytics', href: '/analytics', icon: BarChart3 },
  { name: 'Risks', href: '/risks', icon: AlertTriangle },
  { name: 'Bug Tracker', href: '/bugs', icon: Bug },
  { name: 'Resources', href: '/resources', icon: Users },
  { name: 'Costs', href: '/costs', icon: DollarSign },
  { name: 'AI Insights', href: '/ai-insights', icon: Brain },
  { name: 'Anomalies', href: '/anomalies', icon: Activity },
]

export function Sidebar() {
  const pathname = usePathname()
  
  return (
    <aside className={cn(
      'fixed left-0 top-16 bottom-0',
      'w-64',
      'bg-[#0A0E27]/80 backdrop-blur-2xl',
      'border-r border-white/10',
      'overflow-y-auto'
    )}>
      <nav className="p-4 space-y-2">
        {navigation.map((item) => {
          const isActive = pathname === item.href
          const Icon = item.icon
          
          return (
            <Link
              key={item.name}
              href={item.href}
              className={cn(
                'flex items-center gap-3 px-4 py-3 rounded-xl',
                'font-medium transition-all duration-300',
                isActive ? [
                  'bg-gradient-to-r from-cyan-500/10 to-purple-500/10',
                  'border border-cyan-500/30',
                  'text-white',
                  'shadow-[0_0_10px_rgba(0,245,255,0.2)]'
                ] : [
                  'text-gray-400',
                  'hover:bg-white/5',
                  'hover:text-white'
                ]
              )}
            >
              <Icon className={cn(
                'w-5 h-5',
                isActive ? 'text-cyan-400' : 'text-gray-500'
              )} />
              {item.name}
            </Link>
          )
        })}
      </nav>
      
      {/* Bottom Section */}
      <div className="absolute bottom-0 left-0 right-0 p-4">
        <div className={cn(
          'rounded-xl p-4',
          'bg-gradient-to-br from-purple-500/10 to-pink-500/10',
          'border border-purple-500/20'
        )}>
          <div className="text-sm font-medium text-white mb-1">
            System Status
          </div>
          <div className="flex items-center gap-2 text-xs text-gray-400">
            <span className="w-2 h-2 rounded-full bg-green-400 animate-pulse" />
            All systems operational
          </div>
        </div>
      </div>
    </aside>
  )
}
