"""Settings, read from ~/.config/http-term/config.toml."""

from __future__ import annotations

import os
from dataclasses import dataclass, fields
from pathlib import Path
from typing import Any

from http_term.theme import PALETTES

EDITING_MODES = ("emacs", "vi")


@dataclass
class Settings:
    theme: str = "pitch"
    editing_mode: str = "emacs"
    headers: bool = True  # show response headers
    timeout: float = 30.0
    max_lines: int = 300  # longer bodies are cut; /body shows all of it

    def set(self, name: str, value: Any) -> None:
        """Coerce and assign a setting; raises KeyError for unknown names, ValueError for bad values."""
        spec = {f.name: f for f in fields(self)}[name]
        default = spec.default
        if isinstance(default, bool):
            if isinstance(value, str):
                lowered = value.strip().lower()
                if lowered not in ("on", "off", "true", "false", "yes", "no", "1", "0"):
                    raise ValueError(f"{name} is on or off")
                value = lowered in ("on", "true", "yes", "1")
            value = bool(value)
        elif isinstance(default, (int, float)):
            try:
                value = type(default)(value)
            except (TypeError, ValueError):
                raise ValueError(f"{name} expects a number") from None
            if value <= 0:
                raise ValueError(f"{name} must be positive")
        else:
            value = str(value).strip().lower()
        if name == "theme" and value not in PALETTES:
            raise ValueError(f"theme must be one of: {', '.join(PALETTES)}")
        if name == "editing_mode" and value not in EDITING_MODES:
            raise ValueError("editing_mode must be emacs or vi")
        setattr(self, name, value)


def config_file() -> Path:
    parent = Path(os.environ.get("XDG_CONFIG_HOME") or os.path.expanduser("~/.config"))
    migrate(parent / "flare", parent / "http-term")
    return parent / "http-term" / "config.toml"


def migrate(old: Path, new: Path) -> None:
    """:http used to be called flare: copy its settings, aliases and history over once, unless the
    new folder already holds more than the installer's venv. The old folder is left alone."""
    if not old.is_dir() or (new.is_dir() and any(p.name != "venv" for p in new.iterdir())):
        return
    try:
        import shutil

        shutil.copytree(old, new, symlinks=True, dirs_exist_ok=True, ignore=shutil.ignore_patterns("venv"))
    except OSError:
        pass


def load_settings(path: Path | None = None) -> tuple[Settings, list[str]]:
    settings = Settings()
    warnings: list[str] = []
    path = path or config_file()
    if path.exists():
        try:
            import tomllib
        except ImportError:  # Python 3.10
            import tomli as tomllib  # type: ignore[no-redef]
        try:
            data = tomllib.loads(path.read_text())
        except (OSError, ValueError) as e:
            return settings, [f"could not read {path}: {e}"]
        for key, value in data.items():
            try:
                settings.set(key, value)
            except KeyError:
                warnings.append(f"config: unknown setting {key!r}")
            except ValueError as e:
                warnings.append(f"config: {e}")
    if theme := os.environ.get("HTTP_TERM_THEME"):
        try:
            settings.set("theme", theme)
        except ValueError as e:
            warnings.append(f"HTTP_TERM_THEME: {e}")
    return settings, warnings
