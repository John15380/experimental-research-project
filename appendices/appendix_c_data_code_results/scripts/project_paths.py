"""Shared repository paths for the appendix analysis scripts."""

from pathlib import Path


APPENDIX = Path(__file__).resolve().parents[1]
ROOT = APPENDIX.parents[1]
DATA = APPENDIX / "data"
FIGURES = APPENDIX / "figures"
RAW_MAIN = DATA / "raw" / "main"
RAW_SINGLE = DATA / "raw" / "single"
