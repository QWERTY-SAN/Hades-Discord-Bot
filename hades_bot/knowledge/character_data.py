from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] / "data" / "aether_gazer"


def _load(name: str, default):
    path = ROOT / name
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return default


GAME_KNOWLEDGE = _load("game_knowledge.json", {})
TERMINOLOGY = _load("terminology.json", {})
SOURCE_POLICY = _load("source_policy.json", {})
HADES_DATA = _load("characters/hades.json", {})
# hades_reference.json is the canonical structured Hades reference.
# HADES_DATA remains available as a compatibility alias for older imports.
HADES_REFERENCE = _load("characters/hades_reference.json", HADES_DATA)
