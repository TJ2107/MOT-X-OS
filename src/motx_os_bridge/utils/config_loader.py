from __future__ import annotations
from pathlib import Path
from typing import Any


def _parse_value(value: str) -> Any:
    text = value.strip()
    if text.lower() in {"true", "false"}:
        return text.lower() == "true"
    if text.isdigit():
        return int(text)
    if (text.startswith("'") and text.endswith("'")) or (text.startswith('"') and text.endswith('"')):
        return text[1:-1]
    try:
        return float(text)
    except ValueError:
        return text


def load_settings() -> dict[str, Any]:
    config_path = Path(__file__).resolve().parents[1] / "config" / "settings.yaml"
    if not config_path.exists():
        return {}

    settings: dict[str, Any] = {}
    stack: list[tuple[int, dict[str, Any]]] = [(0, settings)]

    for raw_line in config_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.split("#", 1)[0].rstrip()
        if not line.strip():
            continue

        indent = len(raw_line) - len(raw_line.lstrip(" "))
        while stack and indent < stack[-1][0]:
            stack.pop()

        current = stack[-1][1]
        if ":" not in line:
            continue

        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()

        if not value:
            child: dict[str, Any] = {}
            current[key] = child
            stack.append((indent + 2, child))
        else:
            current[key] = _parse_value(value)

    return settings
