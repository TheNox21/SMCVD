from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
import os
import uuid
from werkzeug.utils import secure_filename


upload_bp = Blueprint('upload', __name__)

ALLOWED_EXTENSIONS = {'.sol', '.solidity'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB per file
MAX_FILES = 20


@upload_bp.route('/upload/validate', methods=['POST'])
@cross_origin()
def validate_files():
    try:
        if 'files' not in request.files:
            return jsonify({'error': 'No files provided'}), 400
        files = request.files.getlist('files')
        if not files:
            return jsonify({'error': 'No files selected'}), 400
        if len(files) > MAX_FILES:
            return jsonify({'error': f'Too many files. Maximum {MAX_FILES} files allowed'}), 400

        validation_results = []
        total_size = 0
        for file in files:
            if file.filename == '':
                continue
            filename = secure_filename(file.filename)
            file_extension = os.path.splitext(filename)[1].lower()
            file_bytes = file.read()
            file_size = len(file_bytes)
            file.seek(0)

            result = {
                'filename': filename,
                'original_filename': file.filename,
                'size': file_size,
                'valid': True,
                'errors': []
            }

            if file_extension not in ALLOWED_EXTENSIONS:
                result['valid'] = False
                result['errors'].append(f'Invalid file type. Only {", ".join(ALLOWED_EXTENSIONS)} files are allowed')
            if file_size > MAX_FILE_SIZE:
                result['valid'] = False
                result['errors'].append(f'File too large. Maximum size is {MAX_FILE_SIZE // (1024*1024)}MB')
            if file_size == 0:
                result['valid'] = False
                result['errors'].append('File is empty')

            total_size += file_size
            validation_results.append(result)

        if total_size > MAX_FILE_SIZE * 5:
            return jsonify({'error': 'Total file size too large', 'max_total_size': MAX_FILE_SIZE * 5}), 400

        valid_files = [r for r in validation_results if r['valid']]
        invalid_files = [r for r in validation_results if not r['valid']]
        return jsonify({'valid_files': len(valid_files), 'invalid_files': len(invalid_files), 'total_size': total_size, 'files': validation_results, 'can_proceed': len(valid_files) > 0}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@upload_bp.route('/upload/process', methods=['POST'])
@cross_origin()
def process_uploaded_files():
    try:
        if 'files' not in request.files:
            return jsonify({'error': 'No files provided'}), 400
        files = request.files.getlist('files')
        if not files:
            return jsonify({'error': 'No files selected'}), 400

        processed_files = []
        upload_id = str(uuid.uuid4())
        for file in files:
            if file.filename == '':
                continue
            filename = secure_filename(file.filename)
            file_extension = os.path.splitext(filename)[1].lower()
            if file_extension not in ALLOWED_EXTENSIONS:
                continue
            try:
                content = file.read().decode('utf-8')
                processed_files.append({'name': filename, 'original_name': file.filename, 'content': content, 'size': len(content), 'type': 'solidity'})
            except UnicodeDecodeError:
                return jsonify({'error': f'File {filename} contains invalid characters. Please ensure it is a valid text file.'}), 400

        if not processed_files:
            return jsonify({'error': 'No valid Solidity files found'}), 400

        return jsonify({'upload_id': upload_id, 'files': processed_files, 'count': len(processed_files), 'total_size': sum(f['size'] for f in processed_files)}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@upload_bp.route('/upload/info', methods=['GET'])
@cross_origin()
def get_upload_info():
    return jsonify({'max_file_size': MAX_FILE_SIZE, 'max_files': MAX_FILES, 'allowed_extensions': list(ALLOWED_EXTENSIONS), 'max_total_size': MAX_FILE_SIZE * 5}), 200


