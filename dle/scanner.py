from __future__ import annotations

import fnmatch
import logging
from dataclasses import dataclass
from pathlib import Path

import networkx as nx

from .graph import build_graph
from .lineage import Transform, build_lineage
from .sql_parser import ParseError, extract_lineage, parse_sql_statements


@dataclass(frozen=True)
class ScanWarning:
    file_path: str
    message: str


@dataclass(frozen=True)
class ScanResult:
    files: list[Path]
    statement_count: int
    transforms: list[Transform]
    graph: nx.DiGraph
    lineage: dict[str, dict[str, list[str]]]
    warnings: list[ScanWarning]


def collect_sql_files(
    path: Path, include_patterns: list[str], exclude_patterns: list[str]
) -> list[Path]:
    if path.is_file():
        return [path]

    candidates = [p for p in path.rglob("*") if p.is_file()]
    matched: list[Path] = []

    for candidate in candidates:
        if _matches_any(candidate, exclude_patterns):
            continue
        if _matches_any(candidate, include_patterns):
            matched.append(candidate)

    return sorted(matched)


def scan_path(
    path: Path,
    dialect: str,
    include_patterns: list[str],
    exclude_patterns: list[str],
    strict: bool,
    logger: logging.Logger,
) -> ScanResult:
    files = collect_sql_files(path, include_patterns, exclude_patterns)
    if not files:
        raise FileNotFoundError("No SQL files found for the given path and patterns.")

    warnings: list[ScanWarning] = []
    transforms: list[Transform] = []
    statement_count = 0

    base_path = path if path.is_dir() else path.parent

    for file_path in files:
        sql_text = file_path.read_text(encoding="utf-8")
        try:
            statements = parse_sql_statements(sql_text, dialect)
        except ParseError as exc:
            message = str(exc)
            if strict:
                raise
            logger.warning("Failed to parse %s: %s", file_path, message)
            warnings.append(ScanWarning(file_path=file_path.as_posix(), message=message))
            continue

        for index, statement in enumerate(statements, start=1):
            statement_count += 1
            lineage = extract_lineage(statement, dialect)
            targets = {t.lower() for t in lineage.targets}
            sources = {s.lower() for s in lineage.sources}
            relative_path = file_path.relative_to(base_path).as_posix()
            transform_id = f"transform:{relative_path}#{index}"
            transforms.append(
                Transform(
                    transform_id=transform_id,
                    file_path=relative_path,
                    statement_index=index,
                    sources=sources,
                    targets=targets,
                )
            )

    graph = build_graph(transforms)
    lineage_map = build_lineage(transforms)

    return ScanResult(
        files=files,
        statement_count=statement_count,
        transforms=transforms,
        graph=graph,
        lineage=lineage_map,
        warnings=warnings,
    )


def _matches_any(path: Path, patterns: list[str]) -> bool:
    if not patterns:
        return False
    posix_path = path.as_posix()
    for pattern in patterns:
        if fnmatch.fnmatch(path.name, pattern) or fnmatch.fnmatch(posix_path, pattern):
            return True
    return False
