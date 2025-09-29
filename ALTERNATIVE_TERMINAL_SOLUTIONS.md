# Alternative Terminal Solutions for SMCVD

This document provides alternative methods to run and test the Smart Contract Vulnerability Detector (SMCVD) without encountering PowerShell terminal issues.

## Problem

The PowerShell terminal is experiencing rendering issues with PSReadLine, causing it to crash when running certain commands. This prevents us from properly testing the SMCVD tool.

## Solutions

### Solution 1: Use Command Prompt (cmd)

1. Open Command Prompt (cmd) as Administrator or regular user
2. Navigate to the project directory:
   ```
   cd /d c:\Users\user23\Downloads\smartcontract
   ```

3. Run the Flask application:
   ```
   python src\app.py
   ```

4. In another cmd window, test the service:
   ```
   curl http://localhost:5000/api/health
   ```

### Solution 2: Use the Complete Test Script

We've created a comprehensive Python script that handles everything:

1. Open Command Prompt (cmd)
2. Navigate to the project directory:
   ```
   cd /d c:\Users\user23\Downloads\smartcontract
   ```

3. Run the complete test:
   ```
   python complete_test.py
   ```

This script will:
- Start the SMCVD service automatically
- Wait for it to be ready
- Perform a health check
- Test GitHub repository analysis
- Test local file analysis
- Check job statuses
- Retrieve results
- Cleanly shut down the service

### Solution 3: Use the Terminal Alternative Script

For interactive testing:

1. Open Command Prompt (cmd)
2. Navigate to the project directory:
   ```
   cd /d c:\Users\user23\Downloads\smartcontract
   ```

3. Start the service in one terminal:
   ```
   python src\app.py
   ```

4. In another terminal, run the interactive tester:
   ```
   python terminal_alternative.py
   ```

### Solution 4: Use the Batch File

We've created a batch file that automates the process:

1. Double-click on `run_tests.bat` in the project directory
2. Or run from Command Prompt:
   ```
   run_tests.bat
   ```

## Testing with Your GitHub Repository

To test with the specific GitHub repository you mentioned (https://github.com/kub-chain/bkc):

1. Using the complete test script:
   ```
   python complete_test.py
   ```

2. Using the interactive tester:
   - Start the service: `python src\app.py`
   - Run the tester: `python terminal_alternative.py`
   - Select option 1 for GitHub analysis

3. Manual testing with curl (in cmd):
   ```
   curl -X POST http://localhost:5000/api/analyze -H "Content-Type: application/json" -d "{\"github_url\": \"https://github.com/kub-chain/bkc\"}"
   ```

## Troubleshooting

### If the service fails to start:

1. Check if port 5000 is already in use:
   ```
   netstat -ano | findstr :5000
   ```

2. If another process is using port 5000, you can:
   - Kill the process: `taskkill /PID <process_id> /F`
   - Or change the port in the app configuration

### If you get connection errors:

1. Make sure the service is running before making requests
2. Check Windows Firewall settings
3. Try using 127.0.0.1 instead of localhost:
   ```
   curl http://127.0.0.1:5000/api/health
   ```

### If Python modules are missing:

Install required dependencies:
```
pip install -r requirements.txt
```

## Files Created for Alternative Solutions

1. `terminal_alternative.py` - Interactive testing interface
2. `complete_test.py` - Automated complete test suite
3. `start_service.py` - Service starter script
4. `run_tests.bat` - Batch file for Windows
5. `simple_github_test.py` - Simple GitHub connectivity test
6. `github_direct_test.py` - Direct GitHub service testing

These alternatives should allow you to run and test the SMCVD tool without encountering the PowerShell terminal issues.