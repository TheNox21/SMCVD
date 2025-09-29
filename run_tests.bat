@echo off
echo SMCVD Test Runner
echo =================

echo Starting SMCVD service...
start "SMCVD" /MIN cmd /c "cd /d c:\Users\user23\Downloads\smartcontract && python src\app.py"

timeout /t 5 /nobreak >nul

echo Testing health check...
curl http://localhost:5000/api/health

echo.
echo Testing with local file...
python github_direct_test.py

echo.
echo All tests completed.
pause