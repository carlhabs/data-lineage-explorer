from __future__ import annotations

from pathlib import Path

from .scanner import ScanResult


def write_report(result: ScanResult, out_path: Path) -> None:
    graph = result.graph
    table_nodes = [n for n, data in graph.nodes(data=True) if data.get("type") == "table"]
    transform_nodes = [
        n for n, data in graph.nodes(data=True) if data.get("type") == "transform"
    ]

    lines: list[str] = []
    lines.append("# Data Lineage Report")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- Files: {len(result.files)}")
    lines.append(f"- Statements: {result.statement_count}")
    lines.append(f"- Tables: {len(table_nodes)}")
    lines.append(f"- Transforms: {len(transform_nodes)}")
    lines.append(f"- Edges: {graph.number_of_edges()}")
    lines.append("")

    lines.append("## Targets")
    lines.append("")
    if not result.lineage:
        lines.append("No target tables found.")
    else:
        for target, details in sorted(result.lineage.items()):
            lines.append(f"### {target}")
            lines.append("")
            sources = details.get("sources", [])
            transforms = details.get("transforms", [])
            lines.append("Sources:")
            if sources:
                for source in sources:
                    lines.append(f"- {source}")
            else:
                lines.append("- (none)")
            lines.append("")
            lines.append("Transforms:")
            if transforms:
                for transform in transforms:
                    lines.append(f"- {transform}")
            else:
                lines.append("- (none)")
            lines.append("")

    if result.warnings:
        lines.append("## Warnings")
        lines.append("")
        for warning in result.warnings:
            lines.append(f"- {warning.file_path}: {warning.message}")
        lines.append("")

    out_path.write_text("\n".join(lines), encoding="utf-8")
