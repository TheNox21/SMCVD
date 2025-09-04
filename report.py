from flask import Blueprint, request, jsonify, send_file
from flask_cors import cross_origin
import os
import tempfile
import uuid
from src.services.report_service import ReportService
from src.routes.analysis import analysis_jobs
import io

report_bp = Blueprint('report', __name__)

@report_bp.route('/report/generate', methods=['POST'])
@cross_origin()
def generate_report():
    """Generate bug bounty report from analysis results"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Get vulnerabilities from job ID or direct input
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
        
        # Report configuration
        report_config = data.get('config', {})
        
        # Generate report
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
    """Download report in specified format"""
    try:
        data = request.get_json()
        
        if not data or 'markdown' not in data:
            return jsonify({'error': 'Report markdown content is required'}), 400
        
        markdown_content = data['markdown']
        format_type = data.get('format', 'markdown').lower()
        filename = data.get('filename', 'security_report')
        
        if format_type == 'markdown':
            # Return markdown file
            file_content = markdown_content.encode('utf-8')
            file_obj = io.BytesIO(file_content)
            
            return send_file(
                file_obj,
                as_attachment=True,
                download_name=f"{filename}.md",
                mimetype='text/markdown'
            )
        
        elif format_type == 'pdf':
            # Convert markdown to PDF (requires additional setup)
            try:
                import weasyprint
                
                # Convert markdown to HTML first (basic conversion)
                html_content = markdown_to_html(markdown_content)
                
                # Generate PDF
                pdf_file = io.BytesIO()
                weasyprint.HTML(string=html_content).write_pdf(pdf_file)
                pdf_file.seek(0)
                
                return send_file(
                    pdf_file,
                    as_attachment=True,
                    download_name=f"{filename}.pdf",
                    mimetype='application/pdf'
                )
                
            except ImportError:
                return jsonify({'error': 'PDF generation not available'}), 400
        
        else:
            return jsonify({'error': 'Unsupported format. Use "markdown" or "pdf"'}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@report_bp.route('/report/preview', methods=['POST'])
@cross_origin()
def preview_report():
    """Generate report preview without full processing"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        vulnerabilities = data.get('vulnerabilities', [])
        config = data.get('config', {})
        
        if not vulnerabilities:
            return jsonify({'error': 'No vulnerabilities provided'}), 400
        
        # Generate preview with limited vulnerabilities
        preview_vulns = vulnerabilities[:3]  # Show only first 3 for preview
        
        report_service = ReportService()
        report_result = report_service.generate_bug_bounty_report(preview_vulns, config)
        
        # Truncate markdown for preview
        markdown_lines = report_result['markdown'].split('\n')
        preview_lines = markdown_lines[:100]  # First 100 lines
        
        if len(markdown_lines) > 100:
            preview_lines.append('\n... (truncated for preview) ...')
        
        preview_markdown = '\n'.join(preview_lines)
        
        return jsonify({
            'preview': preview_markdown,
            'metadata': report_result['metadata'],
            'summary': report_result['summary'],
            'truncated': len(markdown_lines) > 100
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@report_bp.route('/report/templates', methods=['GET'])
@cross_origin()
def get_report_templates():
    """Get available report templates"""
    return jsonify({
        'templates': [
            {
                'id': 'professional',
                'name': 'Professional',
                'description': 'Comprehensive professional bug bounty report with all sections'
            },
            {
                'id': 'detailed',
                'name': 'Detailed Technical',
                'description': 'In-depth technical analysis with extended vulnerability details'
            },
            {
                'id': 'concise',
                'name': 'Concise',
                'description': 'Brief summary report focusing on key findings and actions'
            }
        ],
        'default': 'professional'
    }), 200

@report_bp.route('/report/config', methods=['GET'])
@cross_origin()
def get_report_config():
    """Get report configuration options"""
    return jsonify({
        'options': {
            'templates': ['professional', 'detailed', 'concise'],
            'formats': ['markdown', 'pdf'],
            'sections': {
                'executive_summary': {
                    'name': 'Executive Summary',
                    'description': 'High-level overview and key findings',
                    'default': True
                },
                'vulnerability_details': {
                    'name': 'Vulnerability Details',
                    'description': 'Detailed analysis of each vulnerability',
                    'default': True
                },
                'proof_of_concept': {
                    'name': 'Proof of Concept',
                    'description': 'Working exploit demonstrations',
                    'default': True
                },
                'mitigation': {
                    'name': 'Mitigation Recommendations',
                    'description': 'Security recommendations and fixes',
                    'default': True
                },
                'appendix': {
                    'name': 'Technical Appendix',
                    'description': 'Methodology and reference information',
                    'default': True
                }
            }
        }
    }), 200

def markdown_to_html(markdown_content: str) -> str:
    """Convert markdown to HTML (basic implementation)"""
    # This is a very basic markdown to HTML converter
    # In production, use a proper markdown library like python-markdown
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Security Report</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }}
            h1 {{ color: #333; border-bottom: 2px solid #333; }}
            h2 {{ color: #666; border-bottom: 1px solid #666; }}
            h3 {{ color: #888; }}
            code {{ background-color: #f4f4f4; padding: 2px 4px; border-radius: 3px; }}
            pre {{ background-color: #f4f4f4; padding: 10px; border-radius: 5px; overflow-x: auto; }}
            .severity-critical {{ color: #d32f2f; font-weight: bold; }}
            .severity-high {{ color: #f57c00; font-weight: bold; }}
            .severity-medium {{ color: #fbc02d; font-weight: bold; }}
            .severity-low {{ color: #388e3c; font-weight: bold; }}
        </style>
    </head>
    <body>
    """
    
    # Basic markdown processing
    lines = markdown_content.split('\n')
    for line in lines:
        line = line.strip()
        
        if line.startswith('# '):
            html_content += f"<h1>{line[2:]}</h1>\n"
        elif line.startswith('## '):
            html_content += f"<h2>{line[3:]}</h2>\n"
        elif line.startswith('### '):
            html_content += f"<h3>{line[4:]}</h3>\n"
        elif line.startswith('**') and line.endswith('**'):
            html_content += f"<p><strong>{line[2:-2]}</strong></p>\n"
        elif line.startswith('- '):
            html_content += f"<li>{line[2:]}</li>\n"
        elif line.startswith('```'):
            html_content += "<pre><code>" if not line.endswith('```') else "</code></pre>\n"
        elif line:
            html_content += f"<p>{line}</p>\n"
        else:
            html_content += "<br>\n"
    
    html_content += """
    </body>
    </html>
    """
    
    return html_content

