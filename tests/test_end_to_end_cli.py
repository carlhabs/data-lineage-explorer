import importlib.util
import subprocess
import sys
from pathlib import Path


def test_end_to_end_cli(tmp_path: Path):
    examples_dir = Path(__file__).resolve().parents[1] / "examples"
    out_dir = tmp_path / "out"

    cmd = [
        sys.executable,
        "-m",
        "dle.cli",
        "scan",
        "--path",
        str(examples_dir),
        "--out",
        str(out_dir),
        "--format",
        "graphml,md,html,png",
        "--dialect",
        "postgres",
    ]

    result = subprocess.run(cmd, capture_output=True, text=True, check=False)

    assert result.returncode == 0, result.stderr
    assert (out_dir / "lineage.graphml").exists()
    assert (out_dir / "report.md").exists()

    if importlib.util.find_spec("pyvis") is not None:
        assert (out_dir / "lineage.html").exists()
