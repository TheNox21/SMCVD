# 🚀 SMCVD Enhanced Setup Guide

## What's New in Version 2.0

### ✨ Major Improvements Added:
- **🛡️ Enhanced Security**: Rate limiting, input validation, secure configuration
- **💾 Database Persistence**: SQLite job storage with automatic cleanup
- **🧪 Comprehensive Testing**: Unit tests and import validation
- **📝 Better Logging**: Centralized logging with file rotation
- **⚡ Performance**: Caching, optimized analysis patterns
- **🎨 Enhanced Reports**: Better HTML formatting, styling
- **🔧 Configuration Management**: Structured settings with validation
- **🚨 Better Vulnerability Detection**: Flash loan attacks, price manipulation

## Quick Start

### Option 1: Automated Setup (Recommended)
```powershell
# Run the enhanced startup script
python start_smcvd.py
```

### Option 2: Manual Setup
```powershell
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set environment variables (optional)
$env:OPENAI_API_KEY = "sk-your-api-key-here"
$env:MIN_CONFIDENCE = "0.65"
$env:SECRET_KEY = "your-secret-key"

# 3. Test the setup
python test_imports.py

# 4. Run the application
python src/app.py
```

## New Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENAI_API_KEY` | None | OpenAI API key for AI features |
| `MIN_CONFIDENCE` | 0.65 | Minimum confidence threshold for vulnerabilities |
| `ENABLE_AI` | true | Enable/disable AI enhancements |
| `SECRET_KEY` | dev-secret | Flask secret key (change in production) |
| `LOG_LEVEL` | INFO | Logging level (DEBUG, INFO, WARNING, ERROR) |
| `MAX_FILE_SIZE` | 10MB | Maximum file size for uploads |
| `RATE_LIMIT_PER_MINUTE` | 10 | API rate limit per minute |
| `DB_CLEANUP_DAYS` | 7 | Days to keep old analysis jobs |

## New API Endpoints

### Health Check
```bash
GET /api/health
```
Returns application status and enabled features.

### Enhanced Analysis
- Rate limited (5 requests/minute)
- Persistent job storage
- Improved vulnerability patterns

### Better Reports
- Enhanced HTML styling
- Table formatting
- Severity badges

## File Structure (Updated)

```
smartcontract/
├── src/
│   ├── app.py                 # Enhanced main application
│   ├── config/
│   │   └── settings.py        # Centralized configuration
│   ├── middleware/
│   │   └── rate_limiting.py   # Rate limiting & caching
│   ├── models/
│   │   └── job.py            # Job persistence model
│   ├── services/             # Moved all services here
│   │   ├── analysis_service.py
│   │   ├── ai_service.py
│   │   ├── github_service.py
│   │   └── report_service.py
│   ├── routes/               # API routes
│   └── utils/
│       └── logging.py        # Logging configuration
├── tests/
│   └── test_analysis_service.py  # Unit tests
├── logs/                     # Application logs
├── start_smcvd.py           # Enhanced startup script
├── test_imports.py          # Import validation
└── requirements.txt         # Updated dependencies
```

## Testing the Enhanced Features

### 1. Test Import Structure
```powershell
python test_imports.py
```

### 2. Test Analysis Service
```powershell
python -m pytest tests/test_analysis_service.py -v
```

### 3. Test Rate Limiting
```bash
# Make multiple rapid requests to test rate limiting
curl -X POST http://localhost:5000/api/analyze -H "Content-Type: application/json" -d "{\"files\":[{\"name\":\"test.sol\",\"content\":\"contract Test{}\"}]}"
```

### 4. Test Health Endpoint
```bash
curl http://localhost:5000/api/health
```

### 5. Test Database Persistence
Jobs are now persisted in `smcvd.db` and survive application restarts.

## Production Deployment

### 1. Environment Setup
```bash
export OPENAI_API_KEY="your-production-key"
export SECRET_KEY="your-strong-secret-key"
export FLASK_DEBUG="false"
export MIN_CONFIDENCE="0.70"
export LOG_LEVEL="WARNING"
```

### 2. Using Gunicorn (Recommended)
```bash
gunicorn -w 4 -b 0.0.0.0:5000 src.app:create_app
```

### 3. Database Maintenance
```python
from src.models.job import JobStorage
storage = JobStorage()
storage.cleanup_old_jobs(days=7)  # Clean up old jobs
```

## Troubleshooting

### Common Issues:

1. **Import Errors**: Run `pip install -r requirements.txt`
2. **Missing AI Features**: Set `OPENAI_API_KEY`
3. **Rate Limit Issues**: Adjust `RATE_LIMIT_PER_MINUTE`
4. **Database Issues**: Delete `smcvd.db` to reset
5. **Log Issues**: Check `logs/` directory permissions

### Debug Mode:
```powershell
$env:LOG_LEVEL = "DEBUG"
$env:FLASK_DEBUG = "true"
python src/app.py
```

## Performance Tips

1. **AI Optimization**: Lower `AI_MAX_TOKENS` for faster responses
2. **Rate Limiting**: Increase limits for trusted environments
3. **Database**: Regular cleanup of old jobs
4. **Caching**: Results are cached for repeated requests
5. **File Size**: Adjust `MAX_FILE_SIZE` based on needs

## Security Considerations

1. **Secret Key**: Always set a strong `SECRET_KEY` in production
2. **Rate Limiting**: Protects against abuse
3. **Input Validation**: Enhanced file and data validation
4. **CORS**: Configure `CORS_ORIGINS` for production
5. **Logging**: Sensitive data is not logged

---

🎉 **Congratulations!** Your SMCVD tool now has enterprise-grade features and is ready for production use!
