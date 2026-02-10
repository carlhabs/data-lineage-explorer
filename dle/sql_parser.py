from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import sqlglot
from sqlglot import expressions as exp


class ParseError(Exception):
    pass


@dataclass(frozen=True)
class StatementLineage:
    targets: set[str]
    sources: set[str]


def parse_sql_statements(sql_text: str, dialect: str) -> list[exp.Expression]:
    try:
        return sqlglot.parse(sql_text, read=dialect, error_level="raise")
    except Exception as exc:  # pragma: no cover - exact errors vary by sqlglot
        raise ParseError(str(exc)) from exc


def extract_lineage(statement: exp.Expression, dialect: str) -> StatementLineage:
    stmt = _unwrap_with(statement)
    targets = _extract_targets(stmt, dialect)
    sources = _extract_sources(statement, dialect, targets)
    return StatementLineage(targets=targets, sources=sources)


def _unwrap_with(statement: exp.Expression) -> exp.Expression:
    if isinstance(statement, exp.With):
        return statement.this
    return statement


def _extract_targets(statement: exp.Expression, dialect: str) -> set[str]:
    targets: set[str] = set()

    if isinstance(statement, exp.Create):
        target = _table_name(statement.this, dialect)
        if target:
            targets.add(target)
    elif isinstance(statement, exp.Insert):
        target = _table_name(statement.this, dialect)
        if target:
            targets.add(target)
    elif isinstance(statement, exp.Select):
        target = _table_name(statement.args.get("into"), dialect)
        if target:
            targets.add(target)

    return targets


def _extract_sources(
    statement: exp.Expression, dialect: str, targets: set[str]
) -> set[str]:
    cte_names = _collect_cte_names(statement)
    sources: set[str] = set()

    for table in statement.find_all(exp.Table):
        name = _table_name(table, dialect)
        if not name:
            continue
        normalized = name.lower()
        if normalized in cte_names:
            continue
        if normalized in {t.lower() for t in targets}:
            continue
        sources.add(normalized)

    return sources


def _collect_cte_names(statement: exp.Expression) -> set[str]:
    names: set[str] = set()
    for cte in statement.find_all(exp.CTE):
        alias = cte.alias
        name: str | None = None
        if isinstance(alias, str):
            name = alias
        elif alias is not None and getattr(alias, "name", None):
            name = alias.name
        else:
            alias_expr = cte.args.get("alias")
            if alias_expr is not None and getattr(alias_expr, "name", None):
                name = alias_expr.name
        if name:
            names.add(name.lower())
    return names


def _table_name(table_expr: exp.Expression | None, dialect: str) -> str | None:
    if table_expr is None:
        return None
    if isinstance(table_expr, exp.Table):
        catalog = table_expr.args.get("catalog")
        db = table_expr.args.get("db")
        parts: list[str] = []
        if catalog is not None:
            parts.append(catalog.name)
        if db is not None:
            parts.append(db.name)
        parts.append(table_expr.name)
        return ".".join(p for p in parts if p)
    if isinstance(table_expr, exp.Identifier):
        return table_expr.name
    if isinstance(table_expr, exp.Expression) and hasattr(table_expr, "name"):
        return str(table_expr.name)
    return None


def extract_lineage_batch(
    statements: Iterable[exp.Expression], dialect: str
) -> list[StatementLineage]:
    return [extract_lineage(stmt, dialect) for stmt in statements]
