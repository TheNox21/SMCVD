import os
from openai import OpenAI
from typing import Dict, Any, List
import json

class AIService:
    def __init__(self):
        self.client = OpenAI()
        self.model = "gpt-4"
    
    def enhance_vulnerability(self, vulnerability: Dict[str, Any], contract_code: str) -> Dict[str, Any]:
        """Enhance vulnerability with AI analysis and generate POC"""
        try:
            # Create prompt for vulnerability analysis
            prompt = self._create_vulnerability_prompt(vulnerability, contract_code)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a smart contract security expert. Analyze vulnerabilities and provide detailed explanations with proof-of-concept code."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=2000
            )
            
            ai_analysis = response.choices[0].message.content
            
            # Parse AI response and enhance vulnerability
            enhanced_vuln = vulnerability.copy()
            enhanced_vuln.update(self._parse_ai_response(ai_analysis, vulnerability['type']))
            
            return enhanced_vuln
            
        except Exception as e:
            # Return original vulnerability if AI enhancement fails
            vulnerability['ai_error'] = f"AI enhancement failed: {str(e)}"
            return vulnerability
    
    def generate_poc(self, vulnerability: Dict[str, Any], contract_code: str) -> str:
        """Generate proof-of-concept exploit code"""
        try:
            prompt = f"""
            Generate a proof-of-concept exploit for this smart contract vulnerability:
            
            Vulnerability: {vulnerability['name']}
            Type: {vulnerability['type']}
            Severity: {vulnerability['severity']}
            Description: {vulnerability['description']}
            
            Vulnerable code line: {vulnerability['line_content']}
            Function: {vulnerability['function_name']}
            
            Contract code snippet:
            {self._extract_relevant_code(contract_code, vulnerability['line_number'])}
            
            Please provide:
            1. A working exploit script in JavaScript using ethers.js
            2. Step-by-step explanation of the attack
            3. Expected outcome/impact
            
            Format the response as a JSON object with keys: 'exploit_code', 'explanation', 'impact'.
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a smart contract security researcher. Generate working proof-of-concept exploits for educational purposes."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=1500
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"POC generation failed: {str(e)}"
    
    def get_overall_assessment(self, vulnerabilities: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Get overall security assessment from AI"""
        try:
            if not vulnerabilities:
                return {
                    'risk_level': 'low',
                    'summary': 'No significant vulnerabilities detected.',
                    'recommendations': ['Continue following security best practices']
                }
            
            # Create summary of vulnerabilities
            vuln_summary = []
            for vuln in vulnerabilities:
                vuln_summary.append({
                    'type': vuln['type'],
                    'severity': vuln['severity'],
                    'name': vuln['name']
                })
            
            prompt = f"""
            Analyze this smart contract security assessment and provide an overall evaluation:
            
            Vulnerabilities found: {len(vulnerabilities)}
            
            Vulnerability breakdown:
            {json.dumps(vuln_summary, indent=2)}
            
            Please provide:
            1. Overall risk level (critical/high/medium/low)
            2. Executive summary of findings
            3. Top 3 priority recommendations
            4. Estimated potential financial impact
            
            Format as JSON with keys: 'risk_level', 'summary', 'recommendations', 'financial_impact'.
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a senior smart contract auditor providing executive summaries."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=1000
            )
            
            try:
                return json.loads(response.choices[0].message.content)
            except json.JSONDecodeError:
                # Fallback if JSON parsing fails
                return {
                    'risk_level': self._calculate_overall_risk(vulnerabilities),
                    'summary': response.choices[0].message.content,
                    'recommendations': ['Review all identified vulnerabilities', 'Implement security best practices'],
                    'financial_impact': 'Varies based on contract value and usage'
                }
            
        except Exception as e:
            return {
                'risk_level': self._calculate_overall_risk(vulnerabilities),
                'summary': f'Assessment generation failed: {str(e)}',
                'recommendations': ['Manual security review recommended'],
                'financial_impact': 'Unknown'
            }
    
    def _create_vulnerability_prompt(self, vulnerability: Dict[str, Any], contract_code: str) -> str:
        """Create prompt for vulnerability analysis"""
        relevant_code = self._extract_relevant_code(contract_code, vulnerability['line_number'])
        
        return f"""
        Analyze this smart contract vulnerability in detail:
        
        Vulnerability Type: {vulnerability['type']}
        Name: {vulnerability['name']}
        Severity: {vulnerability['severity']}
        CWE: {vulnerability['cwe']}
        
        Vulnerable line: {vulnerability['line_content']}
        Function: {vulnerability['function_name']}
        File: {vulnerability['file_path']}
        
        Relevant code context:
        {relevant_code}
        
        Please provide:
        1. Detailed technical explanation of the vulnerability
        2. Specific attack scenarios
        3. Potential impact and consequences
        4. Recommended fixes and mitigations
        5. A simple proof-of-concept if applicable
        
        Focus on practical, actionable insights for bug bounty reporting.
        """
    
    def _extract_relevant_code(self, contract_code: str, line_number: int, context_lines: int = 10) -> str:
        """Extract relevant code around the vulnerable line"""
        lines = contract_code.split('\n')
        start = max(0, line_number - context_lines - 1)
        end = min(len(lines), line_number + context_lines)
        
        relevant_lines = []
        for i in range(start, end):
            if i < len(lines):
                marker = " -> " if i == line_number - 1 else "    "
                relevant_lines.append(f"{i+1:3d}{marker}{lines[i]}")
        
        return '\n'.join(relevant_lines)
    
    def _parse_ai_response(self, ai_response: str, vuln_type: str) -> Dict[str, Any]:
        """Parse AI response and extract structured information"""
        # Try to extract structured information from AI response
        enhanced_data = {
            'ai_analysis': ai_response,
            'detailed_description': self._extract_section(ai_response, 'explanation'),
            'attack_scenarios': self._extract_section(ai_response, 'attack'),
            'recommended_fix': self._extract_section(ai_response, 'fix|mitigation|recommendation'),
            'poc_code': self._extract_section(ai_response, 'proof|poc|exploit')
        }
        
        return enhanced_data
    
    def _extract_section(self, text: str, pattern: str) -> str:
        """Extract specific section from AI response"""
        import re
        
        # Look for section headers
        section_match = re.search(f'({pattern})[:\n]([^#]*?)(?=\n#|\n\d+\.|\Z)', text, re.IGNORECASE | re.DOTALL)
        if section_match:
            return section_match.group(2).strip()
        
        return ""
    
    def _calculate_overall_risk(self, vulnerabilities: List[Dict[str, Any]]) -> str:
        """Calculate overall risk level based on vulnerabilities"""
        if not vulnerabilities:
            return 'low'
        
        severity_counts = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0}
        for vuln in vulnerabilities:
            severity = vuln.get('severity', 'low')
            if severity in severity_counts:
                severity_counts[severity] += 1
        
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

