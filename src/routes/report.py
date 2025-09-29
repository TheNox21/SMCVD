from flask import Blueprint, request, jsonify, send_file
from flask_cors import cross_origin
import io

# Try to import rate limiting
try:
    from src.middleware.rate_limiting import rate_limit
except ImportError:
    def rate_limit(*args, **kwargs):
        def decorator(f):
            return f
        return decorator

from src.services.report_service import ReportService
from src.routes.analysis import analysis_jobs
from src.routes.report_utils import markdown_to_html  # will add helper


report_bp = Blueprint('report', __name__)


@report_bp.route('/report/generate', methods=['POST'])
@cross_origin()
@rate_limit(limit=10, window=60)  # 10 reports per minute
def generate_report():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400

        vulnerabilities = []
        if 'job_id' in data:
            job_id = data['job_id']
            if job_id not in analysis_jobs:
                return jsonify({'error': 'Analysis job not found'}), 404
            job = analysis_jobs[job_id]
            if job['status'] != 'completed':
                return jsonify({'error': 'Analysis not completed yet'}), 400
            vulnerabilities = job.get('vulnerabilities', [])
        elif 'vulnerabilities' in data:
            vulnerabilities = data['vulnerabilities']
        else:
            return jsonify({'error': 'Either job_id or vulnerabilities must be provided'}), 400

        if not vulnerabilities:
            return jsonify({'error': 'No vulnerabilities found to report'}), 400

        report_config = data.get('config', {})
        report_service = ReportService()
        report_result = report_service.generate_bug_bounty_report(vulnerabilities, report_config)
        return jsonify({
            'report_id': report_result['metadata']['report_id'],
            'markdown': report_result['markdown'],
            'metadata': report_result['metadata'],
            'summary': report_result['summary']
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@report_bp.route('/report/download', methods=['POST'])
@cross_origin()
def download_report():
    try:
        data = request.get_json()
        if not data or 'markdown' not in data:
            return jsonify({'error': 'Report markdown content is required'}), 400
        markdown_content = data['markdown']
        format_type = data.get('format', 'markdown').lower()
        filename = data.get('filename', 'security_report')

        if format_type == 'markdown':
            file_content = markdown_content.encode('utf-8')
            file_obj = io.BytesIO(file_content)
            return send_file(file_obj, as_attachment=True, download_name=f"{filename}.md", mimetype='text/markdown')
        elif format_type == 'pdf':
            try:
                import weasyprint
                html_content = markdown_to_html(markdown_content)
                pdf_file = io.BytesIO()
                weasyprint.HTML(string=html_content).write_pdf(pdf_file)
                pdf_file.seek(0)
                return send_file(pdf_file, as_attachment=True, download_name=f"{filename}.pdf", mimetype='application/pdf')
            except ImportError:
                return jsonify({'error': 'PDF generation not available'}), 400
        else:
            return jsonify({'error': 'Unsupported format. Use "markdown" or "pdf"'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@report_bp.route('/report/preview', methods=['POST'])
@cross_origin()
def preview_report():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        vulnerabilities = data.get('vulnerabilities', [])
        config = data.get('config', {})
        if not vulnerabilities:
            return jsonify({'error': 'No vulnerabilities provided'}), 400
        preview_vulns = vulnerabilities[:3]
        report_service = ReportService()
        report_result = report_service.generate_bug_bounty_report(preview_vulns, config)
        markdown_lines = report_result['markdown'].split('\n')
        preview_lines = markdown_lines[:100]
        if len(markdown_lines) > 100:
            preview_lines.append('\n... (truncated for preview) ...')
        preview_markdown = '\n'.join(preview_lines)
        return jsonify({'preview': preview_markdown, 'metadata': report_result['metadata'], 'summary': report_result['summary'], 'truncated': len(markdown_lines) > 100}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@report_bp.route('/report/templates', methods=['GET'])
@cross_origin()
def get_report_templates():
    return jsonify({'templates': [
        {'id': 'professional', 'name': 'Professional', 'description': 'Comprehensive professional bug bounty report with all sections'},
        {'id': 'detailed', 'name': 'Detailed Technical', 'description': 'In-depth technical analysis with extended vulnerability details'},
        {'id': 'concise', 'name': 'Concise', 'description': 'Brief summary report focusing on key findings and actions'}
    ], 'default': 'professional'}), 200


@report_bp.route('/report/config', methods=['GET'])
@cross_origin()
def get_report_config():
    return jsonify({'options': {
        'templates': ['professional', 'detailed', 'concise'],
        'formats': ['markdown', 'pdf'],
        'sections': {
            'executive_summary': {'name': 'Executive Summary', 'description': 'High-level overview and key findings', 'default': True},
            'vulnerability_details': {'name': 'Vulnerability Details', 'description': 'Detailed analysis of each vulnerability', 'default': True},
            'proof_of_concept': {'name': 'Proof of Concept', 'description': 'Working exploit demonstrations', 'default': True},
            'mitigation': {'name': 'Mitigation Recommendations', 'description': 'Security recommendations and fixes', 'default': True},
            'appendix': {'name': 'Technical Appendix', 'description': 'Methodology and reference information', 'default': True}
        }
    }}), 200


