import sys
import os
import threading
import time
import requests
import json

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_github_analysis():
    """Test GitHub repository analysis"""
    print("Testing GitHub repository analysis...")
    
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
            timeout=30
        )
        
        # Print the response
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        return response
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the SMCVD service. Is it running?")
    except requests.exceptions.Timeout:
        print("Error: Request timed out")
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
    
    return None

def test_file_analysis():
    """Test local file analysis"""
    print("Testing local file analysis...")
    
    # Read the test contract
    try:
        with open('test_contract.sol', 'r') as f:
            contract_content = f.read()
    except FileNotFoundError:
        print("test_contract.sol not found. Creating a simple test contract...")
        contract_content = '''
pragma solidity ^0.8.0;

contract Test {
    mapping(address => uint256) public balances;
    
    function withdraw(uint256 amount) public {
        require(balances[msg.sender] >= amount, "Insufficient balance");
        balances[msg.sender] -= amount;
        (bool success, ) = msg.sender.call{value: amount}("");
        require(success, "Transfer failed");
    }
}
'''
    
    # Prepare the request data
    data = {
        "files": [
            {
                "name": "test.sol",
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
            timeout=30
        )
        
        # Print the response
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        return response
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the SMCVD service. Is it running?")
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
        print(f"Health Check Response: {response.json()}")
        return response.status_code == 200
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the SMCVD service")
    except Exception as e:
        print(f"Error: {str(e)}")
    
    return False

def main():
    print("SMCVD Terminal Alternative")
    print("=" * 30)
    
    # Check if service is running
    if not health_check():
        print("\nPlease start the SMCVD service first:")
        print("python src/app.py")
        return
    
    print("\nSelect an option:")
    print("1. Test GitHub repository analysis")
    print("2. Test local file analysis")
    print("3. Health check")
    print("4. Exit")
    
    while True:
        try:
            choice = input("\nEnter your choice (1-4): ").strip()
            
            if choice == "1":
                test_github_analysis()
            elif choice == "2":
                test_file_analysis()
            elif choice == "3":
                health_check()
            elif choice == "4":
                print("Exiting...")
                break
            else:
                print("Invalid choice. Please enter 1, 2, 3, or 4.")
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()