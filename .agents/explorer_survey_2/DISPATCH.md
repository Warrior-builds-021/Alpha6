# Survey Explorer 2 Dispatch: 6-Pillar Engine, Risk Shield & Financial Computation

## Assignment
Investigate the requirements and existing codebase for the financial computation logic:
1. 6-Pillar institutional analysis:
   - Volume Growth & Demand (15%)
   - Sales Revenue Growth (20%)
   - Operating Cash Flow Quality (25%)
   - Debt & Solvency Health (15%)
   - Pricing Power & Moat (15%)
   - Promoter Skin in the Game (10%)
2. Piotroski F-Score (0-9 checklist) & Altman Z-Score bankruptcy distress calculation.
3. Capital preservation rule (disqualification on distress or revenue collapse).
4. Dynamic ATR-based position sizing calculator (portfolio size, risk tolerance, 2x ATR stop loss, target profit).
5. yfinance downloading, caching (in-memory TTL cache, sub-20ms queries), and /tmp/py-yfinance cache redirection for serverless/read-only environments.
6. Check existing implementations or gaps in `c:\Users\asaik\OneDrive\Desktop\PROJECT1`.

## Inputs
- `c:\Users\asaik\OneDrive\Desktop\PROJECT1\ORIGINAL_REQUEST.md`

## Output
Write your comprehensive report to `c:\Users\asaik\OneDrive\Desktop\PROJECT1\.agents\explorer_survey_2\handoff.md`.
Use send_message to notify parent when complete.
