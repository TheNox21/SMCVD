import os
from typing import Dict, Any, List, Optional
import json
import re


class AIService:
    def __init__(self):
        # Initialize default values
        self.client = None
        self.model = "gpt-4o-mini"
        self.max_tokens = 1200
        self.temperature = 0.2
        self.timeout = 30
        
        # Check if AI is enabled
        self.ai_enabled = os.getenv('ENABLE_AI', 'true').lower() == 'true'
        
        if not self.ai_enabled:
            return
            
        # Try to use centralized config first, fallback to env vars
        try:
            from src.config.settings import config
            # Safely access config attributes
            if hasattr(config, 'ai'):
                ai_config = config.ai
                api_key = getattr(ai_config, 'openai_api_key', None)
                self.model = getattr(ai_config, 'openai_model', os.getenv("OPENAI_MODEL", "gpt-4o-mini"))
                self.max_tokens = getattr(ai_config, 'max_tokens', int(os.getenv("AI_MAX_TOKENS", "1200")))
                self.temperature = getattr(ai_config, 'temperature', float(os.getenv("AI_TEMPERATURE", "0.2")))
                self.timeout = getattr(ai_config, 'timeout', int(os.getenv("AI_TIMEOUT", "30")))
            else:
                api_key = os.getenv('OPENAI_API_KEY')
                self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
                self.max_tokens = int(os.getenv("AI_MAX_TOKENS", "1200"))
                self.temperature = float(os.getenv("AI_TEMPERATURE", "0.2"))
                self.timeout = int(os.getenv("AI_TIMEOUT", "30"))
            
            # Initialize OpenAI client if API key is available
            if api_key:
                from openai import OpenAI
                self.client = OpenAI(api_key=api_key)
        except ImportError:
            # Fallback to environment variables
            api_key = os.getenv('OPENAI_API_KEY')
            self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
            self.max_tokens = int(os.getenv("AI_MAX_TOKENS", "1200"))
            self.temperature = float(os.getenv("AI_TEMPERATURE", "0.2"))
            self.timeout = int(os.getenv("AI_TIMEOUT", "30"))
            
            if api_key:
                from openai import OpenAI
                self.client = OpenAI(api_key=api_key)
    
    def enhance_vulnerability(self, vulnerability: Dict[str, Any], contract_code: str, program_scope: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Enhance vulnerability with AI analysis and generate POC"""
        # If AI is disabled or client is not available, return original vulnerability
        if not self.ai_enabled or not self.client:
            # Even without AI, we can still generate basic PoC for common vulnerabilities
            enhanced_vuln = vulnerability.copy()
            enhanced_vuln['poc_code'] = self._generate_basic_poc(vulnerability, contract_code)
            return enhanced_vuln
            
        try:
            # Create prompt for vulnerability analysis
            prompt = self._create_vulnerability_prompt(vulnerability, contract_code, program_scope=program_scope if program_scope is not None else {})
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a smart contract security expert. Respond in compact JSON unless asked otherwise."},
                    {"role": "user", "content": prompt + "\nOutput strictly as JSON with keys: detailed_description, attack_scenarios, recommended_fix, poc_code."}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                timeout=self.timeout
            )

            # Handle potential None response
            ai_text = response.choices[0].message.content if response.choices[0].message.content else ""

            # Prefer strict JSON parsing; fallback to regex extraction
            structured = self._safe_json_loads(ai_text) if ai_text else None
            enhanced_vuln = vulnerability.copy()
            if structured:
                enhanced_vuln.update({
                    'ai_analysis': ai_text,
                    'detailed_description': structured.get('detailed_description', ''),
                    'attack_scenarios': structured.get('attack_scenarios', ''),
                    'recommended_fix': structured.get('recommended_fix', ''),
                    'poc_code': structured.get('poc_code', self._generate_basic_poc(vulnerability, contract_code))
                })
            else:
                parsed_response = self._parse_ai_response(ai_text, vulnerability['type']) if ai_text else {}
                # Ensure we always have a PoC
                if 'poc_code' not in parsed_response or not parsed_response['poc_code']:
                    parsed_response['poc_code'] = self._generate_basic_poc(vulnerability, contract_code)
                enhanced_vuln.update(parsed_response)
            
            return enhanced_vuln
            
        except Exception as e:
            # Return original vulnerability with basic PoC if AI enhancement fails
            vulnerability['ai_error'] = f"AI enhancement failed: {str(e)}"
            vulnerability['poc_code'] = self._generate_basic_poc(vulnerability, contract_code)
            return vulnerability
    
    def generate_poc(self, vulnerability: Dict[str, Any], contract_code: str) -> str:
        """Generate proof-of-concept exploit code"""
        # If AI is disabled or client is not available, generate basic PoC
        if not self.ai_enabled or not self.client:
            return self._generate_basic_poc(vulnerability, contract_code)
            
        try:
            prompt = f"""
            Generate a detailed proof-of-concept exploit for this smart contract vulnerability:
            
            Vulnerability: {vulnerability['name']}
            Type: {vulnerability['type']}
            Severity: {vulnerability['severity']}
            Description: {vulnerability['description']}
            
            Vulnerable code line: {vulnerability['line_content']}
            Function: {vulnerability['function_name']}
            
            Contract code snippet:
            {self._extract_relevant_code(contract_code, vulnerability['line_number'])}
            
            Please provide a COMPLETE working exploit with:
            1. A complete Solidity contract that demonstrates the vulnerability (if applicable)
            2. A JavaScript exploit script using ethers.js that shows how to exploit it
            3. Step-by-step explanation of the attack vector
            4. Expected outcome/impact
            5. How to prevent this vulnerability
            
            Format the response as a JSON object with keys: 'solidity_poc', 'exploit_code', 'explanation', 'impact', 'prevention'.
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a smart contract security researcher. Output compact JSON only."},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature * 0.75,  # Slightly lower for POC generation
                max_tokens=self.max_tokens,  # Use full tokens for detailed POC
                timeout=self.timeout
            )

            # Handle potential None response
            content = response.choices[0].message.content if response.choices[0].message.content else ""
            return content
            
        except Exception as e:
            # Fallback to basic PoC generation
            return self._generate_basic_poc(vulnerability, contract_code)
    
    def get_overall_assessment(self, vulnerabilities: List[Dict[str, Any]], program_scope: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get overall security assessment from AI"""
        # If AI is disabled or client is not available, return a basic assessment
        if not self.ai_enabled or not self.client:
            risk_level = self._calculate_overall_risk(vulnerabilities) if vulnerabilities else 'low'
            return {
                'risk_level': risk_level,
                'summary': f'Basic assessment (AI disabled): {len(vulnerabilities)} vulnerabilities found.',
                'recommendations': ['Review all identified vulnerabilities', 'Implement security best practices'],
                'financial_impact': 'Unknown (AI assessment disabled)'
            }
            
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
            
            scope_text = json.dumps(program_scope, indent=2) if program_scope else "{}"
            prompt = f"""
            Analyze this smart contract security assessment and provide an overall evaluation:
            
            Vulnerabilities found: {len(vulnerabilities)}
            
            Vulnerability breakdown:
            {json.dumps(vuln_summary, indent=2)}
            
            Program scope (guidance for relevance and acceptance criteria):
            {scope_text}

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
                    {"role": "system", "content": "You are a senior smart contract auditor. Provide JSON only."},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
                max_tokens=int(self.max_tokens * 0.75),  # 75% for assessment
                timeout=self.timeout
            )
            
            # Handle potential None response
            content = response.choices[0].message.content if response.choices[0].message.content else ""
            
            try:
                return json.loads(content) if content else {}
            except json.JSONDecodeError:
                # Fallback if JSON parsing fails
                return {
                    'risk_level': self._calculate_overall_risk(vulnerabilities),
                    'summary': content,
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
    
    def _create_vulnerability_prompt(self, vulnerability: Dict[str, Any], contract_code: str, program_scope: Optional[Dict[str, Any]] = None) -> str:
        """Create prompt for vulnerability analysis"""
        relevant_code = self._extract_relevant_code(contract_code, vulnerability['line_number'])
        
        scope_text = json.dumps(program_scope, indent=2) if program_scope else "{}"
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
        
        Program scope (to tailor relevance and acceptance):
        {scope_text}

        Please provide:
        1. Detailed technical explanation of the vulnerability
        2. Specific attack scenarios with concrete examples
        3. Potential impact and consequences with monetary estimates if applicable
        4. Recommended fixes and mitigations with code examples
        5. A COMPLETE working proof-of-concept exploit including:
           - Solidity contract demonstrating the vulnerability (if applicable)
           - JavaScript exploit script using ethers.js
           - Step-by-step attack explanation
           - Expected outcome
        
        Focus on practical, actionable insights for bug bounty reporting.
        """
    
    def _extract_relevant_code(self, contract_code: str, line_number: int, context_lines: int = 15) -> str:
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
            'detailed_description': self._extract_section(ai_response, 'detailed|explanation'),
            'attack_scenarios': self._extract_section(ai_response, 'attack|scenario'),
            'recommended_fix': self._extract_section(ai_response, 'fix|mitigation|recommendation'),
            'poc_code': self._extract_section(ai_response, 'proof|poc|exploit')
        }
        
        return enhanced_data
    
    def _extract_section(self, text: str, pattern: str) -> str:
        """Extract specific section from AI response"""
        # Look for section headers
        section_match = re.search(f'({pattern})[:\n]([^#]*?)(?=\n#|\n\\d+\.|\Z)', text, re.IGNORECASE | re.DOTALL)
        if section_match:
            return section_match.group(2).strip()
        
        return ""

    def _safe_json_loads(self, text: str):
        try:
            return json.loads(text)
        except Exception:
            # Try to find a JSON object within text
            try:
                start = text.find('{')
                end = text.rfind('}')
                if start != -1 and end != -1 and end > start:
                    return json.loads(text[start:end+1])
            except Exception:
                return None
        return None
    
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
    
    def _generate_basic_poc(self, vulnerability: Dict[str, Any], contract_code: str) -> str:
        """Generate a basic proof-of-concept for common vulnerabilities"""
        vuln_type = vulnerability.get('type', '').lower()
        
        if vuln_type == 'timestamp_dependence':
            return self._generate_timestamp_poc()
        elif vuln_type == 'unchecked_external_call':
            return self._generate_unchecked_call_poc()
        elif vuln_type == 'reentrancy':
            return self._generate_reentrancy_poc()
        elif vuln_type == 'integer_overflow':
            return self._generate_overflow_poc()
        else:
            # Generic template
            return f"""
// Generic PoC for {vulnerability.get('name', 'Unknown Vulnerability')}
// Vulnerable line: {vulnerability.get('line_content', 'N/A')}
// File: {vulnerability.get('file_path', 'N/A')}
// Line: {vulnerability.get('line_number', 'N/A')}

/*
Exploitation Steps:
1. Identify the vulnerable function
2. Craft malicious input/data
3. Execute the function with malicious data
4. Observe the unexpected behavior

Impact:
{vulnerability.get('impact', 'See vulnerability description')}

Prevention:
{vulnerability.get('mitigation', 'See recommended fixes')}
*/
"""
    
    def _generate_timestamp_poc(self) -> str:
        """Generate PoC for timestamp dependence vulnerability"""
        return """
// Timestamp Dependence Vulnerability PoC
/*
Exploitation Steps:
1. Miner manipulates block.timestamp within allowed range
2. Contract logic dependent on timestamp behaves unexpectedly
3. Attacker profits from the manipulation

Example Vulnerable Code:
function withdraw() public {
    require(block.timestamp > unlockTime); // Vulnerable to timestamp manipulation
    msg.sender.transfer(address(this).balance);
}

Impact:
- Financial loss due to early withdrawals
- Unfair advantage in time-based mechanisms
- Manipulation of auction/lottery outcomes

Prevention:
- Use block.number instead of block.timestamp
- Implement additional validation checks
- Use commit-reveal schemes for critical timing
*/

// Exploit Script (JavaScript with ethers.js)
/*
const exploit = async () => {
    // Miner can manipulate timestamp to bypass time checks
    // This is more of a theoretical exploit as it requires miner cooperation
    console.log("Miner manipulation required for exploitation");
};
*/
"""
    
    def _generate_unchecked_call_poc(self) -> str:
        """Generate PoC for unchecked external call vulnerability"""
        return """
// Unchecked External Call Vulnerability PoC
/*
Vulnerable Pattern:
(bool success, ) = target.call(data);
// Missing: require(success);

Exploitation Steps:
1. Target contract's fallback function fails/reverts
2. Current contract continues execution despite failure
3. Unexpected state changes occur

Impact:
- Silent failures leading to inconsistent state
- Financial loss due to failed transfers
- Logic errors in contract flow

Prevention:
Always check return values:
(bool success, ) = target.call(data);
require(success, "External call failed");
*/

// Exploit Contract
contract Exploiter {
    address vulnerableContract;
    
    constructor(address _target) {
        vulnerableContract = _target;
    }
    
    // Fallback function that always fails
    fallback() external payable {
        revert("Intentional failure");
    }
    
    function demonstrateExploit() public {
        // This call will fail but might not be checked
        (bool success, ) = vulnerableContract.call(
            abi.encodeWithSignature("vulnerableFunction()")
        );
        // If unchecked, contract continues execution
        // even though the call failed
    }
}

// Exploit Script (JavaScript with ethers.js)
/*
const exploit = async () => {
    const exploiter = new ethers.Contract(exploiterAddress, exploiterABI, signer);
    await exploiter.demonstrateExploit();
    console.log("Exploit executed - check for inconsistent state");
};
*/
"""
    
    def _generate_reentrancy_poc(self) -> str:
        """Generate PoC for reentrancy vulnerability"""
        return """
// Reentrancy Vulnerability PoC
/*
Vulnerable Pattern:
function withdraw(uint amount) public {
    require(balances[msg.sender] >= amount);
    msg.sender.call.value(amount)("");  // External call first
    balances[msg.sender] -= amount;     // State change after
}

Exploitation Steps:
1. Create malicious contract with fallback function
2. Call withdraw function
3. In fallback, recursively call withdraw again
4. Drain contract balance before state update

Impact:
- Complete drainage of contract funds
- Loss of all user deposits
- Contract becomes insolvent

Prevention:
- Use Checks-Effects-Interactions pattern
- Implement reentrancy guards (nonReentrant modifier)
*/

// Vulnerable Contract (Simplified)
contract VulnerableBank {
    mapping(address => uint) public balances;
    
    function deposit() public payable {
        balances[msg.sender] += msg.value;
    }
    
    function withdraw(uint amount) public {
        require(balances[msg.sender] >= amount);
        msg.sender.call.value(amount)("");  // Vulnerable!
        balances[msg.sender] -= amount;
    }
}

// Exploit Contract
contract ReentrancyAttacker {
    address vulnerableBank;
    uint amount;
    bool public attackInProgress;
    
    constructor(address _bank, uint _amount) public {
        vulnerableBank = _bank;
        amount = _amount;
    }
    
    function attack() public {
        attackInProgress = true;
        // Start the attack
        VulnerableBank(vulnerableBank).withdraw(amount);
    }
    
    function () external payable {
        // Reentrant call while attackInProgress is true
        if (attackInProgress) {
            attackInProgress = false;
            // Recursive call to drain funds
            VulnerableBank(vulnerableBank).withdraw(amount);
        }
    }
}

// Exploit Script (JavaScript with ethers.js)
/*
const exploit = async () => {
    const attacker = new ethers.Contract(attackerAddress, attackerABI, signer);
    await attacker.attack();
    console.log("Reentrancy attack executed - check contract balance");
};
*/
"""
    
    def _generate_overflow_poc(self) -> str:
        """Generate PoC for integer overflow vulnerability"""
        return """
// Integer Overflow/Underflow Vulnerability PoC
/*
Vulnerable Pattern (Solidity < 0.8.0):
function transfer(address to, uint amount) public {
    balances[msg.sender] -= amount;  // Underflow risk
    balances[to] += amount;           // Overflow risk
}

Exploitation Steps:
1. Find arithmetic operations without SafeMath
2. Provide values that cause overflow/underflow
3. Manipulate balances or counters

Impact:
- Token balance manipulation
- Bypass of supply limits
- Unauthorized access through counter reset

Prevention:
- Use Solidity 0.8+ (built-in overflow protection)
- Use SafeMath library for older versions
- Add explicit overflow checks
*/

// Vulnerable Contract (Solidity < 0.8.0)
contract VulnerableToken {
    mapping(address => uint) public balances;
    uint public totalSupply;
    
    function unsafeAdd(uint a, uint b) public pure returns (uint) {
        return a + b;  // Overflow risk
    }
    
    function transfer(address to, uint amount) public {
        balances[msg.sender] -= amount;  // Underflow risk
        balances[to] += amount;           // Overflow risk
    }
}

// Exploit Script (JavaScript with ethers.js)
/*
const exploit = async () => {
    // For underflow: send more than balance
    // For overflow: cause counter to wrap around
    console.log("Exploit requires specific values to trigger overflow/underflow");
};
*/
"""