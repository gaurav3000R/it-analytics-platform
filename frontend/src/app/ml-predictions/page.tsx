'use client'

import React from 'react'
import { useQuery, useMutation } from '@tanstack/react-query'
import { DashboardLayout } from '@/components/layout/dashboard-layout'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog'
import {
  Brain,
  Activity,
  TrendingUp,
  CheckCircle,
  AlertCircle,
  Target,
  BarChart3,
  Zap,
  RefreshCw,
  Sparkles,
} from 'lucide-react'
import { motion } from 'framer-motion'
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  Legend,
} from 'recharts'
import { mlApi, projectsApi } from '@/services/api'
import { QUERY_KEYS } from '@/lib/constants'
import toast from 'react-hot-toast'

export default function MLPredictionsPage() {
  const [selectedProjectId, setSelectedProjectId] = React.useState<string>('')
  const [predictionResult, setPredictionResult] = React.useState<any>(null)
  const [showPredictionModal, setShowPredictionModal] = React.useState(false)

  const { data: mlHealth, refetch: refetchHealth } = useQuery({
    queryKey: QUERY_KEYS.ML_HEALTH,
    queryFn: mlApi.getHealth,
  })

  const { data: modelInfo } = useQuery({
    queryKey: QUERY_KEYS.ML_MODEL_INFO,
    queryFn: mlApi.getModelInfo,
  })

  const { data: projects } = useQuery({
    queryKey: QUERY_KEYS.PROJECTS,
    queryFn: projectsApi.getAll,
  })

  const predictMutation = useMutation({
    mutationFn: (projectData: any) => mlApi.predict(projectData),
    onSuccess: (data) => {
      setPredictionResult(data)
      setShowPredictionModal(true)
      toast.success('Prediction completed!')
    },
    onError: () => {
      toast.error('Prediction failed')
    },
  })

  const analyzeMutation = useMutation({
    mutationFn: (projectData: any) => mlApi.analyze(projectData),
    onSuccess: (data) => {
      setPredictionResult(data)
      setShowPredictionModal(true)
      toast.success('Analysis completed!')
    },
    onError: () => {
      toast.error('Analysis failed')
    },
  })

  const handlePredict = () => {
    if (!selectedProjectId) {
      toast.error('Please select a project')
      return
    }
    const project = projects?.find((p) => p.id.toString() === selectedProjectId)
    if (project) {
      predictMutation.mutate({
        project_id: project.id,
        team_size: project.team_size,
        budget: project.budget_usd,
        complexity_score: project.complexity_score,
      })
    }
  }

  const handleAnalyze = () => {
    if (!selectedProjectId) {
      toast.error('Please select a project')
      return
    }
    const project = projects?.find((p) => p.id.toString() === selectedProjectId)
    if (project) {
      analyzeMutation.mutate({
        project_id: project.id,
        features: {
          team_size: project.team_size,
          budget: project.budget_usd,
          complexity_score: project.complexity_score,
        },
      })
    }
  }

  const modelMetrics = modelInfo?.metrics || {}
  const metricsData = [
    { metric: 'Accuracy', value: (modelMetrics.accuracy || 0) * 100 },
    { metric: 'Precision', value: (modelMetrics.precision || 0) * 100 },
    { metric: 'Recall', value: (modelMetrics.recall || 0) * 100 },
    { metric: 'F1 Score', value: (modelMetrics.f1_score || 0) * 100 },
  ]

  const performanceData = [
    { name: 'Training', score: modelMetrics.train_score || 0 },
    { name: 'Validation', score: modelMetrics.val_score || 0 },
    { name: 'Test', score: modelMetrics.test_score || 0 },
  ]

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-4xl font-bold gradient-text mb-2">
              <Brain className="inline h-10 w-10 mr-3" />
              ML Predictions
            </h1>
            <p className="text-gray-400">Machine Learning model predictions and analysis</p>
          </div>
          <Button onClick={() => refetchHealth()}>
            <RefreshCw className="h-4 w-4 mr-2" />
            Refresh Status
          </Button>
        </div>

        {/* ML Health Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          {[
            {
              title: 'Model Status',
              value: mlHealth?.status || 'Unknown',
              icon: mlHealth?.status === 'healthy' ? CheckCircle : AlertCircle,
              color:
                mlHealth?.status === 'healthy'
                  ? 'from-green-500 to-emerald-500'
                  : 'from-red-500 to-orange-500',
              description: mlHealth?.version || 'N/A',
            },
            {
              title: 'Model Type',
              value: modelInfo?.model_type || 'N/A',
              icon: Brain,
              color: 'from-blue-500 to-cyan-500',
              description: modelInfo?.algorithm || 'Machine Learning',
            },
            {
              title: 'Predictions Made',
              value: modelInfo?.predictions_count || '0',
              icon: Target,
              color: 'from-purple-500 to-pink-500',
              description: 'Total predictions',
            },
            {
              title: 'Model Accuracy',
              value: `${((modelMetrics.accuracy || 0) * 100).toFixed(1)}%`,
              icon: TrendingUp,
              color: 'from-yellow-500 to-amber-500',
              description: 'Overall accuracy',
            },
          ].map((stat, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.1 }}
            >
              <Card hover glow>
                <CardContent className="p-6">
                  <div className={`p-3 rounded-xl bg-gradient-to-br ${stat.color} bg-opacity-20 mb-4 inline-block`}>
                    <stat.icon className="h-6 w-6" />
                  </div>
                  <h3 className="text-gray-400 text-sm mb-1">{stat.title}</h3>
                  <p className="text-3xl font-bold mb-1">{stat.value}</p>
                  <p className="text-xs text-gray-500">{stat.description}</p>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </div>

        {/* Charts Row */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Model Performance Metrics */}
          <Card hover>
            <CardHeader>
              <CardTitle>Model Performance Metrics</CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <RadarChart data={metricsData}>
                  <PolarGrid stroke="#30363d" />
                  <PolarAngleAxis dataKey="metric" stroke="#8b949e" />
                  <PolarRadiusAxis stroke="#8b949e" domain={[0, 100]} />
                  <Radar
                    name="Performance"
                    dataKey="value"
                    stroke="#3b82f6"
                    fill="#3b82f6"
                    fillOpacity={0.6}
                  />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: 'rgba(30, 41, 59, 0.95)',
                      border: '1px solid rgba(59, 130, 246, 0.3)',
                      borderRadius: '8px',
                    }}
                  />
                </RadarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          {/* Training Performance */}
          <Card hover>
            <CardHeader>
              <CardTitle>Training Performance</CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={performanceData}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#30363d" />
                  <XAxis dataKey="name" stroke="#8b949e" />
                  <YAxis stroke="#8b949e" domain={[0, 1]} />
                  <Tooltip
                    contentStyle={{
                      backgroundColor: 'rgba(30, 41, 59, 0.95)',
                      border: '1px solid rgba(59, 130, 246, 0.3)',
                      borderRadius: '8px',
                    }}
                  />
                  <Bar dataKey="score" fill="#06b6d4" radius={[8, 8, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </div>

        {/* Prediction Interface */}
        <Card hover className="border-2 border-blue-500/20 bg-blue-500/5">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Sparkles className="h-5 w-5 text-blue-400" />
              Make Predictions
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label className="text-sm text-gray-400 mb-2 block">Select Project</label>
                  <select
                    className="w-full bg-white/5 border border-white/10 rounded px-3 py-2 text-sm"
                    value={selectedProjectId}
                    onChange={(e) => setSelectedProjectId(e.target.value)}
                  >
                    <option value="">Choose a project...</option>
                    {projects?.slice(0, 50).map((project) => (
                      <option key={project.id} value={project.id}>
                        {project.project_id} - {project.project_type}
                      </option>
                    ))}
                  </select>
                </div>

                <div className="flex items-end">
                  <Button
                    onClick={handlePredict}
                    disabled={!selectedProjectId || predictMutation.isPending}
                    className="w-full"
                  >
                    {predictMutation.isPending ? (
                      <>
                        <Activity className="h-4 w-4 mr-2 animate-spin" />
                        Predicting...
                      </>
                    ) : (
                      <>
                        <Target className="h-4 w-4 mr-2" />
                        Predict Success
                      </>
                    )}
                  </Button>
                </div>

                <div className="flex items-end">
                  <Button
                    onClick={handleAnalyze}
                    disabled={!selectedProjectId || analyzeMutation.isPending}
                    variant="secondary"
                    className="w-full"
                  >
                    {analyzeMutation.isPending ? (
                      <>
                        <Activity className="h-4 w-4 mr-2 animate-spin" />
                        Analyzing...
                      </>
                    ) : (
                      <>
                        <BarChart3 className="h-4 w-4 mr-2" />
                        Deep Analysis
                      </>
                    )}
                  </Button>
                </div>
              </div>

              {selectedProjectId && (
                <motion.div
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: 'auto' }}
                  className="p-4 rounded-lg bg-white/5 border border-white/10"
                >
                  <h4 className="font-semibold mb-2">Selected Project Details</h4>
                  {projects?.find((p) => p.id.toString() === selectedProjectId) && (
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-sm">
                      <div>
                        <p className="text-gray-400">Team Size</p>
                        <p className="font-medium">
                          {projects.find((p) => p.id.toString() === selectedProjectId)?.team_size}
                        </p>
                      </div>
                      <div>
                        <p className="text-gray-400">Budget</p>
                        <p className="font-medium">
                          $
                          {(
                            (projects.find((p) => p.id.toString() === selectedProjectId)?.budget_usd || 0) / 1000
                          ).toFixed(0)}
                          k
                        </p>
                      </div>
                      <div>
                        <p className="text-gray-400">Complexity</p>
                        <p className="font-medium">
                          {projects.find((p) => p.id.toString() === selectedProjectId)?.complexity_score?.toFixed(1)}
                        </p>
                      </div>
                      <div>
                        <p className="text-gray-400">Risk Level</p>
                        <Badge
                          className={
                            projects.find((p) => p.id.toString() === selectedProjectId)?.risk_level === 'Critical'
                              ? 'bg-red-500/20 text-red-400'
                              : 'bg-yellow-500/20 text-yellow-400'
                          }
                        >
                          {projects.find((p) => p.id.toString() === selectedProjectId)?.risk_level}
                        </Badge>
                      </div>
                    </div>
                  )}
                </motion.div>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Model Information Card */}
        {modelInfo && (
          <Card hover>
            <CardHeader>
              <CardTitle>Model Information</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
                <div>
                  <p className="text-gray-400 text-sm mb-1">Features Count</p>
                  <p className="text-2xl font-bold">{modelInfo.features_count || 'N/A'}</p>
                </div>
                <div>
                  <p className="text-gray-400 text-sm mb-1">Training Samples</p>
                  <p className="text-2xl font-bold">{modelInfo.training_samples || 'N/A'}</p>
                </div>
                <div>
                  <p className="text-gray-400 text-sm mb-1">Last Trained</p>
                  <p className="text-sm font-medium">
                    {modelInfo.last_trained
                      ? new Date(modelInfo.last_trained).toLocaleDateString()
                      : 'Unknown'}
                  </p>
                </div>
                <div>
                  <p className="text-gray-400 text-sm mb-1">Model Version</p>
                  <p className="text-sm font-medium">{modelInfo.version || 'v1.0.0'}</p>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Prediction Result Modal */}
        <Dialog open={showPredictionModal} onOpenChange={setShowPredictionModal}>
          <DialogContent className="max-w-2xl">
            <DialogHeader>
              <DialogTitle className="flex items-center gap-2">
                <Sparkles className="h-5 w-5 text-blue-400" />
                Prediction Results
              </DialogTitle>
            </DialogHeader>
            <div className="space-y-4">
              {predictionResult && (
                <>
                  <div className="p-4 rounded-lg bg-gradient-to-r from-blue-500/10 to-cyan-500/10 border border-blue-500/20">
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="font-semibold text-lg">Success Probability</h3>
                      <span className="text-3xl font-bold text-blue-400">
                        {((predictionResult.prediction || predictionResult.success_probability || 0) * 100).toFixed(
                          1
                        )}
                        %
                      </span>
                    </div>
                    <div className="w-full bg-gray-700 rounded-full h-3">
                      <div
                        className="bg-gradient-to-r from-blue-500 to-cyan-500 h-3 rounded-full transition-all duration-500"
                        style={{
                          width: `${((predictionResult.prediction || predictionResult.success_probability || 0) * 100).toFixed(1)}%`,
                        }}
                      />
                    </div>
                  </div>

                  {predictionResult.confidence && (
                    <div className="grid grid-cols-2 gap-4">
                      <div className="p-4 rounded-lg bg-white/5">
                        <p className="text-gray-400 text-sm mb-1">Confidence</p>
                        <p className="text-2xl font-bold">
                          {(predictionResult.confidence * 100).toFixed(1)}%
                        </p>
                      </div>
                      <div className="p-4 rounded-lg bg-white/5">
                        <p className="text-gray-400 text-sm mb-1">Risk Level</p>
                        <Badge
                          className={
                            predictionResult.risk_level === 'high'
                              ? 'bg-red-500/20 text-red-400'
                              : 'bg-green-500/20 text-green-400'
                          }
                        >
                          {predictionResult.risk_level || 'medium'}
                        </Badge>
                      </div>
                    </div>
                  )}

                  {predictionResult.recommendations && (
                    <div>
                      <h4 className="font-semibold mb-2">Recommendations</h4>
                      <div className="space-y-2">
                        {predictionResult.recommendations.map((rec: string, i: number) => (
                          <div key={i} className="p-3 rounded-lg bg-blue-500/10 border border-blue-500/20 text-sm">
                            💡 {rec}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {predictionResult.features_importance && (
                    <div>
                      <h4 className="font-semibold mb-2">Feature Importance</h4>
                      <div className="space-y-2">
                        {Object.entries(predictionResult.features_importance).map(([feature, importance]: any, i) => (
                          <div key={i} className="flex items-center justify-between">
                            <span className="text-sm text-gray-400">{feature}</span>
                            <div className="flex items-center gap-2">
                              <div className="w-32 bg-gray-700 rounded-full h-2">
                                <div
                                  className="bg-gradient-to-r from-blue-500 to-cyan-500 h-2 rounded-full"
                                  style={{ width: `${importance * 100}%` }}
                                />
                              </div>
                              <span className="text-sm font-medium w-12 text-right">
                                {(importance * 100).toFixed(0)}%
                              </span>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </>
              )}
            </div>
          </DialogContent>
        </Dialog>
      </div>
    </DashboardLayout>
  )
}
