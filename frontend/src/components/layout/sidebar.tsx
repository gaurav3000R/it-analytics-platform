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
  { name: 'Risk Analysis', href: '/risks', icon: AlertTriangle },
  { name: 'Anomalies', href: '/anomalies', icon: Activity },
  { name: 'AI Insights', href: '/ai-insights', icon: Brain },
  { name: 'ML Predictions', href: '/ml-predictions', icon: Zap },
  { name: 'Bug Tracker', href: '/bugs', icon: Bug },
  { name: 'Resources', href: '/resources', icon: Users },
  { name: 'Cost Forecasting', href: '/costs', icon: DollarSign },
  { name: 'Analytics', href: '/analytics', icon: BarChart3 },
]

export function Sidebar() {
  const pathname = usePathname()
  const { isCollapsed, toggleCollapsed } = useSidebarStore()

  return (
    <aside
      className={cn(
        'fixed left-0 top-0 z-40 h-screen transition-all duration-300 bg-[#161b22] border-r border-[#30363d] backdrop-blur-xl',
        isCollapsed ? 'w-20' : 'w-64'
      )}
    >
      <div className="flex h-full flex-col">
        {/* Logo */}
        <div className="flex h-16 items-center justify-between px-4 border-b border-[#30363d]">
          {!isCollapsed && (
            <Link href="/" className="flex items-center gap-2">
              <div className="h-8 w-8 rounded-lg bg-gradient-to-br from-blue-500 to-cyan-500 flex items-center justify-center shadow-lg shadow-blue-500/30">
                <BarChart3 className="h-5 w-5 text-white" />
              </div>
              <span className="text-xl font-bold gradient-text">IT Analytics</span>
            </Link>
          )}
          <button
            onClick={toggleCollapsed}
            className="p-2 rounded-lg hover:bg-white/[0.06] transition-colors text-gray-300 hover:text-white"
          >
            {isCollapsed ? (
              <ChevronRight className="h-5 w-5" />
            ) : (
              <ChevronLeft className="h-5 w-5" />
            )}
          </button>
        </div>

        {/* Navigation */}
        <nav className="flex-1 space-y-1 px-3 py-4 overflow-y-auto">
          {navigation.map((item) => {
            const isActive = pathname === item.href
            const Icon = item.icon
            
            return (
              <Link
                key={item.name}
                href={item.href}
                className={cn(
                  'flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-all',
                  isActive
                    ? 'bg-blue-500/20 text-blue-400 shadow-lg shadow-blue-500/20 border border-blue-500/30'
                    : 'text-gray-400 hover:bg-white/[0.06] hover:text-white',
                  isCollapsed && 'justify-center'
                )}
                title={isCollapsed ? item.name : undefined}
              >
                <Icon className="h-5 w-5 flex-shrink-0" />
                {!isCollapsed && <span>{item.name}</span>}
              </Link>
            )
          })}
        </nav>

        {/* Footer */}
        <div className="border-t border-[#30363d] p-4">
          <Link
            href="/settings"
            className={cn(
              'flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium text-gray-400 transition-all hover:bg-white/[0.06] hover:text-white',
              isCollapsed && 'justify-center'
            )}
            title={isCollapsed ? 'Settings' : undefined}
          >
            <Settings className="h-5 w-5 flex-shrink-0" />
            {!isCollapsed && <span>Settings</span>}
          </Link>
        </div>
      </div>
    </aside>
  )
}
