'use client'

import React from 'react'
import { Bell, Search, Moon, Sun, RefreshCw } from 'lucide-react'
import { useThemeStore } from '@/store'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'

export function Header() {
  const { theme, toggleTheme } = useThemeStore()
  const [searchQuery, setSearchQuery] = React.useState('')

  return (
    <header className="sticky top-0 z-30 bg-[#161b22] border-b border-[#30363d] backdrop-blur-xl">
      <div className="flex h-16 items-center justify-between px-6">
        {/* Search */}
        <div className="flex-1 max-w-2xl">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
            <input
              type="text"
              placeholder="Search projects, risks, insights..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full rounded-lg bg-[#0d1117] border border-[#30363d] py-2 pl-10 pr-4 text-sm text-gray-200 placeholder-gray-500 focus:border-blue-500/50 focus:outline-none focus:ring-2 focus:ring-blue-500/20 transition-all hover:border-[#3d444d]"
            />
          </div>
        </div>

        {/* Actions */}
        <div className="flex items-center gap-3 ml-6">
          <Button
            variant="ghost"
            size="icon"
            onClick={() => window.location.reload()}
            title="Refresh data"
            className="text-gray-300 hover:text-white"
          >
            <RefreshCw className="h-5 w-5" />
          </Button>

          <button
            onClick={toggleTheme}
            className="relative p-2 rounded-lg hover:bg-white/[0.06] transition-colors text-gray-300 hover:text-white"
            title={`Switch to ${theme === 'dark' ? 'light' : 'dark'} mode`}
          >
            {theme === 'dark' ? (
              <Sun className="h-5 w-5" />
            ) : (
              <Moon className="h-5 w-5" />
            )}
          </button>

          <button className="relative p-2 rounded-lg hover:bg-white/[0.06] transition-colors text-gray-300 hover:text-white">
            <Bell className="h-5 w-5" />
            <Badge
              variant="danger"
              className="absolute -top-1 -right-1 h-5 w-5 p-0 flex items-center justify-center text-xs"
            >
              3
            </Badge>
          </button>

          <div className="flex items-center gap-3 pl-3 border-l border-[#30363d]">
            <div className="text-right">
              <div className="text-sm font-medium text-gray-200">Admin User</div>
              <div className="text-xs text-gray-400">admin@example.com</div>
            </div>
            <div className="h-10 w-10 rounded-full bg-gradient-to-br from-blue-500 to-cyan-500 flex items-center justify-center text-sm font-bold shadow-lg shadow-blue-500/30 text-white">
              AU
            </div>
          </div>
        </div>
      </div>
    </header>
  )
}
