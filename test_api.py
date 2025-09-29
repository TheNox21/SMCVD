import requests
import json

# Read the test contract
with open('test_contract.sol', 'r') as f:
    contract_content = f.read()

# Prepare the request data
data = {
    "files": [
        {
            "name": "test_contract.sol",
            "content": contract_content
        }
    ]
}

# Send the request to the analysis API
response = requests.post(
    'http://localhost:5000/api/analyze',
    headers={'Content-Type': 'application/json'},
    data=json.dumps(data)
)

# Print the response
print("Status Code:", response.status_code)
print("Response:", response.json())