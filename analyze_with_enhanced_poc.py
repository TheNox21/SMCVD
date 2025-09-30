import requests
import json
import time

def analyze_with_enhanced_poc():
    """Analyze a repository with enhanced PoC generation capabilities"""
    print("Analyzing repository with enhanced PoC generation...")
    
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
            timeout=120  # Longer timeout for GitHub repos
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
                completed = False
                for i in range(60):  # Check for 60 iterations (2 minutes)
                    time.sleep(2)  # Wait 2 seconds between checks
                    status_response = requests.get(f'http://localhost:5000/api/status/{job_id}')
                    if status_response.status_code == 200:
                        status_data = status_response.json()
                        print(f"Status: {status_data.get('status', 'N/A')}")
                        print(f"Progress: {status_data.get('progress', 0)}%")
                        print(f"Message: {status_data.get('message', 'N/A')}")
                        
                        if status_data.get('status') == 'completed':
                            # Get results
                            results_response = requests.get(f'http://localhost:5000/api/results/{job_id}')
                            if results_response.status_code == 200:
                                results_data = results_response.json()
                                print("\n✅ Analysis completed successfully!")
                                print(f"Total vulnerabilities found: {results_data.get('summary', {}).get('vulnerabilities_found', 0)}")
                                
                                # Print vulnerabilities with PoCs
                                vulnerabilities = results_data.get('vulnerabilities', [])
                                if vulnerabilities:
                                    print("\nVulnerabilities with Exploits:")
                                    for vuln in vulnerabilities:
                                        print(f"\n--- {vuln.get('name', 'Unknown')} ---")
                                        print(f"Severity: {vuln.get('severity', 'Unknown').upper()}")
                                        print(f"File: {vuln.get('file_path', 'N/A')} (Line {vuln.get('line_number', 'N/A')})")
                                        print(f"Description: {vuln.get('description', 'No description')}")
                                        
                                        # Show PoC if available
                                        poc = vuln.get('poc_code')
                                        if poc and poc != 'None':
                                            print("Proof of Concept Exploit:")
                                            print(poc[:300] + "..." if len(poc) > 300 else poc)
                                        else:
                                            print("Proof of Concept: Basic PoC generated")
                                
                                # Save enhanced report
                                with open('enhanced_analysis_results.json', 'w') as f:
                                    json.dump(results_data, f, indent=2)
                                print("\nEnhanced results saved to enhanced_analysis_results.json")
                                
                            completed = True
                            break
                        elif status_data.get('status') == 'error':
                            print(f"❌ Analysis failed: {status_data.get('message')}")
                            completed = True
                            break
                    else:
                        print(f"Failed to get status: {status_response.status_code}")
                        break
                
                if not completed:
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
    analyze_with_enhanced_poc()