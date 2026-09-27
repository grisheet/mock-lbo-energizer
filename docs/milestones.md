# Implementation milestones and reviewer guide

The complete file contents are committed in the repository. The binary Excel deliverable is under `excel/`. This guide preserves a teachable, sequential workflow for the approved complete build. Commands run from the repository root with Python 3.12 and `PYTHONPATH=src`.

## 1. Dated evidence and assumptions

Goal: distinguish sourced history from prospective assumptions and prevent later information entering the case.

Files: `pyproject.toml`, `uv.lock`, `.python-version`, `.env.example`, `.gitignore`, `LICENSE`, `DATA_LICENSE.md`, `config/case.toml`, `config/assumptions.toml`, `data/historical.csv`, `data/historical.json`, `data/source_manifest.csv`, `src/mock_lbo/__init__.py`, `src/mock_lbo/sources.py`, `tests/test_sources.py`, `docs/assumptions.md`.

```bash
python3.12 -m venv .venv
source .venv/bin/activate
export PYTHONPATH="$PWD/src"
python -m unittest discover -s tests -p test_sources.py -v
```

Expected: four input-gate tests pass. The source register distinguishes publication from retrieval. Limit: source HTML is not redistributed; the numerical extracts and source links are included. Suggested commit: `data: freeze sourced financials and practice assumptions`.

## 2. Independent financial engine

Goal: build a transparent reference calculation before trusting a spreadsheet answer.

Files: `src/mock_lbo/transaction.py`, `operating.py`, `debt.py`, `taxes.py`, `returns.py`, `validation.py`, `cli.py`, `tests/test_model.py`, `docs/methodology.md` (Python module paths share the `src/mock_lbo/` prefix).

```bash
python -m mock_lbo.cli validate --case base
python -m mock_lbo.cli validate --case downside
python -m mock_lbo.cli validate --case upside
python -m mock_lbo.cli demo --case base --output build/base.json
python -m unittest discover -s tests -p test_model.py -v
```

Expected: 26 model tests pass; all three cases balance. Base MOIC is approximately 1.66537x and XIRR 10.7332%. The downside reports `feasible: false`. Limit: taxes, PPA, pensions and intraperiod funding remain simplified. Suggested commit: `feat: add quarterly acquisition and financing engine`.

## 3. Linked Excel and independent audit

Goal: make assumptions editable and financial relationships traceable through one model.

Files: `excel/mock_lbo_energizer.xlsx`, `data/workbook_map.json`, `src/mock_lbo/workbook.py`, `tests/test_workbook.py`, `scripts/prepare_build.py`, `scripts/refresh_table_caches.py`, `docs/validation.md`, `docs/validation_results.json`.

```bash
open excel/mock_lbo_energizer.xlsx
python -m mock_lbo.cli audit
python -m unittest discover -s tests -p test_workbook.py -v
```

Expected: saved workbook agrees with the reference model; all 95 table combinations agree. `open` is the macOS command. The Excel tab sequence and linked formulas are the complete model implementation, not screenshots. Limit: direct Excel for Mac execution remains unverified. Suggested commit: `feat: deliver linked LBO workbook with independent audit`.

## 4. Portfolio release

Goal: let another student reproduce and review the case from a public checkout.

Files: `README.md`, `CHANGELOG.md`, `docs/investment_committee.md`, `docs/milestones.md`, `.github/workflows/ci.yml` and updated release evidence.

```bash
python -m unittest discover -s tests -v
uv sync --frozen
uv run pytest -q
uv run ruff check src tests scripts
uv run mypy
uv run mock-lbo audit
git status --short
```

Expected: 31 tests pass, lint/type checks pass, and workbook audit reports no unexplained discrepancies. Suggested commit: `docs: publish reproducible Mock LBO practice case`.

## Acceptance criteria

| Requirement | Evidence |
|---|---|
| Sources equal uses; opening/forecast balance sheets balance | Independent identities and Checks tab |
| Debt, cash, interest and liquidity roll correctly | Quarterly comparisons, waterfall boundary tests |
| Operationally driven five-year forecast | Segment volume, price, FX, margin and working-capital inputs |
| Funded returns only; actual dated convention | Feasibility guard, XIRR baseline and leap-day test |
| Live valuation and operating sensitivities | Five native tables; 95 independent combinations |
| Dated source facts and explicit assumptions | CSV manifest, data gates, separate assumption controls |
| Portable main demo and reviewable project | Standard-library CLI, tests, dependency lock, README |
| Excel for Mac | Manual checklist remains outstanding |

## Risk register

| Risk | Mitigation and remaining limitation |
|---|---|
| Look-ahead/restatement leakage | Fixed availability cutoff; subsequent filings excluded |
| Selected survivor mistaken for a strategy | Single-company case, no backtest or performance claim |
| Acquisition or fiscal-calendar distortion | Actual fiscal-quarter dates; explicit calendar mapping and bridge |
| Optimistic EBITDA normalization | Exclude credits and compensation addback; retain recurring cost reserve |
| Model circularity | Beginning-balance interest; quarter-end principal waterfall |
| Hidden liquidity failure | Capacity-capped revolver and visible shortfall; funded returns suppressed |
| PPA/tax precision overstated | Stated illustrative assumptions; no legal/GAAP opinion |
| Spreadsheet engine differences | Independent audit and native tables; Mac manual gate open |
| Source rights or secret leakage | Source rights register, numerical extracts only, no secrets required |
| Rebuild expectations | Versioned Excel template; Python demo is independently reproducible |
