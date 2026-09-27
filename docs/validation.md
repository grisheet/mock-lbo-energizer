# Validation and release evidence

The saved workbook is audited against an independent Python model. Neither the audit nor CI claims to launch Microsoft Excel. All figures are hypothetical case calculations.

## Executed checks

Release environment: Python 3.12.14, Linux; validation date September 26, 2026. The workbook uses native Excel data tables, not hardcoded sensitivity answers. The authoring engine calculated the main schedules; LibreOffice recalculated the sensitivity combinations. The separately implemented Python engine verified those results.

The release audit records its actual counts and maximum discrepancy in [validation_results.json](validation_results.json). It checks 1,443 numeric comparisons, 95 sensitivity combinations, five native data-table definitions, 103 forecast accounting identities, and 18 historical reconciliations. There were no unexpected formula errors. Dollar comparisons tolerate $0.001m and XIRR comparisons 0.000001; ordinary accounting identities must be within $0.000001m. Historical source rounding is allowed up to $0.15m.

The standard-library suite tests debt conservation, finite revolver capacity, minimum cash, repayment priority, zero debt, zero sweep, no overpayment, NOL/interest limitations, a complete equity wipeout, unfunded downside, annual return baselines, leap-day XIRR, deterministic outputs, source timestamps, duplicates and nonfinite data. Synthetic fixtures only exercise boundaries; they are not market observations.

All 31 local tests passed. Three disposable workbook edits were also exported and recalculated: Downside, Upside, and a one-percentage-point increase in final-year Base battery volume. Each edited workbook passed the full independent audit, including all 95 sensitivities. For the final-year change, the first 16 quarters' EBITDA stayed unchanged and exit-year EBITDA changed. These copies are test fixtures, not alternate deliverables.

```bash
export PYTHONPATH="$PWD/src"
python -m unittest discover -s tests -v
python -m mock_lbo.cli audit --output build/audit.json
python -m mock_lbo.cli validate --case downside
```

The independent two-flow return baseline is `MOIC ** (365 / elapsed_days) - 1`. The default case has equal entry and exit multiples, so multiple expansion contributes zero value creation. Downside funding failure suppresses MOIC and XIRR instead of presenting an infeasible return.

## Recalculation and cache handling

LibreOffice can rewrite Excel's native data-table definitions on save. The release keeps the original Excel formulas and table definitions. `scripts/refresh_table_caches.py` transfers only the 95 independently checked table result caches from the recalculated copy. It does not replace live formulas with static sensitivity values. Keep the original and the recalculated copy in separate directories.

```bash
mkdir -p build/recalculated
soffice --headless --convert-to xlsx --outdir build/recalculated excel/mock_lbo_energizer.xlsx
python scripts/refresh_table_caches.py excel/mock_lbo_energizer.xlsx build/recalculated/mock_lbo_energizer.xlsx
python -m mock_lbo.cli audit
```

These commands require LibreOffice to be installed separately. On a Mac, its command may be `/Applications/LibreOffice.app/Contents/MacOS/soffice`. Normal Excel users should instead recalculate and save directly in Excel. The cache utility is a release-maintenance tool, not part of the ordinary modeling workflow.

The audit reads editable assumptions from the workbook. It therefore checks saved results after a user changes those assumptions; an unrecalculated workbook should fail. The CSV and TOML remain the reproducible release inputs for the standalone Python demo. The workbook is the editable modeling surface.

## Excel for Mac checklist — not yet executed

1. Open the file without repair warnings; enable Automatic calculation including data tables.
2. Recalculate all, save, and run the Python audit on the saved file.
3. Select cases 1, 2 and 3 in Sensitivities D5. Confirm that operating schedules, debt, returns, IC summary and tables change together. Case 2 must report an unfunded path.
4. Change only the final-year battery-volume assumption. Earlier years must remain unchanged; 2030 EBITDA, debt and returns must respond.
5. Change entry and exit multiples separately. Entry changes funding; exit changes proceeds.
6. Increase reference rates and DSO; confirm financing costs, working capital and funding gaps respond.
7. Remove a required numeric assumption. The input diagnostic must flag it and funded return outputs must become unavailable.
8. Restore release inputs, save, and rerun the audit.

## Limits

LibreOffice evidence is not proof of identical behavior in Excel for Mac. The manual checklist remains an explicit compatibility gate. CI validates saved results and Python logic, not native spreadsheet UI behavior. Broadly typed result dictionaries support named financial outputs; the debt waterfall uses a typed immutable dataclass. No claim is made that type checking proves financial correctness.

Additional diligence would require jurisdictional taxes, detailed fixed-asset vintages, intraperiod liquidity, credit covenants, restricted cash, legal refinancing terms and a complete purchase-price allocation. The model is not suitable for a lending decision or live acquisition.
