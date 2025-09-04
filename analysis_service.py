import re
import os
from typing import List, Dict, Any

class AnalysisService:
    def __init__(self):
        self.vulnerability_patterns = self._load_vulnerability_patterns()
        # Minimum confidence required to report a finding (tunable via env)
        try:
            self.min_confidence = float(os.getenv('MIN_CONFIDENCE', '0.65'))
        except ValueError:
            self.min_confidence = 0.65
    
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

        # Pre-compute context helpers
        pragma_line = self._get_pragma_version_line(cleaned_code)
        uses_reentrancy_guard = self._uses_reentrancy_guard(cleaned_code)
        is_solc_08_plus = self._is_solidity_08_plus(pragma_line)
        
        # Check each vulnerability pattern with multi-signal verification
        for vuln_type, vuln_config in self.vulnerability_patterns.items():
            matches = self._find_pattern_matches(cleaned_code, vuln_config['patterns'])
            
            for match in matches:
                # Inline suppression via comments in original code
                if self._is_suppressed_by_comment(contract_code, match['line_number'], vuln_type):
                    continue

                # Contextual false-positive suppression rules
                if vuln_type == 'integer_overflow':
                    if is_solc_08_plus or self._is_line_in_unchecked_block(cleaned_code, match['line_number']):
                        # In 0.8+, overflow/underflow checks are built-in; unchecked indicates intentional
                        continue
                    if self._uses_safemath(cleaned_code):
                        continue
                elif vuln_type == 'reentrancy':
                    if uses_reentrancy_guard:
                        continue
                    # Heuristic: ensure there is a state write after an external call within the same function
                    if not self._has_state_write_after_call_in_function(cleaned_code, match['line_number']):
                        # If no state write after external call, reduce confidence later
                        pass
                elif vuln_type == 'access_control':
                    if self._function_has_access_control(cleaned_code, match['line_number']):
                        continue

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
                # Secondary confidence tuning with context and multi-signal checks
                vulnerability['confidence'] = self._adjust_confidence_with_context(
                    vulnerability['confidence'], vuln_type, cleaned_code, match['line_number']
                )

                # Multi-signal: require at least 2 corroborating indicators for certain types
                corroboration_score = self._corroboration_score(vuln_type, cleaned_code, match['line_number'])
                if corroboration_score < 1 and vuln_type in {'reentrancy', 'access_control', 'integer_overflow'}:
                    # Reduce confidence if not enough corroboration
                    vulnerability['confidence'] *= 0.8

                # Confidence thresholding
                if vulnerability['confidence'] >= self.min_confidence:
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

    def _corroboration_score(self, vuln_type: str, code: str, line_number: int) -> int:
        """Heuristic corroboration count for a suspected issue."""
        score = 0
        bounds = self._get_enclosing_function_bounds(code, line_number)
        window = '\n'.join(code.split('\n')[bounds['start'] - 1:bounds['end']])
        if vuln_type == 'reentrancy':
            if re.search(r'\.call|\.send|\.transfer|delegatecall', window, re.IGNORECASE):
                score += 1
            if re.search(r'balance|balances\[|totalSupply|mapping', window):
                score += 1
            if not re.search(r'checks-effects-interactions|CEI', code, re.IGNORECASE):
                score += 1
        elif vuln_type == 'integer_overflow':
            if re.search(r'\buint(8|16|32|64|128|256)?\b', window):
                score += 1
            if re.search(r'\+\=|\-\=|\*\=|\+\+|\-\-', window):
                score += 1
        elif vuln_type == 'access_control':
            if re.search(r'onlyOwner|Ownable|AccessControl', code):
                score += 1
            if re.search(r'require\s*\(\s*msg\.sender\s*==\s*owner', window.replace(' ', '')):
                score += 1
        return score

    def _get_pragma_version_line(self, code: str) -> str:
        for line in code.split('\n')[:15]:
            if 'pragma solidity' in line:
                return line
        return ''

    def _is_solidity_08_plus(self, pragma_line: str) -> bool:
        if not pragma_line:
            return False
        # Extract version numbers like ^0.8.0, >=0.8.4, 0.8.17
        match = re.search(r'pragma\s+solidity\s+([^;]+);', pragma_line)
        if not match:
            return False
        constraint = match.group(1).strip()
        return any(v in constraint for v in ['0.8', '>=0.8'])

    def _uses_safemath(self, code: str) -> bool:
        return bool(re.search(r'using\s+SafeMath\s+for\s+\w+\s*;', code))

    def _uses_reentrancy_guard(self, code: str) -> bool:
        # Detect import/use of ReentrancyGuard or nonReentrant
        return bool(re.search(r'contract\s+\w+\s+.*ReentrancyGuard', code, re.IGNORECASE) or
                    re.search(r'nonReentrant\b', code))

    def _is_line_in_unchecked_block(self, code: str, line_number: int) -> bool:
        lines = code.split('\n')
        open_blocks = 0
        for i, line in enumerate(lines, 1):
            if re.search(r'\bunchecked\s*\{', line):
                open_blocks += 1
            if '}' in line and open_blocks > 0:
                open_blocks -= line.count('}')
            if i == line_number:
                return open_blocks > 0
        return False

    def _get_enclosing_function_bounds(self, code: str, line_number: int) -> Dict[str, int]:
        lines = code.split('\n')
        start_idx = 0
        brace_balance = 0
        # find function start by scanning upwards
        for i in range(line_number - 1, -1, -1):
            if re.search(r'function\s+\w+\s*\(', lines[i]):
                start_idx = i + 1
                break
        # find function end by scanning downwards counting braces
        for j in range(start_idx - 1, len(lines)):
            brace_balance += lines[j].count('{') - lines[j].count('}')
            if brace_balance == 0 and j >= start_idx:
                return {'start': start_idx, 'end': j + 1}
        return {'start': start_idx or 1, 'end': len(lines)}

    def _has_state_write_after_call_in_function(self, code: str, line_number: int) -> bool:
        bounds = self._get_enclosing_function_bounds(code, line_number)
        lines = code.split('\n')
        # Look for external call first, then a state write after
        external_call_seen = False
        state_write_pattern = re.compile(r'\b\w+\s*\[.*?\]\s*(\+\=|\-\=|=)|\b(totalSupply|balanceOf|owner)\b\s*(\+\=|\-\=|=)')
        for idx in range(bounds['start'] - 1, bounds['end']):
            line = lines[idx]
            if idx + 1 == line_number:
                external_call_seen = True
                continue
            if external_call_seen and state_write_pattern.search(line):
                return True
        return False

    def _function_has_access_control(self, code: str, line_number: int) -> bool:
        # Check if function signature includes onlyOwner/nonReentrant-like modifiers
        lines = code.split('\n')
        for i in range(line_number - 1, -1, -1):
            m = re.search(r'function\s+\w+\s*\([^)]*\)\s*(public|external|internal|private)?\s*([^\{]*)', lines[i])
            if m:
                modifiers = m.group(2) or ''
                if re.search(r'onlyOwner|admin|auth|role|access|Ownable', modifiers, re.IGNORECASE):
                    return True
                # Also look a few lines down for require(msg.sender == owner)
                for j in range(i, min(i + 6, len(lines))):
                    if re.search(r'require\s*\(\s*msg\.sender\s*==\s*owner', lines[j].replace(' ', '')):
                        return True
                break
        return False

    def _is_suppressed_by_comment(self, original_code: str, line_number: int, vuln_type: str) -> bool:
        # Support inline suppression comments like: // analyzer-ignore: reentrancy
        lines = original_code.split('\n')
        target = lines[line_number - 1] if 0 < line_number <= len(lines) else ''
        if re.search(r'analyzer-ignore\s*:\s*\b' + re.escape(vuln_type) + r'\b', target, re.IGNORECASE):
            return True
        # File-level suppression at top: // analyzer-ignore-file: integer_overflow
        header = '\n'.join(lines[:5])
        if re.search(r'analyzer-ignore-file\s*:\s*\b' + re.escape(vuln_type) + r'\b', header, re.IGNORECASE):
            return True
        return False

    def _adjust_confidence_with_context(self, base: float, vuln_type: str, code: str, line_number: int) -> float:
        confidence = base
        if vuln_type == 'reentrancy':
            if not self._has_state_write_after_call_in_function(code, line_number):
                confidence *= 0.7
        if vuln_type == 'access_control':
            if self._function_has_access_control(code, line_number):
                confidence *= 0.5
        return min(max(confidence, 0.0), 1.0)
    
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

