'use client'

import React from 'react'
import Link from 'next/link'
import { Bell, Search, Settings } from 'lucide-react'
import { cn } from '@/lib/utils'

export function Header() {
  const [searchQuery, setSearchQuery] = React.useState('')

  return (
    <header className={cn(
      'fixed top-0 left-0 right-0 z-50',
      'h-16',
      'bg-white/90 backdrop-blur-2xl',
      'border-b border-gray-200',
      'shadow-sm'
    )}>
      <div className="container mx-auto px-6 h-full flex items-center justify-between">
        {/* Logo */}
        <Link href="/" className="flex items-center gap-3 hover:opacity-80 transition-opacity">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-cyan-500 to-purple-500 flex items-center justify-center shadow-md">
            <span className="text-white font-bold text-xl">IT</span>
          </div>
          <span className="text-2xl font-bold bg-gradient-to-r from-cyan-600 via-purple-600 to-pink-600 bg-clip-text text-transparent tracking-tight">
            Analytics Platform
          </span>
        </Link>
        
        {/* Search Bar */}
        <div className="flex-1 max-w-md mx-8 hidden md:block">
          <div className="relative">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400 w-4 h-4" />
            <input
              type="search"
              placeholder="Search projects, teams, metrics..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className={cn(
                'w-full pl-11 pr-4 py-2 rounded-full',
                'bg-gray-50 backdrop-blur-xl',
                'border border-gray-200',
                'text-gray-900 text-sm font-medium placeholder-gray-500',
                'transition-all duration-300',
                'hover:bg-white hover:border-gray-300',
                'focus:outline-none focus:border-cyan-500 focus:ring-2 focus:ring-cyan-500/20'
              )}
            />
          </div>
        </div>
        
        {/* Actions */}
        <div className="flex items-center gap-3">
          <button className={cn(
            'relative w-10 h-10 rounded-full',
            'bg-gray-50 backdrop-blur-xl',
            'border border-gray-200',
            'text-gray-600',
            'transition-all duration-300',
            'hover:bg-cyan-50 hover:border-cyan-400 hover:text-cyan-600'
          )}>
            <Bell className="w-5 h-5 mx-auto" />
            <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full animate-pulse" />
          </button>
          
          <button className={cn(
            'w-10 h-10 rounded-full',
            'bg-gray-50 backdrop-blur-xl',
            'border border-gray-200',
            'text-gray-600',
            'transition-all duration-300',
            'hover:bg-purple-50 hover:border-purple-400 hover:text-purple-600'
          )}>
            <Settings className="w-5 h-5 mx-auto" />
          </button>
          
          <div className="w-10 h-10 rounded-full bg-gradient-to-br from-cyan-500 to-purple-500 cursor-pointer hover:scale-110 transition-transform flex items-center justify-center text-white font-bold text-sm shadow-md">
            AU
          </div>
        </div>
      </div>
    </header>
  )
}
