from __future__ import annotations

import logging
from pathlib import Path

import networkx as nx

from .lineage import Transform


def build_graph(transforms: list[Transform]) -> nx.DiGraph:
    graph = nx.DiGraph()

    for transform in transforms:
        graph.add_node(
            transform.transform_id,
            type="transform",
            label=f"{transform.file_path}#{transform.statement_index}",
        )
        for source in transform.sources:
            table_node = f"table:{source}"
            graph.add_node(table_node, type="table", label=source)
            graph.add_edge(table_node, transform.transform_id)
        for target in transform.targets:
            table_node = f"table:{target}"
            graph.add_node(table_node, type="table", label=target)
            graph.add_edge(transform.transform_id, table_node)

    return graph


def write_graphml(graph: nx.DiGraph, out_path: Path) -> None:
    nx.write_graphml(graph, out_path)


def write_html(graph: nx.DiGraph, out_path: Path, logger: logging.Logger) -> None:
    try:
        from pyvis.network import Network
    except Exception as exc:  # pragma: no cover - optional dependency
        logger.warning("pyvis not available: %s", exc)
        return

    net = Network(height="800px", width="100%", directed=True)

    for node_id, data in graph.nodes(data=True):
        node_type = data.get("type")
        label = data.get("label", node_id)
        if node_type == "transform":
            net.add_node(node_id, label=label, shape="box", color="#f5b042")
        else:
            net.add_node(node_id, label=label, shape="dot", color="#5aa9e6")

    for source, target in graph.edges():
        net.add_edge(source, target)

    net.write_html(str(out_path))


def write_png(graph: nx.DiGraph, out_path: Path, logger: logging.Logger) -> None:
    try:
        from networkx.drawing.nx_pydot import to_pydot
    except Exception as exc:  # pragma: no cover - optional dependency
        logger.warning("pydot not available for PNG export: %s", exc)
        return

    try:
        pydot_graph = to_pydot(graph)
        pydot_graph.write_png(str(out_path))
    except Exception as exc:  # pragma: no cover - graphviz availability varies
        logger.warning("Graphviz PNG export failed: %s", exc)
