'use client'

import React from 'react'
import { PaperCard, PaperCardHeader, PaperCardTitle, PaperCardDescription, PaperCardContent } from './paper-card'
import { FrostedCard, FrostedCardHeader, FrostedCardTitle, FrostedCardDescription, FrostedCardContent } from './frosted-card'
import { TexturedCard, TexturedCardHeader, TexturedCardTitle, TexturedCardDescription, TexturedCardContent } from './textured-card'
import { TrendingUp, Users, DollarSign, AlertTriangle, Activity, Zap } from 'lucide-react'

export function CardShowcase() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-blue-50/30 to-purple-50/30 p-8">
      <div className="max-w-7xl mx-auto space-y-12">
        
        {/* Header */}
        <div className="text-center space-y-2">
          <h1 className="text-4xl font-bold text-gray-900">Beautiful Card Effects</h1>
          <p className="text-lg text-gray-600">Blurry rough paper-like backgrounds with multiple variants</p>
        </div>

        {/* Paper Cards */}
        <section className="space-y-4">
          <h2 className="text-2xl font-semibold text-gray-900">Paper Cards - Soft Blur Effect</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            
            <PaperCard variant="default">
              <PaperCardHeader>
                <div className="flex items-center gap-3">
                  <div className="p-3 bg-blue-100 rounded-lg">
                    <TrendingUp className="w-6 h-6 text-blue-600" />
                  </div>
                  <div>
                    <PaperCardTitle className="text-xl">Default Paper</PaperCardTitle>
                    <PaperCardDescription>Blue to purple gradient</PaperCardDescription>
                  </div>
                </div>
              </PaperCardHeader>
              <PaperCardContent>
                <div className="space-y-3">
                  <div className="text-3xl font-bold text-gray-900">$125.5M</div>
                  <div className="text-sm text-gray-600">Total Portfolio Value</div>
                  <div className="flex items-center gap-2 text-green-600 text-sm">
                    <TrendingUp className="w-4 h-4" />
                    <span>+12.5% from last month</span>
                  </div>
                </div>
              </PaperCardContent>
            </PaperCard>

            <PaperCard variant="subtle">
              <PaperCardHeader>
                <div className="flex items-center gap-3">
                  <div className="p-3 bg-gray-100 rounded-lg">
                    <Users className="w-6 h-6 text-gray-600" />
                  </div>
                  <div>
                    <PaperCardTitle className="text-xl">Subtle Paper</PaperCardTitle>
                    <PaperCardDescription>Gray gradient</PaperCardDescription>
                  </div>
                </div>
              </PaperCardHeader>
              <PaperCardContent>
                <div className="space-y-3">
                  <div className="text-3xl font-bold text-gray-900">350</div>
                  <div className="text-sm text-gray-600">Team Members</div>
                  <div className="flex items-center gap-2 text-blue-600 text-sm">
                    <Activity className="w-4 h-4" />
                    <span>320 active this week</span>
                  </div>
                </div>
              </PaperCardContent>
            </PaperCard>

            <PaperCard variant="vibrant">
              <PaperCardHeader>
                <div className="flex items-center gap-3">
                  <div className="p-3 bg-purple-100 rounded-lg">
                    <Zap className="w-6 h-6 text-purple-600" />
                  </div>
                  <div>
                    <PaperCardTitle className="text-xl">Vibrant Paper</PaperCardTitle>
                    <PaperCardDescription>Cyan to purple</PaperCardDescription>
                  </div>
                </div>
              </PaperCardHeader>
              <PaperCardContent>
                <div className="space-y-3">
                  <div className="text-3xl font-bold text-gray-900">98.5%</div>
                  <div className="text-sm text-gray-600">System Uptime</div>
                  <div className="flex items-center gap-2 text-green-600 text-sm">
                    <Zap className="w-4 h-4" />
                    <span>Excellent performance</span>
                  </div>
                </div>
              </PaperCardContent>
            </PaperCard>

          </div>
        </section>

        {/* Frosted Cards */}
        <section className="space-y-4">
          <h2 className="text-2xl font-semibold text-gray-900">Frosted Glass Cards - Backdrop Blur</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            
            <FrostedCard intensity="light">
              <FrostedCardHeader>
                <div className="flex items-center gap-3">
                  <div className="p-3 bg-blue-100 rounded-lg">
                    <DollarSign className="w-6 h-6 text-blue-600" />
                  </div>
                  <div>
                    <FrostedCardTitle className="text-xl">Light Frost</FrostedCardTitle>
                    <FrostedCardDescription>60% opacity</FrostedCardDescription>
                  </div>
                </div>
              </FrostedCardHeader>
              <FrostedCardContent>
                <div className="space-y-3">
                  <div className="text-3xl font-bold text-gray-900">$45.2M</div>
                  <div className="text-sm text-gray-600">Budget Spent</div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div className="bg-blue-500 h-2 rounded-full" style={{ width: '68%' }} />
                  </div>
                </div>
              </FrostedCardContent>
            </FrostedCard>

            <FrostedCard intensity="medium">
              <FrostedCardHeader>
                <div className="flex items-center gap-3">
                  <div className="p-3 bg-cyan-100 rounded-lg">
                    <Activity className="w-6 h-6 text-cyan-600" />
                  </div>
                  <div>
                    <FrostedCardTitle className="text-xl">Medium Frost</FrostedCardTitle>
                    <FrostedCardDescription>70% opacity</FrostedCardDescription>
                  </div>
                </div>
              </FrostedCardHeader>
              <FrostedCardContent>
                <div className="space-y-3">
                  <div className="text-3xl font-bold text-gray-900">1,234</div>
                  <div className="text-sm text-gray-600">Active Projects</div>
                  <div className="flex gap-2">
                    <div className="px-2 py-1 bg-green-100 text-green-700 rounded text-xs">850 On Track</div>
                    <div className="px-2 py-1 bg-yellow-100 text-yellow-700 rounded text-xs">384 At Risk</div>
                  </div>
                </div>
              </FrostedCardContent>
            </FrostedCard>

            <FrostedCard intensity="strong">
              <FrostedCardHeader>
                <div className="flex items-center gap-3">
                  <div className="p-3 bg-red-100 rounded-lg">
                    <AlertTriangle className="w-6 h-6 text-red-600" />
                  </div>
                  <div>
                    <FrostedCardTitle className="text-xl">Strong Frost</FrostedCardTitle>
                    <FrostedCardDescription>80% opacity</FrostedCardDescription>
                  </div>
                </div>
              </FrostedCardHeader>
              <FrostedCardContent>
                <div className="space-y-3">
                  <div className="text-3xl font-bold text-gray-900">45</div>
                  <div className="text-sm text-gray-600">High Risk Projects</div>
                  <div className="flex items-center gap-2 text-red-600 text-sm">
                    <AlertTriangle className="w-4 h-4" />
                    <span>Requires attention</span>
                  </div>
                </div>
              </FrostedCardContent>
            </FrostedCard>

          </div>
        </section>

        {/* Textured Cards */}
        <section className="space-y-4">
          <h2 className="text-2xl font-semibold text-gray-900">Textured Cards - Various Patterns</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            
            <TexturedCard texture="paper">
              <TexturedCardHeader>
                <TexturedCardTitle className="text-lg">Paper</TexturedCardTitle>
                <TexturedCardDescription>Fractal noise texture</TexturedCardDescription>
              </TexturedCardHeader>
              <TexturedCardContent>
                <div className="space-y-2">
                  <div className="text-2xl font-bold text-gray-900">8.5/10</div>
                  <div className="text-sm text-gray-600">Quality Score</div>
                </div>
              </TexturedCardContent>
            </TexturedCard>

            <TexturedCard texture="canvas">
              <TexturedCardHeader>
                <TexturedCardTitle className="text-lg">Canvas</TexturedCardTitle>
                <TexturedCardDescription>Dotted pattern</TexturedCardDescription>
              </TexturedCardHeader>
              <TexturedCardContent>
                <div className="space-y-2">
                  <div className="text-2xl font-bold text-gray-900">234</div>
                  <div className="text-sm text-gray-600">Open Tasks</div>
                </div>
              </TexturedCardContent>
            </TexturedCard>

            <TexturedCard texture="linen">
              <TexturedCardHeader>
                <TexturedCardTitle className="text-lg">Linen</TexturedCardTitle>
                <TexturedCardDescription>Cross-hatch pattern</TexturedCardDescription>
              </TexturedCardHeader>
              <TexturedCardContent>
                <div className="space-y-2">
                  <div className="text-2xl font-bold text-gray-900">78%</div>
                  <div className="text-sm text-gray-600">Completion Rate</div>
                </div>
              </TexturedCardContent>
            </TexturedCard>

            <TexturedCard texture="grain">
              <TexturedCardHeader>
                <TexturedCardTitle className="text-lg">Grain</TexturedCardTitle>
                <TexturedCardDescription>Fine grain texture</TexturedCardDescription>
              </TexturedCardHeader>
              <TexturedCardContent>
                <div className="space-y-2">
                  <div className="text-2xl font-bold text-gray-900">156</div>
                  <div className="text-sm text-gray-600">Bugs Fixed</div>
                </div>
              </TexturedCardContent>
            </TexturedCard>

          </div>
        </section>

        {/* Usage Examples */}
        <section className="space-y-4">
          <h2 className="text-2xl font-semibold text-gray-900">Real-World Usage Examples</h2>
          
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            
            {/* Dashboard Card */}
            <PaperCard variant="vibrant">
              <PaperCardHeader>
                <PaperCardTitle>Project Health Dashboard</PaperCardTitle>
                <PaperCardDescription>Overview of project metrics and KPIs</PaperCardDescription>
              </PaperCardHeader>
              <PaperCardContent>
                <div className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-1">
                      <div className="text-sm text-gray-600">On Time</div>
                      <div className="text-2xl font-bold text-green-600">82%</div>
                    </div>
                    <div className="space-y-1">
                      <div className="text-sm text-gray-600">On Budget</div>
                      <div className="text-2xl font-bold text-blue-600">78%</div>
                    </div>
                  </div>
                  <div className="pt-2 border-t border-gray-200">
                    <div className="text-sm text-gray-600 mb-2">Risk Distribution</div>
                    <div className="flex gap-2">
                      <div className="flex-1 bg-red-100 rounded-full h-2" style={{ flex: 0.12 }} />
                      <div className="flex-1 bg-yellow-100 rounded-full h-2" style={{ flex: 0.33 }} />
                      <div className="flex-1 bg-green-100 rounded-full h-2" style={{ flex: 0.55 }} />
                    </div>
                  </div>
                </div>
              </PaperCardContent>
            </PaperCard>

            {/* Analytics Card */}
            <FrostedCard intensity="medium">
              <FrostedCardHeader>
                <FrostedCardTitle>Team Performance</FrostedCardTitle>
                <FrostedCardDescription>Weekly productivity insights</FrostedCardDescription>
              </FrostedCardHeader>
              <FrostedCardContent>
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">Velocity</span>
                    <span className="text-sm font-medium text-gray-900">45 pts</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">Stories Completed</span>
                    <span className="text-sm font-medium text-gray-900">23/28</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-600">Bug Resolution</span>
                    <span className="text-sm font-medium text-gray-900">89%</span>
                  </div>
                  <div className="pt-2 border-t border-gray-200">
                    <div className="flex items-center gap-2 text-green-600 text-sm">
                      <TrendingUp className="w-4 h-4" />
                      <span>+15% improvement from last sprint</span>
                    </div>
                  </div>
                </div>
              </FrostedCardContent>
            </FrostedCard>

          </div>
        </section>

        {/* Features List */}
        <section className="space-y-4">
          <h2 className="text-2xl font-semibold text-gray-900">Features</h2>
          <TexturedCard texture="paper">
            <TexturedCardContent className="pt-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="flex items-start gap-3">
                  <div className="w-2 h-2 bg-cyan-500 rounded-full mt-2" />
                  <div>
                    <div className="font-medium text-gray-900">Blurry Backgrounds</div>
                    <div className="text-sm text-gray-600">Soft gradient blurs create depth</div>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <div className="w-2 h-2 bg-cyan-500 rounded-full mt-2" />
                  <div>
                    <div className="font-medium text-gray-900">Paper Textures</div>
                    <div className="text-sm text-gray-600">Realistic paper-like feel</div>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <div className="w-2 h-2 bg-cyan-500 rounded-full mt-2" />
                  <div>
                    <div className="font-medium text-gray-900">Frosted Glass</div>
                    <div className="text-sm text-gray-600">Backdrop blur effects</div>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <div className="w-2 h-2 bg-cyan-500 rounded-full mt-2" />
                  <div>
                    <div className="font-medium text-gray-900">Multiple Variants</div>
                    <div className="text-sm text-gray-600">Choose the perfect style</div>
                  </div>
                </div>
              </div>
            </TexturedCardContent>
          </TexturedCard>
        </section>

      </div>
    </div>
  )
}
