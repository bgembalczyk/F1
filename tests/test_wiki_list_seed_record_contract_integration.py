from __future__ import annotations

import json
from datetime import datetime
from datetime import timezone
from pathlib import Path

from models.contracts.seed import SEED_RECORD_SCHEMA_VERSION
from models.contracts.seed import SeedRecord
from scrapers.wiki.seed_registry import WIKI_LIST_JOB_REGISTRY


def _resolve_layer0_json(job_output_category: str, json_output_path: str) -> Path:
    repo_root = Path(__file__).resolve().parents[1]
    layer0_raw_root = repo_root / "data" / "wiki" / "layers" / "0_layer"
    file_name = Path(json_output_path).name
    if "{year}" in file_name:
        matches = sorted(
            (layer0_raw_root / job_output_category / "raw").glob(
                file_name.replace("{year}", "*"),
            ),
        )
        if not matches:
            msg = f"Missing layer0 file for pattern: {job_output_category}/{file_name}"
            raise AssertionError(msg)
        return matches[-1]

    candidate = layer0_raw_root / job_output_category / "raw" / file_name
    if not candidate.exists():
        msg = f"Missing layer0 file: {candidate}"
        raise AssertionError(msg)
    return candidate


def test_all_wiki_list_jobs_produce_seed_record_compatible_rows() -> None:
    scraped_at = datetime.now(tz=timezone.utc)

    for job in WIKI_LIST_JOB_REGISTRY:
        source_path = _resolve_layer0_json(job.output_category, job.json_output_path)
        payload = json.loads(source_path.read_text(encoding="utf-8"))
        assert isinstance(payload, list), f"{job.seed_name} should produce list records"
        assert payload, f"{job.seed_name} should not produce empty record list"

        normalized = [
            SeedRecord.from_raw(
                record,
                source_url=job.wikipedia_url,
                scraped_at=scraped_at,
            )
            for record in payload
        ]
        assert all(
            record.schema_version == SEED_RECORD_SCHEMA_VERSION for record in normalized
        )
        assert all(record.source_url == job.wikipedia_url for record in normalized)
