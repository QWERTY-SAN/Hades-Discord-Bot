from __future__ import annotations

import os
import py_compile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

for path in ROOT.rglob("*.py"):
    if "__pycache__" not in path.parts:
        py_compile.compile(str(path), doraise=True)

os.environ.setdefault("DISCORD_TOKEN", "test-token")
os.environ.setdefault("GEMINI_API_KEY", "test-key")

from hades_bot.config import SETTINGS  # noqa: E402
from hades_bot.core.scope import contains_forbidden_topic, is_hades_scope_allowed  # noqa: E402

assert SETTINGS.emojis_enabled is True
assert SETTINGS.knowledge_context_max_chars >= 1000
assert is_hades_scope_allowed("Tell me about Hades")
assert is_hades_scope_allowed("How are you?")
assert is_hades_scope_allowed("I had a rough day.")
assert not is_hades_scope_allowed("Hades, what do you think about F1?")
assert not is_hades_scope_allowed("Hades, who won the NBA finals?")
assert not is_hades_scope_allowed("Hades, write me Python code.")
assert not is_hades_scope_allowed("What is the capital of Japan?")
assert contains_forbidden_topic("Formula One")
assert contains_forbidden_topic("basketball")
assert not contains_forbidden_topic("Aether Gazer")

print("Hades static smoke tests passed.")
