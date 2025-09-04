import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '@/components/ui/collapsible'
import { 
  ArrowLeft, 
  FileText, 
  AlertTriangle, 
  Shield, 
  Code, 
  ChevronDown, 
  ChevronRight,
  Download,
  Eye,
  Loader2
} from 'lucide-react'
import { motion } from 'framer-motion'
import { API_BASE_URL } from '../config'

const ResultsPage = () => {
  const { jobId } = useParams()
  const navigate = useNavigate()
  const [results, setResults] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [expandedVulns, setExpandedVulns] = useState(new Set())

  useEffect(() => {
    fetchResults()
  }, [jobId])

  const fetchResults = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/results/${jobId}`)
      const data = await response.json()

      if (response.ok) {
        setResults(data)
      } else {
        setError(data.error || 'Failed to fetch results')
      }
    } catch (err) {
      setError('Failed to fetch analysis results')
    } finally {
      setLoading(false)
    }
  }

  const toggleVulnExpansion = (vulnId) => {
    const newExpanded = new Set(expandedVulns)
    if (newExpanded.has(vulnId)) {
      newExpanded.delete(vulnId)
    } else {
      newExpanded.add(vulnId)
    }
    setExpandedVulns(newExpanded)
  }

  const getSeverityColor = (severity) => {
    const colors = {
      critical: 'bg-red-100 text-red-800 border-red-200',
      high: 'bg-orange-100 text-orange-800 border-orange-200',
      medium: 'bg-yellow-100 text-yellow-800 border-yellow-200',
      low: 'bg-blue-100 text-blue-800 border-blue-200',
      info: 'bg-gray-100 text-gray-800 border-gray-200'
    }
    return colors[severity?.toLowerCase()] || colors.info
  }

  const getSeverityIcon = (severity) => {
    if (severity === 'critical' || severity === 'high') {
      return <AlertTriangle className="h-4 w-4" />
    }
    return <Shield className="h-4 w-4" />
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 flex items-center justify-center">
        <Card className="w-96">
          <CardContent className="flex items-center justify-center py-8">
            <div className="text-center">
              <Loader2 className="h-8 w-8 animate-spin mx-auto mb-4 text-blue-600" />
              <p className="text-slate-600">Loading analysis results...</p>
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
              <h3 className="text-lg font-semibold text-slate-900 mb-2">Error Loading Results</h3>
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
              <span>New Analysis</span>
            </Button>
            <div className="text-lg font-semibold text-slate-900">
              Analysis Results
            </div>
            <Button 
              onClick={() => navigate(`/report/${jobId}`)}
              className="bg-blue-600 hover:bg-blue-700"
            >
              <FileText className="h-4 w-4 mr-2" />
              Generate Report
            </Button>
          </div>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          {/* Summary Cards */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-slate-600">Total Files</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-slate-900">
                  {results?.summary?.total_files || 0}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-slate-600">Vulnerabilities</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-slate-900">
                  {results?.summary?.vulnerabilities_found || 0}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-slate-600">Critical Issues</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-red-600">
                  {results?.summary?.severity_breakdown?.critical || 0}
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium text-slate-600">High Issues</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-orange-600">
                  {results?.summary?.severity_breakdown?.high || 0}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Severity Breakdown */}
          {results?.summary?.severity_breakdown && (
            <Card className="mb-8">
              <CardHeader>
                <CardTitle>Severity Breakdown</CardTitle>
                <CardDescription>
                  Distribution of vulnerabilities by severity level
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="flex flex-wrap gap-2">
                  {Object.entries(results.summary.severity_breakdown).map(([severity, count]) => (
                    count > 0 && (
                      <Badge 
                        key={severity} 
                        className={`${getSeverityColor(severity)} px-3 py-1`}
                      >
                        {severity.charAt(0).toUpperCase() + severity.slice(1)}: {count}
                      </Badge>
                    )
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Vulnerabilities List */}
          {results?.vulnerabilities && results.vulnerabilities.length > 0 ? (
            <Card>
              <CardHeader>
                <CardTitle>Vulnerability Details</CardTitle>
                <CardDescription>
                  Detailed analysis of identified security issues
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {results.vulnerabilities.map((vuln, index) => (
                    <Collapsible
                      key={vuln.id || index}
                      open={expandedVulns.has(vuln.id || index)}
                      onOpenChange={() => toggleVulnExpansion(vuln.id || index)}
                    >
                      <CollapsibleTrigger asChild>
                        <div className="flex items-center justify-between p-4 border rounded-lg hover:bg-slate-50 cursor-pointer">
                          <div className="flex items-center space-x-4">
                            {getSeverityIcon(vuln.severity)}
                            <div>
                              <h3 className="font-semibold text-slate-900">{vuln.name}</h3>
                              <p className="text-sm text-slate-600">
                                {vuln.file_path}:{vuln.line_number} • {vuln.function_name}
                              </p>
                            </div>
                          </div>
                          <div className="flex items-center space-x-2">
                            <Badge className={getSeverityColor(vuln.severity)}>
                              {vuln.severity?.toUpperCase()}
                            </Badge>
                            {expandedVulns.has(vuln.id || index) ? (
                              <ChevronDown className="h-4 w-4" />
                            ) : (
                              <ChevronRight className="h-4 w-4" />
                            )}
                          </div>
                        </div>
                      </CollapsibleTrigger>

                      <CollapsibleContent>
                        <div className="px-4 pb-4 space-y-4">
                          <div className="bg-slate-50 p-4 rounded-lg">
                            <h4 className="font-medium text-slate-900 mb-2">Description</h4>
                            <p className="text-slate-700">{vuln.description}</p>
                          </div>

                          <div className="bg-slate-50 p-4 rounded-lg">
                            <h4 className="font-medium text-slate-900 mb-2">Impact</h4>
                            <p className="text-slate-700">{vuln.impact}</p>
                          </div>

                          <div className="bg-slate-50 p-4 rounded-lg">
                            <h4 className="font-medium text-slate-900 mb-2">Vulnerable Code</h4>
                            <pre className="bg-slate-900 text-slate-100 p-3 rounded text-sm overflow-x-auto">
                              <code>{vuln.line_content}</code>
                            </pre>
                          </div>

                          {vuln.mitigation && (
                            <div className="bg-green-50 p-4 rounded-lg border border-green-200">
                              <h4 className="font-medium text-green-900 mb-2">Recommended Fix</h4>
                              <p className="text-green-800">{vuln.mitigation}</p>
                            </div>
                          )}

                          <div className="flex items-center justify-between text-sm text-slate-500">
                            <span>CWE: {vuln.cwe}</span>
                            <span>Confidence: {Math.round((vuln.confidence || 0) * 100)}%</span>
                          </div>
                        </div>
                      </CollapsibleContent>
                    </Collapsible>
                  ))}
                </div>
              </CardContent>
            </Card>
          ) : (
            <Card>
              <CardContent className="text-center py-12">
                <Shield className="h-16 w-16 text-green-600 mx-auto mb-4" />
                <h3 className="text-lg font-semibold text-slate-900 mb-2">
                  No Vulnerabilities Found
                </h3>
                <p className="text-slate-600 mb-4">
                  Great! No security issues were detected in the analyzed smart contracts.
                </p>
                <Button onClick={() => navigate('/analyze')}>
                  Analyze Another Contract
                </Button>
              </CardContent>
            </Card>
          )}

          {/* Action Buttons */}
          <div className="flex justify-center space-x-4 mt-8">
            <Button 
              variant="outline"
              onClick={() => navigate('/analyze')}
            >
              New Analysis
            </Button>
            {results?.vulnerabilities && results.vulnerabilities.length > 0 && (
              <Button 
                onClick={() => navigate(`/report/${jobId}`)}
                className="bg-blue-600 hover:bg-blue-700"
              >
                <FileText className="h-4 w-4 mr-2" />
                Generate Bug Bounty Report
              </Button>
            )}
          </div>
        </motion.div>
      </div>
    </div>
  )
}

export default ResultsPage

