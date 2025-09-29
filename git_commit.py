import subprocess
import sys
import os

def run_git_command(command):
    """Run a git command and return the output"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, cwd=os.getcwd())
        print(f"Command: {command}")
        print(f"Return code: {result.returncode}")
        if result.stdout:
            print(f"Stdout: {result.stdout}")
        if result.stderr:
            print(f"Stderr: {result.stderr}")
        return result
    except Exception as e:
        print(f"Error running command {command}: {e}")
        return None

def main():
    print("Git Commit Script for SMCVD")
    print("=" * 30)
    
    # Check current directory
    print(f"Current directory: {os.getcwd()}")
    
    # Check git status
    print("\n1. Checking git status...")
    run_git_command("git status")
    
    # Check remote repositories
    print("\n2. Checking remote repositories...")
    run_git_command("git remote -v")
    
    # Add all changes
    print("\n3. Adding all changes...")
    run_git_command("git add .")
    
    # Commit changes
    print("\n4. Committing changes...")
    commit_result = run_git_command('git commit -m "Enhanced SMCVD with improved false positive reduction and terminal alternative solutions"')
    
    # Push to remote repository
    print("\n5. Pushing to remote repository...")
    push_result = run_git_command("git push origin main")
    
    if push_result and push_result.returncode != 0:
        print("\nTrying to push to master branch...")
        run_git_command("git push origin master")
    
    print("\nGit operations completed.")

if __name__ == "__main__":
    main()