import json
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors

def generate_pdf_report():
    """Generate a PDF report from the security analysis data"""
    
    # Read the JSON report data
    try:
        with open('security_analysis_report.json', 'r') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error reading JSON report: {e}")
        return
    
    # Create PDF document
    doc = SimpleDocTemplate("security_analysis_report.pdf", pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        alignment=1  # Center alignment
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        spaceAfter=12
    )
    
    subheading_style = ParagraphStyle(
        'CustomSubHeading',
        parent=styles['Heading3'],
        fontSize=14,
        spaceAfter=10
    )
    
    # Title
    story.append(Paragraph("Smart Contract Security Analysis Report", title_style))
    story.append(Spacer(1, 0.5*inch))
    
    # Repository Information
    story.append(Paragraph("Repository Information", heading_style))
    story.append(Paragraph(f"<b>Repository:</b> eth-infinitism/account-abstraction", styles['Normal']))
    story.append(Paragraph(f"<b>Files Analyzed:</b> {data['summary']['total_files']}", styles['Normal']))
    story.append(Paragraph(f"<b>Analysis Tool:</b> SMCVD (Smart Contract Vulnerability Detector)", styles['Normal']))
    story.append(Paragraph(f"<b>Date:</b> 2025-09-29", styles['Normal']))
    story.append(Spacer(1, 0.3*inch))
    
    # Executive Summary
    story.append(Paragraph("Executive Summary", heading_style))
    story.append(Paragraph(
        "The analysis of the eth-infinitism/account-abstraction repository identified "
        f"{data['summary']['vulnerabilities_found']} medium-severity vulnerabilities. "
        "The overall risk level is assessed as <b>medium</b>.<br/><br/>"
        "Note: AI-enhanced detailed analysis was not available due to API quota limitations.",
        styles['Normal']
    ))
    story.append(Spacer(1, 0.3*inch))
    
    # Risk Assessment
    story.append(Paragraph("Risk Assessment", heading_style))
    story.append(Paragraph(f"<b>Overall Risk Level:</b> Medium", styles['Normal']))
    story.append(Spacer(1, 0.2*inch))
    
    # Severity breakdown table
    story.append(Paragraph("Vulnerabilities by Severity:", styles['Normal']))
    severity_data = [['Severity', 'Count']]
    for severity, count in data['summary']['severity_breakdown'].items():
        if count > 0:
            severity_data.append([severity.capitalize(), str(count)])
    
    severity_table = Table(severity_data)
    severity_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(severity_table)
    story.append(Spacer(1, 0.3*inch))
    
    # Identified Vulnerabilities
    story.append(Paragraph("Identified Vulnerabilities", heading_style))
    
    vulnerabilities = data['vulnerabilities']
    for i, vuln in enumerate(vulnerabilities, 1):
        story.append(Paragraph(f"{i}. {vuln['name']}", subheading_style))
        story.append(Paragraph(f"<b>Severity:</b> {vuln['severity'].capitalize()}", styles['Normal']))
        story.append(Paragraph(f"<b>File:</b> {vuln['file_path']} (Line {vuln['line_number']})", styles['Normal']))
        story.append(Paragraph(f"<b>Confidence:</b> {vuln['confidence']:.2f}", styles['Normal']))
        story.append(Paragraph(f"<b>Description:</b> {vuln['description']}", styles['Normal']))
        story.append(Paragraph(f"<b>Impact:</b> {vuln['impact']}", styles['Normal']))
        story.append(Paragraph(f"<b>Recommendation:</b> {vuln['mitigation']}", styles['Normal']))
        story.append(Spacer(1, 0.2*inch))
    
    # Recommendations
    story.append(Paragraph("Recommendations", heading_style))
    recommendations = [
        "Address Timestamp Dependencies: Replace block.timestamp usage with more secure alternatives where possible.",
        "Implement Return Value Checks: Ensure all external calls check their return values and handle failures appropriately.",
        "Conduct Manual Security Review: Perform a thorough manual review of the identified vulnerabilities.",
        "Upgrade OpenAI Plan: Consider upgrading your OpenAI plan to enable full AI-enhanced analysis capabilities."
    ]
    
    for i, rec in enumerate(recommendations, 1):
        story.append(Paragraph(f"{i}. {rec}", styles['Normal']))
    
    story.append(Spacer(1, 0.3*inch))
    
    # Conclusion
    story.append(Paragraph("Conclusion", heading_style))
    story.append(Paragraph(
        "The eth-infinitism/account-abstraction repository shows good security practices overall "
        "but has some medium-severity issues that should be addressed. The identified vulnerabilities "
        "are not critical but could be exploited under certain conditions. Addressing these issues "
        "will improve the overall security posture of the smart contracts.",
        styles['Normal']
    ))
    
    # Build PDF
    doc.build(story)
    print("PDF report generated successfully: security_analysis_report.pdf")

if __name__ == "__main__":
    generate_pdf_report()