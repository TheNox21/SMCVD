import sys
import os
import requests
import json
import time
import subprocess
import threading

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def start_service():
    """Start the SMCVD service in the background"""
    print("Starting SMCVD service...")
    
    try:
        # Start the Flask app in a subprocess
        process = subprocess.Popen([
            sys.executable,
            os.path.join('src', 'app.py')
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=os.getcwd())
        
        print("SMCVD service started with PID:", process.pid)
        return process
    except Exception as e:
        print(f"Error starting service: {e}")
        return None

def wait_for_service(timeout=30):
    """Wait for the service to be ready"""
    print("Waiting for service to be ready...")
    
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = requests.get('http://localhost:5000/api/health', timeout=2)
            if response.status_code == 200:
                print("Service is ready!")
                return True
        except requests.exceptions.RequestException:
            pass
        
        time.sleep(1)
    
    print("Service did not become ready within timeout")
    return False

def test_github_analysis():
    """Test GitHub repository analysis"""
    print("\nTesting GitHub repository analysis...")
    
    # Prepare the request data for GitHub repository analysis
    data = {
        "github_url": "https://github.com/kub-chain/bkc"
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
            return result.get('job_id')
        else:
            print(f"Error: {response.text}")
            return None
    except Exception as e:
        print(f"Error: {str(e)}")
        return None

def test_file_analysis():
    """Test local file analysis"""
    print("\nTesting local file analysis...")
    
    # Simple test contract
    contract_content = '''
pragma solidity ^0.8.0;

contract SimpleVulnerableContract {
    mapping(address => uint256) public balances;
    
    // Vulnerable to reentrancy
    function withdraw(uint256 amount) public {
        require(balances[msg.sender] >= amount, "Insufficient balance");
        balances[msg.sender] -= amount;
        (bool success, ) = msg.sender.call{value: amount}("");
        require(success, "Transfer failed");
    }
    
    // Vulnerable to integer overflow (for older Solidity versions)
    function unsafeAdd(uint8 a, uint8 b) public pure returns (uint8) {
        return a + b;
    }
    
    // Unprotected self-destruct
    function kill() public {
        selfdestruct(payable(msg.sender));
    }
    
    receive() external payable {
        balances[msg.sender] += msg.value;
    }
}
'''
    
    # Prepare the request data
    data = {
        "files": [
            {
                "name": "SimpleVulnerableContract.sol",
                "content": contract_content
            }
        ]
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
            return result.get('job_id')
        else:
            print(f"Error: {response.text}")
            return None
    except Exception as e:
        print(f"Error: {str(e)}")
        return None

def check_job_status(job_id):
    """Check the status of an analysis job"""
    if not job_id:
        return
    
    print(f"\nChecking status for job {job_id}...")
    
    try:
        response = requests.get(f'http://localhost:5000/api/status/{job_id}', timeout=10)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"Job Status: {result.get('status', 'N/A')}")
            print(f"Progress: {result.get('progress', 'N/A')}")
        else:
            print(f"Error checking status: {response.text}")
    except Exception as e:
        print(f"Error checking status: {str(e)}")

def get_job_results(job_id):
    """Get the results of an analysis job"""
    if not job_id:
        return
    
    print(f"\nGetting results for job {job_id}...")
    
    try:
        response = requests.get(f'http://localhost:5000/api/results/{job_id}', timeout=10)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print("Analysis Results:")
            print(json.dumps(result, indent=2))
        else:
            print(f"Error getting results: {response.text}")
    except Exception as e:
        print(f"Error getting results: {str(e)}")

def health_check():
    """Check if the service is running"""
    print("\nChecking service health...")
    
    try:
        response = requests.get('http://localhost:5000/api/health', timeout=10)
        print(f"Health Check Status Code: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print("Service Health: Healthy")
            print(f"Version: {result.get('version', 'N/A')}")
            print(f"Features: {result.get('features', 'N/A')}")
            return True
        else:
            print(f"Service not healthy: {response.text}")
            return False
    except Exception as e:
        print(f"Error checking health: {str(e)}")
        return False

def main():
    print("SMCVD Complete Test Suite")
    print("=" * 30)
    
    # Start the service
    service_process = start_service()
    if not service_process:
        print("Failed to start service")
        return
    
    # Wait for service to be ready
    if not wait_for_service():
        print("Service failed to start")
        service_process.terminate()
        return
    
    try:
        # Perform health check
        if not health_check():
            print("Service health check failed")
            return
        
        # Test 1: GitHub analysis
        print("\n" + "="*50)
        github_job_id = test_github_analysis()
        
        # Test 2: File analysis
        print("\n" + "="*50)
        file_job_id = test_file_analysis()
        
        # Wait a bit and check statuses
        print("\n" + "="*50)
        print("Waiting for analyses to complete...")
        time.sleep(10)
        
        check_job_status(github_job_id)
        check_job_status(file_job_id)
        
        # Get results
        print("\n" + "="*50)
        get_job_results(github_job_id)
        get_job_results(file_job_id)
        
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Clean up
        print("\nStopping service...")
        service_process.terminate()
        try:
            service_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            service_process.kill()
        print("Service stopped.")

if __name__ == "__main__":
    main()