# Executive assumptions and rationale

Every prospective number is a practice assumption. Public financials calibrate starting levels; they do not validate the proposed debt package or acquisition price.

| Input | Default | Rationale |
|---|---:|---|
| Entry / exit EV multiple | 9.0x / 9.0x | Transparent fixed-multiple baseline with no expansion benefit; sensitivity range 7–11x |
| Senior / junior leverage | 3.5x / 1.0x | Illustrative financing mix on conservative underwritten EBITDA |
| Revolver capacity | 0.75x EBITDA | Explicit finite seasonal liquidity buffer |
| Senior / revolver spread | 4.0% / 3.5% | Hypothetical spread assumptions, not quoted market terms |
| Junior fixed coupon | 11.0% | Illustrative cash-pay subordinated financing |
| Reference-rate floor | 1.0% | Prevents negative-rate artifacts in the exercise |
| Senior amortization | 1.0% of original principal/year | Capped at remaining principal; additional cash sweep permitted |
| Optional cash sweep | 100% | Revolver repaid first; senior second; junior remains bullet |
| Minimum cash | 2.0% of FY2025 sales | Fixed operating liquidity requirement, retained at exit |
| Transaction / exit fees | 2.0% / 1.5% of EV | Explicit expenses and sponsor return drag |
| Debt / revolver upfront fees | 2.0% / 1.0% | Separate cash uses and accounting balances |
| PP&E / intangible step-ups | $40m / $400m | Illustrative PPA only; ten-year book lives |
| Recurring normalization reserve | $20m/year | Avoids assuming every restructuring addback disappears |

Base volume is initially flat to slightly negative, then modestly positive. Price/mix is 2% annually. Cash margins initially fall 100bp and then recover gradually. The downside combines volume contraction, weaker margins, higher working-capital days, higher rates and recurring costs. The upside improves organic volume, margins and working capital without future acquisitions.

Seasonality is derived from reported FY2025 segment sales. Because FY2025 contains acquired sales for only part of the year, those weights are an imperfect steady-state proxy. Forecast driver columns are editable separately for 2026–2030.

Bridge assumptions: October–December 2025 revenue is the corresponding prior-year quarter with −3% volume and +2% price; working capital and other balances remain flat. Capex is 3% of FY2025 sales / four. Existing interest is annual FY2025 interest × 92/360. There are no dividends, buybacks, acquisitions or FX balance-sheet changes in the bridge. It is a transparent estimate, not a reconstructed actual closing statement.

See [config/assumptions.toml](../config/assumptions.toml) for every numeric term and the full case arrays. The hypothetical closing date does not imply an actual announced transaction.
