@echo off
echo Git Commit and Push Script for SMCVD
echo ===================================

echo Current directory:
cd

echo.
echo 1. Checking git status...
git status

echo.
echo 2. Checking remote repositories...
git remote -v

echo.
echo 3. Adding all changes...
git add .

echo.
echo 4. Committing changes...
git commit -m "Enhanced SMCVD with improved false positive reduction and terminal alternative solutions"

echo.
echo 5. Pushing to remote repository...
git push origin main

echo.
echo If the above failed, trying to push to master branch...
git push origin master

echo.
echo Git operations completed.
pause