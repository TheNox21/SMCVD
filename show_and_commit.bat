@echo off
echo SMCVD Git Status and Commit
echo ==========================

echo.
echo Current directory:
cd

echo.
echo Git status:
git status

echo.
echo Listing untracked files:
git ls-files --others --exclude-standard

echo.
echo Adding all changes...
git add .

echo.
echo Committing changes...
git commit -m "Enhanced SMCVD with improved false positive reduction and terminal alternative solutions. Added comprehensive documentation and testing files."

echo.
echo Pushing to remote repository...
git push origin main

echo.
echo If push to main failed, trying master...
git push origin master

echo.
echo Git operations completed.
pause