'use client'

import React from 'react'
import { Sidebar } from './sidebar'
import { Header } from './header'
import { useSidebarStore } from '@/store'
import { cn } from '@/lib/utils'

export function DashboardLayout({ children }: { children: React.ReactNode }) {
  const { isCollapsed } = useSidebarStore()

  return (
    <div className="min-h-screen">
      <Sidebar />
      <div
        className={cn(
          'transition-all duration-300',
          isCollapsed ? 'ml-20' : 'ml-64'
        )}
      >
        <Header />
        <main className="p-6">{children}</main>
      </div>
    </div>
  )
}
