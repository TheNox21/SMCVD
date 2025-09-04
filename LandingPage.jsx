import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Shield, Zap, FileText, Github, Upload, Brain, CheckCircle, AlertTriangle } from 'lucide-react'
import { motion } from 'framer-motion'

const LandingPage = () => {
  const navigate = useNavigate()
  const [hoveredFeature, setHoveredFeature] = useState(null)

  const features = [
    {
      icon: Github,
      title: 'GitHub Integration',
      description: 'Seamlessly analyze smart contracts directly from GitHub repositories',
      color: 'text-blue-600'
    },
    {
      icon: Brain,
      title: 'Advanced Analysis',
      description: 'Advanced machine learning algorithms detect complex vulnerabilities',
      color: 'text-purple-600'
    },
    {
      icon: FileText,
      title: 'Professional Reports',
      description: 'Generate comprehensive bug bounty reports with proof-of-concept exploits',
      color: 'text-green-600'
    },
    {
      icon: Zap,
      title: 'Real-time Processing',
      description: 'Fast analysis with live progress tracking and instant results',
      color: 'text-yellow-600'
    }
  ]

  const vulnerabilityTypes = [
    'Reentrancy Attacks',
    'Integer Overflow/Underflow',
    'Access Control Issues',
    'Timestamp Dependence',
    'Unchecked External Calls',
    'Weak Randomness',
    'Front-running Vulnerabilities',
    'DoS Gas Limit Issues'
  ]

  const stats = [
    { label: 'Vulnerability Types', value: '10+', icon: AlertTriangle },
    { label: 'Analysis Speed', value: '<2min', icon: Zap },
    { label: 'Accuracy Rate', value: '95%', icon: CheckCircle },
    { label: 'Report Formats', value: '3', icon: FileText }
  ]

  return (
    <div className="min-h-screen">
      {/* Navigation */}
      <nav className="bg-white/80 backdrop-blur-md border-b border-slate-200 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-2">
              <Shield className="h-8 w-8 text-blue-600" />
              <span className="text-xl font-bold text-slate-900">SmartSecure</span>
            </div>
            <div className="flex items-center space-x-4">
              <Button variant="ghost" className="text-slate-600 hover:text-slate-900">
                Features
              </Button>
              <Button variant="ghost" className="text-slate-600 hover:text-slate-900">
                Documentation
              </Button>
              <Button 
                onClick={() => navigate('/analyze')}
                className="bg-blue-600 hover:bg-blue-700 text-white"
              >
                Get Started
              </Button>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="text-center"
          >
            <Badge variant="secondary" className="mb-4">
              Comprehensive Security Analysis
            </Badge>
            <h1 className="text-5xl md:text-6xl font-bold text-slate-900 mb-6">
              Smart Contract
              <span className="text-blue-600 block">Vulnerability Detection</span>
            </h1>
            <p className="text-xl text-slate-600 mb-8 max-w-3xl mx-auto">
              Discover security vulnerabilities in smart contracts using advanced analysis. 
              Generate professional bug bounty reports with proof-of-concept exploits in minutes.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Button 
                size="lg" 
                onClick={() => navigate('/analyze')}
                className="bg-blue-600 hover:bg-blue-700 text-white px-8 py-3"
              >
                <Upload className="mr-2 h-5 w-5" />
                Start Analysis
              </Button>
              <Button 
                size="lg" 
                variant="outline"
                className="border-slate-300 text-slate-700 hover:bg-slate-50 px-8 py-3"
              >
                <Github className="mr-2 h-5 w-5" />
                View Demo
              </Button>
            </div>
          </motion.div>
        </div>

        {/* Floating Elements */}
        <div className="absolute top-20 left-10 opacity-20">
          <motion.div
            animate={{ y: [0, -10, 0] }}
            transition={{ duration: 3, repeat: Infinity }}
          >
            <Shield className="h-16 w-16 text-blue-500" />
          </motion.div>
        </div>
        <div className="absolute top-32 right-16 opacity-20">
          <motion.div
            animate={{ y: [0, 10, 0] }}
            transition={{ duration: 4, repeat: Infinity }}
          >
            <Brain className="h-12 w-12 text-purple-500" />
          </motion.div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-16 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            {stats.map((stat, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, scale: 0.9 }}
                whileInView={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
                className="text-center"
              >
                <div className="flex justify-center mb-2">
                  <stat.icon className="h-8 w-8 text-blue-600" />
                </div>
                <div className="text-3xl font-bold text-slate-900 mb-1">{stat.value}</div>
                <div className="text-sm text-slate-600">{stat.label}</div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="text-center mb-16"
          >
            <h2 className="text-4xl font-bold text-slate-900 mb-4">
              Powerful Features for Security Researchers
            </h2>
            <p className="text-xl text-slate-600 max-w-2xl mx-auto">
              Everything you need to identify, analyze, and report smart contract vulnerabilities
            </p>
          </motion.div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {features.map((feature, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: index * 0.1 }}
                onMouseEnter={() => setHoveredFeature(index)}
                onMouseLeave={() => setHoveredFeature(null)}
              >
                <Card className={`h-full transition-all duration-300 hover:shadow-lg ${
                  hoveredFeature === index ? 'scale-105 border-blue-200' : ''
                }`}>
                  <CardHeader>
                    <feature.icon className={`h-12 w-12 ${feature.color} mb-4`} />
                    <CardTitle className="text-xl">{feature.title}</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <CardDescription className="text-base">
                      {feature.description}
                    </CardDescription>
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Vulnerability Types Section */}
      <section className="py-20 bg-slate-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="text-center mb-16"
          >
            <h2 className="text-4xl font-bold text-slate-900 mb-4">
              Comprehensive Vulnerability Detection
            </h2>
            <p className="text-xl text-slate-600 max-w-2xl mx-auto">
              Our analysis engine detects a wide range of smart contract vulnerabilities
            </p>
          </motion.div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
            {vulnerabilityTypes.map((type, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, scale: 0.9 }}
                whileInView={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.5, delay: index * 0.05 }}
              >
                <Badge 
                  variant="secondary" 
                  className="w-full py-3 px-4 text-center justify-center hover:bg-blue-100 hover:text-blue-800 transition-colors cursor-default"
                >
                  {type}
                </Badge>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-blue-600">
        <div className="max-w-4xl mx-auto text-center px-4 sm:px-6 lg:px-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
          >
            <h2 className="text-4xl font-bold text-white mb-4">
              Ready to Secure Your Smart Contracts?
            </h2>
            <p className="text-xl text-blue-100 mb-8">
              Start analyzing your smart contracts today and discover vulnerabilities before attackers do.
            </p>
            <Button 
              size="lg"
              onClick={() => navigate('/analyze')}
              className="bg-white text-blue-600 hover:bg-blue-50 px-8 py-3"
            >
              <Shield className="mr-2 h-5 w-5" />
              Start Free Analysis
            </Button>
          </motion.div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-slate-900 text-white py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col md:flex-row justify-between items-center">
            <div className="flex items-center space-x-2 mb-4 md:mb-0">
              <Shield className="h-6 w-6 text-blue-400" />
              <span className="text-lg font-semibold">SmartSecure</span>
            </div>
            <div className="text-slate-400 text-sm">
              © 2024 SmartSecure. Built for security researchers and bug bounty hunters.
            </div>
          </div>
        </div>
      </footer>
    </div>
  )
}

export default LandingPage

