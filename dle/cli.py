from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from .graph import write_graphml, write_html, write_png
from .reporting import write_report
from .scanner import scan_path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="dle", description="Data Lineage Explorer")
    subparsers = parser.add_subparsers(dest="command", required=True)

    scan_parser = subparsers.add_parser("scan", help="Scan SQL files for lineage")
    scan_parser.add_argument("--path", required=True, help="File or directory to scan")
    scan_parser.add_argument("--out", required=True, help="Output directory")
    scan_parser.add_argument("--dialect", default="postgres", help="SQL dialect")
    scan_parser.add_argument(
        "--format",
        default="graphml,md",
        help="Comma-separated formats: graphml,md,html,png",
    )
    scan_parser.add_argument("--strict", action="store_true", help="Fail on parse errors")
    scan_parser.add_argument("--verbose", action="store_true", help="Enable debug logs")
    scan_parser.add_argument(
        "--include",
        default="*.sql",
        help="Glob pattern for included files",
    )
    scan_parser.add_argument(
        "--exclude",
        default="",
        help="Glob pattern for excluded files",
    )

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=log_level, format="%(levelname)s: %(message)s")
    logger = logging.getLogger("dle")

    include_patterns = [p.strip() for p in args.include.split(",") if p.strip()]
    exclude_patterns = [p.strip() for p in args.exclude.split(",") if p.strip()]
    output_dir = Path(args.out)
    output_dir.mkdir(parents=True, exist_ok=True)

    try:
        result = scan_path(
            Path(args.path),
            dialect=args.dialect,
            include_patterns=include_patterns,
            exclude_patterns=exclude_patterns,
            strict=args.strict,
            logger=logger,
        )
    except FileNotFoundError as exc:
        logger.error(str(exc))
        return 2
    except Exception as exc:  # pragma: no cover - CLI fallback
        logger.error("Scan failed: %s", exc)
        return 1

    formats = {f.strip().lower() for f in args.format.split(",") if f.strip()}
    graphml_path = output_dir / "lineage.graphml"
    report_path = output_dir / "report.md"

    write_graphml(result.graph, graphml_path)
    write_report(result, report_path)

    if "html" in formats:
        write_html(result.graph, output_dir / "lineage.html", logger)
    if "png" in formats:
        write_png(result.graph, output_dir / "lineage.png", logger)

    logger.info("Wrote outputs to %s", output_dir.as_posix())
    return 0


if __name__ == "__main__":
    sys.exit(main())
