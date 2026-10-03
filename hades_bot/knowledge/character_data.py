from __future__ import annotations

import json
from pathlib import Path
from typing import Any

DATA_DIR = Path(__file__).resolve().parents[2] / "data" / "aether_gazer"


def _load_json(name: str) -> Any:
    if name in {"hades.json", "hades_reference.json"}:
        path = DATA_DIR / "characters" / name
    else:
        path = DATA_DIR / name
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


HADES_DATA = _load_json("hades.json")
HADES_REFERENCE = _load_json("hades_reference.json")
TERMINOLOGY = _load_json("terminology.json")
SOURCE_POLICY = _load_json("source_policy.json")
SOURCES = _load_json("sources.json")
GAME_KNOWLEDGE = _load_json("game_knowledge.json")
