def markdown_to_html(markdown_content: str) -> str:
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Security Report</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }
            h1 { color: #333; border-bottom: 2px solid #333; }
            h2 { color: #666; border-bottom: 1px solid #666; }
            h3 { color: #888; }
            code { background-color: #f4f4f4; padding: 2px 4px; border-radius: 3px; }
            pre { background-color: #f4f4f4; padding: 10px; border-radius: 5px; overflow-x: auto; }
            .severity-critical { color: #d32f2f; font-weight: bold; }
            .severity-high { color: #f57c00; font-weight: bold; }
            .severity-medium { color: #fbc02d; font-weight: bold; }
            .severity-low { color: #388e3c; font-weight: bold; }
        </style>
    </head>
    <body>
    """

    lines = markdown_content.split('\n')
    in_code = False
    for line in lines:
        line = line.strip()
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
        if line.startswith('# '):
            html_content += f"<h1>{line[2:]}</h1>\n"
        elif line.startswith('## '):
            html_content += f"<h2>{line[3:]}</h2>\n"
        elif line.startswith('### '):
            html_content += f"<h3>{line[4:]}</h3>\n"
        elif line.startswith('- '):
            html_content += f"<li>{line[2:]}</li>\n"
        elif line:
            html_content += f"<p>{line}</p>\n"
        else:
            html_content += "<br>\n"

    html_content += """
    </body>
    </html>
    """
    return html_content


