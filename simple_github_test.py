import requests

# Test if we can access the GitHub repository
repo_url = "https://github.com/kub-chain/bkc"

try:
    # Try to access the repository
    response = requests.get(repo_url, timeout=10)
    print(f"Status Code: {response.status_code}")
    print(f"Success: {response.status_code == 200}")
    
    # Check if it's a GitHub repository by looking for specific content
    if "github" in response.url.lower():
        print("This is a valid GitHub repository")
    else:
        print("This might not be a GitHub repository")
        
except requests.exceptions.RequestException as e:
    print(f"Error accessing repository: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")