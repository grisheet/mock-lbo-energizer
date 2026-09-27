"""Export release assumptions and factual records to plain JSON for analysis."""
import csv
import json
import tomllib
from pathlib import Path

root=Path(__file__).resolve().parents[1]
payload={'history':json.loads((root/'data/historical.json').read_text()),
         'assumptions':tomllib.loads((root/'config/assumptions.toml').read_text())}
with (root/'data/historical.csv').open() as f:
    payload['records']=list(csv.DictReader(f))
(root/'build').mkdir(exist_ok=True)
(root/'build/inputs.json').write_text(json.dumps(payload))
