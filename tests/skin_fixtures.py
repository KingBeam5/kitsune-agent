"""Kitsune Agent ships one skin (ryu). Upstream tests that need a second, distinct skin install it here."""
from pathlib import Path


def install_skin(home, name: str, tool_prefix: str = "┊") -> Path:
    skins = Path(home) / "skins"
    skins.mkdir(parents=True, exist_ok=True)
    path = skins / f"{name}.yaml"
    path.write_text(
        f'name: {name}\ndescription: test fixture\ntool_prefix: "{tool_prefix}"\n', encoding="utf-8")
    return path
