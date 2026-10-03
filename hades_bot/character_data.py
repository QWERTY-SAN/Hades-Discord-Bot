from __future__ import annotations

import json
from pathlib import Path
from typing import Any

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def _load_json(name: str) -> Any:
    path = DATA_DIR / name
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


HADES_DATA = _load_json("hades.json")
TERMINOLOGY = _load_json("terminology.json")
SOURCES = _load_json("sources.json")
