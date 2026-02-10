from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Transform:
    transform_id: str
    file_path: str
    statement_index: int
    sources: set[str]
    targets: set[str]


def build_lineage(transforms: list[Transform]) -> dict[str, dict[str, list[str]]]:
    lineage: dict[str, dict[str, list[str]]] = {}
    for transform in transforms:
        for target in transform.targets:
            entry = lineage.setdefault(target, {"sources": [], "transforms": []})
            entry["transforms"].append(transform.transform_id)
            for source in sorted(transform.sources):
                if source not in entry["sources"]:
                    entry["sources"].append(source)
    return lineage
