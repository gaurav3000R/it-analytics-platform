'use client'

import React from 'react'
import { useQuery } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import { DashboardLayout } from '@/components/layout/dashboard-layout'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import {
  Brain,
  Sparkles,
  TrendingUp,
  Lightbulb,
  AlertCircle,
  FileText,
  Zap,
  Target,
} from 'lucide-react'
import { aiInsightsApi, projectsApi } from '@/services/api'
import { QUERY_KEYS } from '@/lib/constants'
import toast from 'react-hot-toast'

export default function AIInsightsPage() {
  const [selectedProject, setSelectedProject] = React.useState<string>('')
  const [analysisData, setAnalysisData] = React.useState<{ raw_analysis: string; generated_at: string } | null>(null)
  const [recommendationsData, setRecommendationsData] = React.useState<{ recommendations: string[]; generated_at: string } | null>(null)

  const { data: projects } = useQuery({
    queryKey: QUERY_KEYS.PROJECTS,
    queryFn: projectsApi.getAll,
  })

  const { data: portfolioTrends, isLoading: trendsLoading } = useQuery({
    queryKey: QUERY_KEYS.AI_PORTFOLIO_TRENDS,
    queryFn: aiInsightsApi.getPortfolioTrends,
    enabled: true,
  })

  const { data: executiveSummary, isLoading: summaryLoading } = useQuery({
    queryKey: QUERY_KEYS.AI_EXECUTIVE_SUMMARY,
    queryFn: aiInsightsApi.getExecutiveSummary,
    enabled: true,
  })

  const handleRiskAnalysis = async () => {
    if (!selectedProject) {
      toast.error('Please select a project first')
      return
    }

    toast.promise(
      aiInsightsApi.getRiskAnalysis(selectedProject),
      {
        loading: 'Generating AI risk analysis...',
        success: (data) => {
          setAnalysisData(data)
          return 'Analysis complete!'
        },
        error: 'AI features require GOOGLE_API_KEY to be configured',
      }
    )
  }

  const handleRecommendations = async () => {
    if (!selectedProject) {
      toast.error('Please select a project first')
      return
    }

    toast.promise(
      aiInsightsApi.getRecommendations(selectedProject),
      {
        loading: 'Generating AI recommendations...',
        success: (data) => {
          setRecommendationsData(data)
          return 'Recommendations generated!'
        },
        error: 'AI features require GOOGLE_API_KEY to be configured',
      }
    )
  }

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-4xl font-bold gradient-text mb-2">
              <Brain className="inline h-10 w-10 mr-3" />
              AI Insights
            </h1>
            <p className="text-gray-400">Powered by Google Gemini AI for advanced analytics</p>
          </div>
          <Badge variant="info" className="text-lg px-4 py-2">
            <Sparkles className="h-5 w-5 mr-2" />
            Gemini AI
          </Badge>
        </div>

        {/* Info Banner */}
        <Card className="border-purple-500/50 bg-purple-500/10">
          <CardContent className="p-6">
            <div className="flex items-start gap-4">
              <AlertCircle className="h-6 w-6 text-purple-400 flex-shrink-0 mt-1" />
              <div>
                <h3 className="font-semibold text-purple-400 mb-2">AI Features Configuration</h3>
                <p className="text-sm text-gray-300 mb-3">
                  To use AI-powered insights, ensure GOOGLE_API_KEY is configured in your backend .env file.
                  Get your API key from Google AI Studio.
                </p>
                <a
                  href="https://makersuite.google.com/app/apikey"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-sm text-purple-400 hover:text-purple-300 underline"
                >
                  Get API Key →
                </a>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Project Analysis Section */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card hover glow>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Target className="h-5 w-5 text-purple-400" />
                Project Risk Analysis
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <select
                value={selectedProject}
                onChange={(e) => setSelectedProject(e.target.value)}
                className="input-field w-full"
              >
                <option value="">Select a project...</option>
                {projects?.map((project) => (
                  <option key={project.id} value={project.id}>
                    {project.name}
                  </option>
                ))}
              </select>

              <Button onClick={handleRiskAnalysis} className="w-full" disabled={!selectedProject}>
                <Brain className="h-4 w-4 mr-2" />
                Generate AI Analysis
              </Button>

              {analysisData && (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="p-4 rounded-lg bg-white/5 border border-purple-500/30"
                >
                  <h4 className="font-semibold text-purple-400 mb-2">AI Analysis Result</h4>
                  <p className="text-sm text-gray-300 whitespace-pre-wrap">{analysisData.raw_analysis}</p>
                  <p className="text-xs text-gray-500 mt-2">
                    Generated: {new Date(analysisData.generated_at).toLocaleString()}
                  </p>
                </motion.div>
              )}
            </CardContent>
          </Card>

          <Card hover glow>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Lightbulb className="h-5 w-5 text-yellow-400" />
                AI Recommendations
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <select
                value={selectedProject}
                onChange={(e) => setSelectedProject(e.target.value)}
                className="input-field w-full"
              >
                <option value="">Select a project...</option>
                {projects?.map((project) => (
                  <option key={project.id} value={project.id}>
                    {project.name}
                  </option>
                ))}
              </select>

              <Button onClick={handleRecommendations} className="w-full" disabled={!selectedProject}>
                <Zap className="h-4 w-4 mr-2" />
                Generate Recommendations
              </Button>

              {recommendationsData && (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="p-4 rounded-lg bg-white/5 border border-yellow-500/30"
                >
                  <h4 className="font-semibold text-yellow-400 mb-2">AI Recommendations</h4>
                  <div className="space-y-2">
                    {recommendationsData.recommendations?.map((rec: string, index: number) => (
                      <div key={index} className="text-sm text-gray-300 flex items-start gap-2">
                        <span className="text-yellow-400 font-bold">{index + 1}.</span>
                        <span>{rec}</span>
                      </div>
                    ))}
                  </div>
                  <p className="text-xs text-gray-500 mt-2">
                    Generated: {new Date(recommendationsData.generated_at).toLocaleString()}
                  </p>
                </motion.div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Portfolio Trends */}
        <Card hover glow>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <TrendingUp className="h-5 w-5 text-green-400" />
              Portfolio Trends Analysis
            </CardTitle>
          </CardHeader>
          <CardContent>
            {trendsLoading ? (
              <div className="text-center py-12">
                <div className="w-12 h-12 border-4 border-purple-500 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
                <p className="text-gray-400">Analyzing portfolio trends...</p>
              </div>
            ) : portfolioTrends ? (
              <div className="p-4 rounded-lg bg-white/5">
                <p className="text-gray-300 whitespace-pre-wrap">{portfolioTrends.raw_analysis}</p>
                <p className="text-xs text-gray-500 mt-4">
                  Generated: {new Date(portfolioTrends.generated_at).toLocaleString()}
                </p>
              </div>
            ) : (
              <div className="text-center py-8 text-gray-400">
                Configure GOOGLE_API_KEY to enable AI portfolio analysis
              </div>
            )}
          </CardContent>
        </Card>

        {/* Executive Summary */}
        <Card hover glow>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <FileText className="h-5 w-5 text-blue-400" />
              Executive Summary
            </CardTitle>
          </CardHeader>
          <CardContent>
            {summaryLoading ? (
              <div className="text-center py-12">
                <div className="w-12 h-12 border-4 border-purple-500 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
                <p className="text-gray-400">Generating executive summary...</p>
              </div>
            ) : executiveSummary ? (
              <div className="p-4 rounded-lg bg-white/5">
                <p className="text-gray-300 whitespace-pre-wrap">{executiveSummary.raw_summary}</p>
                <p className="text-xs text-gray-500 mt-4">
                  Generated: {new Date(executiveSummary.generated_at).toLocaleString()}
                </p>
              </div>
            ) : (
              <div className="text-center py-8 text-gray-400">
                Configure GOOGLE_API_KEY to enable AI executive summaries
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  )
}
