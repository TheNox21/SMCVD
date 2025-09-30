import json
import markdown
from weasyprint import HTML, CSS

def generate_pdf_report():
    """Generate a PDF version of the enhanced ERC-4337 security analysis report"""
    try:
        # Read the enhanced markdown report
        with open('erc4337_security_analysis_report_enhanced.md', 'r', encoding='utf-8') as f:
            markdown_content = f.read()
        
        # Convert markdown to HTML
        html_content = markdown.markdown(markdown_content, extensions=['tables', 'fenced_code'])
        
        # Add basic styling
        html_with_style = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>ERC-4337 Security Analysis Report</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                    max-width: 800px;
                    margin: 0 auto;
                    padding: 20px;
                }}
                h1, h2, h3 {{
                    color: #333;
                }}
                code {{
                    background-color: #f4f4f4;
                    padding: 2px 4px;
                    border-radius: 3px;
                    font-family: 'Courier New', monospace;
                }}
                pre {{
                    background-color: #f4f4f4;
                    padding: 10px;
                    border-radius: 5px;
                    overflow-x: auto;
                }}
                pre code {{
                    background-color: transparent;
                    padding: 0;
                }}
                table {{
                    border-collapse: collapse;
                    width: 100%;
                }}
                th, td {{
                    border: 1px solid #ddd;
                    padding: 8px;
                    text-align: left;
                }}
                th {{
                    background-color: #f2f2f2;
                }}
            </style>
        </head>
        <body>
            {html_content}
        </body>
        </html>
        """
        
        # Generate PDF
        HTML(string=html_with_style).write_pdf('erc4337_security_analysis_report_enhanced.pdf')
        print("Enhanced PDF report generated successfully: erc4337_security_analysis_report_enhanced.pdf")
        
    except Exception as e:
        print(f"Error generating PDF report: {str(e)}")

if __name__ == "__main__":
    generate_pdf_report()