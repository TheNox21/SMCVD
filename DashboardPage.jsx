import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Progress } from '@/components/ui/progress'
import { Badge } from '@/components/ui/badge'
import { ArrowLeft, Loader2, CheckCircle, AlertTriangle, FileCode } from 'lucide-react'
import { motion } from 'framer-motion'
import { API_BASE_URL } from '../config'

const DashboardPage = () => {
  const { jobId } = useParams()
  const navigate = useNavigate()
  const [status, setStatus] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    if (jobId) {
      monitorProgress()
    }
  }, [jobId])

  const monitorProgress = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/status/${jobId}`)
      const data = await response.json()

      if (response.ok) {
        setStatus(data)
        setLoading(false)

        if (data.status === 'completed') {
          // Redirect to results after a short delay
          setTimeout(() => {
            navigate(`/results/${jobId}`)
          }, 2000)
        } else if (data.status === 'error') {
          setError(data.message || 'Analysis failed')
        } else if (data.status !== 'completed' && data.status !== 'error') {
          // Continue monitoring
          setTimeout(monitorProgress, 2000)
        }
      } else {
        setError(data.error || 'Failed to fetch status')
        setLoading(false)
      }
    } catch (err) {
      setError('Failed to monitor analysis progress')
      setLoading(false)
    }
  }

  const getStatusIcon = (currentStatus) => {
    switch (currentStatus) {
      case 'completed':
        return <CheckCircle className="h-5 w-5 text-green-600" />
      case 'error':
        return <AlertTriangle className="h-5 w-5 text-red-600" />
      default:
        return <Loader2 className="h-5 w-5 animate-spin text-blue-600" />
    }
  }

  const getStatusColor = (currentStatus) => {
    switch (currentStatus) {
      case 'completed':
        return 'bg-green-100 text-green-800 border-green-200'
      case 'error':
        return 'bg-red-100 text-red-800 border-red-200'
      default:
        return 'bg-blue-100 text-blue-800 border-blue-200'
    }
  }

  const getProgressSteps = () => {
    const steps = [
      { id: 'initializing', label: 'Initializing', description: 'Setting up analysis environment' },
      { id: 'fetching', label: 'Fetching', description: 'Downloading repository files' },
      { id: 'scanning', label: 'Scanning', description: 'Finding smart contract files' },
      { id: 'processing', label: 'Processing', description: 'Analyzing contract code' },
      { id: 'ai_analysis', label: 'AI Analysis', description: 'Running AI-powered vulnerability detection' },
      { id: 'completed', label: 'Completed', description: 'Analysis finished successfully' }
    ]

    const currentStep = status?.status || 'initializing'
    const currentIndex = steps.findIndex(step => step.id === currentStep)

    return steps.map((step, index) => ({
      ...step,
      completed: index < currentIndex || currentStep === 'completed',
      active: index === currentIndex,
      upcoming: index > currentIndex
    }))
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 flex items-center justify-center">
        <Card className="w-96">
          <CardContent className="flex items-center justify-center py-8">
            <div className="text-center">
              <Loader2 className="h-8 w-8 animate-spin mx-auto mb-4 text-blue-600" />
              <p className="text-slate-600">Connecting to analysis...</p>
            </div>
          </CardContent>
        </Card>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 flex items-center justify-center">
        <Card className="w-96">
          <CardContent className="py-8">
            <div className="text-center">
              <AlertTriangle className="h-8 w-8 text-red-600 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-slate-900 mb-2">Analysis Failed</h3>
              <p className="text-slate-600 mb-4">{error}</p>
              <Button onClick={() => navigate('/analyze')}>
                Start New Analysis
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    )
  }

  const progressSteps = getProgressSteps()

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      {/* Navigation */}
      <nav className="bg-white/80 backdrop-blur-md border-b border-slate-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <Button 
              variant="ghost" 
              onClick={() => navigate('/analyze')}
              className="flex items-center space-x-2"
            >
              <ArrowLeft className="h-4 w-4" />
              <span>Back to Analysis</span>
            </Button>
            <div className="text-lg font-semibold text-slate-900">
              Analysis Dashboard
            </div>
            <div className="w-32"></div> {/* Spacer for centering */}
          </div>
        </div>
      </nav>

      <div className="max-w-4xl mx-auto py-12 px-4 sm:px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          {/* Status Header */}
          <Card className="mb-8">
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle className="flex items-center space-x-2">
                    {getStatusIcon(status?.status)}
                    <span>Analysis in Progress</span>
                  </CardTitle>
                  <CardDescription>
                    Job ID: {jobId}
                  </CardDescription>
                </div>
                <Badge className={getStatusColor(status?.status)}>
                  {status?.status?.toUpperCase() || 'RUNNING'}
                </Badge>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div>
                  <div className="flex justify-between text-sm text-slate-600 mb-2">
                    <span>Overall Progress</span>
                    <span>{status?.progress || 0}%</span>
                  </div>
                  <Progress value={status?.progress || 0} className="w-full" />
                </div>
                
                {status?.message && (
                  <div className="text-sm text-slate-700 bg-slate-50 p-3 rounded">
                    {status.message}
                  </div>
                )}
              </div>
            </CardContent>
          </Card>

          {/* Progress Steps */}
          <Card className="mb-8">
            <CardHeader>
              <CardTitle>Analysis Steps</CardTitle>
              <CardDescription>
                Track the progress of your smart contract analysis
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {progressSteps.map((step, index) => (
                  <motion.div
                    key={step.id}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ duration: 0.3, delay: index * 0.1 }}
                    className={`flex items-center space-x-4 p-3 rounded-lg ${
                      step.active ? 'bg-blue-50 border border-blue-200' :
                      step.completed ? 'bg-green-50 border border-green-200' :
                      'bg-slate-50 border border-slate-200'
                    }`}
                  >
                    <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
                      step.completed ? 'bg-green-600' :
                      step.active ? 'bg-blue-600' :
                      'bg-slate-300'
                    }`}>
                      {step.completed ? (
                        <CheckCircle className="h-4 w-4 text-white" />
                      ) : step.active ? (
                        <Loader2 className="h-4 w-4 text-white animate-spin" />
                      ) : (
                        <span className="text-xs font-medium text-white">{index + 1}</span>
                      )}
                    </div>
                    <div className="flex-1">
                      <h3 className={`font-medium ${
                        step.active ? 'text-blue-900' :
                        step.completed ? 'text-green-900' :
                        'text-slate-600'
                      }`}>
                        {step.label}
                      </h3>
                      <p className={`text-sm ${
                        step.active ? 'text-blue-700' :
                        step.completed ? 'text-green-700' :
                        'text-slate-500'
                      }`}>
                        {step.description}
                      </p>
                    </div>
                  </motion.div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Statistics */}
          {status && (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-slate-600">Files Found</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center space-x-2">
                    <FileCode className="h-5 w-5 text-blue-600" />
                    <span className="text-2xl font-bold text-slate-900">
                      {status.total_files || 0}
                    </span>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-slate-600">Files Analyzed</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center space-x-2">
                    <CheckCircle className="h-5 w-5 text-green-600" />
                    <span className="text-2xl font-bold text-slate-900">
                      {status.files_analyzed || 0}
                    </span>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="pb-2">
                  <CardTitle className="text-sm font-medium text-slate-600">Issues Found</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center space-x-2">
                    <AlertTriangle className="h-5 w-5 text-orange-600" />
                    <span className="text-2xl font-bold text-slate-900">
                      {status.vulnerabilities?.length || 0}
                    </span>
                  </div>
                </CardContent>
              </Card>
            </div>
          )}

          {/* Completion Message */}
          {status?.status === 'completed' && (
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.5 }}
              className="mt-8"
            >
              <Card className="bg-green-50 border-green-200">
                <CardContent className="text-center py-8">
                  <CheckCircle className="h-16 w-16 text-green-600 mx-auto mb-4" />
                  <h3 className="text-lg font-semibold text-green-900 mb-2">
                    Analysis Complete!
                  </h3>
                  <p className="text-green-700 mb-4">
                    Your smart contract analysis has finished successfully. 
                    Redirecting to results...
                  </p>
                  <Button 
                    onClick={() => navigate(`/results/${jobId}`)}
                    className="bg-green-600 hover:bg-green-700"
                  >
                    View Results Now
                  </Button>
                </CardContent>
              </Card>
            </motion.div>
          )}
        </motion.div>
      </div>
    </div>
  )
}

export default DashboardPage

