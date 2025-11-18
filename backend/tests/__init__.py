"""Test package bootstrap for backend."""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
SRC_PATH = ROOT / "src"
SRC_STR = str(SRC_PATH)
if SRC_STR not in sys.path:
    sys.path.insert(0, SRC_STR)
