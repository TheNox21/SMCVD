import re
from typing import List, Dict, Any

def markdown_to_html(markdown_content: str) -> str:
    """Enhanced markdown to HTML conversion with better styling"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Security Analysis Report</title>
        <style>
            body { 
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
                margin: 40px auto; 
                line-height: 1.6; 
                max-width: 1200px;
                color: #333;
            }
            h1 { color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }
            h2 { color: #34495e; border-bottom: 1px solid #bdc3c7; padding-bottom: 5px; margin-top: 30px; }
            h3 { color: #7f8c8d; margin-top: 25px; }
            code { 
                background-color: #f8f9fa; 
                padding: 2px 6px; 
                border-radius: 3px; 
                font-family: 'Monaco', 'Consolas', monospace;
                border: 1px solid #e9ecef;
            }
            pre { 
                background-color: #f8f9fa; 
                padding: 15px; 
                border-radius: 5px; 
                overflow-x: auto;
                border: 1px solid #e9ecef;
            }
            .severity-critical { color: #e74c3c; font-weight: bold; background: #fdf2f2; padding: 2px 6px; border-radius: 3px; }
            .severity-high { color: #e67e22; font-weight: bold; background: #fef9f3; padding: 2px 6px; border-radius: 3px; }
            .severity-medium { color: #f39c12; font-weight: bold; background: #fffbf3; padding: 2px 6px; border-radius: 3px; }
            .severity-low { color: #27ae60; font-weight: bold; background: #f3fdf6; padding: 2px 6px; border-radius: 3px; }
            table {
                border-collapse: collapse;
                width: 100%;
                margin: 20px 0;
            }
            th, td {
                border: 1px solid #ddd;
                padding: 12px;
                text-align: left;
            }
            th {
                background-color: #f2f2f2;
                font-weight: bold;
            }
            .vulnerability-card {
                background: #fff;
                border: 1px solid #e1e5e9;
                border-radius: 6px;
                padding: 20px;
                margin: 15px 0;
                box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            }
        </style>
    </head>
    <body>
    """

    lines = markdown_content.split('\n')
    in_code = False
    in_table = False
    for line in lines:
        original_line = line
        line = line.rstrip()
        
        # Handle code blocks
        if line.startswith('```'):
            if not in_code:
                html_content += "<pre><code>"
                in_code = True
            else:
                html_content += "</code></pre>\n"
                in_code = False
            continue
        
        if in_code:
            html_content += f"{line}\n"
            continue
            
        # Handle tables
        if '|' in line and not line.strip().startswith('#'):
            if not in_table:
                html_content += "<table>\n"
                in_table = True
            
            cells = [cell.strip() for cell in line.split('|')[1:-1]]  # Remove empty first/last
            if all(cell.replace('-', '').replace(' ', '') == '' for cell in cells):  # Header separator
                continue
            
            tag = 'th' if '---' not in original_line and not any('|' in prev for prev in lines[max(0, lines.index(original_line)-3):lines.index(original_line)]) else 'td'
            html_content += "<tr>"
            for cell in cells:
                # Apply severity styling if cell contains severity keywords
                styled_cell = cell
                for severity in ['critical', 'high', 'medium', 'low']:
                    if severity.upper() in cell.upper():
                        styled_cell = f'<span class="severity-{severity}">{cell}</span>'
                        break
                html_content += f"<{tag}>{styled_cell}</{tag}>"
            html_content += "</tr>\n"
            continue
        elif in_table:
            html_content += "</table>\n"
            in_table = False
        
        # Handle headers
        if line.startswith('# '):
            html_content += f"<h1>{line[2:]}</h1>\n"
        elif line.startswith('## '):
            html_content += f"<h2>{line[3:]}</h2>\n"
        elif line.startswith('### '):
            html_content += f"<h3>{line[4:]}</h3>\n"
        elif line.startswith('- '):
            html_content += f"<li>{line[2:]}</li>\n"
        elif line.startswith('* '):
            html_content += f"<li>{line[2:]}</li>\n"
        elif line.strip():
            # Apply inline code styling
            styled_line = re.sub(r'`([^`]+)`', r'<code>\1</code>', line)
            # Apply bold styling
            styled_line = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', styled_line)
            # Apply italic styling
            styled_line = re.sub(r'\*([^*]+)\*', r'<em>\1</em>', styled_line)
            html_content += f"<p>{styled_line}</p>\n"
        else:
            html_content += "<br>\n"

    if in_table:
        html_content += "</table>\n"
        
    html_content += """
    </body>
    </html>
    """
    return html_content


def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe operations"""
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    filename = re.sub(r'\s+', '_', filename)
    return filename[:100]


def format_severity_badge(severity: str) -> str:
    """Format severity as colored badge"""
    severity = severity.lower()
    badges = {
        'critical': '🔴 **CRITICAL**',
        'high': '🟠 **HIGH**',
        'medium': '🟡 **MEDIUM**',
        'low': '🟢 **LOW**',
        'info': '🔵 **INFO**'
    }
    return badges.get(severity, f'⚪ **{severity.upper()}**')


