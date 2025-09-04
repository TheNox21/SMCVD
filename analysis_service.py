import re
import os
from typing import List, Dict, Any

class AnalysisService:
    def __init__(self):
        self.vulnerability_patterns = self._load_vulnerability_patterns()
    
    def _load_vulnerability_patterns(self):
        """Load vulnerability detection patterns"""
        return {
            'reentrancy': {
                'name': 'Reentrancy Vulnerability',
                'severity': 'critical',
                'cwe': 'CWE-362',
                'patterns': [
                    r'\.call\.value\([^)]*\)\(\)',
                    r'\.call\{value:\s*[^}]*\}\([^)]*\)',
                    r'\.transfer\([^)]*\).*balances\[[^]]*\]\s*[-+]=',
                    r'\.send\([^)]*\).*balances\[[^]]*\]\s*[-+]=',
                    r'external\.call.*balances\[[^]]*\]\s*[-+]='
                ],
                'description': 'External call made before state changes, allowing reentrancy attacks'
            },
            'integer_overflow': {
                'name': 'Integer Overflow/Underflow',
                'severity': 'high',
                'cwe': 'CWE-190',
                'patterns': [
                    r'uint\d*\s+\w+\s*\+\s*\w+',
                    r'uint\d*\s+\w+\s*\*\s*\w+',
                    r'balances\[[^]]*\]\s*\+=',
                    r'totalSupply\s*\+=',
                    r'(?<!require\s*\()[^;]*\+\+[^;]*(?!;)'
                ],
                'description': 'Arithmetic operations without overflow protection'
            },
            'access_control': {
                'name': 'Access Control Vulnerability',
                'severity': 'high',
                'cwe': 'CWE-284',
                'patterns': [
                    r'function\s+\w+\([^)]*\)\s*public\s*{[^}]*(?:selfdestruct|suicide)',
                    r'function\s+\w+\([^)]*\)\s*{[^}]*(?:selfdestruct|suicide)(?![^}]*require)',
                    r'function\s+\w+\([^)]*\)\s*public\s*{(?![^}]*(?:require|modifier|onlyOwner))',
                    r'modifier\s+\w+\s*{[^}]*_;[^}]*}(?![^}]*require)'
                ],
                'description': 'Missing or insufficient access control mechanisms'
            },
            'timestamp_dependence': {
                'name': 'Timestamp Dependence',
                'severity': 'medium',
                'cwe': 'CWE-829',
                'patterns': [
                    r'block\.timestamp',
                    r'now\s*[<>=!]',
                    r'block\.number\s*[<>=!]'
                ],
                'description': 'Reliance on block timestamp for critical operations'
            },
            'unchecked_external_call': {
                'name': 'Unchecked External Call',
                'severity': 'medium',
                'cwe': 'CWE-252',
                'patterns': [
                    r'\.call\([^)]*\);(?!\s*require)',
                    r'\.send\([^)]*\);(?!\s*require)',
                    r'\.delegatecall\([^)]*\);(?!\s*require)'
                ],
                'description': 'External call without checking return value'
            },
            'weak_randomness': {
                'name': 'Weak Randomness',
                'severity': 'medium',
                'cwe': 'CWE-330',
                'patterns': [
                    r'keccak256\([^)]*block\.timestamp[^)]*\)',
                    r'keccak256\([^)]*block\.difficulty[^)]*\)',
                    r'keccak256\([^)]*block\.number[^)]*\)',
                    r'uint\([^)]*keccak256[^)]*\)\s*%'
                ],
                'description': 'Use of predictable values for randomness'
            },
            'tx_origin': {
                'name': 'tx.origin Usage',
                'severity': 'medium',
                'cwe': 'CWE-346',
                'patterns': [
                    r'tx\.origin\s*==',
                    r'require\([^)]*tx\.origin[^)]*\)'
                ],
                'description': 'Use of tx.origin for authorization (phishing vulnerability)'
            },
            'unprotected_selfdestruct': {
                'name': 'Unprotected Self-Destruct',
                'severity': 'critical',
                'cwe': 'CWE-284',
                'patterns': [
                    r'selfdestruct\([^)]*\)(?![^;]*require)',
                    r'suicide\([^)]*\)(?![^;]*require)'
                ],
                'description': 'Self-destruct function without proper access control'
            },
            'dos_gas_limit': {
                'name': 'Denial of Service (Gas Limit)',
                'severity': 'medium',
                'cwe': 'CWE-400',
                'patterns': [
                    r'for\s*\([^)]*\.length[^)]*\)',
                    r'while\s*\([^)]*\.length[^)]*\)',
                    r'for\s*\([^)]*balances\.length[^)]*\)'
                ],
                'description': 'Loops that depend on external data length (gas limit DoS)'
            },
            'front_running': {
                'name': 'Front-Running Vulnerability',
                'severity': 'low',
                'cwe': 'CWE-362',
                'patterns': [
                    r'function\s+\w*[Bb]id\w*\([^)]*\)\s*public',
                    r'function\s+\w*[Aa]uction\w*\([^)]*\)\s*public',
                    r'function\s+\w*[Pp]urchase\w*\([^)]*\)\s*public'
                ],
                'description': 'Public functions susceptible to front-running attacks'
            }
        }
    
    def analyze_contract(self, contract_code: str, file_path: str = "") -> List[Dict[str, Any]]:
        """Analyze smart contract for vulnerabilities"""
        vulnerabilities = []
        
        # Remove comments to avoid false positives
        cleaned_code = self._remove_comments(contract_code)
        
        # Check each vulnerability pattern
        for vuln_type, vuln_config in self.vulnerability_patterns.items():
            matches = self._find_pattern_matches(cleaned_code, vuln_config['patterns'])
            
            for match in matches:
                vulnerability = {
                    'id': f"{vuln_type}_{hash(match['line_content']) % 10000}",
                    'type': vuln_type,
                    'name': vuln_config['name'],
                    'severity': vuln_config['severity'],
                    'cwe': vuln_config['cwe'],
                    'description': vuln_config['description'],
                    'file_path': os.path.basename(file_path) if file_path else 'unknown',
                    'line_number': match['line_number'],
                    'line_content': match['line_content'].strip(),
                    'function_name': self._extract_function_name(contract_code, match['line_number']),
                    'impact': self._assess_impact(vuln_type, vuln_config['severity']),
                    'confidence': self._calculate_confidence(vuln_type, match['line_content']),
                    'poc': None,  # Will be generated by AI service
                    'mitigation': self._get_mitigation_suggestion(vuln_type)
                }
                vulnerabilities.append(vulnerability)
        
        # Remove duplicates and sort by severity
        vulnerabilities = self._deduplicate_vulnerabilities(vulnerabilities)
        vulnerabilities = self._sort_by_severity(vulnerabilities)
        
        return vulnerabilities
    
    def _remove_comments(self, code: str) -> str:
        """Remove single-line and multi-line comments"""
        # Remove single-line comments
        code = re.sub(r'//.*$', '', code, flags=re.MULTILINE)
        # Remove multi-line comments
        code = re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL)
        return code
    
    def _find_pattern_matches(self, code: str, patterns: List[str]) -> List[Dict[str, Any]]:
        """Find all matches for given patterns"""
        matches = []
        lines = code.split('\n')
        
        for pattern in patterns:
            for line_num, line in enumerate(lines, 1):
                if re.search(pattern, line, re.IGNORECASE):
                    matches.append({
                        'line_number': line_num,
                        'line_content': line,
                        'pattern': pattern
                    })
        
        return matches
    
    def _extract_function_name(self, code: str, line_number: int) -> str:
        """Extract function name containing the vulnerable line"""
        lines = code.split('\n')
        
        # Look backwards from the line to find function declaration
        for i in range(line_number - 1, -1, -1):
            if i < len(lines):
                line = lines[i]
                function_match = re.search(r'function\s+(\w+)\s*\(', line)
                if function_match:
                    return function_match.group(1)
        
        return 'unknown'
    
    def _assess_impact(self, vuln_type: str, severity: str) -> str:
        """Assess potential impact of vulnerability"""
        impact_map = {
            'reentrancy': 'Complete drainage of contract funds, loss of user deposits',
            'integer_overflow': 'Token supply manipulation, balance corruption',
            'access_control': 'Unauthorized access to admin functions, privilege escalation',
            'timestamp_dependence': 'Manipulation of time-based logic, unfair advantages',
            'unchecked_external_call': 'Silent failures, unexpected behavior',
            'weak_randomness': 'Predictable outcomes, gaming of random events',
            'tx_origin': 'Phishing attacks, unauthorized transactions',
            'unprotected_selfdestruct': 'Contract destruction, permanent loss of funds',
            'dos_gas_limit': 'Contract becomes unusable, denial of service',
            'front_running': 'MEV attacks, unfair transaction ordering'
        }
        
        return impact_map.get(vuln_type, 'Potential security risk')
    
    def _calculate_confidence(self, vuln_type: str, line_content: str) -> float:
        """Calculate confidence level for vulnerability detection"""
        # Base confidence levels
        confidence_map = {
            'reentrancy': 0.8,
            'integer_overflow': 0.7,
            'access_control': 0.6,
            'timestamp_dependence': 0.9,
            'unchecked_external_call': 0.8,
            'weak_randomness': 0.9,
            'tx_origin': 0.95,
            'unprotected_selfdestruct': 0.9,
            'dos_gas_limit': 0.7,
            'front_running': 0.6
        }
        
        base_confidence = confidence_map.get(vuln_type, 0.5)
        
        # Adjust based on context
        if 'require(' in line_content:
            base_confidence *= 0.7  # Lower confidence if there's a require statement
        if 'modifier' in line_content:
            base_confidence *= 0.6  # Lower confidence if there's a modifier
        
        return min(base_confidence, 1.0)
    
    def _get_mitigation_suggestion(self, vuln_type: str) -> str:
        """Get mitigation suggestion for vulnerability type"""
        mitigation_map = {
            'reentrancy': 'Use checks-effects-interactions pattern, implement reentrancy guard',
            'integer_overflow': 'Use SafeMath library or Solidity 0.8+ built-in overflow protection',
            'access_control': 'Implement proper access control modifiers (onlyOwner, etc.)',
            'timestamp_dependence': 'Avoid using block.timestamp for critical logic, use block numbers',
            'unchecked_external_call': 'Always check return values of external calls',
            'weak_randomness': 'Use commit-reveal schemes or external oracles for randomness',
            'tx_origin': 'Use msg.sender instead of tx.origin for authorization',
            'unprotected_selfdestruct': 'Add access control to selfdestruct functions',
            'dos_gas_limit': 'Avoid loops over dynamic arrays, implement pagination',
            'front_running': 'Use commit-reveal schemes or implement MEV protection'
        }
        
        return mitigation_map.get(vuln_type, 'Review and secure the vulnerable code')
    
    def _deduplicate_vulnerabilities(self, vulnerabilities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Remove duplicate vulnerabilities"""
        seen = set()
        unique_vulns = []
        
        for vuln in vulnerabilities:
            # Create a unique key based on type, file, and line
            key = (vuln['type'], vuln['file_path'], vuln['line_number'])
            if key not in seen:
                seen.add(key)
                unique_vulns.append(vuln)
        
        return unique_vulns
    
    def _sort_by_severity(self, vulnerabilities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Sort vulnerabilities by severity"""
        severity_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3, 'info': 4}
        
        return sorted(vulnerabilities, key=lambda x: severity_order.get(x['severity'], 5))
    
    def get_contract_metrics(self, contract_code: str) -> Dict[str, Any]:
        """Get basic metrics about the contract"""
        lines = contract_code.split('\n')
        
        return {
            'total_lines': len(lines),
            'code_lines': len([line for line in lines if line.strip() and not line.strip().startswith('//')]),
            'function_count': len(re.findall(r'function\s+\w+', contract_code)),
            'modifier_count': len(re.findall(r'modifier\s+\w+', contract_code)),
            'event_count': len(re.findall(r'event\s+\w+', contract_code)),
            'external_calls': len(re.findall(r'\.call\(|\.send\(|\.transfer\(', contract_code))
        }

