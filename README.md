# SMCVD — Smart Contract Vulnerability Detector

SMCVD scans Solidity smart contracts from a GitHub repository or local files and returns high‑confidence vulnerability findings with detailed context and remediation guidance.

## Prerequisites
- Python 3.9+
- Git (for analyzing GitHub repos)
- An OpenAI API key (only required for enhanced explanations/PoCs)

## Quick start (Windows PowerShell)
```powershell
cd C:\Users\user23\Downloads\smartcontract
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -U pip
pip install -r requirements.txt

# Optional: enable AI explanations and tune thresholds
$env:OPENAI_API_KEY = "sk-..."
$env:OPENAI_MODEL   = "gpt-4o-mini"   # optional override
$env:MIN_CONFIDENCE = "0.65"          # raise to reduce noise further
$env:ENABLE_AI      = "true"          # set to false to skip AI enrichment

python src/app.py
```

The API will start on `http://localhost:5000`.

## Configuration (env)
- `OPENAI_API_KEY`: Enables model‑generated explanations/PoCs.
- `OPENAI_MODEL`: Model name (default `gpt-4o-mini`).
- `MIN_CONFIDENCE`: Minimum confidence to report (default `0.65`).
- `ENABLE_AI`: `true|false` to enable/disable AI enhancement (default `true`).

## Endpoints
- `POST /api/analyze` — Start analysis (GitHub URL or uploaded files)
- `GET  /api/status/{job_id}` — Check progress
- `GET  /api/results/{job_id}` — Fetch findings and summary
- `POST /api/report/generate` — Build a report (JSON/Markdown)

## Usage examples

### Analyze a GitHub repository
```bash
curl -X POST http://localhost:5000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "github_url": "https://github.com/OWNER/REPO",
    "program_scope": {
      "focus_areas": ["reentrancy", "access_control"],
      "in_scope_vulns": ["reentrancy", "integer_overflow"],
      "out_of_scope_vulns": ["dos_gas_limit"],
      "rules": ["no_mainnet_exploits"],
      "disclosure": "coordinated",
      "severity_allow": { "reentrancy": ["critical", "high"], "access_control": ["high", "medium"] },
      "path_include": ["contracts/"],
      "path_exclude": ["node_modules/"],
      "reject_if": ["no_mainnet_exploits"]
    }
  }'
```
Response contains `job_id`. Poll status and fetch results:
```bash
curl http://localhost:5000/api/status/JOB_ID
curl http://localhost:5000/api/results/JOB_ID
```

### Analyze local Solidity files
Base64 or raw text upload isn’t required here; this API expects simple text content per file for convenience.
```bash
curl -X POST http://localhost:5000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "files": [
      {"name": "Contract.sol", "content": "contract C { /* solidity code */ }"}
    ],
    "program_scope": {
      "focus_areas": ["reentrancy"],
      "in_scope_vulns": ["reentrancy"],
      "out_of_scope_vulns": ["front_running"],
      "severity_allow": { "reentrancy": ["critical", "high"] },
      "path_include": ["contracts/"],
      "reject_if": ["no_mainnet_exploits"]
    }
  }'
```

### Generate a report
```bash
curl -X POST http://localhost:5000/api/report/generate \
  -H "Content-Type: application/json" \
  -d '{
    "job_id": "JOB_ID",
    "format": "markdown",
    "template": "professional"
  }'
```

## Reducing false positives
- Solidity ≥ 0.8 arithmetic is treated as safe unless inside `unchecked {}`.
- SafeMath usage, `onlyOwner`/`AccessControl`, and `nonReentrant` reduce or filter findings.
- Inline suppressions:
  - Line: `// analyzer-ignore: reentrancy`
  - File: `// analyzer-ignore-file: integer_overflow`
- Advanced multi-signal verification reduces false positives by cross-referencing multiple indicators.
- Contextual analysis identifies likely false positives in view functions, validation checks, and constructors.
- Tune via `MIN_CONFIDENCE` (higher = fewer findings). Default is now 0.8 for better precision.

## Notes
- PDF output via WeasyPrint is optional and not required for core usage. On Windows it may need extra system dependencies; Markdown export works out of the box.
- If you prefer not to use AI features, set `ENABLE_AI=false` (engine still returns strong static findings).

## License
This project is licensed under the Apache License 2.0. See the `LICENSE` file for details.

## Development
- Main entry point: `src/app.py` (Flask app + blueprints)
- Key services:
  - `src/services/analysis_service.py` — static analysis engine (with FP suppression)
  - `src/services/ai_service.py` — optional model‑generated explanations/PoCs
  - `src/routes/*` — API endpoints

## Troubleshooting
- 401/403 calling model API: ensure `OPENAI_API_KEY` is set.
- No findings? Lower `MIN_CONFIDENCE` or verify the repo actually contains `.sol` files.
- Windows PowerShell execution policy: if venv activation fails, run PowerShell as admin and `Set-ExecutionPolicy RemoteSigned`.

