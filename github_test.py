import requests
import json

# Prepare the request data for GitHub repository analysis
data = {
    "github_url": "https://github.com/kub-chain/bkc"
}

# Send the request to the analysis API
try:
    response = requests.post(
        'http://localhost:5000/api/analyze',
        headers={'Content-Type': 'application/json'},
        data=json.dumps(data)
    )
    
    # Print the response
    print("Status Code:", response.status_code)
    print("Response:", response.json())
except Exception as e:
    print("Error:", str(e))