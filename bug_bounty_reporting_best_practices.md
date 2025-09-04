# Bug Bounty Reporting Best Practices

Effective bug bounty reports are crucial for clear communication with program owners and successful vulnerability submissions. Based on various resources, here are the key elements and best practices for writing high-quality bug bounty reports:

## I. Essential Elements of a Bug Bounty Report

1.  **Clear and Concise Title:** The title should accurately reflect the vulnerability, making it easy to understand at a glance (e.g., "Reentrancy Vulnerability in `transfer` function").

2.  **Vulnerability Summary:** A brief overview of the vulnerability, its type, and its potential impact. This provides immediate context for the triager.

3.  **Steps to Reproduce (STR):** This is the most critical section. It must be a precise, step-by-step guide that allows anyone to reproduce the vulnerability. Include:
    *   **Prerequisites:** Any setup required (e.g., specific environment, tools, accounts).
    *   **Actions:** Each step should be clearly numbered and describe the exact actions taken.
    *   **Expected Result:** What should happen if the vulnerability were not present.
    *   **Actual Result:** What actually happens, demonstrating the vulnerability.

4.  **Proof of Concept (POC):** A working demonstration of the vulnerability. For smart contracts, this could be:
    *   **Code Snippets:** Relevant lines of code from the vulnerable contract.
    *   **Exploit Code:** A minimal, runnable script (e.g., Python, JavaScript using web3.js/ethers.js) that triggers the vulnerability.
    *   **Transaction Hashes:** Links to transactions on a blockchain explorer that demonstrate the exploit.
    *   **Visual Aids:** Screenshots, screen recordings, or diagrams that clearly illustrate the steps and the impact. These are highly recommended.

5.  **Impact:** Clearly explain the potential consequences of the vulnerability. This helps the program owner understand the severity and prioritize the fix. Examples of impact include:
    *   Loss of funds (e.g., draining contract balance).
    *   Unauthorized access or privilege escalation.
    *   Denial of Service (DoS).
    *   Data manipulation or theft.
    *   Reputation damage.

6.  **Affected Components/Systems:** Specify which parts of the smart contract, functions, or related systems are affected by the vulnerability.

7.  **Environment Details:** Provide information about the environment where the bug was found, such as:
    *   Blockchain network (e.g., Ethereum Mainnet, Ropsten Testnet).
    *   Contract address.
    *   Compiler version (e.g., Solidity 0.8.0).
    *   Tools used (e.g., Remix, Truffle, Hardhat).
    *   Browser and OS (if applicable for web interfaces).

8.  **Suggested Mitigation/Fix (Optional but Recommended):** While not always required, providing a potential solution demonstrates a deeper understanding of the vulnerability and can be highly valued by the program owner.

## II. General Best Practices

*   **Read the Scope:** Always understand the program's scope and rules before testing and reporting.
*   **Be Detailed and Unambiguous:** Provide comprehensive details, leaving no room for misinterpretation.
*   **Focus on Impact:** Clearly articulate the real-world impact of the vulnerability.
*   **Quality over Quantity:** A single, well-documented critical vulnerability is better than multiple poorly reported low-severity issues.
*   **Be Professional:** Maintain a respectful and professional tone throughout the report.
*   **Avoid Tool Names:** When generating reports based on automated scans, present findings as if discovered through manual analysis or other unspecified methods. Do not explicitly mention the name of the scanning tool used.
*   **Timely Submission:** Submit reports promptly after discovery.
*   **Follow-up:** Be prepared to answer questions and provide additional information if requested by the program owner.

By adhering to these best practices, bug bounty hunters can significantly increase the chances of their reports being accepted and rewarded.

