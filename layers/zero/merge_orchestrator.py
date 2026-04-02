from pathlib import Path

from layers.zero.merge_io import iter_mergeable_domain_dirs
from layers.zero.merge_io import load_domain_records
from layers.zero.merge_io import write_merged_domain_records
from layers.zero.merge_post_process import post_process_domain_records


def merge_layer_zero_raw_outputs(base_wiki_dir: Path) -> None:
    layer_zero_dir = base_wiki_dir / "layers" / "0_layer"
    if not layer_zero_dir.exists():
        return

    for domain_dir in iter_mergeable_domain_dirs(layer_zero_dir):
        merged_records = load_domain_records(domain_dir)
        if not merged_records:
            continue
        merged_records = post_process_domain_records(domain_dir.name, merged_records)
        write_merged_domain_records(domain_dir, merged_records)
