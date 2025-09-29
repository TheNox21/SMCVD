import sys
import os
import requests
import json
import time

def test_kub_chain_repository():
    """Test analysis of the kub-chain/bkc repository"""
    print("Testing analysis of kub-chain/bkc repository")
    print("=" * 50)
    
    # Prepare the request data for GitHub repository analysis
    data = {
        "github_url": "https://github.com/kub-chain/bkc",
        "program_scope": {
            "focus_areas": ["reentrancy", "access_control", "integer_overflow"],
            "in_scope_vulns": ["reentrancy", "access_control", "integer_overflow", "unchecked_external_call"],
            "out_of_scope_vulns": ["front_running", "dos_gas_limit"],
            "severity_allow": {
                "reentrancy": ["critical", "high"],
                "access_control": ["high", "medium"],
                "integer_overflow": ["high", "medium"]
            }
        }
    }
    
    try:
        print("Sending analysis request...")
        # Send the request to the analysis API
        response = requests.post(
            'http://localhost:5000/api/analyze',
            headers={'Content-Type': 'application/json'},
            data=json.dumps(data),
            timeout=120
        )
        
        # Print the response
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print("Analysis request successful!")
            print(f"Job ID: {result.get('job_id', 'N/A')}")
            
            job_id = result.get('job_id')
            if job_id:
                # Wait and check status
                print("\nWaiting for analysis to complete...")
                time.sleep(10)
                
                # Check status
                status_response = requests.get(f'http://localhost:5000/api/status/{job_id}', timeout=10)
                if status_response.status_code == 200:
                    status_result = status_response.json()
                    print(f"Job Status: {status_result.get('status', 'N/A')}")
                    print(f"Progress: {status_result.get('progress', 'N/A')}")
                
                # Get results
                print("\nGetting analysis results...")
                results_response = requests.get(f'http://localhost:5000/api/results/{job_id}', timeout=30)
                if results_response.status_code == 200:
                    results = results_response.json()
                    print("Analysis Results:")
                    print(json.dumps(results, indent=2))
                else:
                    print(f"Error getting results: {results_response.text}")
            
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
    
    # Test the kub-chain repository
    test_kub_chain_repository()

if __name__ == "__main__":
    main()