'use client'

import React from 'react'
import { Sidebar } from './sidebar'
import { Header } from './header'

export function DashboardLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen bg-gradient-to-br from-white via-gray-50 to-white">
      <Header />
      <Sidebar />
      <main className="ml-64 pt-16 min-h-screen">
        <div className="p-6 md:p-8">
          {children}
        </div>
      </main>
    </div>
  )
}
