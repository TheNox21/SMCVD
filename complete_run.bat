@echo off
echo SMCVD Complete Analysis Run
echo ==========================

echo Starting SMCVD service...
start "SMCVD Service" /MIN cmd /c "cd /d c:\Users\user23\Downloads\smartcontract && python src\app.py"

echo Waiting for service to start...
timeout /t 10 /nobreak >nul

echo Running analysis of kub-chain/bkc repository...
cd /d c:\Users\user23\Downloads\smartcontract
python analyze_kub_chain.py

echo.
echo Complete run finished.
pause