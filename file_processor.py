import os
import re
import hashlib
from typing import List, Dict, Any, Optional

class FileProcessor:
    """Utility class for processing smart contract files"""
    
    @staticmethod
    def is_solidity_file(filename: str) -> bool:
        """Check if file is a Solidity file"""
        return filename.lower().endswith(('.sol', '.solidity'))
    
    @staticmethod
    def extract_contract_info(content: str, filename: str = "") -> Dict[str, Any]:
        """Extract basic information from Solidity contract"""
        info = {
            'filename': filename,
            'contracts': [],
            'imports': [],
            'pragma': [],
            'functions': [],
            'modifiers': [],
            'events': [],
            'errors': [],
            'lines_of_code': len(content.split('\n')),
            'file_hash': hashlib.md5(content.encode()).hexdigest()
        }
        
        # Extract pragma statements
        pragma_matches = re.findall(r'pragma\s+solidity\s+([^;]+);', content)
        info['pragma'] = pragma_matches
        
        # Extract imports
        import_matches = re.findall(r'import\s+["\']([^"\']+)["\'];', content)
        info['imports'] = import_matches
        
        # Extract contract names
        contract_matches = re.findall(r'(?:contract|library|interface)\s+(\w+)', content)
        info['contracts'] = contract_matches
        
        # Extract function signatures
        function_matches = re.findall(r'function\s+(\w+)\s*\([^)]*\)(?:\s+\w+)*(?:\s+returns\s*\([^)]*\))?', content)
        info['functions'] = function_matches
        
        # Extract modifiers
        modifier_matches = re.findall(r'modifier\s+(\w+)', content)
        info['modifiers'] = modifier_matches
        
        # Extract events
        event_matches = re.findall(r'event\s+(\w+)', content)
        info['events'] = event_matches
        
        # Extract custom errors (Solidity 0.8.4+)
        error_matches = re.findall(r'error\s+(\w+)', content)
        info['errors'] = error_matches
        
        return info
    
    @staticmethod
    def validate_solidity_syntax(content: str) -> Dict[str, Any]:
        """Basic Solidity syntax validation"""
        validation = {
            'valid': True,
            'errors': [],
            'warnings': []
        }
        
        lines = content.split('\n')
        
        # Check for basic syntax issues
        brace_count = 0
        paren_count = 0
        
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            
            # Skip comments
            if line.startswith('//') or line.startswith('/*') or line.startswith('*'):
                continue
            
            # Count braces and parentheses
            brace_count += line.count('{') - line.count('}')
            paren_count += line.count('(') - line.count(')')
            
            # Check for common syntax errors
            if line.endswith('{') and not line.startswith('//'):
                # Check if line before opening brace has proper structure
                if not re.search(r'(function|modifier|if|for|while|contract|library|interface|struct|enum)', line):
                    validation['warnings'].append(f"Line {line_num}: Unusual opening brace usage")
            
            # Check for missing semicolons (basic check)
            if (line and not line.endswith((';', '{', '}', ')', '*/')) and 
                not line.startswith(('pragma', 'import', 'contract', 'library', 'interface', '//', '/*', '*')) and
                not re.search(r'(if|for|while|function|modifier|event|error)\s*\(', line)):
                validation['warnings'].append(f"Line {line_num}: Possible missing semicolon")
        
        # Check for unmatched braces
        if brace_count != 0:
            validation['valid'] = False
            validation['errors'].append(f"Unmatched braces: {brace_count} extra {'opening' if brace_count > 0 else 'closing'} braces")
        
        # Check for unmatched parentheses
        if paren_count != 0:
            validation['valid'] = False
            validation['errors'].append(f"Unmatched parentheses: {paren_count} extra {'opening' if paren_count > 0 else 'closing'} parentheses")
        
        return validation
    
    @staticmethod
    def extract_functions_with_context(content: str) -> List[Dict[str, Any]]:
        """Extract functions with their full context"""
        functions = []
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines):
            # Look for function declarations
            function_match = re.search(r'function\s+(\w+)\s*\(([^)]*)\)(?:\s+(\w+))*(?:\s+returns\s*\(([^)]*)\))?', line)
            if function_match:
                function_name = function_match.group(1)
                parameters = function_match.group(2)
                visibility = function_match.group(3) or 'internal'
                returns = function_match.group(4) or ''
                
                # Extract function body
                body_start = line_num
                brace_count = 0
                body_lines = []
                
                for i in range(line_num, len(lines)):
                    body_lines.append(lines[i])
                    brace_count += lines[i].count('{') - lines[i].count('}')
                    
                    if brace_count == 0 and '{' in lines[i]:
                        break
                
                functions.append({
                    'name': function_name,
                    'parameters': parameters.strip(),
                    'visibility': visibility,
                    'returns': returns.strip(),
                    'line_start': line_num + 1,
                    'line_end': line_num + len(body_lines),
                    'body': '\n'.join(body_lines)
                })
        
        return functions
    
    @staticmethod
    def calculate_complexity_metrics(content: str) -> Dict[str, int]:
        """Calculate basic complexity metrics"""
        metrics = {
            'cyclomatic_complexity': 1,  # Base complexity
            'function_count': 0,
            'modifier_count': 0,
            'external_calls': 0,
            'loops': 0,
            'conditionals': 0,
            'state_variables': 0
        }
        
        # Count functions
        metrics['function_count'] = len(re.findall(r'function\s+\w+', content))
        
        # Count modifiers
        metrics['modifier_count'] = len(re.findall(r'modifier\s+\w+', content))
        
        # Count external calls
        metrics['external_calls'] = len(re.findall(r'\.call\(|\.send\(|\.transfer\(|\.delegatecall\(', content))
        
        # Count loops
        metrics['loops'] = len(re.findall(r'for\s*\(|while\s*\(', content))
        
        # Count conditionals
        metrics['conditionals'] = len(re.findall(r'if\s*\(|else\s+if\s*\(', content))
        
        # Count state variables (basic heuristic)
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if (re.match(r'(uint|int|bool|address|string|bytes)\d*\s+\w+', line) and
                not line.startswith('function') and
                not line.startswith('mapping') and
                ';' in line):
                metrics['state_variables'] += 1
        
        # Calculate cyclomatic complexity
        metrics['cyclomatic_complexity'] = (1 + metrics['conditionals'] + 
                                          metrics['loops'] + 
                                          metrics['function_count'])
        
        return metrics
    
    @staticmethod
    def find_potential_entry_points(content: str) -> List[Dict[str, Any]]:
        """Find potential entry points for attacks"""
        entry_points = []
        
        # Find public/external functions
        public_functions = re.findall(r'function\s+(\w+)\s*\([^)]*\)\s+(public|external)', content)
        for func_name, visibility in public_functions:
            entry_points.append({
                'type': 'function',
                'name': func_name,
                'visibility': visibility,
                'risk': 'medium'
            })
        
        # Find payable functions
        payable_functions = re.findall(r'function\s+(\w+)\s*\([^)]*\).*payable', content)
        for func_name in payable_functions:
            entry_points.append({
                'type': 'payable_function',
                'name': func_name,
                'visibility': 'public',
                'risk': 'high'
            })
        
        # Find fallback/receive functions
        if 'fallback()' in content or 'receive()' in content:
            entry_points.append({
                'type': 'fallback',
                'name': 'fallback/receive',
                'visibility': 'external',
                'risk': 'high'
            })
        
        return entry_points
    
    @staticmethod
    def extract_dependencies(content: str) -> Dict[str, List[str]]:
        """Extract contract dependencies"""
        dependencies = {
            'imports': [],
            'inheritance': [],
            'interfaces': [],
            'libraries': []
        }
        
        # Extract imports
        import_matches = re.findall(r'import\s+["\']([^"\']+)["\'];', content)
        dependencies['imports'] = import_matches
        
        # Extract inheritance
        inheritance_matches = re.findall(r'contract\s+\w+\s+is\s+([^{]+)', content)
        for match in inheritance_matches:
            parents = [p.strip() for p in match.split(',')]
            dependencies['inheritance'].extend(parents)
        
        # Extract interface usage
        interface_matches = re.findall(r'interface\s+(\w+)', content)
        dependencies['interfaces'] = interface_matches
        
        # Extract library usage
        library_matches = re.findall(r'using\s+(\w+)\s+for', content)
        dependencies['libraries'] = library_matches
        
        return dependencies

