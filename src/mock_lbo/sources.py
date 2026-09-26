"""Offline factual extracts, with date and uniqueness validation."""
import csv
import json
import math
import tomllib
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def load_inputs(root: Path = ROOT) -> tuple[dict[str, float], dict]:
    """Load numeric facts and hypothetical assumptions from the repository."""
    settings = tomllib.loads((root / "config/case.toml").read_text())
    cutoff = datetime.fromisoformat(settings["information_cutoff"])
    if cutoff.utcoffset() is None:
        raise ValueError("Information cutoff must be timezone-aware")
    with (root / "data/source_manifest.csv").open() as f:
        manifest = {r["source_id"]: r for r in csv.DictReader(f)}
    with (root / "data/historical.csv").open() as f:
        rows = list(csv.DictReader(f))
    keys: set[tuple[str, str]] = set()
    for row in rows:
        key = row["field"], row["period_end"]
        if key in keys:
            raise ValueError(f"Duplicate observation: {key}")
        keys.add(key)
        published = datetime.fromisoformat(manifest[row["source_id"]]["published_at"])
        if published.utcoffset() is None:
            raise ValueError("Publication timestamp must be timezone-aware")
        if published > cutoff:
            raise ValueError(f"Future source: {row['source_id']}")
        if not math.isfinite(float(row["value"])):
            raise ValueError(f"Missing or nonfinite observation: {key}")
    facts = {r["field"]: float(r["value"]) for r in rows if r["fiscal_year"] == "2025"}
    assumptions = tomllib.loads((root / "config/assumptions.toml").read_text())
    return facts, assumptions


def historical_checks(root: Path = ROOT) -> dict[str, float]:
    """Reconcile published controls, allowing only displayed-source rounding."""
    data = json.loads((root / "data/historical.json").read_text())
    checks = {}
    for year, h in data.items():
        checks[f"{year}_balance_sheet"] = h["assets"] - h["liabilities"] - h["equity"]
        checks[f"{year}_gross_profit"] = h["revenue"] - h["cogs"] - h["gross_profit"]
        checks[f"{year}_net_income"] = h["pretax"] - h["tax"] - h["net_income"]
        checks[f"{year}_segments"] = h["battery_sales"] + h["auto_sales"] - h["revenue"]
        checks[f"{year}_cash_flows"] = h["cfo"] + h["cfi"] + h["cff"] + h["fx_cash"] - h["cash_change"]
        checks[f"{year}_cash_roll"] = h["cash_begin"] + h["cash_change"] - h["cash_end"]
    return checks
