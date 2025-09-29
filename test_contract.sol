pragma solidity ^0.8.0;

contract TestContract {
    mapping(address => uint256) public balances;
    
    // This is a vulnerable function with a reentrancy issue
    function withdraw(uint256 amount) public {
        require(balances[msg.sender] >= amount, "Insufficient balance");
        balances[msg.sender] -= amount;
        (bool success, ) = msg.sender.call{value: amount}("");
        require(success, "Transfer failed");
    }
    
    // This is a safe function using the checks-effects-interactions pattern
    function safeWithdraw(uint256 amount) public {
        require(balances[msg.sender] >= amount, "Insufficient balance");
        uint256 balanceBefore = balances[msg.sender];
        balances[msg.sender] -= amount;
        (bool success, ) = msg.sender.call{value: amount}("");
        require(success, "Transfer failed");
        // Additional check to ensure balance was properly updated
        assert(balances[msg.sender] == balanceBefore - amount);
    }
    
    // This is a safe function with reentrancy guard
    function guardedWithdraw(uint256 amount) public {
        require(balances[msg.sender] >= amount, "Insufficient balance");
        balances[msg.sender] -= amount;
        // Simulate reentrancy guard
        bool _reentrancyGuard = true;
        require(_reentrancyGuard, "ReentrancyGuard: reentrant call");
        (bool success, ) = msg.sender.call{value: amount}("");
        require(success, "Transfer failed");
        _reentrancyGuard = false;
    }
    
    // This is a view function that should not trigger reentrancy warnings
    function getBalance() public view returns (uint256) {
        address(this).call(""); // This should not be flagged
        return balances[msg.sender];
    }
    
    // This is a validation check that should not trigger overflow warnings
    function validateAmount(uint256 a, uint256 b) public pure {
        require(a + b > 0, "Amounts must be positive"); // This is validation, not vulnerability
    }
    
    // This is a vulnerable function with access control issues
    function dangerousFunction() public {
        selfdestruct(payable(msg.sender)); // Unprotected self-destruct
    }
    
    // This is a safe function with access control
    address public owner;
    
    constructor() {
        owner = msg.sender;
    }
    
    function safeFunction() public {
        require(msg.sender == owner, "Not authorized");
        selfdestruct(payable(msg.sender)); // Protected self-destruct
    }
}