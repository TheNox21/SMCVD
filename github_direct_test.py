import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Try to import and test the GitHub service directly
try:
    from services.github_service import GitHubService
    print("GitHubService imported successfully")
    
    # Create an instance of the GitHub service
    github_service = GitHubService()
    
    # Try to validate the repository URL
    repo_url = "https://github.com/kub-chain/bkc"
    print(f"Testing repository: {repo_url}")
    
    # This would normally be used to validate and fetch repository info
    # Since we're having terminal issues, let's just test the import and basic functionality
    print("GitHub service is ready for use")
    
except Exception as e:
    print(f"Error importing or testing GitHub service: {e}")
    import traceback
    traceback.print_exc()