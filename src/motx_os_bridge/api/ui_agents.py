"""État et contrôle des agents affichés dans l'UI (onglet Agents)."""

from __future__ import annotations

import asyncio
import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

_voice_engine = None
_black_hole_watch_task: Optional[asyncio.Task] = None


def get_voice_engine():
    global _voice_engine
    if _voice_engine is None:
        from ..plugins.voice_engine_enhanced import EnhancedVoiceEngine
        _voice_engine = EnhancedVoiceEngine()
    return _voice_engine


def _lazy_imports():
    from .server_v2 import (
        get_black_hole,
        get_eye_tracking,
        get_semantic_rewind,
        get_shadow_mode,
    )
    return get_black_hole, get_eye_tracking, get_semantic_rewind, get_shadow_mode


async def ensure_black_hole_watch() -> None:
    global _black_hole_watch_task
    get_black_hole, _, _, _ = _lazy_imports()
    hole = get_black_hole()
    hole.watching_enabled = True
    if _black_hole_watch_task is None or _black_hole_watch_task.done():
        _black_hole_watch_task = asyncio.create_task(hole.watch_nexus_folder())
        logger.info("Black Hole watcher démarré depuis l'UI agents")


def _shadow_is_recording(shadow) -> bool:
    session = shadow.observation_session
    return bool(session and session.get("status") == "recording")


async def build_ui_agents_snapshot() -> List[Dict[str, Any]]:
    get_black_hole, get_eye_tracking, get_semantic_rewind, get_shadow_mode = _lazy_imports()
    shadow = get_shadow_mode()
    hole = get_black_hole()
    rewind = get_semantic_rewind()
    eye = get_eye_tracking()
    voice = get_voice_engine()

    nexus_count = len(hole.ingested_files)
    shadow_captures = len(shadow.recorded_actions)
    workflows = len(shadow.workflow_candidates)
    episodes = len(rewind.episodic_memory)
    voice_commands = getattr(voice, "commands_processed", 0)

    shadow_active = _shadow_is_recording(shadow)
    voice_active = bool(getattr(voice, "is_listening", False))
    eye_active = bool(getattr(eye, "is_enabled", False))
    nexus_active = bool(getattr(hole, "watching_enabled", False))

    return [
        {
            "id": "blackhole",
            "active": nexus_active,
            "score": nexus_count,
            "stat": f"{nexus_count} fichier{'s' if nexus_count != 1 else ''}",
        },
        {
            "id": "shadow",
            "active": shadow_active,
            "score": shadow_captures,
            "stat": f"{shadow_captures} capture{'s' if shadow_captures != 1 else ''} · {workflows} workflow{'s' if workflows != 1 else ''}",
        },
        {
            "id": "voice",
            "active": voice_active,
            "score": voice_commands,
            "stat": f"{voice_commands} commande{'s' if voice_commands != 1 else ''}",
        },
        {
            "id": "eyetrack",
            "active": eye_active,
            "score": 100 if getattr(eye, "calibration_done", False) else (50 if eye_active else 0),
            "stat": "Calibré" if getattr(eye, "calibration_done", False) else ("Actif" if eye_active else "Non calibré"),
        },
        {
            "id": "rewind",
            "active": episodes > 0 or getattr(rewind, "collection", None) is not None,
            "score": episodes,
            "stat": f"{episodes} épisode{'s' if episodes != 1 else ''}",
        },
    ]


async def toggle_ui_agent(agent_id: str, active: bool) -> Dict[str, Any]:
    get_black_hole, get_eye_tracking, get_semantic_rewind, get_shadow_mode = _lazy_imports()
    agent_id = (agent_id or "").strip().lower()

    try:
        if agent_id == "blackhole":
            hole = get_black_hole()
            if active:
                await ensure_black_hole_watch()
            else:
                hole.watching_enabled = False

        elif agent_id == "shadow":
            shadow = get_shadow_mode()
            if active:
                if not _shadow_is_recording(shadow):
                    await shadow.start_shadow_mode()
            else:
                if _shadow_is_recording(shadow):
                    await shadow.stop_shadow_mode()

        elif agent_id == "voice":
            voice = get_voice_engine()
            if active:
                if not voice.is_listening:
                    await voice.initialize()
            else:
                voice.is_listening = False

        elif agent_id == "eyetrack":
            eye = get_eye_tracking()
            if active:
                if not eye.is_enabled:
                    await eye.initialize()
            else:
                eye.is_enabled = False

        elif agent_id == "rewind":
            if active:
                await get_semantic_rewind().record_episode(
                    {"app": "MOT-X", "text": "Activation agent Semantic Rewind"}
                )
        else:
            return {"success": False, "message": f"Agent inconnu: {agent_id}"}

        agents = await build_ui_agents_snapshot()
        return {"success": True, "agent_id": agent_id, "active": active, "agents": agents}
    except Exception as exc:
        logger.error("Toggle agent %s failed: %s", agent_id, exc)
        return {"success": False, "message": str(exc), "agent_id": agent_id}
