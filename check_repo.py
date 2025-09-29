import requests
import sys

def check_repository(url):
    try:
        print(f"Checking repository: {url}")
        response = requests.get(url, timeout=10)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            print("Repository is accessible")
            # Check if it's actually a GitHub repository
            if "github.com" in response.url:
                print("This is a valid GitHub repository")
                return True
            else:
                print("This might not be a GitHub repository")
                return False
        else:
            print(f"Repository not accessible. Status code: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"Error accessing repository: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False

if __name__ == "__main__":
    repo_url = "https://github.com/kub-chain/bkc"
    is_accessible = check_repository(repo_url)
    sys.exit(0 if is_accessible else 1)