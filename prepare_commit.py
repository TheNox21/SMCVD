import subprocess
import sys
import os

def run_command(command):
    """Run a command and return the output"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, cwd=os.getcwd())
        return result
    except Exception as e:
        print(f"Error running command {command}: {e}")
        return None

def main():
    print("Preparing to commit changes to SMCVD repository")
    print("=" * 50)
    
    # Check current directory
    current_dir = os.getcwd()
    print(f"Current directory: {current_dir}")
    
    # Check if this is a git repository
    git_result = run_command("git rev-parse --is-inside-work-tree")
    if not git_result or git_result.returncode != 0:
        print("Error: This is not a git repository")
        return
    
    # Check git status
    print("\nChecking git status...")
    status_result = run_command("git status --porcelain")
    if status_result and status_result.stdout:
        print("Modified files:")
        print(status_result.stdout)
    else:
        print("No changes to commit")
        return
    
    # Check remote repository
    print("\nChecking remote repository...")
    remote_result = run_command("git remote get-url origin")
    if remote_result and remote_result.stdout:
        print(f"Remote repository: {remote_result.stdout.strip()}")
    else:
        print("No remote repository found")
    
    # List all new files
    print("\nNew files to be added:")
    new_files_result = run_command("git ls-files --others --exclude-standard")
    if new_files_result and new_files_result.stdout:
        new_files = new_files_result.stdout.strip().split('\n')
        for file in new_files:
            if file:  # Skip empty lines
                print(f"  {file}")
    else:
        print("  No new files")
    
    print("\nReady to commit changes.")
    print("To commit and push, run the git_commit.bat file.")

if __name__ == "__main__":
    main()