import os
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from jinja2 import Template
from src.services.ai_service import AIService

class ReportService:
    def __init__(self):
        self.ai_service = AIService()
        self.report_templates = self._load_templates()
    
    def _load_templates(self) -> Dict[str, str]:
        """Load report templates"""
        return {
            'professional': self._get_professional_template(),
            'detailed': self._get_detailed_template(),
            'concise': self._get_concise_template()
        }
    
    def generate_bug_bounty_report(self, 
                                 vulnerabilities: List[Dict[str, Any]], 
                                 config: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate comprehensive bug bounty report"""
        
        if not config:
            config = {}
        
        # Default configuration
        default_config = {
            'title': 'Smart Contract Security Analysis Report',
            'researcher': 'Security Researcher',
            'target_program': 'Bug Bounty Program',
            'template': 'professional',
            'include_poc': True,
            'include_mitigation': True,
            'include_executive_summary': True
        }
        
        # Merge with provided config
        report_config = {**default_config, **config}
        
        # Filter vulnerabilities based on selection
        selected_vulns = vulnerabilities
        if 'selected_vulnerabilities' in config:
            selected_ids = config['selected_vulnerabilities']
            selected_vulns = [v for v in vulnerabilities if v.get('id') in selected_ids]
        
        # Generate report sections
        report_data = {
            'metadata': self._generate_metadata(report_config),
            'executive_summary': self._generate_executive_summary(selected_vulns),
            'vulnerability_details': self._generate_vulnerability_details(selected_vulns, report_config),
            'recommendations': self._generate_recommendations(selected_vulns),
            'appendix': self._generate_appendix(selected_vulns)
        }
        
        # Generate report in different formats
        template = self.report_templates.get(report_config['template'], self.report_templates['professional'])
        
        markdown_report = self._render_template(template, report_data)
        
        return {
            'markdown': markdown_report,
            'metadata': report_data['metadata'],
            'summary': {
                'total_vulnerabilities': len(selected_vulns),
                'severity_breakdown': self._get_severity_breakdown(selected_vulns),
                'risk_level': self._calculate_overall_risk(selected_vulns)
            }
        }
    
    def _generate_metadata(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate report metadata"""
        return {
            'title': config['title'],
            'researcher': config['researcher'],
            'target_program': config['target_program'],
            'date': datetime.now().strftime('%Y-%m-%d'),
            'timestamp': datetime.now().isoformat(),
            'report_id': f"SC-{datetime.now().strftime('%Y%m%d')}-{hash(config['title']) % 10000:04d}"
        }
    
    def _generate_executive_summary(self, vulnerabilities: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate executive summary"""
        if not vulnerabilities:
            return {
                'overview': 'No significant vulnerabilities were identified during the analysis.',
                'key_findings': [],
                'risk_assessment': 'Low',
                'recommendations': ['Continue following security best practices']
            }
        
        severity_breakdown = self._get_severity_breakdown(vulnerabilities)
        risk_level = self._calculate_overall_risk(vulnerabilities)
        
        # Get top vulnerabilities
        critical_vulns = [v for v in vulnerabilities if v.get('severity') == 'critical']
        high_vulns = [v for v in vulnerabilities if v.get('severity') == 'high']
        
        key_findings = []
        if critical_vulns:
            key_findings.extend([f"Critical: {v['name']}" for v in critical_vulns[:3]])
        if high_vulns:
            key_findings.extend([f"High: {v['name']}" for v in high_vulns[:3]])
        
        overview = f"""
        During the security analysis of the smart contract(s), {len(vulnerabilities)} vulnerabilities were identified across different severity levels. 
        The analysis revealed {severity_breakdown.get('critical', 0)} critical, {severity_breakdown.get('high', 0)} high, 
        {severity_breakdown.get('medium', 0)} medium, and {severity_breakdown.get('low', 0)} low severity issues.
        
        The overall risk level is assessed as {risk_level.upper()}, requiring immediate attention for critical and high-severity vulnerabilities.
        """.strip()
        
        return {
            'overview': overview,
            'key_findings': key_findings,
            'risk_assessment': risk_level.title(),
            'severity_breakdown': severity_breakdown,
            'recommendations': self._get_priority_recommendations(vulnerabilities)
        }
    
    def _generate_vulnerability_details(self, vulnerabilities: List[Dict[str, Any]], config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate detailed vulnerability information"""
        detailed_vulns = []
        
        for i, vuln in enumerate(vulnerabilities, 1):
            detailed_vuln = {
                'index': i,
                'id': vuln.get('id', f'vuln_{i}'),
                'title': vuln.get('name', 'Unknown Vulnerability'),
                'severity': vuln.get('severity', 'medium').title(),
                'cwe': vuln.get('cwe', 'N/A'),
                'description': vuln.get('description', 'No description available'),
                'location': {
                    'file': vuln.get('file_path', 'unknown'),
                    'line': vuln.get('line_number', 0),
                    'function': vuln.get('function_name', 'unknown')
                },
                'impact': vuln.get('impact', 'Potential security risk'),
                'vulnerable_code': vuln.get('line_content', ''),
                'confidence': vuln.get('confidence', 0.5),
                'mitigation': vuln.get('mitigation', 'Review and secure the vulnerable code')
            }
            
            # Add AI-enhanced details if available
            if vuln.get('ai_analysis'):
                detailed_vuln['detailed_analysis'] = vuln['ai_analysis']
            
            if vuln.get('detailed_description'):
                detailed_vuln['technical_details'] = vuln['detailed_description']
            
            if vuln.get('attack_scenarios'):
                detailed_vuln['attack_scenarios'] = vuln['attack_scenarios']
            
            # Generate POC if requested
            if config.get('include_poc', True):
                poc = self._generate_poc_for_vulnerability(vuln)
                if poc:
                    detailed_vuln['proof_of_concept'] = poc
            
            detailed_vulns.append(detailed_vuln)
        
        return detailed_vulns
    
    def _generate_poc_for_vulnerability(self, vulnerability: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Generate proof of concept for vulnerability"""
        try:
            # Check if POC already exists
            if vulnerability.get('poc_code'):
                return {
                    'code': vulnerability['poc_code'],
                    'explanation': vulnerability.get('poc_explanation', 'Proof of concept demonstration'),
                    'type': 'existing'
                }
            
            # Generate new POC using AI
            poc_prompt = f"""
            Create a proof-of-concept exploit for this vulnerability:
            
            Vulnerability: {vulnerability.get('name', 'Unknown')}
            Type: {vulnerability.get('type', 'unknown')}
            Severity: {vulnerability.get('severity', 'medium')}
            
            Vulnerable code: {vulnerability.get('line_content', '')}
            Function: {vulnerability.get('function_name', 'unknown')}
            
            Provide a working JavaScript/Solidity example that demonstrates the vulnerability.
            Include step-by-step explanation and expected impact.
            """
            
            poc_response = self.ai_service.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a smart contract security expert. Create clear, working proof-of-concept exploits for educational purposes."},
                    {"role": "user", "content": poc_prompt}
                ],
                temperature=0.2,
                max_tokens=1500
            )
            
            poc_content = poc_response.choices[0].message.content
            
            return {
                'code': poc_content,
                'explanation': 'AI-generated proof of concept demonstration',
                'type': 'generated',
                'note': 'This POC is for educational and testing purposes only'
            }
            
        except Exception as e:
            return {
                'code': f'// POC generation failed: {str(e)}',
                'explanation': 'Manual POC creation required',
                'type': 'error'
            }
    
    def _generate_recommendations(self, vulnerabilities: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate security recommendations"""
        if not vulnerabilities:
            return {
                'immediate_actions': ['Continue following security best practices'],
                'long_term_improvements': ['Regular security audits', 'Code review processes'],
                'best_practices': ['Use latest Solidity version', 'Implement proper testing']
            }
        
        immediate_actions = []
        long_term_improvements = []
        best_practices = []
        
        # Analyze vulnerabilities for recommendations
        vuln_types = set(v.get('type', '') for v in vulnerabilities)
        
        if 'reentrancy' in vuln_types:
            immediate_actions.append('Implement reentrancy guards on vulnerable functions')
            best_practices.append('Follow checks-effects-interactions pattern')
        
        if 'integer_overflow' in vuln_types:
            immediate_actions.append('Use SafeMath library or Solidity 0.8+ overflow protection')
            best_practices.append('Always validate arithmetic operations')
        
        if 'access_control' in vuln_types:
            immediate_actions.append('Add proper access control modifiers to sensitive functions')
            best_practices.append('Implement role-based access control')
        
        # General recommendations
        critical_count = len([v for v in vulnerabilities if v.get('severity') == 'critical'])
        high_count = len([v for v in vulnerabilities if v.get('severity') == 'high'])
        
        if critical_count > 0:
            immediate_actions.insert(0, f'Address {critical_count} critical vulnerabilities immediately')
        
        if high_count > 0:
            immediate_actions.append(f'Prioritize fixing {high_count} high-severity vulnerabilities')
        
        long_term_improvements.extend([
            'Implement comprehensive testing suite',
            'Set up continuous security monitoring',
            'Establish regular security audit schedule',
            'Create incident response procedures'
        ])
        
        best_practices.extend([
            'Follow secure coding guidelines',
            'Use static analysis tools in CI/CD pipeline',
            'Implement proper error handling',
            'Document security assumptions and requirements'
        ])
        
        return {
            'immediate_actions': immediate_actions[:5],  # Top 5 immediate actions
            'long_term_improvements': long_term_improvements[:5],
            'best_practices': best_practices[:5]
        }
    
    def _generate_appendix(self, vulnerabilities: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate report appendix"""
        return {
            'methodology': 'Static analysis combined with AI-powered vulnerability detection',
            'tools_used': 'Custom analysis engine with pattern matching and machine learning',
            'scope': 'Smart contract source code analysis',
            'limitations': [
                'Analysis based on static code review',
                'Runtime behavior not evaluated',
                'Business logic vulnerabilities may require manual review'
            ],
            'references': [
                'OWASP Smart Contract Top 10',
                'SWC Registry (Smart Contract Weakness Classification)',
                'Consensys Smart Contract Best Practices'
            ]
        }
    
    def _get_severity_breakdown(self, vulnerabilities: List[Dict[str, Any]]) -> Dict[str, int]:
        """Get vulnerability count by severity"""
        breakdown = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0, 'info': 0}
        for vuln in vulnerabilities:
            severity = vuln.get('severity', 'info').lower()
            if severity in breakdown:
                breakdown[severity] += 1
        return breakdown
    
    def _calculate_overall_risk(self, vulnerabilities: List[Dict[str, Any]]) -> str:
        """Calculate overall risk level"""
        if not vulnerabilities:
            return 'low'
        
        severity_counts = self._get_severity_breakdown(vulnerabilities)
        
        if severity_counts['critical'] > 0:
            return 'critical'
        elif severity_counts['high'] > 2:
            return 'critical'
        elif severity_counts['high'] > 0:
            return 'high'
        elif severity_counts['medium'] > 3:
            return 'high'
        elif severity_counts['medium'] > 0:
            return 'medium'
        else:
            return 'low'
    
    def _get_priority_recommendations(self, vulnerabilities: List[Dict[str, Any]]) -> List[str]:
        """Get priority recommendations based on vulnerabilities"""
        recommendations = []
        
        critical_count = len([v for v in vulnerabilities if v.get('severity') == 'critical'])
        high_count = len([v for v in vulnerabilities if v.get('severity') == 'high'])
        
        if critical_count > 0:
            recommendations.append(f'Immediately address {critical_count} critical security vulnerabilities')
        
        if high_count > 0:
            recommendations.append(f'Prioritize fixing {high_count} high-severity issues')
        
        recommendations.extend([
            'Implement comprehensive security testing',
            'Conduct thorough code review before deployment'
        ])
        
        return recommendations[:3]  # Top 3 recommendations
    
    def _render_template(self, template_str: str, data: Dict[str, Any]) -> str:
        """Render report template with data"""
        template = Template(template_str)
        return template.render(**data)
    
    def _get_professional_template(self) -> str:
        """Professional bug bounty report template"""
        return """# {{ metadata.title }}

**Report ID:** {{ metadata.report_id }}  
**Date:** {{ metadata.date }}  
**Researcher:** {{ metadata.researcher }}  
**Target Program:** {{ metadata.target_program }}

---

## Executive Summary

{{ executive_summary.overview }}

### Key Findings
{% for finding in executive_summary.key_findings %}
- {{ finding }}
{% endfor %}

**Overall Risk Assessment:** {{ executive_summary.risk_assessment }}

### Severity Breakdown
- **Critical:** {{ executive_summary.severity_breakdown.critical }}
- **High:** {{ executive_summary.severity_breakdown.high }}
- **Medium:** {{ executive_summary.severity_breakdown.medium }}
- **Low:** {{ executive_summary.severity_breakdown.low }}

---

## Vulnerability Details

{% for vuln in vulnerability_details %}
### {{ vuln.index }}. {{ vuln.title }}

**Severity:** {{ vuln.severity }}  
**CWE:** {{ vuln.cwe }}  
**Location:** {{ vuln.location.file }}:{{ vuln.location.line }} ({{ vuln.location.function }})  
**Confidence:** {{ "%.0f"|format(vuln.confidence * 100) }}%

#### Description
{{ vuln.description }}

#### Impact
{{ vuln.impact }}

#### Vulnerable Code
```solidity
{{ vuln.vulnerable_code }}
```

{% if vuln.technical_details %}
#### Technical Analysis
{{ vuln.technical_details }}
{% endif %}

{% if vuln.attack_scenarios %}
#### Attack Scenarios
{{ vuln.attack_scenarios }}
{% endif %}

{% if vuln.proof_of_concept %}
#### Proof of Concept
{{ vuln.proof_of_concept.explanation }}

```javascript
{{ vuln.proof_of_concept.code }}
```
{% endif %}

#### Recommended Mitigation
{{ vuln.mitigation }}

---
{% endfor %}

## Recommendations

### Immediate Actions Required
{% for action in recommendations.immediate_actions %}
- {{ action }}
{% endfor %}

### Long-term Security Improvements
{% for improvement in recommendations.long_term_improvements %}
- {{ improvement }}
{% endfor %}

### Security Best Practices
{% for practice in recommendations.best_practices %}
- {{ practice }}
{% endfor %}

---

## Appendix

**Methodology:** {{ appendix.methodology }}  
**Tools Used:** {{ appendix.tools_used }}  
**Analysis Scope:** {{ appendix.scope }}

### Limitations
{% for limitation in appendix.limitations %}
- {{ limitation }}
{% endfor %}

### References
{% for reference in appendix.references %}
- {{ reference }}
{% endfor %}

---

*This report was generated on {{ metadata.timestamp }} for security research purposes.*
"""
    
    def _get_detailed_template(self) -> str:
        """Detailed technical report template"""
        # Similar to professional but with more technical details
        return self._get_professional_template()  # Simplified for now
    
    def _get_concise_template(self) -> str:
        """Concise report template"""
        return """# {{ metadata.title }}

**Date:** {{ metadata.date }} | **Researcher:** {{ metadata.researcher }}

## Summary
{{ executive_summary.overview }}

**Risk Level:** {{ executive_summary.risk_assessment }}

## Vulnerabilities Found

{% for vuln in vulnerability_details %}
### {{ vuln.index }}. {{ vuln.title }} ({{ vuln.severity }})
**Location:** {{ vuln.location.file }}:{{ vuln.location.line }}

{{ vuln.description }}

**Impact:** {{ vuln.impact }}

**Fix:** {{ vuln.mitigation }}

{% if vuln.proof_of_concept %}
**POC:**
```
{{ vuln.proof_of_concept.code }}
```
{% endif %}

---
{% endfor %}

## Priority Actions
{% for action in recommendations.immediate_actions %}
- {{ action }}
{% endfor %}
"""

