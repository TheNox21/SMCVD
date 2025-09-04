# Smart Contract Security Analyzer

A comprehensive web application for bug bounty hunters that analyzes smart contracts from GitHub repositories using AI/ML to detect vulnerabilities and generates detailed bug bounty reports with proof-of-concept exploits.

## 🚀 Deployed Application

### Frontend (React)
- **URL**: Ready for deployment (publish button available in UI)
- **Features**: Modern, responsive interface with professional design
- **Technology**: React, Tailwind CSS, shadcn/ui components

### Backend (Flask API)
- **URL**: https://w5hni7cp7e53.manus.space
- **Status**: ✅ Live and operational
- **API Documentation**: Available at the base URL

## 📋 Features

### Core Functionality
- **GitHub Integration**: Seamlessly analyze smart contracts directly from GitHub repositories
- **File Upload**: Support for direct Solidity file uploads (.sol files)
- **AI-Powered Analysis**: Advanced vulnerability detection using OpenAI GPT models
- **Real-time Progress**: Live progress tracking with detailed status updates
- **Professional Reports**: Generate comprehensive bug bounty reports in multiple formats

### Vulnerability Detection
The application detects various types of smart contract vulnerabilities including:
- Reentrancy Attacks
- Integer Overflow/Underflow
- Access Control Issues
- Timestamp Dependence
- Unchecked External Calls
- Weak Randomness
- Front-running Vulnerabilities
- DoS Gas Limit Issues

### Report Generation
- **Multiple Templates**: Professional, Detailed Technical, and Concise formats
- **Customizable Content**: Select specific vulnerabilities to include
- **Export Formats**: Markdown and PDF support
- **Proof-of-Concept**: AI-generated exploit demonstrations
- **Professional Formatting**: Industry-standard bug bounty report structure

## 🏗️ Architecture

### Frontend (React Application)
```
src/
├── components/
│   ├── LandingPage.jsx      # Homepage with feature showcase
│   ├── AnalysisPage.jsx     # Upload/GitHub input interface
│   ├── DashboardPage.jsx    # Real-time progress monitoring
│   ├── ResultsPage.jsx      # Vulnerability results display
│   └── ReportPage.jsx       # Report generation interface
├── hooks/
│   └── use-toast.js         # Toast notification system
├── config.js                # API configuration
└── App.jsx                  # Main routing component
```

### Backend (Flask API)
```
src/
├── routes/
│   ├── analysis.py          # Analysis job management
│   ├── github.py            # GitHub repository integration
│   ├── upload.py            # File upload handling
│   └── report.py            # Report generation
├── services/
│   ├── github_service.py    # GitHub API interactions
│   ├── analysis_service.py  # Vulnerability detection engine
│   ├── ai_service.py        # OpenAI integration
│   └── report_service.py    # Report generation logic
├── utils/
│   └── file_processor.py    # File processing utilities
└── main.py                  # Flask application entry point
```

## 🔧 Technology Stack

### Frontend
- **React 18**: Modern React with hooks and functional components
- **React Router**: Client-side routing
- **Tailwind CSS**: Utility-first CSS framework
- **shadcn/ui**: High-quality UI components
- **Lucide Icons**: Beautiful icon library
- **Framer Motion**: Smooth animations and transitions
- **Sonner**: Toast notifications

### Backend
- **Flask**: Lightweight Python web framework
- **Flask-CORS**: Cross-origin resource sharing
- **OpenAI API**: AI-powered vulnerability analysis
- **PyGithub**: GitHub API integration
- **Jinja2**: Template engine for report generation
- **WeasyPrint**: PDF generation capability

## 📊 API Endpoints

### Analysis Endpoints
- `POST /api/analyze` - Start smart contract analysis
- `GET /api/status/{job_id}` - Get analysis progress
- `GET /api/results/{job_id}` - Get analysis results

### GitHub Integration
- `POST /api/github/validate` - Validate GitHub repository URL

### Report Generation
- `POST /api/report/generate` - Generate bug bounty report
- `POST /api/report/download` - Download report in specified format
- `GET /api/report/templates` - Get available report templates

## 🎯 Usage Workflow

1. **Input**: User provides GitHub repository URL or uploads Solidity files
2. **Validation**: System validates input and checks for smart contracts
3. **Analysis**: AI-powered engine analyzes code for vulnerabilities
4. **Progress**: Real-time progress tracking with detailed status updates
5. **Results**: Comprehensive vulnerability report with severity ratings
6. **Report**: Generate professional bug bounty report with POCs
7. **Export**: Download report in Markdown or PDF format

## 🔍 Vulnerability Analysis Engine

### Detection Methods
- **Pattern Matching**: Known vulnerability patterns in Solidity code
- **Contextual Filters**: Pragma parsing, unchecked blocks, SafeMath usage, access modifiers
- **Heuristic Signals**: Multi-signal corroboration for reentrancy and arithmetic issues
- **AI Analysis**: Model-guided explanations and PoCs (JSON-structured)
- **Static Analysis**: Code structure and flow analysis
- **Best Practice Checks**: Solidity coding standard compliance

### Severity Classification
- **Critical**: Immediate fund loss or contract compromise
- **High**: Significant security impact
- **Medium**: Moderate security concerns
- **Low**: Minor issues or best practice violations

### Report Quality
- **Detailed Descriptions**: Clear vulnerability explanations
- **Impact Assessment**: Business impact and risk analysis
- **Proof-of-Concept**: Working exploit demonstrations
- **Mitigation Strategies**: Specific fix recommendations
- **Professional Format**: Industry-standard report structure
- **Confidence ratings**

### False Positive Suppression
- Inline suppression: `// analyzer-ignore: reentrancy` or file-level `// analyzer-ignore-file: integer_overflow`
- Solidity ≥0.8 arithmetic is treated as safe unless inside `unchecked {}`
- SafeMath usage, `onlyOwner`/`AccessControl`, and `nonReentrant` reduce or filter findings
- Reentrancy requires call-before-state-change corroboration to report

### Configuration
- `MIN_CONFIDENCE` (env): Minimum confidence threshold (default `0.65`)
- `OPENAI_MODEL` (env): Override default AI model (default `gpt-4o-mini`)

## 📈 Sample Analysis Results

The application provides comprehensive analysis including:
- Total files analyzed
- Vulnerability count by severity
- Detailed vulnerability descriptions
- Vulnerable code snippets
- Impact assessments
- Mitigation recommendations
- Confidence ratings

## 🚀 Deployment Information

### Backend Deployment
- **Platform**: Manus deployment platform
- **URL**: https://w5hni7cp7e53.manus.space
- **Status**: Production ready
- **Scaling**: Auto-scaling enabled

### Frontend Deployment
- **Platform**: Static hosting via Manus
- **Status**: Ready for publication
- **CDN**: Global content delivery
- **Performance**: Optimized build with code splitting

## 🔐 Security Considerations

- **API Security**: CORS enabled for cross-origin requests
- **Input Validation**: Comprehensive input sanitization
- **Rate Limiting**: Protection against abuse
- **Error Handling**: Secure error messages without information leakage

## 📝 Development Notes

### Key Implementation Details
- **Modular Architecture**: Clean separation of concerns
- **Responsive Design**: Mobile-first approach
- **Error Handling**: Comprehensive error management
- **Progress Tracking**: Real-time status updates
- **State Management**: Efficient React state handling

### Future Enhancements
- **Database Integration**: Persistent storage for analysis history
- **User Authentication**: User accounts and analysis history
- **Advanced AI Models**: Integration with specialized security models
- **Batch Processing**: Multiple repository analysis
- **Integration APIs**: Third-party security tool integration

## 🎨 User Interface Highlights

### Landing Page
- Hero section with clear value proposition
- Feature showcase with interactive elements
- Statistics and credibility indicators
- Smooth animations and transitions

### Analysis Interface
- Dual input methods (GitHub/Upload)
- Real-time validation feedback
- Progress visualization
- Professional status indicators

### Results Display
- Collapsible vulnerability details
- Severity-based color coding
- Code snippet highlighting
- Actionable recommendations

### Report Generation
- Customizable report configuration
- Template selection
- Vulnerability filtering
- Multiple export formats

## 📞 Support and Documentation

For technical support or questions about the Smart Contract Security Analyzer:
- Review the API documentation at the backend URL
- Check the comprehensive vulnerability detection capabilities
- Explore the professional report generation features
- Test the full workflow from analysis to report export

---

**Built for security researchers and bug bounty hunters** | **Powered by AI and modern web technologies**

