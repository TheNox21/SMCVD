import requests
import json

def get_readable_report():
    """Get a readable report for the eth-infinitism/account-abstraction analysis"""
    print("Retrieving readable report for eth-infinitism/account-abstraction analysis...")
    
    # We'll use the job ID from the previous analysis
    job_id = "066481ac-9cda-42da-88d4-1a75a8515b90"  # This was from our previous run
    
    try:
        # Get results
        results_response = requests.get(f'http://localhost:5000/api/results/{job_id}')
        if results_response.status_code == 200:
            results_data = results_response.json()
            
            # Create a readable report
            report_lines = []
            report_lines.append("SMART CONTRACT SECURITY ANALYSIS REPORT")
            report_lines.append("=" * 50)
            report_lines.append(f"Repository: eth-infinitism/account-abstraction")
            report_lines.append(f"Job ID: {job_id}")
            report_lines.append("")
            
            # Summary
            summary = results_data.get('summary', {})
            report_lines.append("EXECUTIVE SUMMARY")
            report_lines.append("-" * 30)
            report_lines.append(f"Total Files Analyzed: {summary.get('total_files', 0)}")
            report_lines.append(f"Files Processed: {summary.get('files_analyzed', 0)}")
            report_lines.append(f"Vulnerabilities Found: {summary.get('vulnerabilities_found', 0)}")
            report_lines.append("")
            
            # Overall assessment
            overall_assessment = results_data.get('overall_assessment', {})
            report_lines.append("OVERALL ASSESSMENT")
            report_lines.append("-" * 30)
            report_lines.append(f"Risk Level: {overall_assessment.get('risk_level', 'N/A')}")
            report_lines.append(f"Summary: {overall_assessment.get('summary', 'N/A')}")
            report_lines.append("")
            
            # Recommendations
            recommendations = overall_assessment.get('recommendations', [])
            if recommendations:
                report_lines.append("RECOMMENDATIONS")
                report_lines.append("-" * 30)
                for i, rec in enumerate(recommendations, 1):
                    report_lines.append(f"{i}. {rec}")
                report_lines.append("")
            
            # Detailed vulnerabilities
            vulnerabilities = results_data.get('vulnerabilities', [])
            if vulnerabilities:
                report_lines.append("IDENTIFIED VULNERABILITIES")
                report_lines.append("-" * 30)
                for i, vuln in enumerate(vulnerabilities, 1):
                    report_lines.append(f"{i}. {vuln.get('name', 'Unknown Vulnerability')}")
                    report_lines.append(f"   Severity: {vuln.get('severity', 'N/A').upper()}")
                    report_lines.append(f"   File: {vuln.get('file_path', 'N/A')} (Line {vuln.get('line_number', 'N/A')})")
                    report_lines.append(f"   Confidence: {vuln.get('confidence', 0):.1f}")
                    report_lines.append(f"   Description: {vuln.get('description', 'N/A')}")
                    
                    # AI-enhanced details if available
                    if vuln.get('detailed_description'):
                        report_lines.append(f"   Analysis: {vuln.get('detailed_description', '')[:200]}...")
                    
                    report_lines.append("")
            
            # Print the report
            for line in report_lines:
                print(line)
            
            # Save to file
            with open('readable_security_report.txt', 'w', encoding='utf-8') as f:
                for line in report_lines:
                    f.write(line + '\n')
            print(f"\nReadable report saved to readable_security_report.txt")
            
        else:
            print(f"Error retrieving results: {results_response.text}")
            
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the SMCVD service. Is it running?")
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    get_readable_report()