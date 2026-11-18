#!/usr/bin/env python3
"""Run the canonical appendix script while preserving the tools entry point."""

from pathlib import Path
import runpy
import sys


SCRIPT = (
    Path(__file__).resolve().parents[1]
    / "appendices"
    / "appendix_c_data_code_results"
    / "scripts"
    / "generate_tikz_figures.py"
)

if __name__ == "__main__":
    sys.path.insert(0, str(SCRIPT.parent))
    runpy.run_path(str(SCRIPT), run_name="__main__")
