// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract VulnerableWallet {
    mapping(address => uint256) public balances;
    address public owner;
    bool private locked;

    constructor() {
        owner = msg.sender;
    }

    modifier onlyOwner() {
        require(msg.sender == owner, "Not owner");
        _;
    }

    modifier noReentrancy() {
        require(!locked, "ReentrancyGuard: reentrant call");
        locked = true;
        _;
        locked = false;
    }

    function deposit() public payable {
        balances[msg.sender] += msg.value;
    }

    // Vulnerable function - reentrancy issue (no reentrancy guard)
    function withdraw(uint256 amount) public {
        require(balances[msg.sender] >= amount, "Insufficient balance");
        balances[msg.sender] -= amount;
        payable(msg.sender).call{value: amount}(""); // Vulnerable to reentrancy
    }

    // Another vulnerable function - reentrancy with state change after external call
    function vulnerableTransfer(address to, uint256 amount) public {
        require(balances[msg.sender] >= amount, "Insufficient balance");
        balances[msg.sender] -= amount;
        (bool success, ) = to.call{value: amount}(""); // External call
        require(success, "Transfer failed");
        balances[to] += amount; // State change after external call - vulnerable to reentrancy
    }

    // Vulnerable function - integer overflow/underflow (without SafeMath)
    function unsafeAdd(uint256 a, uint256 b) public pure returns (uint256) {
        return a + b; // Could overflow
    }

    function unsafeSubtract(uint256 a, uint256 b) public pure returns (uint256) {
        return a - b; // Could underflow
    }

    // Vulnerable function - access control
    function setOwner(address newOwner) public {
        owner = newOwner; // Missing access control
    }

    // Vulnerable function - unchecked external call
    function unsafeCall(address target, bytes memory data) public {
        (bool success, ) = target.call(data); // Unchecked call
    }

    receive() external payable {}
}