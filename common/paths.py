"""Folder locations used by every part of the project.

Scripts use these names instead of typing file paths, so the project still works
if you move the folder somewhere else.
"""
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"          # the three original files. Never edit these.
SCHEMA_DIR = PROJECT_ROOT / "schema"      # SQL to import into MySQL
OUTPUT_DIR = PROJECT_ROOT / "outputs"     # files the pipeline creates

OUTPUT_DIR.mkdir(exist_ok=True)
