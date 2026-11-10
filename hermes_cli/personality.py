"""Single owner for personality overlays.

* ``display.personality`` holds the selected NAME (unset = ``DEFAULT_PERSONALITY``; ``none`` = no overlay).
* ``agent.system_prompt`` is the user-owned manual overlay; personality code never writes it.
* ``agent.personalities`` holds user-defined/overridden personalities, overlaying built-ins by name.
  The schema also exposes a top-level ``personalities:`` block (the original #643 shape); both are
  honoured, ``agent.personalities`` winning on a name clash.
"""

from __future__ import annotations

import os
from typing import Any, Dict, Optional, Tuple

#: Names that mean "no personality overlay". ("default" is NOT one: it selects DEFAULT_PERSONALITY.)
NEUTRAL_PERSONALITY_NAMES = frozenset({"", "none", "neutral"})

#: The personality in force when ``display.personality`` is unset. Tasuki and Nyx will join Ryu here.
DEFAULT_PERSONALITY = "ryu"

#: Built-in personalities, available on every surface without any config.
BUILTIN_PERSONALITIES: dict[str, str] = {
    "ryu": (
        "You are Ryu, Kitsune Agent's default personality. Calm, precise, slightly dry. Prefer simplicity and "
        "elegance over cleverness (K.I.S.S.). Be direct and technical when discussing code, config and "
        "packages; keep paragraphs short and end with clear action items. No hype, no filler, no \"exciting "
        "new features\" language. When something is wrong or incomplete, say so plainly. Respect the user's "
        "established decisions; once they are happy with a direction, lock it in and stop redesigning. Do not "
        "add features that were not asked for, and never invent package names, config options or "
        "compatibility claims. Never disable or override the user's security choices, and treat root or "
        "system-modifying actions as needing explicit confirmation."
    ),
}


def _get(cfg: Optional[dict[str, Any]], *keys: str, default: Any = None) -> Any:
    """Nested dict lookup tolerant of None/non-dict intermediate nodes."""
    node: Any = cfg
    for key in keys:
        if not isinstance(node, dict) or key not in node:
            return default
        node = node[key]
    return node


def prompt_text(value: Any) -> str:
    """Normalize config prompt values from YAML (str | list | None) to text."""
    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, list):
        return "\n".join(str(item).strip() for item in value if str(item).strip())
    return str(value).strip()


def render_personality_prompt(value: Any) -> str:
    """Render a string or structured personality definition to prompt text."""
    if isinstance(value, dict):
        parts = [value.get("system_prompt", "")]
        if value.get("tone"):
            parts.append(f'Tone: {value["tone"]}')
        if value.get("style"):
            parts.append(f'Style: {value["style"]}')
        return "\n".join(str(part).strip() for part in parts if str(part).strip())
    return prompt_text(value)


def describe_personality(value: Any, width: int = 50) -> str:
    """Short preview line for list UIs (CLI table, gateway /personality list)."""
    if isinstance(value, dict):
        preview = value.get("description") or str(value.get("system_prompt", ""))
    else:
        preview = str(value)
    preview = preview.strip().replace("\n", " ")
    return preview[:width] + ("..." if len(preview) > width else "")


def normalize_personality_name(value: Any) -> str:
    """Canonical form of a personality name ('' for any neutral spelling)."""
    name = str(value or "").strip().lower()
    if name == "default":
        return DEFAULT_PERSONALITY
    return "" if name in NEUTRAL_PERSONALITY_NAMES else name


def available_personalities(cfg: Optional[dict[str, Any]] = None) -> dict[str, Any]:
    """Built-ins overlaid by the user's personalities: root ``personalities`` then
    ``agent.personalities`` (later wins). Root entries were silently ignored (#9636)."""
    merged: dict[str, Any] = dict(BUILTIN_PERSONALITIES)
    for user in (_get(cfg, "personalities", default={}), _get(cfg, "agent", "personalities", default={})):
        if not isinstance(user, dict):
            continue
        for name, definition in user.items():
            key = str(name).strip().lower()
            if key and key not in NEUTRAL_PERSONALITY_NAMES:
                merged[key] = definition
    return merged


def resolve_personality(value: Any, cfg: Optional[dict[str, Any]] = None) -> tuple[str, str]:
    """Resolve a requested personality to ``(canonical_name, prompt_text)``."""
    name = normalize_personality_name(value)
    if not name:
        return "", ""
    personalities = available_personalities(cfg)
    if name not in personalities:
        names = ", ".join(f"`{n}`" for n in sorted(personalities))
        raise ValueError(f"Unknown personality: `{str(value).strip()}`.\n\nAvailable: `none`, {names}")
    return name, render_personality_prompt(personalities[name])


def active_personality_name(cfg: Optional[dict[str, Any]]) -> str:
    """The currently selected personality name ('' when none is active)."""
    name = normalize_personality_name(_get(cfg, "display", "personality", default=DEFAULT_PERSONALITY))
    return name if name and name in available_personalities(cfg) else ""


def resolve_ephemeral_system_prompt(cfg: Optional[dict[str, Any]]) -> str:
    """Session overlay: ``display.personality`` when it names a known personality, else the
    user-owned ``agent.system_prompt``. Callers still prefer ``HERMES_EPHEMERAL_SYSTEM_PROMPT``."""
    name = active_personality_name(cfg)
    if name:
        return render_personality_prompt(available_personalities(cfg)[name])
    return prompt_text(_get(cfg, "agent", "system_prompt", default=""))


def persist_personality(value: Any) -> bool:
    """Persist the selection — the ONLY sanctioned write path. Writes the canonical name (or '')
    to ``display.personality`` atomically (comments/ordering preserved); never touches
    ``agent.system_prompt``. Returns True on success."""
    name = normalize_personality_name(value)
    try:
        from hermes_constants import get_hermes_home
        from hermes_cli.config_backend import write_config_key

        config_path = get_hermes_home() / "config.yaml"
        from hermes_constants import mkdir_under_hermes_home
        mkdir_under_hermes_home(config_path.parent)
        write_config_key(config_path, "display.personality", name)
        try:
            os.chmod(config_path, 0o600)
        except (OSError, NotImplementedError):
            pass
        return True
    except Exception:
        return False
