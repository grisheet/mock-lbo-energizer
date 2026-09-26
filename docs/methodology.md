# Model methodology

## Scope and information timing

The model uses a single fixed information set through November 30, 2025, 23:59:59 Eastern time. SEC acceptance timestamps are stored with UTC offsets. The issuer release has a publication date but no verified time; it is conservatively assigned end-of-day Eastern time. Retrieval dates are separate from economic availability dates.

Historical income/cash-flow statements cover fiscal years ended September 30, 2023–2025. Balance sheets are the corresponding fiscal year-end stocks. Fiscal FY2025 Q1–Q4 sales are mapped to their actual quarter-end dates. Calendar Q1 uses fiscal Q2 weights, calendar Q2 fiscal Q3, calendar Q3 fiscal Q4, and calendar Q4 fiscal Q1. A single explicitly estimated October–December 2025 closing bridge separates reported history from the hypothetical acquisition.

Corporate acquisitions included in reported figures are not restated into invented pro-forma history. FY2025 acquired sales remain in the operating base; no additional acquisition synergies or annualization uplift is assumed. Consequently, a partial-year acquisition contribution is a limitation of the calibration. No share-price series, adjusted share price, split adjustment or inferred acquisition premium is used. Entry is an assumed enterprise-value multiple, not an observed takeover offer.

## Units, signs and annualization

Financial amounts are USD millions. Rates are decimal fractions and multiples are unitless. Historical capex in the cash-flow extract is negative, matching the source. Forecast capex is a positive use in its schedule and negative on cash flow. Debt principal, drawn balances, expenses and taxes are positive balances/uses. Sponsor contributions are negative cash flows; distributions positive.

Annual income and cash flows sum four quarters. Opening annual balances use the first quarter opening; ending annual balances use the fourth quarter closing. Annual liquidity risk uses the maximum quarterly shortfall. Forecast revenue is a full-year operational run rate allocated with historical seasonality, not quarter revenue multiplied by four. Quarterly leverage uses that year's full-year forecast EBITDA as its denominator and is labeled as a forward annual denominator, not an LTM actual ratio.

## Earnings normalization

Issuer EBITDA = pretax income + interest + loss on debt extinguishment/modification + D&A. This is an issuer-defined non-GAAP construct, not a GAAP subtotal.

Management adjusted EBITDA is separately reconciled from the issuer's published adjustments. Underwritten entry EBITDA is $623.6m management adjusted EBITDA less $25.6m share compensation (assumed cash replacement), $42.9m current-year production credits, a hypothetical $20.0m recurring cost reserve, and $1.1m nonoperating income = $534.0m. The current-year credit is derived from $120.9m recognized total credits less $78.0m attributable to prior fiscal years. This conservative exclusion is a case assumption about cash reliability, not a claim that credits are ineligible.

The independent operating calibration yields the same EBITDA: segment revenue less segment cost of sales, plus segment depreciation, less current-year production credits, advertising/R&D, adjusted SG&A and the recurring cash reserve. Segment depreciation is assumed entirely in cost of sales. SG&A and share compensation are treated as cash costs, avoiding a cash-flow addback for compensation without a replacement cost.

## Operating drivers and cash conversion

Annual segment revenue = prior annual segment revenue × (1 + volume change) × (1 + price/mix change) × (1 + FX change). Each variable is an explicit hypothetical driver; physical unit counts are not invented. Annual margin changes are absolute percentage-point changes added to the prior cash gross margin. Fixed SG&A grows at its own inflation rate. Advertising/R&D is variable with sales. Recurring cost reserves are cash expenses that reduce EBITDA.

Receivables = quarterly revenue / actual days in quarter × DSO. Inventory = annual cash COGS / 365 × DIO. Payables = annual cash COGS / 365 × DPO. Change in working capital = change in receivables + inventory − payables. Other operating assets/liabilities are flat. Production credits are not assumed collected during the forecast.

Capex = quarterly revenue × capex percentage. Legacy PP&E uses assumed straight-line runoff. New investment enters PP&E at quarter-end, with next-quarter depreciation at opening net book value / assumed eight years / four. This is a declining-balance approximation, not a vintage-based asset register. Legacy intangible amortization uses $51.6m per year as a practice run-rate assumption informed by the disclosed FY2026 estimate; it is not the issuer's entire future amortization schedule. PPA asset step-ups use straight-line ten-year lives with no goodwill amortization.

## Transaction and purchase accounting

Entry EV = underwritten entry EBITDA × entry multiple. Seller equity proceeds = EV − financial debt principal − retained finance leases − pension deficit + acquired cash.

Uses = seller equity proceeds + financial debt refinancing + transaction fees + financing fees + minimum cash. Sources = senior term debt + junior debt + acquired cash + sponsor equity. The revolver begins undrawn. All acquired cash is shown as a source and minimum cash is separately funded as a use, preventing double counting.

Existing principal is sourced from the debt footnote, not just carrying value. Existing debt issuance costs are removed when valuing identifiable net assets. Illustrative PP&E/intangible step-ups generate a new deferred tax liability because the assumed stock acquisition has no tax-basis step-up. Goodwill = equity consideration − fair value of identifiable net assets. Existing goodwill is replaced rather than added twice.

Transaction fees are expensed at closing, reducing book equity. New term financing fees are a contra-debt balance; revolver fees are an asset. Senior fees amortize over six assumed years and the remaining unamortized portion is proportionally written off on principal repayment. Junior and revolver fees amortize over six and five years respectively. Financing-fee tax deductions are conservatively excluded. Tax book-value effects are not asserted to be a GAAP opinion.

## Interest and financing waterfall

Cash interest = opening principal × annual coupon × actual quarter days / 360. Senior/revolver coupons equal max(reference-rate assumption, floor) + spread. Junior and lease rates are fixed. Commitment fees apply to opening undrawn revolver capacity. A rate-stress control adds to the reference rate before applying the floor.

FCF before principal = EBITDA − cash financing costs − cash taxes − capex − increase in working capital. Required senior amortization is a percentage of original principal / four, capped at outstanding debt. Lease principal is a separate assumed annual amount / four. Cash then draws on the capped revolver to fund the minimum cash requirement. Excess cash first repays the revolver, then sweeps senior debt at the chosen percentage. There is no optional junior repayment before exit. Surplus cash after senior repayment accumulates.

Interest does not depend on ending debt, and taxes do not depend on current-quarter fee writeoffs. This eliminates iterative circularity. All draws/payments occur at quarter-end. The shortfall output records cash below the required minimum; negative cash is retained visibly as a diagnostic deficit, never hidden by a balance-sheet plug. The first breach invalidates funded sponsor returns for the whole path. Later-period calculations help measure stress and do not imply continued financing is available.

## Tax simplification

Cash tax uses a blended 25% practice rate, a quarterly deduction capacity of 30% of positive EBITDA, and a maximum NOL offset of 80% of positive taxable income. These are explicit educational proxy assumptions, not implementation of current tax law or a company-specific tax opinion. Unused interest deductions and NOLs carry forward. Opening tax attributes are zero for this illustration. Losses produce no immediate refund. New deferred tax assets from carryforwards are fully valuation-allowed.

Tax depreciation excludes PPA book-only step-ups. Book tax expense = cash tax − incremental PPA deferred-tax release. Existing reported DTA/DTL balances stay flat, a material simplification. No country-by-country allocation, tax-credit realization, attribute limitations or intercompany tax planning is modeled.

## Returns and sensitivity mechanics

Exit EV = final calendar-year EBITDA × exit multiple. Distributable cash excludes minimum cash. Sponsor proceeds = max(0, exit EV − all debt principal + distributable cash − retained pension deficit − exit fees). No interim distributions or management equity are assumed.

MOIC = distributions / contributions. XIRR solves sum(CF_i / (1+r)^((date_i−date_0)/365)) = 0 using actual dates. Excel uses XIRR; Python independently brackets and bisects conventional cash flows. In the two-flow case, the result must equal MOIC^(365/elapsed days) − 1. A total equity wipeout reports MOIC 0 and XIRR unavailable. An unfunded operating path reports both unavailable. No misleading zero-return substitute is used.

Native two-variable tables change the actual model controls. Entry multiple changes fees, sponsor funding, goodwill and opening balance-sheet amounts. Operating-case sensitivities rerun revenue, margins, working capital, tax, debt and cash. Rate/DSO sensitivities rerun financing and liquidity. The original Excel data-table definitions remain in the file; checked caches are supplied for initial viewing.

## Scope boundaries

No legal credit agreement, lender commitment, observed debt pricing, purchase-price fairness opinion or issuer forecast is asserted. No covenants, management equity, carried interest, preferred equity, call premiums, hedging, intra-quarter borrowing peaks, restricted cash or forecast M&A are modeled. Pension/operating-lease balances are held flat while operating costs remain embedded. This case is a teaching/review artifact with explicit limitations.
