import requests
import json
import time
import sys

def test_account_abstraction_analysis():
    """Test analysis of eth-infinitism/account-abstraction repository"""
    print("Testing analysis of eth-infinitism/account-abstraction repository...")
    
    # Prepare the request data for GitHub repository analysis
    data = {
        "github_url": "https://github.com/eth-infinitism/account-abstraction"
    }
    
    try:
        # Send the request to the analysis API
        response = requests.post(
            'http://localhost:5000/api/analyze',
            headers={'Content-Type': 'application/json'},
            data=json.dumps(data),
            timeout=60
        )
        
        # Print the response
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print("Analysis started successfully!")
            print(f"Job ID: {result.get('job_id', 'N/A')}")
            
            job_id = result.get('job_id')
            if job_id:
                # Monitor progress
                print("\nMonitoring progress...")
                for i in range(30):  # Check for 30 iterations
                    time.sleep(2)  # Wait 2 seconds between checks
                    status_response = requests.get(f'http://localhost:5000/api/status/{job_id}')
                    if status_response.status_code == 200:
                        status_data = status_response.json()
                        print(f"Status: {status_data.get('status', 'N/A')}")
                        print(f"Progress: {status_data.get('progress', 0)}%")
                        print(f"Message: {status_data.get('message', 'N/A')}")
                        
                        if status_data.get('status') in ['completed', 'error']:
                            if status_data.get('status') == 'error':
                                print(f"ERROR: {status_data.get('message')}")
                            break
                    else:
                        print(f"Failed to get status: {status_response.status_code}")
                        break
                else:
                    print("Analysis is taking longer than expected...")
            
            return result.get('job_id')
        else:
            print(f"Error starting analysis: {response.text}")
            return None
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the SMCVD service. Is it running?")
    except requests.exceptions.Timeout:
        print("Error: Request timed out")
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
    
    return None

if __name__ == "__main__":
    test_account_abstraction_analysis()