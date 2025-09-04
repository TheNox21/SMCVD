import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { Checkbox } from '@/components/ui/checkbox'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { useToast } from '@/hooks/use-toast'
import { 
  ArrowLeft, 
  FileText, 
  Download, 
  Eye, 
  Loader2, 
  CheckCircle,
  AlertTriangle,
  Copy
} from 'lucide-react'
import { motion } from 'framer-motion'
import { API_BASE_URL } from '../config'

const ReportPage = () => {
  const { jobId } = useParams()
  const navigate = useNavigate()
  const { toast } = useToast()
  const [results, setResults] = useState(null)
  const [loading, setLoading] = useState(true)
  const [generating, setGenerating] = useState(false)
  const [report, setReport] = useState(null)
  const [config, setConfig] = useState({
    title: 'Smart Contract Security Analysis Report',
    researcher: '',
    target_program: '',
    template: 'professional',
    selected_vulnerabilities: []
  })

  useEffect(() => {
    fetchResults()
  }, [jobId])

  const fetchResults = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/results/${jobId}`)
      const data = await response.json()

      if (response.ok) {
        setResults(data)
        // Select all vulnerabilities by default
        setConfig(prev => ({
          ...prev,
          selected_vulnerabilities: data.vulnerabilities?.map(v => v.id) || []
        }))
      } else {
        toast({
          title: "Error",
          description: data.error || 'Failed to fetch results',
          variant: "destructive"
        })
      }
    } catch (err) {
      toast({
        title: "Error",
        description: 'Failed to fetch analysis results',
        variant: "destructive"
      })
    } finally {
      setLoading(false)
    }
  }

  const generateReport = async () => {
    setGenerating(true)
    
    try {
      const response = await fetch(`${API_BASE_URL}/api/report/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          job_id: jobId,
          config: config
        })
      })

      const data = await response.json()

      if (response.ok) {
        setReport(data)
        toast({
          title: "Report Generated",
          description: "Your bug bounty report has been generated successfully",
        })
      } else {
        throw new Error(data.error || 'Failed to generate report')
      }
    } catch (error) {
      toast({
        title: "Generation Failed",
        description: error.message || "Failed to generate report",
        variant: "destructive"
      })
    } finally {
      setGenerating(false)
    }
  }

  const downloadReport = async (format = 'markdown') => {
    if (!report) return

    try {
      const response = await fetch(`${API_BASE_URL}/api/report/download`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          markdown: report.markdown,
          format: format,
          filename: `security_report_${jobId}`
        })
      })

      if (response.ok) {
        const blob = await response.blob()
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.style.display = 'none'
        a.href = url
        a.download = `security_report_${jobId}.${format === 'pdf' ? 'pdf' : 'md'}`
        document.body.appendChild(a)
        a.click()
        window.URL.revokeObjectURL(url)
        
        toast({
          title: "Download Started",
          description: `Report downloaded as ${format.toUpperCase()}`,
        })
      } else {
        throw new Error('Download failed')
      }
    } catch (error) {
      toast({
        title: "Download Failed",
        description: error.message || "Failed to download report",
        variant: "destructive"
      })
    }
  }

  const copyToClipboard = async () => {
    if (!report?.markdown) return

    try {
      await navigator.clipboard.writeText(report.markdown)
      toast({
        title: "Copied",
        description: "Report content copied to clipboard",
      })
    } catch (error) {
      toast({
        title: "Copy Failed",
        description: "Failed to copy to clipboard",
        variant: "destructive"
      })
    }
  }

  const toggleVulnerability = (vulnId) => {
    setConfig(prev => ({
      ...prev,
      selected_vulnerabilities: prev.selected_vulnerabilities.includes(vulnId)
        ? prev.selected_vulnerabilities.filter(id => id !== vulnId)
        : [...prev.selected_vulnerabilities, vulnId]
    }))
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

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 flex items-center justify-center">
        <Card className="w-96">
          <CardContent className="flex items-center justify-center py-8">
            <div className="text-center">
              <Loader2 className="h-8 w-8 animate-spin mx-auto mb-4 text-blue-600" />
              <p className="text-slate-600">Loading results...</p>
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
              onClick={() => navigate(`/results/${jobId}`)}
              className="flex items-center space-x-2"
            >
              <ArrowLeft className="h-4 w-4" />
              <span>Back to Results</span>
            </Button>
            <div className="text-lg font-semibold text-slate-900">
              Bug Bounty Report Generator
            </div>
            <div className="w-32"></div>
          </div>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Configuration Panel */}
            <div className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle>Report Configuration</CardTitle>
                  <CardDescription>
                    Customize your bug bounty report settings
                  </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="title">Report Title</Label>
                    <Input
                      id="title"
                      value={config.title}
                      onChange={(e) => setConfig(prev => ({ ...prev, title: e.target.value }))}
                      placeholder="Smart Contract Security Analysis Report"
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="researcher">Researcher Name</Label>
                    <Input
                      id="researcher"
                      value={config.researcher}
                      onChange={(e) => setConfig(prev => ({ ...prev, researcher: e.target.value }))}
                      placeholder="Your Name"
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="program">Target Program</Label>
                    <Input
                      id="program"
                      value={config.target_program}
                      onChange={(e) => setConfig(prev => ({ ...prev, target_program: e.target.value }))}
                      placeholder="Bug Bounty Program Name"
                    />
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="template">Report Template</Label>
                    <Select 
                      value={config.template} 
                      onValueChange={(value) => setConfig(prev => ({ ...prev, template: value }))}
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Select template" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="professional">Professional</SelectItem>
                        <SelectItem value="detailed">Detailed Technical</SelectItem>
                        <SelectItem value="concise">Concise</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </CardContent>
              </Card>

              {/* Vulnerability Selection */}
              {results?.vulnerabilities && results.vulnerabilities.length > 0 && (
                <Card>
                  <CardHeader>
                    <CardTitle>Include Vulnerabilities</CardTitle>
                    <CardDescription>
                      Select which vulnerabilities to include in the report
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3 max-h-64 overflow-y-auto">
                      {results.vulnerabilities.map((vuln) => (
                        <div key={vuln.id} className="flex items-center space-x-3">
                          <Checkbox
                            id={vuln.id}
                            checked={config.selected_vulnerabilities.includes(vuln.id)}
                            onCheckedChange={() => toggleVulnerability(vuln.id)}
                          />
                          <div className="flex-1 min-w-0">
                            <div className="flex items-center space-x-2">
                              <label 
                                htmlFor={vuln.id}
                                className="text-sm font-medium text-slate-900 cursor-pointer"
                              >
                                {vuln.name}
                              </label>
                              <Badge className={getSeverityColor(vuln.severity)}>
                                {vuln.severity?.toUpperCase()}
                              </Badge>
                            </div>
                            <p className="text-xs text-slate-600 truncate">
                              {vuln.file_path}:{vuln.line_number}
                            </p>
                          </div>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              )}

              <Button 
                onClick={generateReport}
                disabled={generating || config.selected_vulnerabilities.length === 0}
                className="w-full bg-blue-600 hover:bg-blue-700"
              >
                {generating ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    Generating Report...
                  </>
                ) : (
                  <>
                    <FileText className="h-4 w-4 mr-2" />
                    Generate Report
                  </>
                )}
              </Button>
            </div>

            {/* Report Preview/Output */}
            <div className="space-y-6">
              {report ? (
                <Card>
                  <CardHeader>
                    <div className="flex items-center justify-between">
                      <div>
                        <CardTitle>Generated Report</CardTitle>
                        <CardDescription>
                          Report ID: {report.report_id}
                        </CardDescription>
                      </div>
                      <div className="flex space-x-2">
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={copyToClipboard}
                        >
                          <Copy className="h-4 w-4 mr-2" />
                          Copy
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => downloadReport('markdown')}
                        >
                          <Download className="h-4 w-4 mr-2" />
                          Markdown
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => downloadReport('pdf')}
                        >
                          <Download className="h-4 w-4 mr-2" />
                          PDF
                        </Button>
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <Tabs defaultValue="preview">
                      <TabsList>
                        <TabsTrigger value="preview">Preview</TabsTrigger>
                        <TabsTrigger value="markdown">Markdown</TabsTrigger>
                      </TabsList>
                      
                      <TabsContent value="preview" className="mt-4">
                        <div className="bg-white p-6 rounded-lg border max-h-96 overflow-y-auto">
                          <div className="prose prose-sm max-w-none">
                            {/* Simple markdown preview */}
                            <pre className="whitespace-pre-wrap text-sm">
                              {report.markdown.substring(0, 2000)}
                              {report.markdown.length > 2000 && '...'}
                            </pre>
                          </div>
                        </div>
                      </TabsContent>
                      
                      <TabsContent value="markdown" className="mt-4">
                        <div className="bg-slate-900 text-slate-100 p-4 rounded-lg max-h-96 overflow-y-auto">
                          <pre className="text-sm">
                            <code>{report.markdown}</code>
                          </pre>
                        </div>
                      </TabsContent>
                    </Tabs>
                  </CardContent>
                </Card>
              ) : (
                <Card>
                  <CardContent className="text-center py-12">
                    <FileText className="h-16 w-16 text-slate-400 mx-auto mb-4" />
                    <h3 className="text-lg font-semibold text-slate-900 mb-2">
                      No Report Generated
                    </h3>
                    <p className="text-slate-600 mb-4">
                      Configure your report settings and click "Generate Report" to create your bug bounty report.
                    </p>
                  </CardContent>
                </Card>
              )}

              {/* Report Summary */}
              {report?.summary && (
                <Card>
                  <CardHeader>
                    <CardTitle>Report Summary</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <div className="text-2xl font-bold text-slate-900">
                          {report.summary.total_vulnerabilities}
                        </div>
                        <div className="text-sm text-slate-600">Total Issues</div>
                      </div>
                      <div>
                        <div className="text-2xl font-bold text-red-600">
                          {report.summary.severity_breakdown.critical || 0}
                        </div>
                        <div className="text-sm text-slate-600">Critical</div>
                      </div>
                    </div>
                    
                    <div className="mt-4 flex flex-wrap gap-2">
                      {Object.entries(report.summary.severity_breakdown).map(([severity, count]) => (
                        count > 0 && (
                          <Badge key={severity} className={getSeverityColor(severity)}>
                            {severity}: {count}
                          </Badge>
                        )
                      ))}
                    </div>
                  </CardContent>
                </Card>
              )}
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  )
}

export default ReportPage

