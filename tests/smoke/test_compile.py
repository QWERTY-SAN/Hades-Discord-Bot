from pathlib import Path
import py_compile


def test_python_sources_compile():
    root = Path(__file__).resolve().parents[2]
    for path in root.rglob("*.py"):
        if ".venv" in path.parts:
            continue
        py_compile.compile(str(path), doraise=True)
