// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract SimpleWallet {
    mapping(address => uint256) public balances;
    address public owner;

    constructor() {
        owner = msg.sender;
    }

    modifier onlyOwner() {
        require(msg.sender == owner, "Not owner");
        _;
    }

    function deposit() public payable {
        balances[msg.sender] += msg.value;
    }

    function withdraw(uint256 amount) public {
        require(balances[msg.sender] >= amount, "Insufficient balance");
        balances[msg.sender] -= amount;
        payable(msg.sender).transfer(amount);
    }

    function transfer(address to, uint256 amount) public {
        require(balances[msg.sender] >= amount, "Insufficient balance");
        balances[msg.sender] -= amount;
        balances[to] += amount;
    }

    // Vulnerable function - reentrancy issue
    function vulnerableWithdraw(uint256 amount) public {
        require(balances[msg.sender] >= amount);
        payable(msg.sender).call{value: amount}("");
        balances[msg.sender] -= amount;
    }

    receive() external payable {}
}