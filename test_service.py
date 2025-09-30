import requests
import json

def test_service():
    try:
        response = requests.get('http://localhost:5000/api/health')
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    success = test_service()
    print(f"Service test {'PASSED' if success else 'FAILED'}")