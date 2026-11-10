"""Kitsune skin/theme engine — the theme SDK for every surface."""

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from hermes_constants import get_hermes_home

logger = logging.getLogger(__name__)


@dataclass
class SkinConfig:
    """Complete skin configuration."""
    name: str
    description: str = ""
    colors: dict[str, str] = field(default_factory=dict)
    # Paired palettes for the opposite background polarity (mirrors the desktop app's
    # colors/darkColors pairing): a light terminal prefers `light_colors` (falling back to
    # `colors`), and vice versa for `dark_colors`.
    light_colors: dict[str, str] = field(default_factory=dict)
    dark_colors: dict[str, str] = field(default_factory=dict)
    spinner: dict[str, Any] = field(default_factory=dict)
    branding: dict[str, str] = field(default_factory=dict)
    tool_prefix: str = "┊"
    tool_emojis: dict[str, str] = field(default_factory=dict)  # per-tool emoji overrides
    banner_logo: str = ""    # Rich-markup ASCII art logo (replaces HERMES_AGENT_LOGO)
    banner_hero: str = ""    # Rich-markup hero art (replaces HERMES_CADUCEUS)
    banner_hero_compact: str = ""  # Smaller hero used when the terminal is too narrow for banner_hero
    custom_css: str = ""     # Raw CSS injected as a <style> tag on the desktop GUI (32 KiB cap)

    def get_color(self, key: str, fallback: str = "") -> str:
        return self.colors.get(key, fallback)

    def get_branding(self, key: str, fallback: str = "") -> str:
        return self.branding.get(key, fallback)

    def get_spinner_wings(self) -> list[tuple[str, str]]:
        """Spinner wing pairs, or empty list if none."""
        return [(str(pair[0]), str(pair[1])) for pair in self.spinner.get("wings", [])
                if isinstance(pair, (list, tuple)) and len(pair) == 2]


def _branding(who: str, symbol: str, goodbye: str, prompt: str = "", help_header: str = "") -> dict[str, str]:
    """Branding block for a "<who> Agent" persona keyed by its glyph."""
    return {
        "agent_name": f"{who} Agent",
        "welcome": f"Welcome to {who} Agent! Type your message or /help for commands.",
        "goodbye": goodbye, "response_label": f" {symbol} {who} ", "prompt_symbol": prompt or symbol,
        "help_header": help_header or f"({symbol}) Available Commands"}


def _wings(*glyphs) -> list[list[str]]:
    """Spinner wing pairs `⟪g` / `g⟫`; a (left, right) tuple gives asymmetric glyphs."""
    return [[f"⟪{g[0] if isinstance(g, tuple) else g}", f"{g[1] if isinstance(g, tuple) else g}⟫"]
            for g in glyphs]


# Branding shared by every Kitsune-named built-in (mono/daylight override help_header).
_HERMES_BRANDING: dict[str, str] = _branding(
    "Kitsune", "☤", "Goodbye! ☤", prompt="❯", help_header="(^_^)? Available Commands")

_BUILTIN_SKINS: dict[str, dict[str, Any]] = {
    "default": {
        "name": "default", "description": "Classic Kitsune — gold and kawaii",
        # Dark-authored; values match the TUI's DARK_THEME so both render the same gold.
        "colors": {
            "banner_border": "#CD7F32", "banner_title": "#FFD700", "banner_accent": "#FFBF00",
            "banner_dim": "#B8860B", "banner_text": "#FFF8DC", "ui_accent": "#FFBF00",
            "ui_label": "#DAA520", "ui_ok": "#4caf50", "ui_error": "#ef5350", "ui_warn": "#ffa726",
            "prompt": "#FFF8DC", "input_rule": "#CD7F32", "response_border": "#FFD700",
            "status_bar_bg": "#1a1a2e", "status_bar_text": "#C0C0C0",
            "status_bar_strong": "#FFD700", "status_bar_dim": "#8A7A4A",
            "status_bar_good": "#8FBC8F", "status_bar_warn": "#FFD700", "status_bar_bad": "#FF8C00",
            "status_bar_critical": "#FF6B6B", "session_label": "#DAA520",
            "session_border": "#8B8682", "completion_menu_bg": "#1a1a2e",
            "completion_menu_current_bg": "#333355", "selection_bg": "#3a3a55",
            "shell_dollar": "#4dabf7", "voice_status_bg": "#1a1a2e"},
        # Light overlay (merged onto `colors`). Goldenrod ladder: on white the vivid
        # #FFD700/#FFBF00 read as glare and WCAG-darkened mustard (#867000) as mud; the
        # statusbar's goldenrod family (#B8860B/#DAA520) keeps the hue, tames saturation.
        # Hierarchy on white: ink body 8.9:1 > fade 5.2 > label 3.7 > muted 3.3 > title 2.7 >
        # headers 2.4. Fills (*_bg) flip the dark navy surfaces to light polarity.
        "light_colors": {
            "banner_title": "#C8961E", "banner_accent": "#D89B04", "banner_dim": "#B8860B",
            "banner_text": "#5C4718", "ui_accent": "#D89B04", "ui_label": "#A97E10",
            "ui_ok": "#2E7D32", "ui_error": "#C62828", "ui_warn": "#D97706", "prompt": "#5C4718",
            "response_border": "#C8961E", "session_label": "#A97E10", "status_bar_text": "#6F6F6F",
            "status_bar_strong": "#C8961E", "status_bar_dim": "#9A8A5A",
            "status_bar_good": "#2E7D32", "status_bar_warn": "#C8961E", "status_bar_bad": "#C2410C",
            "status_bar_critical": "#B91C1C", "shell_dollar": "#1E6FC0",
            "completion_menu_bg": "#F5F5F5", "completion_menu_current_bg": "#E0D1BF",
            "selection_bg": "#D4E4F7", "status_bar_bg": "#F5F5F5", "voice_status_bg": "#F5F5F5"},
        "spinner": {},  # empty = hardcoded defaults in display.py
        "branding": _HERMES_BRANDING,
        "tool_prefix": "┊"},
}

# Kitsune Agent ships a single skin (ryu, bundled as data/skins/ryu.yaml). The stock dict above is kept
# only as the merge base for skin YAML files that omit keys; it is not a selectable skin.
_BASE_SKIN: dict[str, Any] = _BUILTIN_SKINS.pop("default")

_active_skin: Optional[SkinConfig] = None
DEFAULT_SKIN = "ryu"  # Kitsune Agent: bundled skin used when display.skin is unset
_active_skin_name: str = DEFAULT_SKIN
# Routed multiplex profiles: (name, skin) per home key. ``display.skin`` and ``<home>/skins/*.yaml``
# are per profile, and the relay display name / TUI skin payload are read under each profile's
# override — one module slot would be last-writer-wins across profiles. Unscoped keeps the module slot.
_active_skin_by_home: dict[str, tuple[str, SkinConfig]] = {}


def _routed_home_key() -> Optional[str]:
    from hermes_constants import get_hermes_home_override, hermes_home_key
    return None if get_hermes_home_override() is None else hermes_home_key()


def _profile_config() -> dict:
    try:
        from hermes_cli.config import load_config_readonly
        return load_config_readonly() or {}
    except Exception:
        return {}


def _skins_dir() -> Path:
    return get_hermes_home() / "skins"


def _bundled_skins_dir() -> Path:
    """Skins shipped inside the package (Kitsune Agent: ryu)."""
    return Path(__file__).parent / "data" / "skins"


def _load_skin_from_yaml(path: Path) -> Optional[dict[str, Any]]:
    """Load a skin definition from a YAML file; None on any failure."""
    try:
        import hermes_yaml as yaml
        with open(path, "r", encoding="utf-8-sig") as f:
            data = yaml.safe_load(f)
        if isinstance(data, dict) and "name" in data:
            return data
    except Exception as e:
        logger.debug("Failed to load skin from %s: %s", path, e)
    return None


def _build_skin_config(data: dict[str, Any]) -> SkinConfig:
    """Build a SkinConfig from a raw dict (built-in or loaded from YAML)."""
    default = _BASE_SKIN
    skin_name = str(data.get("name", "unknown"))

    def section(key: str) -> dict[str, Any]:
        value = data.get(key)
        if isinstance(value, dict):
            return value
        if value is not None:
            logger.warning("Skin '%s' has invalid '%s' section type (%s); ignoring section",
                           skin_name, key, type(value).__name__)
        return {}

    def merged(key: str) -> dict[str, Any]:
        return {**default.get(key, {}), **section(key)}
    # Paired palettes are NOT merged over the default skin's blocks: an empty block means
    # "no hand-tuned variant for that polarity" and consumers (the TUI) fall back to `colors`
    # + automatic adaptation, which beats the default's gold light palette under a crimson skin.
    return SkinConfig(
        name=skin_name, description=data.get("description", ""), colors=merged("colors"),
        light_colors=section("light_colors"), dark_colors=section("dark_colors"),
        spinner=merged("spinner"), branding=merged("branding"),
        tool_prefix=data.get("tool_prefix", default.get("tool_prefix", "┊")),
        tool_emojis=section("tool_emojis"), banner_logo=data.get("banner_logo", ""),
        banner_hero=data.get("banner_hero", ""),
        banner_hero_compact=data.get("banner_hero_compact", ""),
        custom_css=str(data.get("customCSS", "")).strip()[:32768])


def list_skins() -> list[dict[str, str]]:
    """List all available skins (built-in + user-installed); user skins never shadow built-ins."""
    result = [{"name": name, "description": data.get("description", ""), "source": "builtin"}
              for name, data in _BUILTIN_SKINS.items()]
    for source, skins_path in (("bundled", _bundled_skins_dir()), ("user", _skins_dir())):
        for f in sorted(skins_path.glob("*.yaml")) if skins_path.is_dir() else ():
            data = _load_skin_from_yaml(f)
            if data and not any(s["name"] == data.get("name", f.stem) for s in result):
                result.append({"name": data.get("name", f.stem), "description": data.get("description", ""),
                               "source": source})
    return result


def load_skin(name: str) -> SkinConfig:
    """Load a skin by name: user skins first, then bundled; unknown names fall back to ryu."""
    for path in (_skins_dir() / f"{name}.yaml", _bundled_skins_dir() / f"{name}.yaml"):
        data = _load_skin_from_yaml(path) if path.is_file() else None
        if data:
            return _build_skin_config(data)
    if name != DEFAULT_SKIN:
        logger.warning("Skin '%s' not found, using %s", name, DEFAULT_SKIN)
        return load_skin(DEFAULT_SKIN)
    return _build_skin_config(_BASE_SKIN)  # bundled ryu.yaml missing/corrupt: never crash


def get_active_skin() -> SkinConfig:
    """Currently active skin config (cached)."""
    global _active_skin
    home_key = _routed_home_key()
    if home_key is not None:
        entry = _active_skin_by_home.get(home_key)
        if entry is None:
            # Cold routed profile: its own ``display.skin`` (nobody ran init_skin_from_config for it).
            init_skin_from_config(_profile_config())
            entry = _active_skin_by_home[home_key]
        return entry[1]
    if _active_skin is None:
        _active_skin = load_skin(_active_skin_name)
    return _active_skin


def set_active_skin(name: str) -> SkinConfig:
    """Switch the active skin. Returns the new SkinConfig."""
    global _active_skin, _active_skin_name
    skin = load_skin(name)
    home_key = _routed_home_key()
    if home_key is not None:
        _active_skin_by_home[home_key] = (name, skin)
        return skin
    _active_skin_name = name
    _active_skin = skin
    return _active_skin


def get_active_skin_name() -> str:
    home_key = _routed_home_key()
    if home_key is not None:
        entry = _active_skin_by_home.get(home_key)
        return entry[0] if entry else DEFAULT_SKIN
    return _active_skin_name


def init_skin_from_config(config: dict) -> None:
    """Initialize the active skin from CLI config at startup."""
    display = config.get("display") or {}
    skin_name = display.get("skin", DEFAULT_SKIN) if isinstance(display, dict) else DEFAULT_SKIN
    set_active_skin(skin_name.strip() if isinstance(skin_name, str) and skin_name.strip() else DEFAULT_SKIN)


def _active_branding(key: str, fallback: str) -> str:
    try:
        return get_active_skin().get_branding(key, fallback)
    except Exception:
        return fallback


def get_active_prompt_symbol(fallback: str = "❯") -> str:
    """Interactive prompt symbol (skins store a bare token) plus a single trailing space."""
    cleaned = (_active_branding("prompt_symbol", fallback) or fallback).strip()
    return f"{cleaned or fallback.strip()} "


def get_active_help_header(fallback: str = "(^_^)? Available Commands") -> str:
    return _active_branding("help_header", fallback)


def get_active_goodbye(fallback: str = "Goodbye! ☤") -> str:
    return _active_branding("goodbye", fallback)


# Palette resolution order for prompt_toolkit styles: (name, skin color key, fallback). A
# fallback starting with "@" names an earlier entry (so a missing key inherits its remapped value).
_STYLE_PALETTE = (
    ("prompt", "prompt", ""), ("input_rule", "input_rule", "#CD7F32"),
    ("title", "banner_title", "#FFD700"), ("text", "banner_text", "#FFF8DC"),
    ("dim", "banner_dim", "#555555"), ("label", "ui_label", "@title"), ("warn", "ui_warn", "#FF8C00"),
    ("error", "ui_error", "#FF6B6B"), ("status_bg", "status_bar_bg", "#1a1a2e"),
    ("status_text", "status_bar_text", "@text"), ("status_strong", "status_bar_strong", "@title"),
    ("status_dim", "status_bar_dim", "@dim"), ("ok", "ui_ok", "#8FBC8F"),
    ("status_good", "status_bar_good", "@ok"), ("status_warn", "status_bar_warn", "@warn"),
    ("accent", "banner_accent", "@warn"), ("status_bad", "status_bar_bad", "@accent"),
    ("status_critical", "status_bar_critical", "@error"), ("voice_bg", "voice_status_bg", "@status_bg"),
    ("menu_bg", "completion_menu_bg", "#1a1a2e"), ("menu_current_bg", "completion_menu_current_bg", "#333355"),
    ("menu_meta_bg", "completion_menu_meta_bg", "@menu_bg"),
    ("menu_meta_current_bg", "completion_menu_meta_current_bg", "@menu_current_bg"))

# prompt_toolkit style class -> format template over the resolved palette names.
_STYLE_TEMPLATES = {
    "input-area": "",  # terminal default fg/bg — `prompt` styles the symbol, NOT typed text
    "placeholder": "{dim} italic", "prompt": "{prompt}", "prompt-working": "{dim} italic",
    "hint": "{dim} italic",
    "status-bar": "bg:{status_bg} {status_text}", "status-bar-strong": "bg:{status_bg} {status_strong} bold",
    "status-bar-session-title": "bg:{badge_bg} {badge_fg} bold",
    "status-bar-dim": "bg:{status_bg} {status_dim}", "status-bar-good": "bg:{status_bg} {status_good} bold",
    "status-bar-warn": "bg:{status_bg} {status_warn} bold", "status-bar-bad": "bg:{status_bg} {status_bad} bold",
    "status-bar-critical": "bg:{status_bg} {status_critical} bold",
    "subagent-dock": "bg:{status_bg} {status_text}",
    "subagent-dock.heading": "bg:{status_bg} {status_strong} bold",
    "subagent-dock.selected": "bg:{menu_current_bg} {text} bold",
    "input-rule": "{input_rule}", "image-badge": "{label} bold",
    "completion-menu": "bg:{menu_bg} {text}", "completion-menu.completion": "bg:{menu_bg} {text}",
    "completion-menu.completion.current": "bg:{menu_current_bg} {title}",
    "completion-menu.meta.completion": "bg:{menu_meta_bg} {dim}",
    "completion-menu.meta.completion.current": "bg:{menu_meta_current_bg} {label}",
    "clarify-border": "{input_rule}", "clarify-title": "{title} bold", "clarify-question": "{text} bold",
    "clarify-choice": "{dim}", "clarify-selected": "{title} bold", "clarify-active-other": "{title} italic",
    "clarify-countdown": "{input_rule}",
    "sudo-prompt": "{error} bold", "sudo-border": "{input_rule}", "sudo-title": "{error} bold",
    "sudo-text": "{text}",
    "approval-border": "{input_rule}", "approval-title": "{warn} bold", "approval-desc": "{text} bold",
    "approval-cmd": "{dim} italic", "approval-choice": "{dim}", "approval-selected": "{title} bold",
    "voice-status": "bg:{voice_bg} {label}", "voice-status-recording": "bg:{voice_bg} {error} bold"}


def get_prompt_toolkit_style_overrides() -> dict[str, str]:
    """Return prompt_toolkit style overrides derived from the active skin."""
    try:
        skin = get_active_skin()
    except Exception:
        return {}
    # `prompt` is unset by default so typed text inherits the terminal's foreground (readable
    # on light and dark schemes); skins opt into a colored prompt symbol via `prompt` in YAML.
    # Every read goes through skin.get_color (cli.py wraps it for light-mode remapping).
    palette: dict[str, str] = {}
    for name, key, fallback in _STYLE_PALETTE:
        palette[name] = skin.get_color(key, palette[fallback[1:]] if fallback.startswith("@") else fallback)
    # This badge paints both sides; foreground-only light remapping destroys its contrast.
    palette["badge_bg"] = skin.colors.get(
        "status_bar_strong", skin.colors.get("banner_title", "#FFD700"))
    palette["badge_fg"] = skin.colors.get("status_bar_bg", "#1a1a2e")
    return {cls: tpl.format(**palette) for cls, tpl in _STYLE_TEMPLATES.items()}
