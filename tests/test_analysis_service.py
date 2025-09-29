"""
Unit tests for AnalysisService
"""
import unittest
import os
import sys

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from analysis_service import AnalysisService


class TestAnalysisService(unittest.TestCase):
    
    def setUp(self):
        self.service = AnalysisService()
    
    def test_reentrancy_detection(self):
        """Test reentrancy vulnerability detection"""
        vulnerable_code = """
        contract Vulnerable {
            mapping(address => uint) balances;
            
            function withdraw() public {
                uint amount = balances[msg.sender];
                msg.sender.call{value: amount}("");
                balances[msg.sender] = 0;
            }
        }
        """
        
        vulnerabilities = self.service.analyze_contract(vulnerable_code, "test.sol")
        
        # Should detect reentrancy vulnerability
        reentrancy_vulns = [v for v in vulnerabilities if v['type'] == 'reentrancy']
        self.assertGreater(len(reentrancy_vulns), 0, "Should detect reentrancy vulnerability")
    
    def test_safe_contract_no_false_positives(self):
        """Test that safe contracts don't trigger false positives"""
        safe_code = """
        pragma solidity ^0.8.0;
        
        import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
        
        contract Safe is ReentrancyGuard {
            mapping(address => uint256) public balances;
            
            function withdraw() external nonReentrant {
                uint256 amount = balances[msg.sender];
                require(amount > 0, "No balance");
                balances[msg.sender] = 0;
                (bool success,) = msg.sender.call{value: amount}("");
                require(success, "Transfer failed");
            }
        }
        """
        
        vulnerabilities = self.service.analyze_contract(safe_code, "safe.sol")
        
        # Should have minimal or no vulnerabilities for well-protected contract
        high_confidence_vulns = [v for v in vulnerabilities if v['confidence'] > 0.8]
        self.assertEqual(len(high_confidence_vulns), 0, "Safe contract should not have high-confidence vulnerabilities")
    
    def test_solidity_08_overflow_handling(self):
        """Test that Solidity 0.8+ contracts are not flagged for overflow issues"""
        solidity08_code = """
        pragma solidity ^0.8.0;
        
        contract Math {
            function add(uint256 a, uint256 b) public pure returns (uint256) {
                return a + b; // This is safe in 0.8+
            }
        }
        """
        
        vulnerabilities = self.service.analyze_contract(solidity08_code, "math.sol")
        
        # Should not detect integer overflow in Solidity 0.8+
        overflow_vulns = [v for v in vulnerabilities if v['type'] == 'integer_overflow']
        self.assertEqual(len(overflow_vulns), 0, "Solidity 0.8+ should not trigger overflow warnings")
    
    def test_suppression_comments(self):
        """Test inline suppression comments work"""
        code_with_suppression = """
        contract Test {
            function risky() public {
                msg.sender.call{value: 1 ether}(""); // analyzer-ignore: reentrancy
            }
        }
        """
        
        vulnerabilities = self.service.analyze_contract(code_with_suppression, "test.sol")
        
        # Should not detect reentrancy due to suppression comment
        reentrancy_vulns = [v for v in vulnerabilities if v['type'] == 'reentrancy']
        self.assertEqual(len(reentrancy_vulns), 0, "Suppression comment should prevent detection")
    
    def test_confidence_calculation(self):
        """Test that confidence calculations are reasonable"""
        code = """
        contract Test {
            function dangerous() public {
                tx.origin == msg.sender; // High confidence issue
            }
        }
        """
        
        vulnerabilities = self.service.analyze_contract(code, "test.sol")
        
        tx_origin_vulns = [v for v in vulnerabilities if v['type'] == 'tx_origin']
        self.assertGreater(len(tx_origin_vulns), 0, "Should detect tx.origin usage")
        self.assertGreater(tx_origin_vulns[0]['confidence'], 0.8, "tx.origin should have high confidence")
    
    def test_false_positive_reduction_in_view_functions(self):
        """Test that reentrancy in view functions is not flagged"""
        code = """
        contract Test {
            mapping(address => uint) public balances;
            
            function getBalance() public view returns (uint) {
                address(this).call(""); // This should not be flagged as reentrancy
                return balances[msg.sender];
            }
        }
        """
        
        vulnerabilities = self.service.analyze_contract(code, "test.sol")
        
        # Should not detect reentrancy vulnerability in view function
        reentrancy_vulns = [v for v in vulnerabilities if v['type'] == 'reentrancy']
        self.assertEqual(len(reentrancy_vulns), 0, "View functions should not trigger reentrancy warnings")
    
    def test_false_positive_reduction_with_contextual_analysis(self):
        """Test that contextual analysis reduces false positives"""
        code = """
        pragma solidity ^0.8.0;
        
        contract Test {
            function validateAmount(uint a, uint b) public pure {
                require(a + b > 0, "Amounts must be positive"); // This is validation, not vulnerability
            }
        }
        """
        
        vulnerabilities = self.service.analyze_contract(code, "test.sol")
        
        # Should not detect integer overflow in require statements (validation)
        overflow_vulns = [v for v in vulnerabilities if v['type'] == 'integer_overflow']
        self.assertEqual(len(overflow_vulns), 0, "Validation checks should not trigger overflow warnings")


if __name__ == '__main__':
    unittest.main()
