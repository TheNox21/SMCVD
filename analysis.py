from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
import os
import tempfile
import shutil
from src.services.github_service import GitHubService
from src.services.analysis_service import AnalysisService
from src.services.ai_service import AIService
import uuid
import threading
import time

analysis_bp = Blueprint('analysis', __name__)

# In-memory storage for analysis jobs (in production, use Redis or database)
analysis_jobs = {}

@analysis_bp.route('/analyze', methods=['POST'])
@cross_origin()
def start_analysis():
    """Start smart contract analysis from GitHub repository or uploaded files"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Generate unique job ID
        job_id = str(uuid.uuid4())
        
        # Initialize job status
        analysis_jobs[job_id] = {
            'status': 'initializing',
            'progress': 0,
            'message': 'Starting analysis...',
            'vulnerabilities': [],
            'files_analyzed': 0,
            'total_files': 0,
            'created_at': time.time()
        }
        
        # Start analysis in background thread
        if 'github_url' in data:
            thread = threading.Thread(target=analyze_github_repo, args=(job_id, data['github_url']))
        elif 'files' in data:
            thread = threading.Thread(target=analyze_uploaded_files, args=(job_id, data['files']))
        else:
            return jsonify({'error': 'Either github_url or files must be provided'}), 400
        
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'job_id': job_id,
            'status': 'started',
            'message': 'Analysis started successfully'
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@analysis_bp.route('/status/<job_id>', methods=['GET'])
@cross_origin()
def get_analysis_status(job_id):
    """Get analysis status and progress"""
    try:
        if job_id not in analysis_jobs:
            return jsonify({'error': 'Job not found'}), 404
        
        job = analysis_jobs[job_id]
        return jsonify(job), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@analysis_bp.route('/results/<job_id>', methods=['GET'])
@cross_origin()
def get_analysis_results(job_id):
    """Get complete analysis results"""
    try:
        if job_id not in analysis_jobs:
            return jsonify({'error': 'Job not found'}), 404
        
        job = analysis_jobs[job_id]
        
        if job['status'] != 'completed':
            return jsonify({'error': 'Analysis not completed yet'}), 400
        
        return jsonify({
            'job_id': job_id,
            'vulnerabilities': job['vulnerabilities'],
            'summary': {
                'total_files': job['total_files'],
                'files_analyzed': job['files_analyzed'],
                'vulnerabilities_found': len(job['vulnerabilities']),
                'severity_breakdown': get_severity_breakdown(job['vulnerabilities'])
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def analyze_github_repo(job_id, github_url):
    """Analyze smart contracts from GitHub repository"""
    try:
        # Update status
        analysis_jobs[job_id]['status'] = 'fetching'
        analysis_jobs[job_id]['message'] = 'Fetching repository from GitHub...'
        analysis_jobs[job_id]['progress'] = 10
        
        # Fetch repository
        github_service = GitHubService()
        temp_dir = github_service.clone_repository(github_url)
        
        # Find Solidity files
        analysis_jobs[job_id]['status'] = 'scanning'
        analysis_jobs[job_id]['message'] = 'Scanning for smart contract files...'
        analysis_jobs[job_id]['progress'] = 20
        
        solidity_files = find_solidity_files(temp_dir)
        analysis_jobs[job_id]['total_files'] = len(solidity_files)
        
        if not solidity_files:
            analysis_jobs[job_id]['status'] = 'completed'
            analysis_jobs[job_id]['message'] = 'No Solidity files found in repository'
            analysis_jobs[job_id]['progress'] = 100
            return
        
        # Analyze files
        analyze_files(job_id, solidity_files)
        
        # Cleanup
        shutil.rmtree(temp_dir, ignore_errors=True)
        
    except Exception as e:
        analysis_jobs[job_id]['status'] = 'error'
        analysis_jobs[job_id]['message'] = f'Error: {str(e)}'
        analysis_jobs[job_id]['progress'] = 0

def analyze_uploaded_files(job_id, files):
    """Analyze uploaded smart contract files"""
    try:
        # Create temporary directory for uploaded files
        temp_dir = tempfile.mkdtemp()
        
        # Save uploaded files
        analysis_jobs[job_id]['status'] = 'processing'
        analysis_jobs[job_id]['message'] = 'Processing uploaded files...'
        analysis_jobs[job_id]['progress'] = 10
        
        file_paths = []
        for file_data in files:
            file_path = os.path.join(temp_dir, file_data['name'])
            with open(file_path, 'w') as f:
                f.write(file_data['content'])
            file_paths.append(file_path)
        
        analysis_jobs[job_id]['total_files'] = len(file_paths)
        
        # Analyze files
        analyze_files(job_id, file_paths)
        
        # Cleanup
        shutil.rmtree(temp_dir, ignore_errors=True)
        
    except Exception as e:
        analysis_jobs[job_id]['status'] = 'error'
        analysis_jobs[job_id]['message'] = f'Error: {str(e)}'
        analysis_jobs[job_id]['progress'] = 0

def analyze_files(job_id, file_paths):
    """Analyze list of Solidity files"""
    try:
        analysis_service = AnalysisService()
        ai_service = AIService()
        
        total_files = len(file_paths)
        vulnerabilities = []
        
        for i, file_path in enumerate(file_paths):
            # Update progress
            progress = 30 + (i / total_files) * 50  # 30-80% for file analysis
            analysis_jobs[job_id]['progress'] = int(progress)
            analysis_jobs[job_id]['message'] = f'Analyzing {os.path.basename(file_path)}...'
            analysis_jobs[job_id]['files_analyzed'] = i + 1
            
            # Read file content
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Static analysis
            file_vulnerabilities = analysis_service.analyze_contract(content, file_path)
            
            # AI enhancement for each vulnerability
            for vuln in file_vulnerabilities:
                enhanced_vuln = ai_service.enhance_vulnerability(vuln, content)
                vulnerabilities.append(enhanced_vuln)
        
        # Final AI analysis
        analysis_jobs[job_id]['status'] = 'ai_analysis'
        analysis_jobs[job_id]['message'] = 'Running AI-powered analysis...'
        analysis_jobs[job_id]['progress'] = 85
        
        # Get overall assessment from AI
        overall_assessment = ai_service.get_overall_assessment(vulnerabilities)
        
        # Complete analysis
        analysis_jobs[job_id]['status'] = 'completed'
        analysis_jobs[job_id]['message'] = 'Analysis completed successfully'
        analysis_jobs[job_id]['progress'] = 100
        analysis_jobs[job_id]['vulnerabilities'] = vulnerabilities
        analysis_jobs[job_id]['overall_assessment'] = overall_assessment
        
    except Exception as e:
        analysis_jobs[job_id]['status'] = 'error'
        analysis_jobs[job_id]['message'] = f'Analysis error: {str(e)}'
        analysis_jobs[job_id]['progress'] = 0

def find_solidity_files(directory):
    """Find all Solidity files in directory"""
    solidity_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.sol'):
                solidity_files.append(os.path.join(root, file))
    return solidity_files

def get_severity_breakdown(vulnerabilities):
    """Get breakdown of vulnerabilities by severity"""
    breakdown = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0, 'info': 0}
    for vuln in vulnerabilities:
        severity = vuln.get('severity', 'info').lower()
        if severity in breakdown:
            breakdown[severity] += 1
    return breakdown

