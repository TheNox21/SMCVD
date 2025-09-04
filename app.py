from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import time
import uuid
import re
from datetime import datetime

app = Flask(__name__)
CORS(app)

# In-memory storage for demo
analysis_jobs = {}
sample_vulnerabilities = []

def create_sample_vulnerabilities():
    """Create sample vulnerabilities for demonstration"""
    return [
        {
            'id': 'vuln_1',
            'name': 'Reentrancy Vulnerability',
            'severity': 'critical',
            'type': 'reentrancy',
            'cwe': 'CWE-362',
            'description': 'The contract is vulnerable to reentrancy attacks due to external calls before state changes.',
            'impact': 'Attackers can drain contract funds by repeatedly calling the vulnerable function.',
            'file_path': 'contracts/VulnerableContract.sol',
            'line_number': 45,
            'function_name': 'withdraw',
            'line_content': 'msg.sender.call{value: amount}("");',
            'confidence': 0.95,
            'mitigation': 'Use the checks-effects-interactions pattern and implement reentrancy guards.'
        },
        {
            'id': 'vuln_2',
            'name': 'Integer Overflow',
            'severity': 'high',
            'type': 'integer_overflow',
            'cwe': 'CWE-190',
            'description': 'Arithmetic operations may overflow without proper checks.',
            'impact': 'Could lead to unexpected behavior and potential fund loss.',
            'file_path': 'contracts/Token.sol',
            'line_number': 78,
            'function_name': 'transfer',
            'line_content': 'balances[to] += amount;',
            'confidence': 0.87,
            'mitigation': 'Use SafeMath library or Solidity 0.8+ built-in overflow protection.'
        },
        {
            'id': 'vuln_3',
            'name': 'Access Control Issue',
            'severity': 'medium',
            'type': 'access_control',
            'cwe': 'CWE-284',
            'description': 'Function lacks proper access control modifiers.',
            'impact': 'Unauthorized users may be able to call sensitive functions.',
            'file_path': 'contracts/Governance.sol',
            'line_number': 123,
            'function_name': 'updateSettings',
            'line_content': 'function updateSettings(uint256 newValue) public {',
            'confidence': 0.78,
            'mitigation': 'Add appropriate access control modifiers like onlyOwner or role-based access.'
        }
    ]

@app.route('/')
def index():
    return jsonify({
        'message': 'Smart Contract Security Analyzer API',
        'version': '1.0.0',
        'status': 'running'
    })

@app.route('/api/github/validate', methods=['POST'])
def validate_github():
    """Validate GitHub repository URL"""
    data = request.get_json()
    url = data.get('url', '')
    
    # Simple URL validation
    github_pattern = r'https://github\.com/[\w\-\.]+/[\w\-\.]+'
    if not re.match(github_pattern, url):
        return jsonify({
            'valid': False,
            'message': 'Invalid GitHub repository URL format'
        }), 400
    
    # Mock validation response
    return jsonify({
        'valid': True,
        'repository': {
            'full_name': url.split('/')[-2] + '/' + url.split('/')[-1],
            'language': 'Solidity'
        },
        'solidity_files': 5,
        'files': ['Contract1.sol', 'Contract2.sol', 'Token.sol']
    })

@app.route('/api/analyze', methods=['POST'])
def analyze():
    """Start smart contract analysis"""
    data = request.get_json()
    
    job_id = str(uuid.uuid4())[:8]
    
    # Initialize job
    analysis_jobs[job_id] = {
        'id': job_id,
        'status': 'initializing',
        'progress': 0,
        'message': 'Starting analysis...',
        'created_at': datetime.now().isoformat(),
        'total_files': 0,
        'files_analyzed': 0,
        'vulnerabilities': []
    }
    
    return jsonify({
        'job_id': job_id,
        'status': 'started',
        'message': 'Analysis job created successfully'
    })

@app.route('/api/status/<job_id>')
def get_status(job_id):
    """Get analysis job status"""
    if job_id not in analysis_jobs:
        return jsonify({'error': 'Job not found'}), 404
    
    job = analysis_jobs[job_id]
    
    # Simulate progress
    if job['status'] == 'initializing':
        job['status'] = 'fetching'
        job['progress'] = 20
        job['message'] = 'Fetching repository files...'
    elif job['status'] == 'fetching':
        job['status'] = 'scanning'
        job['progress'] = 40
        job['message'] = 'Scanning for smart contracts...'
        job['total_files'] = 5
    elif job['status'] == 'scanning':
        job['status'] = 'processing'
        job['progress'] = 60
        job['message'] = 'Analyzing contract code...'
        job['files_analyzed'] = 3
    elif job['status'] == 'processing':
        job['status'] = 'ai_analysis'
        job['progress'] = 80
        job['message'] = 'Running AI vulnerability detection...'
        job['files_analyzed'] = 5
    elif job['status'] == 'ai_analysis':
        job['status'] = 'completed'
        job['progress'] = 100
        job['message'] = 'Analysis completed successfully'
        job['vulnerabilities'] = create_sample_vulnerabilities()
    
    return jsonify(job)

@app.route('/api/results/<job_id>')
def get_results(job_id):
    """Get analysis results"""
    if job_id not in analysis_jobs:
        return jsonify({'error': 'Job not found'}), 404
    
    job = analysis_jobs[job_id]
    
    if job['status'] != 'completed':
        return jsonify({'error': 'Analysis not completed yet'}), 400
    
    vulnerabilities = job.get('vulnerabilities', [])
    
    # Calculate severity breakdown
    severity_breakdown = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0, 'info': 0}
    for vuln in vulnerabilities:
        severity = vuln.get('severity', 'info').lower()
        if severity in severity_breakdown:
            severity_breakdown[severity] += 1
    
    return jsonify({
        'job_id': job_id,
        'status': job['status'],
        'vulnerabilities': vulnerabilities,
        'summary': {
            'total_files': job.get('total_files', 0),
            'vulnerabilities_found': len(vulnerabilities),
            'severity_breakdown': severity_breakdown
        }
    })

@app.route('/api/report/generate', methods=['POST'])
def generate_report():
    """Generate bug bounty report"""
    data = request.get_json()
    job_id = data.get('job_id')
    config = data.get('config', {})
    
    if job_id and job_id in analysis_jobs:
        vulnerabilities = analysis_jobs[job_id].get('vulnerabilities', [])
    else:
        vulnerabilities = data.get('vulnerabilities', [])
    
    if not vulnerabilities:
        return jsonify({'error': 'No vulnerabilities found'}), 400
    
    # Filter selected vulnerabilities
    selected_ids = config.get('selected_vulnerabilities', [])
    if selected_ids:
        vulnerabilities = [v for v in vulnerabilities if v.get('id') in selected_ids]
    
    # Generate simple markdown report
    report_id = f"SC-{datetime.now().strftime('%Y%m%d')}-{hash(str(vulnerabilities)) % 10000:04d}"
    
    markdown_report = f"""# {config.get('title', 'Smart Contract Security Analysis Report')}

**Report ID:** {report_id}  
**Date:** {datetime.now().strftime('%Y-%m-%d')}  
**Researcher:** {config.get('researcher', 'Security Researcher')}  
**Target Program:** {config.get('target_program', 'Bug Bounty Program')}

---

## Executive Summary

During the security analysis of the smart contract(s), {len(vulnerabilities)} vulnerabilities were identified across different severity levels.

### Severity Breakdown
"""
    
    # Add severity breakdown
    severity_breakdown = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0}
    for vuln in vulnerabilities:
        severity = vuln.get('severity', 'low').lower()
        if severity in severity_breakdown:
            severity_breakdown[severity] += 1
    
    for severity, count in severity_breakdown.items():
        if count > 0:
            markdown_report += f"- **{severity.title()}:** {count}\n"
    
    markdown_report += "\n---\n\n## Vulnerability Details\n\n"
    
    # Add vulnerability details
    for i, vuln in enumerate(vulnerabilities, 1):
        markdown_report += f"""### {i}. {vuln.get('name', 'Unknown Vulnerability')}

**Severity:** {vuln.get('severity', 'medium').title()}  
**CWE:** {vuln.get('cwe', 'N/A')}  
**Location:** {vuln.get('file_path', 'unknown')}:{vuln.get('line_number', 0)} ({vuln.get('function_name', 'unknown')})  
**Confidence:** {int((vuln.get('confidence', 0.5) * 100))}%

#### Description
{vuln.get('description', 'No description available')}

#### Impact
{vuln.get('impact', 'Potential security risk')}

#### Vulnerable Code
```solidity
{vuln.get('line_content', '')}
```

#### Recommended Mitigation
{vuln.get('mitigation', 'Review and secure the vulnerable code')}

---
"""
    
    markdown_report += f"""
## Recommendations

### Immediate Actions Required
- Address {severity_breakdown.get('critical', 0)} critical vulnerabilities immediately
- Prioritize fixing {severity_breakdown.get('high', 0)} high-severity vulnerabilities
- Implement comprehensive testing suite

### Security Best Practices
- Follow secure coding guidelines
- Use static analysis tools in CI/CD pipeline
- Implement proper error handling
- Document security assumptions and requirements

---

*This report was generated on {datetime.now().isoformat()} for security research purposes.*
"""
    
    return jsonify({
        'report_id': report_id,
        'markdown': markdown_report,
        'metadata': {
            'title': config.get('title', 'Smart Contract Security Analysis Report'),
            'researcher': config.get('researcher', 'Security Researcher'),
            'target_program': config.get('target_program', 'Bug Bounty Program'),
            'date': datetime.now().strftime('%Y-%m-%d'),
            'report_id': report_id
        },
        'summary': {
            'total_vulnerabilities': len(vulnerabilities),
            'severity_breakdown': severity_breakdown,
            'risk_level': 'critical' if severity_breakdown.get('critical', 0) > 0 else 'high' if severity_breakdown.get('high', 0) > 0 else 'medium'
        }
    })

@app.route('/api/report/download', methods=['POST'])
def download_report():
    """Download report in specified format"""
    from flask import send_file
    import io
    
    data = request.get_json()
    markdown_content = data.get('markdown', '')
    format_type = data.get('format', 'markdown').lower()
    filename = data.get('filename', 'security_report')
    
    if format_type == 'markdown':
        file_content = markdown_content.encode('utf-8')
        file_obj = io.BytesIO(file_content)
        
        return send_file(
            file_obj,
            as_attachment=True,
            download_name=f"{filename}.md",
            mimetype='text/markdown'
        )
    
    return jsonify({'error': 'Only markdown format supported in demo'}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

