"""Détection d'activité réelle (fenêtre au premier plan, processus Windows)."""

from __future__ import annotations

import logging
import sys
from typing import Dict, List, Optional, Tuple

import psutil

logger = logging.getLogger(__name__)

# process name fragment (lower) -> label affiché
APP_LABELS = {
    "code": "VS Code",
    "cursor": "Cursor",
    "devenv": "Visual Studio",
    "pycharm": "PyCharm",
    "idea64": "IntelliJ",
    "chrome": "Chrome",
    "msedge": "Edge",
    "firefox": "Firefox",
    "brave": "Brave",
    "notion": "Notion",
    "obsidian": "Obsidian",
    "winword": "Word",
    "excel": "Excel",
    "powerpnt": "PowerPoint",
    "figma": "Figma",
    "zoom": "Zoom",
    "teams": "Microsoft Teams",
    "slack": "Slack",
    "discord": "Discord",
    "spotify": "Spotify",
    "vlc": "VLC",
    "explorer": "Explorateur",
    "windowsterminal": "Terminal",
    "pwsh": "PowerShell",
    "powershell": "PowerShell",
    "cmd": "Invite de commandes",
    "python": "Python",
    "node": "Node.js",
}

STATE_RULES: List[Tuple[str, List[str]]] = [
    ("MEETING", ["zoom", "teams", "slack", "discord", "webex", "skype"]),
    ("CODING", ["code", "cursor", "devenv", "pycharm", "idea", "idea64", "vscodium", "windowsterminal", "pwsh", "powershell", "cmd", "python", "node", "git"]),
    ("CREATIVE", ["figma", "photoshop", "illustrator", "indesign", "blender", "canva"]),
    ("RELAXATION", ["spotify", "vlc", "steam", "netflix", "youtube"]),
    ("FOCUS", ["notion", "obsidian", "winword", "word", "excel", "onenote"]),
]

IGNORED_PROCESSES = {
    "system", "registry", "smss.exe", "csrss.exe", "wininit.exe", "services.exe",
    "lsass.exe", "svchost.exe", "dwm.exe", "fontdrvhost.exe", "sihost.exe",
    "taskhostw.exe", "runtimebroker.exe", "searchhost.exe", "startmenuexperiencehost.exe",
    "shellhost.exe", "applicationframehost.exe", "textinputhost.exe", "lockapp.exe",
    "securityhealthsystray.exe", "motx", "uvicorn", "python.exe",
}


def _normalize_process_name(name: Optional[str]) -> str:
    if not name:
        return ""
    return name.lower().replace(".exe", "")


def friendly_app_name(process_name: Optional[str]) -> Optional[str]:
    key = _normalize_process_name(process_name)
    if not key:
        return None
    for fragment, label in APP_LABELS.items():
        if fragment in key:
            return label
    if process_name and process_name.lower().endswith(".exe"):
        return process_name[:-4]
    return process_name


def get_foreground_process_name() -> Optional[str]:
    if sys.platform != "win32":
        return None
    try:
        import ctypes

        user32 = ctypes.windll.user32
        hwnd = user32.GetForegroundWindow()
        if not hwnd:
            return None
        pid = ctypes.c_ulong()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        if not pid.value:
            return None
        return psutil.Process(pid.value).name()
    except Exception as exc:
        logger.debug("Foreground window detection failed: %s", exc)
        return None


def infer_cognitive_state_id(process_name: Optional[str]) -> Tuple[str, float]:
    """Retourne un id UI (CODING, FOCUS, …) et un score de confiance 0–1."""
    key = _normalize_process_name(process_name)
    if not key:
        return "FOCUS", 0.2

    for state_id, fragments in STATE_RULES:
        if any(fragment in key for fragment in fragments):
            return state_id, 0.88

    if any(browser in key for browser in ("chrome", "msedge", "firefox", "brave")):
        return "FOCUS", 0.55

    return "FOCUS", 0.4


def collect_activity_snapshot() -> Dict:
    foreground_raw = get_foreground_process_name()
    foreground = friendly_app_name(foreground_raw)
    state_id, confidence = infer_cognitive_state_id(foreground_raw)

    detected_apps: List[str] = []
    if foreground:
        detected_apps.append(foreground)

    return {
        "cognitive_state": state_id,
        "cognitive_state_backend": state_id.lower(),
        "foreground_app": foreground,
        "foreground_process": foreground_raw,
        "detected_apps": detected_apps,
        "confidence": round(confidence, 2),
    }
