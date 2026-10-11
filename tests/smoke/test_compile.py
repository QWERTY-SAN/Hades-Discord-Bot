from pathlib import Path
import py_compile


def test_python_sources_compile():
    root = Path(__file__).resolve().parents[2]
    for path in root.rglob("*.py"):
        if ".venv" in path.parts:
            continue
        py_compile.compile(str(path), doraise=True)

def test_ai_handler_reply_context_is_explicit():
    root = Path(__file__).resolve().parents[2]
    source = (root / "hades_bot" / "bot.py").read_text()
    assert "direct_reply: bool = False" in source
    assert "direct_reply=direct_reply" in source
    assert "trigger=trigger, direct_reply=replied" in source


def test_presence_and_separate_cooldown_maintenance_are_configured():
    root = Path(__file__).resolve().parents[2]
    source = (root / "hades_bot" / "bot.py").read_text()
    assert 'activity=discord.CustomActivity(name=f"{SETTINGS.bot_prefix}help @GitHub")' in source
    assert "@tasks.loop(seconds=SETTINGS.cooldown_prune_interval)" in source
    assert "self.cooldown_maintenance_loop.start()" in source
