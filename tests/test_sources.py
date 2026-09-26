"""Point-in-time and missing-data gates use synthetic corruptions of local fixtures."""
import csv
import shutil
import tempfile
import unittest
from pathlib import Path

from mock_lbo.sources import ROOT, load_inputs


class InputGateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        shutil.copytree(ROOT / "data", self.root / "data")
        shutil.copytree(ROOT / "config", self.root / "config")

    def mutate(self, filename: str, field: str, value: str) -> None:
        file = self.root / "data" / filename
        with file.open() as stream:
            reader = csv.DictReader(stream)
            fields = reader.fieldnames
            rows = list(reader)
        assert fields is not None
        rows[0][field] = value
        with file.open("w", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)

    def test_future_source_rejected(self) -> None:
        self.mutate("source_manifest.csv", "published_at", "2026-01-01T00:00:00+00:00")
        with self.assertRaisesRegex(ValueError, "Future source"):
            load_inputs(self.root)

    def test_naive_timestamp_rejected(self) -> None:
        self.mutate("source_manifest.csv", "published_at", "2025-01-01T00:00:00")
        with self.assertRaisesRegex(ValueError, "timezone-aware"):
            load_inputs(self.root)

    def test_nan_rejected(self) -> None:
        self.mutate("historical.csv", "value", "NaN")
        with self.assertRaisesRegex(ValueError, "nonfinite"):
            load_inputs(self.root)

    def test_duplicate_rejected(self) -> None:
        file = self.root / "data/historical.csv"
        with file.open() as stream:
            reader = csv.DictReader(stream)
            fields = reader.fieldnames
            first = next(reader)
        assert fields is not None
        with file.open("a", newline="") as stream:
            csv.DictWriter(stream, fieldnames=fields).writerow(first)
        with self.assertRaisesRegex(ValueError, "Duplicate observation"):
            load_inputs(self.root)
