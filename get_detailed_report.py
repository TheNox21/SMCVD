import requests
import json

def get_detailed_report():
    """Get the detailed report for the eth-infinitism/account-abstraction analysis"""
    print("Retrieving detailed report for eth-infinitism/account-abstraction analysis...")
    
    # We'll use the job ID from the previous analysis
    # In a real scenario, you would store this job ID or retrieve it from the API
    job_id = "066481ac-9cda-42da-88d4-1a75a8515b90"  # This was from our previous run
    
    try:
        # Get results
        results_response = requests.get(f'http://localhost:5000/api/results/{job_id}')
        if results_response.status_code == 200:
            results_data = results_response.json()
            print("\n" + "="*80)
            print("DETAILED SECURITY ANALYSIS REPORT")
            print("="*80)
            print(f"Repository: eth-infinitism/account-abstraction")
            print(f"Job ID: {job_id}")
            print(f"Analysis Date: {results_data.get('timestamp', 'N/A')}")
            print("="*80)
            
            # Summary
            summary = results_data.get('summary', {})
            print(f"\nSUMMARY:")
            print(f"  Total Files Analyzed: {summary.get('total_files', 0)}")
            print(f"  Files Processed: {summary.get('files_analyzed', 0)}")
            print(f"  Vulnerabilities Found: {summary.get('vulnerabilities_found', 0)}")
            
            # Severity breakdown
            severity_breakdown = summary.get('severity_breakdown', {})
            print(f"\nSEVERITY BREAKDOWN:")
            for severity, count in severity_breakdown.items():
                if count > 0:
                    print(f"  {severity.capitalize()}: {count}")
            
            # Overall assessment
            overall_assessment = results_data.get('overall_assessment', {})
            print(f"\nOVERALL ASSESSMENT:")
            print(f"  Risk Level: {overall_assessment.get('risk_level', 'N/A')}")
            print(f"  Summary: {overall_assessment.get('summary', 'N/A')}")
            
            # Recommendations
            recommendations = overall_assessment.get('recommendations', [])
            if recommendations:
                print(f"\nRECOMMENDATIONS:")
                for i, rec in enumerate(recommendations, 1):
                    print(f"  {i}. {rec}")
            
            # Detailed vulnerabilities
            vulnerabilities = results_data.get('vulnerabilities', [])
            if vulnerabilities:
                print(f"\nDETAILED VULNERABILITIES:")
                print("-" * 80)
                for i, vuln in enumerate(vulnerabilities, 1):
                    print(f"\n{i}. {vuln.get('name', 'Unknown Vulnerability')}")
                    print(f"   Type: {vuln.get('type', 'N/A')}")
                    print(f"   Severity: {vuln.get('severity', 'N/A')}")
                    print(f"   CWE: {vuln.get('cwe', 'N/A')}")
                    print(f"   File: {vuln.get('file_path', 'N/A')}")
                    print(f"   Line: {vuln.get('line_number', 'N/A')}")
                    print(f"   Confidence: {vuln.get('confidence', 0):.2f}")
                    print(f"   Description: {vuln.get('description', 'N/A')}")
                    
                    # AI-enhanced details
                    if vuln.get('detailed_description'):
                        print(f"   Detailed Analysis: {vuln.get('detailed_description', '')}")
                    
                    if vuln.get('attack_scenarios'):
                        print(f"   Attack Scenarios: {vuln.get('attack_scenarios', '')}")
                    
                    if vuln.get('recommended_fix'):
                        print(f"   Recommended Fix: {vuln.get('recommended_fix', '')}")
                    
                    if vuln.get('poc_code'):
                        print(f"   Proof of Concept: {vuln.get('poc_code', '')}")
                    
                    print("-" * 80)
            else:
                print("\nNo vulnerabilities found.")
                
            # Save report to file
            with open('security_analysis_report.json', 'w') as f:
                json.dump(results_data, f, indent=2)
            print(f"\nReport saved to security_analysis_report.json")
            
        else:
            print(f"Error retrieving results: {results_response.text}")
            
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the SMCVD service. Is it running?")
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    get_detailed_report()