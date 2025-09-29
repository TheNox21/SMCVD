from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
import os
import tempfile
import shutil
import uuid
import threading
import time

# Try to import new components, fallback if not available
try:
    from src.middleware.rate_limiting import rate_limit
    from src.models.job import JobStorage
    use_job_storage = True
except ImportError:
    # Fallback decorator that does nothing
    def rate_limit(*args, **kwargs):
        def decorator(f):
            return f
        return decorator
    use_job_storage = False

from src.services.github_service import GitHubService
from src.services.analysis_service import AnalysisService
from src.services.ai_service import AIService


analysis_bp = Blueprint('analysis', __name__)

# Initialize job storage
if use_job_storage:
    try:
        job_storage = JobStorage()
    except Exception as e:
        print(f"Warning: Could not initialize job storage: {e}")
        job_storage = None
else:
    job_storage = None

# In-memory storage for analysis jobs (fallback or additional storage)
analysis_jobs = {}


def update_job_status(job_id, updates):
    """Update job status in both memory and persistent storage"""
    if job_id in analysis_jobs:
        analysis_jobs[job_id].update(updates)
        
    if job_storage:
        try:
            # Get current job data and update it
            current_data = job_storage.get_job(job_id) or analysis_jobs.get(job_id, {})
            current_data.update(updates)
            job_storage.save_job(job_id, current_data)
        except Exception as e:
            print(f"Warning: Could not update persistent storage: {e}")


@analysis_bp.route('/analyze', methods=['POST'])
@cross_origin()
@rate_limit(limit=5, window=60)  # 5 requests per minute
def start_analysis():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        job_id = str(uuid.uuid4())
        job_data = {
            'status': 'initializing',
            'progress': 0,
            'message': 'Starting analysis...',
            'vulnerabilities': [],
            'files_analyzed': 0,
            'total_files': 0,
            'created_at': time.time()
        }
        
        # Store in both memory and persistent storage
        analysis_jobs[job_id] = job_data
        if job_storage:
            try:
                job_storage.save_job(job_id, job_data)
            except Exception as e:
                print(f"Warning: Could not save job to persistent storage: {e}")

        # Optional program scope passed by client to tailor analysis
        analysis_jobs[job_id]['program_scope'] = data.get('program_scope')

        if 'github_url' in data:
            thread = threading.Thread(target=analyze_github_repo, args=(job_id, data['github_url']))
        elif 'files' in data:
            thread = threading.Thread(target=analyze_uploaded_files, args=(job_id, data['files']))
        else:
            return jsonify({'error': 'Either github_url or files must be provided'}), 400

        thread.daemon = True
        thread.start()

        return jsonify({'job_id': job_id, 'status': 'started', 'message': 'Analysis started successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@analysis_bp.route('/status/<job_id>', methods=['GET'])
@cross_origin()
def get_analysis_status(job_id):
    try:
        # Try persistent storage first, then memory
        job_data = None
        if job_storage:
            try:
                job_data = job_storage.get_job(job_id)
            except Exception:
                pass
        
        if not job_data and job_id in analysis_jobs:
            job_data = analysis_jobs[job_id]
        
        if not job_data:
            return jsonify({'error': 'Job not found'}), 404
            
        return jsonify(job_data), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@analysis_bp.route('/results/<job_id>', methods=['GET'])
@cross_origin()
def get_analysis_results(job_id):
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
            },
            'overall_assessment': job.get('overall_assessment')
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def analyze_github_repo(job_id, github_url):
    try:
        update_job_status(job_id, {
            'status': 'fetching',
            'message': 'Fetching repository from GitHub...',
            'progress': 10
        })

        github_service = GitHubService()
        temp_dir = github_service.clone_repository(github_url)

        update_job_status(job_id, {
            'status': 'scanning',
            'message': 'Scanning for smart contract files...',
            'progress': 20
        })

        solidity_files = find_solidity_files(temp_dir)
        update_job_status(job_id, {'total_files': len(solidity_files)})

        if not solidity_files:
            update_job_status(job_id, {
                'status': 'completed',
                'message': 'No Solidity files found in repository',
                'progress': 100
            })
            return

        analyze_files(job_id, solidity_files)
        shutil.rmtree(temp_dir, ignore_errors=True)
    except Exception as e:
        update_job_status(job_id, {
            'status': 'error',
            'message': f'Error: {str(e)}',
            'progress': 0
        })


def analyze_uploaded_files(job_id, files):
    try:
        temp_dir = tempfile.mkdtemp()
        update_job_status(job_id, {
            'status': 'processing',
            'message': 'Processing uploaded files...',
            'progress': 10
        })

        file_paths = []
        for file_data in files:
            file_path = os.path.join(temp_dir, file_data['name'])
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(file_data['content'])
            file_paths.append(file_path)

        update_job_status(job_id, {'total_files': len(file_paths)})
        analyze_files(job_id, file_paths)
        shutil.rmtree(temp_dir, ignore_errors=True)
    except Exception as e:
        update_job_status(job_id, {
            'status': 'error',
            'message': f'Error: {str(e)}',
            'progress': 0
        })


def analyze_files(job_id, file_paths):
    try:
        analysis_service = AnalysisService()
        ai_service = AIService()
        total_files = len(file_paths)
        vulnerabilities = []
        program_scope = analysis_jobs.get(job_id, {}).get('program_scope')

        for i, file_path in enumerate(file_paths):
            progress = 30 + (i / total_files) * 50
            update_job_status(job_id, {
                'progress': int(progress),
                'message': f'Analyzing {os.path.basename(file_path)}...',
                'files_analyzed': i + 1
            })

            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            file_vulnerabilities = analysis_service.analyze_contract(content, file_path)
            # Apply program scope filtering/downgrading
            if program_scope:
                file_vulnerabilities = analysis_service.apply_program_scope(file_vulnerabilities, program_scope)

            enable_ai = os.getenv('ENABLE_AI', 'true').lower() == 'true'
            for vuln in file_vulnerabilities:
                if enable_ai:
                    enhanced_vuln = ai_service.enhance_vulnerability(vuln, content, program_scope=program_scope)
                else:
                    enhanced_vuln = vuln
                vulnerabilities.append(enhanced_vuln)

        update_job_status(job_id, {
            'status': 'analysis',
            'message': 'Running advanced analysis...',
            'progress': 85
        })

        enable_ai = os.getenv('ENABLE_AI', 'true').lower() == 'true'
        if enable_ai:
            overall_assessment = ai_service.get_overall_assessment(vulnerabilities, program_scope=program_scope)
        else:
            overall_assessment = {
                'risk_level': 'medium' if vulnerabilities else 'low',
                'summary': 'Static analysis findings summary.',
                'recommendations': ['Review identified issues', 'Add tests', 'Follow best practices']
            }

        update_job_status(job_id, {
            'status': 'completed',
            'message': 'Analysis completed successfully',
            'progress': 100,
            'vulnerabilities': vulnerabilities,
            'overall_assessment': overall_assessment
        })
    except Exception as e:
        update_job_status(job_id, {
            'status': 'error',
            'message': f'Analysis error: {str(e)}',
            'progress': 0
        })


def find_solidity_files(directory):
    solidity_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.sol'):
                solidity_files.append(os.path.join(root, file))
    return solidity_files


def get_severity_breakdown(vulnerabilities):
    breakdown = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0, 'info': 0}
    for vuln in vulnerabilities:
        severity = vuln.get('severity', 'info').lower()
        if severity in breakdown:
            breakdown[severity] += 1
    return breakdown


