import re
import os
from typing import List, Dict, Any

class AnalysisService:
    def __init__(self):
        self.vulnerability_patterns = self._load_vulnerability_patterns()
        self.min_confidence = float(os.getenv('MIN_CONFIDENCE', '0.8'))
    
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
                    r'external\.call.*balances\[[^]]*\]\s*[-+]=',
                    r'\.(?:call|send|transfer)\s*\([^)]*\)\s*;\s*[^}]*balances\[[^]]*\]\s*[-+]=',
                    r'\.(?:call|send|transfer)\s*\{[^}]*\}\s*\([^)]*\)\s*;\s*[^}]*balances\[[^]]*\]\s*[-+]=' 
                ],
                'anti_patterns': [
                    r'nonReentrant\s*\(',
                    r'isReentrancyGuardSet\s*\(',
                    r'beforeTokenTransfer\s*\('
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
                    r'\w+\s*\+\+'
                ],
                'anti_patterns': [
                    r'\bSafeMath\b',
                    r'\badd\([^)]*\)',
                    r'\bsub\([^)]*\)',
                    r'\bmul\([^)]*\)',
                    r'\bchecked\s*\{',
                    r'\brequire\([^)]*\+\+[^)]*\)',
                    r'\brequire\([^)]*\+=\s*[^)]*\)'
                ],
                'description': 'Arithmetic operations without overflow protection'
            },
            'access_control': {
                'name': 'Access Control Vulnerability',
                'severity': 'high',
                'cwe': 'CWE-284',
                'patterns': [
                    r'function\s+\w+\([^)]*\)\s*public\s*{[^}]*(?:selfdestruct|suicide)',
                    r'function\s+\w+\([^)]*\)\s*{[^}]*(?:selfdestruct|suicide)(?!.*?require)'
                    r'function\s+\w+\([^)]*\)\s*public\s*{(?!.*?require|.*?modifier|.*?onlyOwner)',
                    r'modifier\s+\w+\s*{[^}]*_;[^}]*}(?!.*?require)'
                ],
                'anti_patterns': [
                    r'onlyOwner\s*\(',
                    r'onlyAdmin\s*\(',
                    r'hasRole\s*\(',
                    r'isAdmin\s*\(',
                    r'isOwner\s*\(',
                    r'msg\.sender\s*==\s*owner',
                    r'require\([^)]*msg\.sender[^)]*\)'
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
                    r'\.call\([^)]*\);(?!.*?require)',
                    r'\.send\([^)]*\);(?!.*?require)',
                    r'\.delegatecall\([^)]*\);(?!.*?require)'
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
                    r'selfdestruct\([^)]*\)(?!.*?require)',
                    r'suicide\([^)]*\)(?!.*?require)'
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
            },
            'flash_loan_attack': {
                'name': 'Flash Loan Attack Vulnerability',
                'severity': 'critical',
                'cwe': 'CWE-284',
                'patterns': [
                    r'flashLoan\(',
                    r'onFlashLoan\(',
                    r'executeOperation\(',
                    r'balanceOf\([^)]*\)\s*[-+*\/]',
                    r'getReserves\([^)]*\)\s*[-+*\/]'
                ],
                'description': 'Potential flash loan attack vectors'
            },
            'price_manipulation': {
                'name': 'Price Oracle Manipulation',
                'severity': 'high',
                'cwe': 'CWE-829',
                'patterns': [
                    r'getPrice\([^)]*\)',
                    r'latestAnswer\([^)]*\)',
                    r'pair\.getReserves',
                    r'TWAP(?!.*?require)',
                    r'spotPrice(?!.*?require)'
                ],
                'description': 'Vulnerable to price oracle manipulation'
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
            anti_patterns = vuln_config.get('anti_patterns', [])
            matches = self._find_pattern_matches(cleaned_code, vuln_config['patterns'], anti_patterns)
            
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
                    'confidence': self._calculate_confidence(vuln_type, match['line_content'], self._get_context_window(cleaned_code, match['line_number'])),
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
                
                # Additional false positive reduction for high-confidence matches
                if vulnerability['confidence'] >= 0.9:
                    # Apply additional verification for high-confidence findings
                    if self._is_likely_false_positive(vuln_type, cleaned_code, match['line_number']):
                        vulnerability['confidence'] *= 0.5  # Significantly reduce confidence
                
                # Apply stricter threshold for critical vulnerabilities
                if vulnerability['severity'] == 'critical' and vulnerability['confidence'] < 0.85:
                    continue  # Skip critical vulnerabilities with low confidence

                # Confidence thresholding with stricter requirements for critical vulnerabilities
                min_confidence_threshold = self.min_confidence
                if vulnerability['severity'] == 'critical':
                    min_confidence_threshold = max(min_confidence_threshold, 0.85)  # Higher threshold for critical issues
                elif vulnerability['severity'] == 'high':
                    min_confidence_threshold = max(min_confidence_threshold, 0.8)   # Higher threshold for high issues
                        
                if vulnerability['confidence'] >= min_confidence_threshold:
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
    
    def _find_pattern_matches(self, code: str, patterns: List[str], anti_patterns: List[str] = None) -> List[Dict[str, Any]]:
        """Find all matches for given patterns, excluding those that match anti-patterns"""
        matches = []
        lines = code.split('\n')
        
        # Compile anti-patterns for efficiency
        anti_pattern_regexes = [re.compile(pattern, re.IGNORECASE) for pattern in anti_patterns or []]
        
        for pattern in patterns:
            regex = re.compile(pattern, re.IGNORECASE)
            for line_num, line in enumerate(lines, 1):
                if regex.search(line):
                    # Check if line matches any anti-patterns
                    if anti_pattern_regexes:
                        anti_match = False
                        for anti_regex in anti_pattern_regexes:
                            if anti_regex.search(line):
                                anti_match = True
                                break
                        if anti_match:
                            continue  # Skip this match as it matches an anti-pattern
                    
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
            # Check for external calls
            if re.search(r'\.call|\.send|\.transfer|delegatecall', window, re.IGNORECASE):
                score += 2  # Higher weight for external calls
            # Check for state variables
            if re.search(r'balance|balances\[|totalSupply|mapping', window):
                score += 1
            # Check for missing security patterns
            if not re.search(r'checks-effects-interactions|CEI', code, re.IGNORECASE):
                score += 1
            # Check for reentrancy guard absence
            if not re.search(r'nonReentrant|ReentrancyGuard', code, re.IGNORECASE):
                score += 1
        elif vuln_type == 'integer_overflow':
            # Check for integer types
            if re.search(r'\buint(8|16|32|64|128|256)?\b', window):
                score += 2  # Higher weight for integer types
            # Check for arithmetic operations
            if re.search(r'\+\=|\-\=|\*\=|\+\+|\-\-', window):
                score += 2  # Higher weight for arithmetic operations
            # Check for lack of SafeMath
            if not re.search(r'SafeMath|require\([^)]*\+[^)]*\)|checked\s*\{', window):
                score += 1
        elif vuln_type == 'access_control':
            # Check for access control mechanisms
            if re.search(r'onlyOwner|Ownable|AccessControl|hasRole|isAdmin', code):
                score -= 1  # Reduce score if access control mechanisms exist
            # Check for authorization checks
            if re.search(r'require\s*\(\s*msg\.sender\s*==\s*owner', window.replace(' ', '')):
                score -= 1  # Reduce score if authorization checks exist
            # Check for public functions without access control
            function_lines = [line for line in window.split('\n') if 'function' in line and 'public' in line]
            if function_lines and not any(re.search(r'onlyOwner|onlyAdmin|hasRole', line) for line in function_lines):
                score += 2  # Higher weight for public functions without access control
        
        return max(0, score)  # Ensure non-negative score

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

    def _is_likely_false_positive(self, vuln_type: str, code: str, line_number: int) -> bool:
        """Apply additional checks to identify likely false positives"""
        bounds = self._get_enclosing_function_bounds(code, line_number)
        window = '\n'.join(code.split('\n')[bounds['start'] - 1:bounds['end']])
        
        if vuln_type == 'reentrancy':
            # Check if the pattern is in a view/pure function (cannot modify state)
            function_line = ''
            lines = code.split('\n')
            for i in range(max(0, line_number - 20), line_number):
                if i < len(lines) and re.search(r'function\s+\w+\s*\(', lines[i]):
                    function_line = lines[i]
                    break
            
            if 'view' in function_line or 'pure' in function_line:
                return True  # View/pure functions cannot have reentrancy issues
            
            # Check if there's a state change after the external call
            lines = window.split('\n')
            external_call_found = False
            for line in lines:
                if re.search(r'\.(?:call|send|transfer)\s*\(', line):
                    external_call_found = True
                elif external_call_found and re.search(r'\w+\s*=|\w+\s*[-+*/]=|\w+\s*\+\+', line):
                    # State change found after external call
                    return False
            
            # If no state change after external call, likely a false positive
            if external_call_found:
                return True
        
        elif vuln_type == 'integer_overflow':
            # Check if the operation is within a require statement (validation, not vulnerability)
            lines = code.split('\n')
            if line_number <= len(lines):
                line = lines[line_number - 1]
                # Look for the line in a require context
                context_start = max(0, line_number - 5)
                context_end = min(len(lines), line_number + 5)
                context = '\n'.join(lines[context_start:context_end])
                
                if 'require(' in context and line in context:
                    # Likely a validation check, not a vulnerability
                    return True
        
        elif vuln_type == 'access_control':
            # Check if this is in a constructor (not a vulnerability after deployment)
            lines = code.split('\n')
            context_start = max(0, line_number - 20)
            context = '\n'.join(lines[context_start:line_number])
            
            if 'constructor(' in context:
                return True  # Setting initial state in constructor is not a vulnerability
        
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
    
    def _get_context_window(self, code: str, line_number: int, window_size: int = 15) -> str:
        """Get a context window around the vulnerable line"""
        lines = code.split('\n')
        start = max(0, line_number - window_size - 1)
        end = min(len(lines), line_number + window_size)
        return '\n'.join(lines[start:end])
    
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
    
    def _calculate_confidence(self, vuln_type: str, line_content: str, context_window: str = "") -> float:
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
        
        # Additional context-based adjustments
        if context_window:
            # Check for security-related keywords that might indicate proper handling
            security_keywords = ['nonReentrant', 'onlyOwner', 'SafeMath', 'require', 'assert', 'check']
            security_matches = sum(1 for keyword in security_keywords if keyword in context_window)
            if security_matches > 0:
                base_confidence *= (0.9 ** security_matches)  # Reduce confidence for each security keyword
        
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

    def apply_program_scope(self, findings: List[Dict[str, Any]], program_scope: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Filter or adjust findings based on bug bounty program scope.
        program_scope example:
        {
          "focus_areas": ["reentrancy", "access_control"],
          "in_scope": ["smart_contract", "solidity"],
          "out_of_scope": ["web", "mobile"],
          "in_scope_vulns": ["reentrancy", "integer_overflow"],
          "out_of_scope_vulns": ["dos_gas_limit"],
          "rules": ["no_mainnet_exploits"],
          "disclosure": "coordinated"
        }
        """
        if not program_scope:
            return findings

        in_scope_vulns = set([v.lower() for v in program_scope.get('in_scope_vulns', [])])
        out_of_scope_vulns = set([v.lower() for v in program_scope.get('out_of_scope_vulns', [])])
        focus_areas = set([v.lower() for v in program_scope.get('focus_areas', [])])
        # Extended schema
        severity_allow = {k.lower(): set([s.lower() for s in v]) for k, v in program_scope.get('severity_allow', {}).items()}  # { vuln_type: [severities...] }
        path_include = [p for p in program_scope.get('path_include', [])]  # substrings or globs (basic substr)
        path_exclude = [p for p in program_scope.get('path_exclude', [])]
        reject_if = [r.lower() for r in program_scope.get('reject_if', [])]  # simple rule keywords

        filtered: List[Dict[str, Any]] = []
        for f in findings:
            vtype = f.get('type', '').lower()
            file_path = f.get('file_path', '')
            severity = (f.get('severity') or 'low').lower()

            # Path-based include/exclude
            if path_include and not any(seg in file_path for seg in path_include):
                continue
            if path_exclude and any(seg in file_path for seg in path_exclude):
                continue

            # Reject rules (e.g., "no_mainnet_exploits") can be extended; here we just tag
            if reject_if:
                f_rules = ' '.join(reject_if)
                if 'no_mainnet_exploits' in f_rules:
                    # example: downgrade issues that imply on-chain active exploitation
                    if 'poc' in f and f['poc']:
                        f = f.copy()
                        f['poc'] = None
            # Exclude explicit out-of-scope vulnerability types
            if vtype in out_of_scope_vulns:
                continue
            # If in-scope vulns specified, keep only those
            if in_scope_vulns and vtype not in in_scope_vulns:
                # downgrade severity instead of dropping completely
                downgraded = f.copy()
                downgraded['severity'] = 'low'
                downgraded['confidence'] = min(downgraded.get('confidence', 0.6), 0.6)
                filtered.append(downgraded)
                continue
            # Severity allowlist per vuln type
            if severity_allow:
                allowed = severity_allow.get(vtype)
                if allowed and severity not in allowed:
                    downgraded = f.copy()
                    downgraded['severity'] = 'low'
                    downgraded['confidence'] = min(downgraded.get('confidence', 0.6), 0.6)
                    filtered.append(downgraded)
                    continue
            # Slightly boost confidence for focus areas
            boosted = f.copy()
            if vtype in focus_areas:
                boosted['confidence'] = min(boosted.get('confidence', 0.7) * 1.1, 1.0)
            filtered.append(boosted)

        return filtered

