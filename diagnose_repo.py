import requests
import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.services.github_service import GitHubService

def diagnose_repository():
    """Diagnose issues with the eth-infinitism/account-abstraction repository"""
    print("Diagnosing eth-infinitism/account-abstraction repository...")
    
    github_url = "https://github.com/eth-infinitism/account-abstraction"
    
    try:
        # Test 1: Validate the GitHub URL
        print("\n1. Validating GitHub URL...")
        github_service = GitHubService()
        is_valid, message = github_service.validate_github_url(github_url)
        print(f"   Valid: {is_valid}")
        print(f"   Message: {message}")
        
        if not is_valid:
            print("   ❌ URL validation failed")
            return False
            
        # Test 2: Get repository info
        print("\n2. Getting repository info...")
        try:
            repo_info = github_service.get_repository_info(github_url)
            print(f"   Name: {repo_info.get('name')}")
            print(f"   Full name: {repo_info.get('full_name')}")
            print(f"   Description: {repo_info.get('description')}")
            print(f"   Language: {repo_info.get('language')}")
            print(f"   Stars: {repo_info.get('stars')}")
            print(f"   Default branch: {repo_info.get('default_branch')}")
        except Exception as e:
            print(f"   ❌ Error getting repository info: {e}")
            return False
            
        # Test 3: Try to clone the repository
        print("\n3. Attempting to clone repository...")
        try:
            temp_dir = github_service.clone_repository(github_url)
            print(f"   ✅ Repository cloned to: {temp_dir}")
            
            # List some files to verify
            print("\n4. Checking repository contents...")
            solidity_files = []
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    if file.endswith('.sol'):
                        solidity_files.append(os.path.join(root, file))
            
            print(f"   Found {len(solidity_files)} Solidity files")
            if solidity_files:
                print("   First few Solidity files:")
                for i, file in enumerate(solidity_files[:5]):
                    print(f"     - {os.path.relpath(file, temp_dir)}")
            
            # Cleanup
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)
            print("   ✅ Cleanup completed")
            
        except Exception as e:
            print(f"   ❌ Error cloning repository: {e}")
            import traceback
            traceback.print_exc()
            return False
            
        print("\n✅ All tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = diagnose_repository()
    sys.exit(0 if success else 1)