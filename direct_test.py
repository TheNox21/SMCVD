import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from services.analysis_service import AnalysisService

# Read the test contract
with open('test_contract.sol', 'r') as f:
    contract_content = f.read()

# Create an instance of the analysis service
analyzer = AnalysisService()

# Analyze the contract
print("Analyzing contract...")
vulnerabilities = analyzer.analyze_contract(contract_content, "test_contract.sol")

# Print the results
print(f"Found {len(vulnerabilities)} vulnerabilities:")

for i, vuln in enumerate(vulnerabilities, 1):
    print(f"\n{i}. {vuln['name']} ({vuln['severity']}) - Confidence: {vuln['confidence']:.2f}")
    print(f"   Line {vuln['line_number']}: {vuln['line_content']}")
    print(f"   Function: {vuln['function_name']}")
    print(f"   Description: {vuln['description']}")