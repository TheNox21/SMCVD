import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Badge } from '@/components/ui/badge'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Progress } from '@/components/ui/progress'
import { useToast } from '@/hooks/use-toast'
import { Github, Upload, FileCode, ArrowLeft, Loader2, CheckCircle, AlertCircle } from 'lucide-react'
import { API_BASE_URL } from '../config'

const AnalysisPage = () => {
  const navigate = useNavigate()
  const { toast } = useToast()
  const [activeTab, setActiveTab] = useState('github')
  const [githubUrl, setGithubUrl] = useState('')
  const [isValidating, setIsValidating] = useState(false)
  const [validationResult, setValidationResult] = useState(null)
  const [uploadedFiles, setUploadedFiles] = useState([])
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [analysisProgress, setAnalysisProgress] = useState(0)

  const validateGithubUrl = async () => {
    if (!githubUrl.trim()) {
      toast({
        title: "Error",
        description: "Please enter a GitHub repository URL",
        variant: "destructive"
      })
      return
    }

    setIsValidating(true)
    setValidationResult(null)

    try {
      const response = await fetch(`${API_BASE_URL}/api/github/validate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ url: githubUrl })
      })

      const data = await response.json()

      if (response.ok && data.valid) {
        setValidationResult({
          valid: true,
          repository: data.repository,
          solidityFiles: data.solidity_files,
          files: data.files || []
        })
        toast({
          title: "Repository Validated",
          description: `Found ${data.solidity_files} Solidity files`,
        })
      } else {
        setValidationResult({
          valid: false,
          message: data.message || 'Invalid repository URL'
        })
        toast({
          title: "Validation Failed",
          description: data.message || 'Invalid repository URL',
          variant: "destructive"
        })
      }
    } catch (error) {
      console.error('Validation error:', error)
      toast({
        title: "Error",
        description: "Failed to validate repository. Please try again.",
        variant: "destructive"
      })
    } finally {
      setIsValidating(false)
    }
  }

  const handleFileUpload = (event) => {
    const files = Array.from(event.target.files)
    const validFiles = files.filter(file => 
      file.name.endsWith('.sol') || file.name.endsWith('.solidity')
    )

    if (validFiles.length === 0) {
      toast({
        title: "Invalid Files",
        description: "Please upload only Solidity (.sol) files",
        variant: "destructive"
      })
      return
    }

    if (validFiles.length > 20) {
      toast({
        title: "Too Many Files",
        description: "Maximum 20 files allowed",
        variant: "destructive"
      })
      return
    }

    const processedFiles = validFiles.map(file => ({
      name: file.name,
      size: file.size,
      file: file
    }))

    setUploadedFiles(processedFiles)
    toast({
      title: "Files Uploaded",
      description: `${validFiles.length} Solidity files ready for analysis`,
    })
  }

  const startAnalysis = async () => {
    setIsAnalyzing(true)
    setAnalysisProgress(0)

    try {
      let analysisData = {}

      if (activeTab === 'github' && validationResult?.valid) {
        analysisData = { github_url: githubUrl }
      } else if (activeTab === 'upload' && uploadedFiles.length > 0) {
        // Read file contents
        const fileContents = await Promise.all(
          uploadedFiles.map(async (fileData) => {
            const content = await fileData.file.text()
            return {
              name: fileData.name,
              content: content
            }
          })
        )
        analysisData = { files: fileContents }
      } else {
        toast({
          title: "Error",
          description: "Please provide valid input for analysis",
          variant: "destructive"
        })
        setIsAnalyzing(false)
        return
      }

      const response = await fetch(`${API_BASE_URL}/api/analyze`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(analysisData)
      })

      const data = await response.json()

      if (response.ok) {
        // Start progress monitoring
        const jobId = data.job_id
        monitorProgress(jobId)
      } else {
        throw new Error(data.error || 'Analysis failed to start')
      }
    } catch (error) {
      console.error('Analysis error:', error)
      toast({
        title: "Analysis Failed",
        description: error.message || "Failed to start analysis",
        variant: "destructive"
      })
      setIsAnalyzing(false)
    }
  }

  const monitorProgress = async (jobId) => {
    const checkProgress = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/api/status/${jobId}`)
        const data = await response.json()

        if (response.ok) {
          setAnalysisProgress(data.progress || 0)

          if (data.status === 'completed') {
            toast({
              title: "Analysis Complete",
              description: "Redirecting to results...",
            })
            setTimeout(() => {
              navigate(`/results/${jobId}`)
            }, 1000)
            return
          } else if (data.status === 'error') {
            throw new Error(data.message || 'Analysis failed')
          } else {
            // Continue monitoring
            setTimeout(checkProgress, 2000)
          }
        } else {
          throw new Error('Failed to check progress')
        }
      } catch (error) {
        console.error('Progress monitoring error:', error)
        toast({
          title: "Error",
          description: "Failed to monitor analysis progress",
          variant: "destructive"
        })
        setIsAnalyzing(false)
      }
    }

    checkProgress()
  }

  const removeFile = (index) => {
    const newFiles = uploadedFiles.filter((_, i) => i !== index)
    setUploadedFiles(newFiles)
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      {/* Navigation */}
      <nav className="bg-white/80 backdrop-blur-md border-b border-slate-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <Button 
              variant="ghost" 
              onClick={() => navigate('/')}
              className="flex items-center space-x-2"
            >
              <ArrowLeft className="h-4 w-4" />
              <span>Back to Home</span>
            </Button>
            <div className="text-lg font-semibold text-slate-900">
              Smart Contract Analysis
            </div>
            <div className="w-24"></div> {/* Spacer for centering */}
          </div>
        </div>
      </nav>

      <div className="max-w-4xl mx-auto py-12 px-4 sm:px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
        >
          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-slate-900 mb-2">
              Analyze Smart Contracts
            </h1>
            <p className="text-slate-600">
              Upload your smart contracts or provide a GitHub repository for comprehensive security analysis
            </p>
          </div>

          {isAnalyzing ? (
            <Card className="mb-8">
              <CardHeader>
                <CardTitle className="flex items-center space-x-2">
                  <Loader2 className="h-5 w-5 animate-spin" />
                  <span>Analysis in Progress</span>
                </CardTitle>
                <CardDescription>
                  Please wait while we analyze your smart contracts for vulnerabilities
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <Progress value={analysisProgress} className="w-full" />
                  <div className="text-center text-sm text-slate-600">
                    {analysisProgress}% Complete
                  </div>
                </div>
              </CardContent>
            </Card>
          ) : (
            <Card>
              <CardHeader>
                <CardTitle>Choose Analysis Method</CardTitle>
                <CardDescription>
                  Select how you want to provide your smart contracts for analysis
                </CardDescription>
              </CardHeader>
              <CardContent>
                <Tabs value={activeTab} onValueChange={setActiveTab}>
                  <TabsList className="grid w-full grid-cols-2">
                    <TabsTrigger value="github" className="flex items-center space-x-2">
                      <Github className="h-4 w-4" />
                      <span>GitHub Repository</span>
                    </TabsTrigger>
                    <TabsTrigger value="upload" className="flex items-center space-x-2">
                      <Upload className="h-4 w-4" />
                      <span>File Upload</span>
                    </TabsTrigger>
                  </TabsList>

                  <TabsContent value="github" className="space-y-4">
                    <div className="space-y-2">
                      <Label htmlFor="github-url">GitHub Repository URL</Label>
                      <div className="flex space-x-2">
                        <Input
                          id="github-url"
                          placeholder="https://github.com/username/repository"
                          value={githubUrl}
                          onChange={(e) => setGithubUrl(e.target.value)}
                          disabled={isValidating}
                        />
                        <Button 
                          onClick={validateGithubUrl}
                          disabled={isValidating || !githubUrl.trim()}
                        >
                          {isValidating ? (
                            <Loader2 className="h-4 w-4 animate-spin" />
                          ) : (
                            'Validate'
                          )}
                        </Button>
                      </div>
                    </div>

                    {validationResult && (
                      <Alert className={validationResult.valid ? 'border-green-200 bg-green-50' : 'border-red-200 bg-red-50'}>
                        {validationResult.valid ? (
                          <CheckCircle className="h-4 w-4 text-green-600" />
                        ) : (
                          <AlertCircle className="h-4 w-4 text-red-600" />
                        )}
                        <AlertDescription>
                          {validationResult.valid ? (
                            <div>
                              <p className="font-medium text-green-800">Repository validated successfully!</p>
                              {validationResult.repository && (
                                <div className="mt-2 space-y-1 text-sm text-green-700">
                                  <p><strong>Name:</strong> {validationResult.repository.full_name}</p>
                                  <p><strong>Language:</strong> {validationResult.repository.language || 'Mixed'}</p>
                                  <p><strong>Solidity Files:</strong> {validationResult.solidityFiles}</p>
                                </div>
                              )}
                            </div>
                          ) : (
                            <p className="text-red-800">{validationResult.message}</p>
                          )}
                        </AlertDescription>
                      </Alert>
                    )}
                  </TabsContent>

                  <TabsContent value="upload" className="space-y-4">
                    <div className="space-y-2">
                      <Label htmlFor="file-upload">Upload Solidity Files</Label>
                      <div className="border-2 border-dashed border-slate-300 rounded-lg p-6 text-center hover:border-slate-400 transition-colors">
                        <input
                          id="file-upload"
                          type="file"
                          multiple
                          accept=".sol,.solidity"
                          onChange={handleFileUpload}
                          className="hidden"
                        />
                        <label htmlFor="file-upload" className="cursor-pointer">
                          <Upload className="h-12 w-12 text-slate-400 mx-auto mb-4" />
                          <p className="text-slate-600 mb-2">
                            Click to upload or drag and drop
                          </p>
                          <p className="text-sm text-slate-500">
                            Solidity files only (.sol, .solidity) - Max 20 files
                          </p>
                        </label>
                      </div>
                    </div>

                    {uploadedFiles.length > 0 && (
                      <div className="space-y-2">
                        <Label>Uploaded Files ({uploadedFiles.length})</Label>
                        <div className="space-y-2 max-h-40 overflow-y-auto">
                          {uploadedFiles.map((file, index) => (
                            <div key={index} className="flex items-center justify-between p-2 bg-slate-50 rounded">
                              <div className="flex items-center space-x-2">
                                <FileCode className="h-4 w-4 text-blue-600" />
                                <span className="text-sm font-medium">{file.name}</span>
                                <Badge variant="secondary" className="text-xs">
                                  {(file.size / 1024).toFixed(1)} KB
                                </Badge>
                              </div>
                              <Button
                                size="sm"
                                variant="ghost"
                                onClick={() => removeFile(index)}
                                className="h-6 w-6 p-0 text-slate-400 hover:text-red-600"
                              >
                                ×
                              </Button>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </TabsContent>
                </Tabs>

                <div className="flex justify-end pt-6">
                  <Button
                    onClick={startAnalysis}
                    disabled={
                      (activeTab === 'github' && !validationResult?.valid) ||
                      (activeTab === 'upload' && uploadedFiles.length === 0)
                    }
                    className="bg-blue-600 hover:bg-blue-700"
                  >
                    Start Analysis
                  </Button>
                </div>
              </CardContent>
            </Card>
          )}
        </motion.div>
      </div>
    </div>
  )
}

export default AnalysisPage

