import requests
import json
import time
import sys

def analyze_github_repository():
    # Prepare the request data for GitHub repository analysis
    data = {
        "github_url": "https://github.com/kub-chain/bkc",
        "program_scope": {
            "focus_areas": ["reentrancy", "access_control", "integer_overflow"],
            "in_scope_vulns": ["reentrancy", "access_control", "integer_overflow"],
            "severity_allow": {
                "reentrancy": ["critical", "high"],
                "access_control": ["high", "medium"],
                "integer_overflow": ["high", "medium"]
            }
        }
    }
    
    try:
        print("Sending analysis request for kub-chain/bkc repository...")
        # Send the request to the analysis API
        response = requests.post(
            'http://localhost:5000/api/analyze',
            headers={'Content-Type': 'application/json'},
            data=json.dumps(data),
            timeout=30
        )
        
        # Print the response
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print("Analysis request successful!")
            print(f"Job ID: {result.get('job_id', 'N/A')}")
            
            job_id = result.get('job_id')
            if job_id:
                # Wait and check status multiple times
                print("\nWaiting for analysis to complete...")
                for i in range(10):  # Check status 10 times
                    time.sleep(5)  # Wait 5 seconds between checks
                    
                    # Check status
                    try:
                        status_response = requests.get(f'http://localhost:5000/api/status/{job_id}', timeout=10)
                        if status_response.status_code == 200:
                            status_result = status_response.json()
                            status = status_result.get('status', 'N/A')
                            progress = status_result.get('progress', 'N/A')
                            print(f"Attempt {i+1}: Job Status: {status}, Progress: {progress}")
                            
                            # If completed, get results
                            if status == 'completed':
                                print("\nAnalysis completed! Getting results...")
                                results_response = requests.get(f'http://localhost:5000/api/results/{job_id}', timeout=30)
                                if results_response.status_code == 200:
                                    results = results_response.json()
                                    print("\nAnalysis Results:")
                                    print(json.dumps(results, indent=2))
                                    return results
                                else:
                                    print(f"Error getting results: {results_response.text}")
                                    return None
                        else:
                            print(f"Error checking status: {status_response.text}")
                    except Exception as e:
                        print(f"Error checking status: {e}")
                
                print("Analysis did not complete within expected time.")
                
            return result.get('job_id')
        else:
            print(f"Error: {response.text}")
            return None
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the SMCVD service. Is it running?")
        print("Please start the service with: python src/app.py")
    except requests.exceptions.Timeout:
        print("Error: Request timed out")
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
    
    return None

def health_check():
    """Check if the service is running"""
    print("Checking service health...")
    
    try:
        response = requests.get('http://localhost:5000/api/health', timeout=10)
        print(f"Health Check Status Code: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print("Service Health: Healthy")
            print(f"Version: {result.get('version', 'N/A')}")
            return True
        else:
            print(f"Service not healthy: {response.text}")
            return False
    except Exception as e:
        print(f"Error checking health: {str(e)}")
        return False

def main():
    print("Kub-Chain BKC Repository Analysis")
    print("=" * 40)
    
    # Check if service is running
    if not health_check():
        print("\nPlease start the SMCVD service first:")
        print("python src/app.py")
        return
    
    # Analyze the kub-chain repository
    analyze_github_repository()

if __name__ == "__main__":
    main()