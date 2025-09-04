# User Interface Wireframes and Mockups

## Landing Page
```
+----------------------------------------------------------+
|  [Logo] Smart Contract Security Analyzer                |
|                                                          |
|  ┌────────────────────────────────────────────────────┐ |
|  │              Hero Section                          │ |
|  │  "AI-Powered Smart Contract Vulnerability         │ |
|  │   Detection for Bug Bounty Hunters"               │ |
|  │                                                    │ |
|  │  [Get Started] [Learn More]                       │ |
|  └────────────────────────────────────────────────────┘ |
|                                                          |
|  Features:                                               |
|  • GitHub Integration  • AI Analysis  • Report Gen      |
+----------------------------------------------------------+
```

## Repository Input Page
```
+----------------------------------------------------------+
|  [Back] Smart Contract Analysis                         |
|                                                          |
|  ┌────────────────────────────────────────────────────┐ |
|  │  Step 1: Repository Input                         │ |
|  │                                                    │ |
|  │  GitHub Repository URL:                           │ |
|  │  [https://github.com/user/repo        ] [Validate]│ |
|  │                                                    │ |
|  │  OR                                                │ |
|  │                                                    │ |
|  │  ┌─────────────────────────────────────────────┐  │ |
|  │  │  Drag & Drop Smart Contract Files Here     │  │ |
|  │  │  or click to browse                        │  │ |
|  │  └─────────────────────────────────────────────┘  │ |
|  │                                                    │ |
|  │  [Start Analysis]                                  │ |
|  └────────────────────────────────────────────────────┘ |
+----------------------------------------------------------+
```

## Analysis Dashboard
```
+----------------------------------------------------------+
|  [Home] Analysis in Progress...                         |
|                                                          |
|  Repository: user/smart-contract-repo                    |
|  ████████████████████████████████████████████ 75%       |
|                                                          |
|  Current Step: AI-powered vulnerability analysis        |
|                                                          |
|  ┌─────────────┬─────────────┬─────────────┬───────────┐|
|  │Files Found  │Vulnerabilities│Severity    │Status     ││
|  │     12      │      3       │   High: 1  │Processing ││
|  │             │              │   Med: 2   │           ││
|  └─────────────┴─────────────┴─────────────┴───────────┘|
|                                                          |
|  Recent Activity:                                        |
|  • Detected reentrancy vulnerability in transfer()      |
|  • Found access control issue in withdraw()             |
|  • Analyzing integer overflow patterns...               |
+----------------------------------------------------------+
```

## Results View
```
+----------------------------------------------------------+
|  [Home] Analysis Complete ✓                             |
|                                                          |
|  Repository: user/smart-contract-repo                    |
|  Analysis completed in 2m 34s                           |
|                                                          |
|  ┌─────────────────────────────────────────────────────┐|
|  │ VULNERABILITY SUMMARY                               │|
|  │ Critical: 1  High: 2  Medium: 3  Low: 1            │|
|  └─────────────────────────────────────────────────────┘|
|                                                          |
|  🔴 CRITICAL: Reentrancy in transfer() function         |
|  📄 File: contracts/Token.sol:45                        |
|  💰 Impact: Complete fund drainage possible             |
|  [View Details] [Generate POC]                          |
|                                                          |
|  🟠 HIGH: Access Control Bypass                         |
|  📄 File: contracts/Token.sol:78                        |
|  💰 Impact: Unauthorized admin access                   |
|  [View Details] [Generate POC]                          |
|                                                          |
|  [Generate Bug Bounty Report] [Export Results]          |
+----------------------------------------------------------+
```

## Vulnerability Detail View
```
+----------------------------------------------------------+
|  [Back] Reentrancy Vulnerability Details                |
|                                                          |
|  ┌─────────────────────────────────────────────────────┐|
|  │ VULNERABILITY: Reentrancy Attack                   │|
|  │ SEVERITY: Critical                                  │|
|  │ CWE: CWE-362                                        │|
|  │ FILE: contracts/Token.sol                           │|
|  │ FUNCTION: transfer() at line 45                     │|
|  └─────────────────────────────────────────────────────┘|
|                                                          |
|  Description:                                            |
|  The transfer function makes an external call before     |
|  updating the balance, allowing for reentrancy attacks. |
|                                                          |
|  Vulnerable Code:                                        |
|  ┌─────────────────────────────────────────────────────┐|
|  │ function transfer(address to, uint amount) {        │|
|  │   require(balances[msg.sender] >= amount);          │|
|  │   to.call.value(amount)();  // ← Vulnerable line   │|
|  │   balances[msg.sender] -= amount;                   │|
|  │ }                                                   │|
|  └─────────────────────────────────────────────────────┘|
|                                                          |
|  Impact:                                                 |
|  • Complete drainage of contract funds                   |
|  • Loss of user deposits                                 |
|  • Potential for $XXX,XXX in damages                    |
|                                                          |
|  [Generate POC] [View Mitigation] [Add to Report]       |
+----------------------------------------------------------+
```

## Bug Bounty Report Generator
```
+----------------------------------------------------------+
|  [Back] Bug Bounty Report Generator                     |
|                                                          |
|  ┌─────────────────────────────────────────────────────┐|
|  │ REPORT CONFIGURATION                                │|
|  │                                                     │|
|  │ Report Title: [Reentrancy Vulnerability in...    ] │|
|  │ Target Program: [Program Name                     ] │|
|  │ Researcher: [Your Name                            ] │|
|  │                                                     │|
|  │ Include Vulnerabilities:                            │|
|  │ ☑ Critical: Reentrancy in transfer()              │|
|  │ ☑ High: Access Control Bypass                      │|
|  │ ☐ Medium: Integer Overflow Risk                    │|
|  │                                                     │|
|  │ Report Format: [Professional] [Detailed] [Concise] │|
|  └─────────────────────────────────────────────────────┘|
|                                                          |
|  Preview:                                                |
|  ┌─────────────────────────────────────────────────────┐|
|  │ # Vulnerability Report                              │|
|  │                                                     │|
|  │ ## Summary                                          │|
|  │ Multiple critical vulnerabilities discovered...     │|
|  │                                                     │|
|  │ ## Vulnerability 1: Reentrancy Attack              │|
|  │ **Severity:** Critical                              │|
|  │ **Impact:** Complete fund drainage...               │|
|  └─────────────────────────────────────────────────────┘|
|                                                          |
|  [Generate Report] [Download PDF] [Copy Markdown]       |
+----------------------------------------------------------+
```

## Design Principles
- **Clean and Professional**: Modern, minimalist design suitable for security professionals
- **Progress Indication**: Clear feedback on analysis progress
- **Severity-Based Color Coding**: Red for critical, orange for high, yellow for medium, blue for low
- **Interactive Elements**: Expandable vulnerability details, filterable results
- **Export Options**: Multiple formats for different use cases
- **Responsive Design**: Works on desktop and mobile devices

