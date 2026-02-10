# Data Lineage Explorer

Data Lineage Explorer (DLE) is a lightweight tool to rebuild simplified data lineage
from SQL files. It extracts source tables, transformations, and target tables to build
a dependency graph and generate reports. Useful for data cataloging, traceability, and
data assurance checks.

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
```

## Usage

```bash
dle scan --path examples --out out --format graphml,md,html,png --dialect postgres
```

## Outputs

- `lineage.graphml`: graph export for downstream tools.
- `report.md`: summary report with targets and direct sources.
- `lineage.html`: interactive graph (requires `pyvis`).
- `lineage.png`: static image (requires Graphviz + `pydot`).

## Optional Dependencies

- `pyvis` for HTML graph export.
- Graphviz + `pydot` for PNG export.
- `pyyaml` and `jinja2` are optional helpers for future extensions.

## Limitations

- SQL parsing is best-effort and may not support very complex statements.
- Dialect differences can affect parsing; adjust `--dialect` as needed.
- Python lineage extraction is not implemented yet.