# Common Smart Contract Vulnerabilities

Based on the search results, here are some of the most common smart contract vulnerabilities:

*   **Reentrancy Attacks:** Occur when an external call to an untrusted contract is made, and the external contract calls back into the original contract before the first invocation is finished, leading to repeated execution of code and potential draining of funds.
*   **Integer Overflow and Underflow:** These vulnerabilities arise when arithmetic operations result in numbers that exceed the maximum or fall below the minimum value that a data type can hold, leading to unexpected behavior and potential exploits.
*   **Access Control Vulnerabilities:** Insufficient or improper access controls can allow unauthorized users to execute sensitive functions or modify critical data.
*   **Timestamp Dependence:** Relying on `block.timestamp` for critical operations can be risky, as miners can manipulate timestamps within a certain range.
*   **Front-running Attacks:** Malicious actors can observe pending transactions and submit their own transactions with higher gas prices to get them mined first, potentially exploiting price differences or order of operations.
*   **Business Logic Errors:** Flaws in the contract's business logic can lead to unintended behavior, such as incorrect distribution of funds or manipulation of game mechanics.
*   **Insecure Randomness:** Using predictable sources for randomness (e.g., `block.timestamp`, `block.difficulty`) can allow attackers to predict outcomes and exploit the contract.
*   **Unchecked External Calls:** Failing to check the return values of external calls can lead to unexpected behavior if the external call fails.
*   **Missing Protection against Signature Replay:** Signatures can be replayed to execute the same transaction multiple times if not properly protected.
*   **Oracle Manipulation:** If a contract relies on external data feeds (oracles), manipulation of these oracles can lead to incorrect decision-making within the contract.
*   **Flash Loan Attacks:** Exploiting vulnerabilities in decentralized finance (DeFi) protocols by taking out large, uncollateralized flash loans and manipulating asset prices or liquidity within a single transaction.

This list is not exhaustive but covers the most frequently encountered and impactful vulnerabilities in smart contracts.

