from flask import Blueprint, request, jsonify
from flask_cors import cross_origin

# Try to import rate limiting
try:
    from src.middleware.rate_limiting import rate_limit
except ImportError:
    def rate_limit(*args, **kwargs):
        def decorator(f):
            return f
        return decorator
from src.services.github_service import GitHubService


github_bp = Blueprint('github', __name__)


@github_bp.route('/github/validate', methods=['POST'])
@cross_origin()
@rate_limit(limit=15, window=60)  # 15 validations per minute
def validate_github_url():
    try:
        data = request.get_json()
        if not data or 'url' not in data:
            return jsonify({'error': 'GitHub URL is required'}), 400

        github_url = data['url'].strip()
        if not github_url:
            return jsonify({'error': 'GitHub URL cannot be empty'}), 400

        github_service = GitHubService()
        is_valid, message = github_service.validate_github_url(github_url)

        if is_valid:
            try:
                repo_info = github_service.get_repository_info(github_url)
                solidity_files = github_service.find_solidity_files(github_url)
                return jsonify({
                    'valid': True,
                    'message': message,
                    'repository': repo_info,
                    'solidity_files': len(solidity_files),
                    'files': solidity_files[:10]
                }), 200
            except Exception as e:
                return jsonify({
                    'valid': True,
                    'message': message,
                    'repository': None,
                    'solidity_files': 0,
                    'files': [],
                    'warning': f'Could not fetch repository details: {str(e)}'
                }), 200
        else:
            return jsonify({'valid': False, 'message': message}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@github_bp.route('/github/info', methods=['POST'])
@cross_origin()
def get_repository_info():
    try:
        data = request.get_json()
        if not data or 'url' not in data:
            return jsonify({'error': 'GitHub URL is required'}), 400

        github_url = data['url'].strip()
        github_service = GitHubService()

        is_valid, message = github_service.validate_github_url(github_url)
        if not is_valid:
            return jsonify({'error': message}), 400

        repo_info = github_service.get_repository_info(github_url)
        solidity_files = github_service.find_solidity_files(github_url)
        return jsonify({
            'repository': repo_info,
            'solidity_files': {'count': len(solidity_files), 'files': solidity_files}
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@github_bp.route('/github/files', methods=['POST'])
@cross_origin()
def get_solidity_files():
    try:
        data = request.get_json()
        if not data or 'url' not in data:
            return jsonify({'error': 'GitHub URL is required'}), 400

        github_url = data['url'].strip()
        github_service = GitHubService()
        solidity_files = github_service.find_solidity_files(github_url)
        return jsonify({'files': solidity_files, 'count': len(solidity_files)}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@github_bp.route('/github/file-content', methods=['POST'])
@cross_origin()
def get_file_content():
    try:
        data = request.get_json()
        if not data or 'url' not in data or 'file_path' not in data:
            return jsonify({'error': 'GitHub URL and file path are required'}), 400

        github_url = data['url'].strip()
        file_path = data['file_path'].strip()
        github_service = GitHubService()
        file_content = github_service.get_file_content(github_url, file_path)
        return jsonify({'file_path': file_path, 'content': file_content, 'size': len(file_content)}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


