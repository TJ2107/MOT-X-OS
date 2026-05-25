from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import asyncio
import json
import logging
import re

from fastapi import FastAPI, HTTPException, UploadFile, File, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn

from ..core.engine import MOTXAutomationEngine
from ..core.multi_agent_system import AgentType, MultiAgentSystem
from ..plugins.enhanced_analytics import EnhancedAnalytics
from ..plugins.real_time_sync import RealTimeSync
from ..plugins.vision_engine import VisionEngine

logger = logging.getLogger(__name__)


class ExecuteRequest(BaseModel):
    instruction: str
    user_id: str = "default"
    metadata: Optional[Dict[str, Any]] = None


class CognitiveRequest(BaseModel):
    instruction: str
    include_emergence: bool = True
    user_id: str = "default"


class AgentCoordinationRequest(BaseModel):
    instruction: str
    agents: List[str] = ["browser", "vision", "logic", "creativity"]
    user_id: str = "default"


class VisionRequest(BaseModel):
    image_path: str
    task: str = "ocr"


class CommandRequest(BaseModel):
    command: str
    user_id: str = "default"


class AgentToggleRequest(BaseModel):
    agent_id: str
    active: bool


app = FastAPI(
    title="MOT-X Automation Engine v2",
    description="Cognitive Operating System with Multi-Agent Orchestration",
    version="2.0.0",
    docs_url="/api/docs",
    openapi_url="/api/openapi.json"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(GZipMiddleware, minimum_size=1000)

# Try to mount the frontend production build (Vite `dist`) if available.
# Common locations checked (local repo during development, or copied
# into the image at /app/static during Docker build).
dist_paths = [
    Path(__file__).resolve().parents[2] / "motx-frontend" / "dist",
    Path.cwd() / "static",
    Path(__file__).resolve().parent / "static",
]
for p in dist_paths:
    try:
        if p.exists():
            app.mount("/", StaticFiles(directory=str(p), html=True), name="frontend")
            logger.info(f"Mounting frontend static files from {p}")
            break
    except Exception:
        # ignore filesystem issues during import; continue to next candidate
        continue

engine: Optional[MOTXAutomationEngine] = None
multi_agent: Optional[MultiAgentSystem] = None
analytics: Optional[EnhancedAnalytics] = None
real_time: Optional[RealTimeSync] = None
vision_engine: Optional[VisionEngine] = None
eye_tracking = None
shadow_mode = None
semantic_rewind = None
liquid_os = None
black_hole = None
active_connections: List[WebSocket] = []


def get_eye_tracking():
    global eye_tracking
    if eye_tracking is None:
        from ..plugins.eye_tracking_integrated import IntegratedEyeTracking
        eye_tracking = IntegratedEyeTracking()
    return eye_tracking


def get_shadow_mode():
    global shadow_mode
    if shadow_mode is None:
        from ..plugins.shadow_mode_engine import ShadowModeEngine
        shadow_mode = ShadowModeEngine()
    return shadow_mode


def get_semantic_rewind():
    global semantic_rewind
    if semantic_rewind is None:
        from ..plugins.semantic_rewind_engine import SemanticRewindEngine
        semantic_rewind = SemanticRewindEngine()
    return semantic_rewind


def get_liquid_os():
    global liquid_os
    if liquid_os is None:
        from ..plugins.liquid_os_engine import LiquidOSEngine
        liquid_os = LiquidOSEngine()
    return liquid_os


def get_black_hole():
    global black_hole
    if black_hole is None:
        from ..plugins.black_hole_folder import BlackHoleFolder
        black_hole = BlackHoleFolder()
    return black_hole


def _format_command_message(payload: Any) -> str:
    if payload is None:
        return "Aucun résultat"
    if isinstance(payload, str):
        return payload
    try:
        return json.dumps(payload, ensure_ascii=False, indent=2, default=str)
    except (TypeError, ValueError):
        return str(payload)


COMMAND_TIMEOUT_SEC = 45
NEXUS_RECOVER_DELAY_SEC = 3.2


def _nexus_recover_preamble(recovery_index: int) -> str:
    lines = [
        "══════════════════════════════════════════════════════",
        "  ⛔ AVERTISSEMENT NEXUS — RÉCUPÉRATION DÉCONSEILLÉE",
        "══════════════════════════════════════════════════════",
        "",
        "Ce fichier a été absorbé volontairement dans le vide.",
        "Le Black Hole existe pour que vous ne triiez plus — pas pour",
        "récupérer à la légère ce que vous aviez décidé d'oublier.",
        "",
        "Forcer une extraction :",
        "  • perturbe la mémoire vectorielle du Nexus,",
        "  • récompense la désorganisation,",
        "  • peut corrompre l'aperçu sémantique des autres archives.",
        "",
        "Si vous n'êtes pas certain, fermez ce terminal et utilisez",
        "uniquement nexus.search() pour CONSULTER sans extraire.",
    ]
    if recovery_index >= 2:
        lines.extend([
            "",
            f"⚡ Récupération n°{recovery_index} sur cette session.",
            "   Votre discipline de classement se dégrade mesurablement.",
        ])
    if recovery_index >= 4:
        lines.extend([
            "",
            "🛑 SEUIL NEXUS FRANCHI — le trou noir se refermera plus vite",
            "   sur vos prochains dépôts. Réfléchissez avant de réessayer.",
        ])
    lines.extend(["", "Extraction en cours malgré votre insistance…", ""])
    return "\n".join(lines)


async def _execute_nexus_recover(file_id: str) -> Dict[str, Any]:
    hole = get_black_hole()
    hole.recovery_count += 1
    recovery_index = hole.recovery_count
    preamble = _nexus_recover_preamble(recovery_index)

    await asyncio.sleep(NEXUS_RECOVER_DELAY_SEC)
    result = await hole.retrieve_file(file_id)

    if result.get("status") == "restored":
        footer = [
            "",
            "══ RÉSULTAT : EXTRACTION FORCÉE ══",
            f"📤 « {result.get('filename', '?')} » a été arraché au vide.",
            f"📁 Chemin : {result.get('path', '~/MOT-X_Nexus')}",
            "",
            "Ce fichier pourrait être réabsorbé si vous le laissez dans le Nexus.",
            "Ne déposez plus ce que vous n'êtes pas prêt à perdre.",
        ]
        return {
            "success": True,
            "message": preamble + "\n".join(footer),
            "data": {
                **result,
                "effect": "nexus_recover",
                "recovery_index": recovery_index,
                "dissuasive": True,
            },
        }

    footer = [
        "",
        "══ ÉCHEC — LE NEXUS REFUSE DE RELÂCHER ══",
        result.get("message") or result.get("error") or "Identifiant introuvable.",
        "",
        "C'est peut‑être un signe. Laissez ce fichier dans l'oubli.",
        "Utilisez nexus.search('…') pour retrouver l'ID correct.",
    ]
    return {
        "success": False,
        "message": preamble + "\n".join(footer),
        "data": {
            **result,
            "effect": "nexus_recover_denied",
            "recovery_index": recovery_index,
            "dissuasive": True,
        },
    }


async def dispatch_terminal_command(command: str) -> Dict[str, Any]:
    """Route les commandes du terminal UI (ex. system.status())."""
    cmd = (command or "").strip().rstrip(";")
    if not cmd:
        return {"success": False, "message": "Commande vide"}

    async def _run() -> Dict[str, Any]:
        if cmd == "system.status()":
            status = await get_status()
            return {"success": True, "message": _format_command_message(status), "data": status}

        if cmd == "shadow.start()":
            result = await get_shadow_mode().start_shadow_mode()
            return {"success": True, "message": _format_command_message(result), "data": result}

        if cmd == "shadow.stop()":
            result = await get_shadow_mode().stop_shadow_mode()
            return {"success": True, "message": _format_command_message(result), "data": result}

        nexus_match = re.fullmatch(r"nexus\.search\((['\"])(.*)\1\)", cmd)
        if nexus_match:
            query = nexus_match.group(2)
            result = await get_black_hole().semantic_search_files(query)
            return {"success": True, "message": _format_command_message(result), "data": result}

        recover_match = re.fullmatch(r"nexus\.recover\((['\"])([^'\"]+)\1\)", cmd)
        if recover_match:
            file_id = recover_match.group(2).strip()
            if not file_id:
                return {
                    "success": False,
                    "message": "⛔ file_id requis. Trouvez-le via nexus.search('mot-clé').",
                    "data": {"effect": "nexus_recover_denied"},
                }
            return await _execute_nexus_recover(file_id)

        if cmd == "cognitive.detect()":
            liquid = get_liquid_os()
            await liquid.detect_cognitive_state({})
            payload = await liquid.get_activity_snapshot()
            payload["current_state"] = liquid.current_state.value
            return {"success": True, "message": _format_command_message(payload), "data": payload}

        if cmd == "rewind.capture()":
            result = await get_semantic_rewind().record_episode({"app": "MOT-X", "text": "capture manuelle"})
            return {"success": True, "message": _format_command_message(result), "data": result}

        if cmd == "agents.list()":
            payload = await get_agents_status()
            return {"success": True, "message": _format_command_message(payload), "data": payload}

        if not engine:
            return {"success": False, "message": "Moteur d'automatisation indisponible"}

        result = await engine.process_instruction(cmd)
        return {"success": True, "message": _format_command_message(result), "data": result}

    try:
        return await asyncio.wait_for(_run(), timeout=COMMAND_TIMEOUT_SEC)
    except asyncio.TimeoutError:
        logger.warning("Commande terminal expirée (%ss): %s", COMMAND_TIMEOUT_SEC, cmd)
        return {
            "success": False,
            "message": f"Délai dépassé ({COMMAND_TIMEOUT_SEC}s). Le serveur est peut‑être occupé — réessayez.",
        }
    except Exception as e:
        logger.error(f"Commande terminal échouée ({cmd}): {e}")
        return {"success": False, "message": str(e)}


@app.on_event("startup")
async def startup_event():
    global engine, multi_agent, analytics, real_time, vision_engine
    logger.info("🚀 Démarrage MOT-X v2...")

    try:
        engine = MOTXAutomationEngine()
        logger.info("✅ Moteur principal initialisé")

        multi_agent = MultiAgentSystem()
        logger.info("✅ Système multi-agent initialisé")

        analytics = EnhancedAnalytics()
        logger.info("✅ Analytics initialisées")

        real_time = RealTimeSync()
        logger.info("✅ Sync real-time initialisée")

        vision_engine = VisionEngine()
        logger.info("✅ Vision engine initialisé")

        logger.info("🎉 MOT-X v2 prêt !")
        from .ui_agents import ensure_black_hole_watch
        asyncio.create_task(ensure_black_hole_watch())
        asyncio.create_task(_ui_agents_broadcaster_loop())
    except Exception as e:
        logger.error(f"❌ Erreur startup: {str(e)}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("👋 Arrêt MOT-X v2...")
    for connection in list(active_connections):
        try:
            await connection.close()
        except Exception:
            pass
    logger.info("✅ Arrêt propre")


@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "MOT-X v2",
        "timestamp": datetime.now().isoformat(),
        "components": {
            "engine": "ready" if engine else "loading",
            "agents": "ready" if multi_agent else "loading",
            "analytics": "ready" if analytics else "loading",
            "vision": "ready" if vision_engine else "loading"
        }
    }


@app.get("/api/config")
async def get_config():
    return {
        "name": "MOT-X",
        "version": "2.0.0",
        "features": [
            "cognitive_emergence",
            "multi_agent_system",
            "real_time_sync",
            "vision_engine",
            "advanced_analytics",
            "websocket_streaming"
        ],
        "supported_agents": [
            "browser",
            "vision",
            "voice",
            "security",
            "logic",
            "creativity",
            "optimization"
        ]
    }


async def _ui_agents_broadcaster_loop() -> None:
    from .ui_agents import build_ui_agents_snapshot
    while True:
        try:
            for agent in await build_ui_agents_snapshot():
                await broadcast_update({
                    "type": "agent_update",
                    "agent_id": agent["id"],
                    "active": agent["active"],
                    "stat": agent["stat"],
                    "score": agent["score"],
                })
        except Exception as exc:
            logger.debug("UI agents broadcaster: %s", exc)
        await asyncio.sleep(5)


async def broadcast_update(message: Dict[str, Any]):
    disconnected: List[WebSocket] = []
    for connection in list(active_connections):
        try:
            await connection.send_json(message)
        except Exception as e:
            logger.error(f"Erreur broadcast: {str(e)}")
            disconnected.append(connection)
    for connection in disconnected:
        try:
            active_connections.remove(connection)
        except Exception:
            pass


def _resolve_agent_type(agent_name: str) -> AgentType:
    normalized = agent_name.strip().lower()
    name_map = {
        "browser": AgentType.BROWSER,
        "vision": AgentType.VISION,
        "voice": AgentType.VOICE,
        "security": AgentType.SECURITY,
        "research": AgentType.RESEARCH,
        "development": AgentType.DEVELOPMENT,
        "monitoring": AgentType.MONITORING,
        "logic": AgentType.RESEARCH,
        "creativity": AgentType.DEVELOPMENT,
        "optimization": AgentType.MONITORING,
    }
    if normalized not in name_map:
        raise HTTPException(status_code=400, detail=f"Unknown agent '{agent_name}'")
    return name_map[normalized]


async def _dispatch_agent(agent_name: str, instruction: str, user_id: str) -> Dict[str, Any]:
    agent_type = _resolve_agent_type(agent_name)
    if not multi_agent:
        raise HTTPException(status_code=500, detail="Multi-agent system unavailable")
    response = await multi_agent.dispatch_task(agent_type, instruction, {"action": "auto", "user_id": user_id})
    return asdict(response)


@app.post("/api/command")
async def run_terminal_command(request: CommandRequest):
    outcome = await dispatch_terminal_command(request.command)
    return {
        "command": request.command,
        "success": outcome.get("success", False),
        "message": outcome.get("message", ""),
        "data": outcome.get("data"),
        "timestamp": datetime.now().isoformat(),
    }


@app.post("/api/execute")
async def execute_instruction(request: ExecuteRequest):
    try:
        logger.info(f"📥 Instruction: {request.instruction}")
        if not engine:
            raise HTTPException(status_code=503, detail="Engine unavailable")
        result = await engine.process_instruction(request.instruction)
        payload = {
            "status": "success",
            "execution_id": str(abs(hash(json.dumps(result, default=str)))) if result else None,
            "timestamp": datetime.now().isoformat(),
            "data": result
        }
        if request.metadata:
            payload["metadata"] = request.metadata
        await broadcast_update({
            "type": "execution_complete",
            "user_id": request.user_id,
            "result": payload
        })
        return payload
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erreur execution: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/cognitive")
async def cognitive_cycle(request: CognitiveRequest):
    try:
        logger.info(f"🧠 Cycle cognitif: {request.instruction}")
        if engine and hasattr(engine, "cognitive_network"):
            cognitive_result = await engine.cognitive_network.process_with_emergence(request.instruction)
        else:
            cognitive_result = {
                "status": "unavailable",
                "message": "Cognitive network is not configured in the current engine"
            }
        return {
            "status": "success",
            "instruction": request.instruction,
            "cognitive_analysis": cognitive_result,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"❌ Erreur cognitive: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/agents/coordinate")
async def coordinate_agents(request: AgentCoordinationRequest):
    try:
        logger.info(f"🤝 Coordination agents: {request.agents}")
        if not multi_agent:
            raise HTTPException(status_code=503, detail="Multi-agent system unavailable")

        agent_results: Dict[str, Any] = {}
        for agent_name in request.agents:
            try:
                agent_results[agent_name] = await _dispatch_agent(agent_name, request.instruction, request.user_id)
            except HTTPException as exc:
                agent_results[agent_name] = {"error": exc.detail}

        synthesis = await multi_agent.coordinate_agents(request.instruction) if hasattr(multi_agent, "coordinate_agents") else {}
        await broadcast_update({
            "type": "agent_coordination_complete",
            "user_id": request.user_id,
            "agents": request.agents,
            "synthesis": synthesis
        })
        return {
            "status": "success",
            "instruction": request.instruction,
            "agents_involved": request.agents,
            "individual_results": agent_results,
            "synthesis": synthesis,
            "timestamp": datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erreur coordination: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/vision/ocr")
async def ocr_vision(file: UploadFile = File(...)):
    try:
        if not vision_engine:
            raise HTTPException(status_code=503, detail="Vision engine unavailable")
        contents = await file.read()
        result = await vision_engine.ocr(contents)
        return {
            "status": "success",
            "ocr_result": result,
            "timestamp": datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erreur vision: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/vision/analyze")
async def analyze_vision(file: UploadFile = File(...)):
    try:
        if not vision_engine:
            raise HTTPException(status_code=503, detail="Vision engine unavailable")
        contents = await file.read()
        result = await vision_engine.analyze(contents)
        return {
            "status": "success",
            "analysis": result,
            "timestamp": datetime.now().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Erreur analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/status")
async def get_status():
    return {
        "engine": {
            "interactive": engine.interactive if engine else False,
            "memory_size": len(engine.memory.history) if engine and hasattr(engine, "memory") else 0
        },
        "agents": multi_agent.get_agent_status() if multi_agent else {},
        "analytics": analytics.get_summary() if analytics else {},
        "timestamp": datetime.now().isoformat()
    }


@app.on_event("startup")
async def startup_eye_tracking():
    try:
        result = await get_eye_tracking().initialize()
        logger.info(f"Eye tracking: {result}")
    except Exception as e:
        logger.warning(f"Eye tracking init failed: {str(e)}")


@app.get("/api/eye/status")
async def get_eye_status():
    return await get_eye_tracking().get_gaze_position()


@app.post("/api/eye/calibrate")
async def calibrate_eye():
    return await get_eye_tracking().calibrate()


@app.websocket("/ws/eye/{user_id}")
async def eye_tracking_stream(websocket: WebSocket, user_id: str):
    await websocket.accept()
    while True:
        try:
            position = await get_eye_tracking().get_gaze_position()
            await websocket.send_json(position)
            await asyncio.sleep(0.05)
        except Exception:
            break


@app.get("/api/cognitive/snapshot")
async def get_cognitive_snapshot():
    liquid = get_liquid_os()
    await liquid.detect_cognitive_state({})
    snapshot = await liquid.get_activity_snapshot()
    return {**snapshot, "timestamp": datetime.now().isoformat()}


@app.websocket("/ws/ambient/{user_id}")
async def ambient_websocket(websocket: WebSocket, user_id: str):
    await websocket.accept()
    while True:
        try:
            liquid = get_liquid_os()
            snapshot = await liquid.get_activity_snapshot()
            await liquid.detect_cognitive_state(snapshot)
            update = {
                "type": "ambient_update",
                "cognitive_state": snapshot.get("cognitive_state"),
                "foreground_app": snapshot.get("foreground_app"),
                "detected_apps": snapshot.get("detected_apps", []),
                "confidence": snapshot.get("confidence", 0),
                "active_workflows": len(get_shadow_mode().workflow_candidates) if hasattr(get_shadow_mode(), 'workflow_candidates') else 0,
                "memory_size": len(get_semantic_rewind().episodic_memory) if hasattr(get_semantic_rewind(), 'episodic_memory') else 0,
                "nexus_files": len(get_black_hole().ingested_files) if hasattr(get_black_hole(), 'ingested_files') else 0,
            }
            await websocket.send_json(update)
            await asyncio.sleep(5)
        except Exception:
            break


@app.get("/api/agents/status")
async def get_agents_status():
    return {
        "agents": multi_agent.get_agent_status() if multi_agent else {},
        "active_tasks": multi_agent.active_tasks if multi_agent else {},
        "completed_tasks": [asdict(t) for t in multi_agent.completed_tasks] if multi_agent else [],
        "timestamp": datetime.now().isoformat()
    }


@app.get("/api/agents/ui")
async def get_ui_agents():
    from .ui_agents import build_ui_agents_snapshot
    agents = await build_ui_agents_snapshot()
    return {"agents": agents, "timestamp": datetime.now().isoformat()}


@app.post("/api/agents/toggle")
async def toggle_ui_agent_route(request: AgentToggleRequest):
    from .ui_agents import toggle_ui_agent
    result = await toggle_ui_agent(request.agent_id, request.active)
    if result.get("success") and result.get("agents"):
        for agent in result["agents"]:
            await broadcast_update({
                "type": "agent_update",
                "agent_id": agent["id"],
                "active": agent["active"],
                "stat": agent["stat"],
                "score": agent["score"],
            })
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("message", "Échec du basculement"))
    return {**result, "timestamp": datetime.now().isoformat()}


@app.get("/api/analytics/dashboard")
async def get_analytics_dashboard():
    return {
        "overview": analytics.get_overview() if analytics else {},
        "performance": analytics.get_performance_metrics() if analytics else {},
        "trends": analytics.get_trends() if analytics else {},
        "predictions": analytics.get_predictions() if analytics else {},
        "timestamp": datetime.now().isoformat()
    }


@app.get("/api/history")
async def get_history(limit: int = 10, user_id: str = "default"):
    history = []
    total = 0
    if engine and hasattr(engine, "memory"):
        history = engine.memory.get_history()
        total = len(history)
    return {
        "history": history[:limit],
        "total": total,
        "user_id": user_id
    }


@app.get("/api/memory")
async def get_memory():
    memory_data = {}
    if engine and hasattr(engine, "memory"):
        memory_data = {
            "entries": engine.memory.get_history(),
            "size": len(engine.memory.get_history())
        }
    return {
        "memory": memory_data,
        "timestamp": datetime.now().isoformat()
    }


async def _ws_send_execution_result(
    websocket: WebSocket,
    command: str,
    outcome: Dict[str, Any],
    request_id: Optional[str] = None,
) -> None:
    try:
        await websocket.send_json({
            "type": "execution_result",
            "command": command,
            "request_id": request_id,
            "success": outcome.get("success", False),
            "message": outcome.get("message", ""),
            "data": outcome.get("data"),
        })
    except Exception as exc:
        logger.debug("Impossible d'envoyer execution_result: %s", exc)


async def _ws_handle_run_command(websocket: WebSocket, command: str, request_id: Optional[str]) -> None:
    outcome = await dispatch_terminal_command(command)
    await _ws_send_execution_result(websocket, command, outcome, request_id)


@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    await websocket.accept()
    active_connections.append(websocket)
    logger.info(f"🔌 WebSocket connecté: {user_id}")

    await websocket.send_json({
        "type": "connection_established",
        "user_id": user_id,
        "timestamp": datetime.now().isoformat()
    })

    try:
        while True:
            data = await websocket.receive_json()
            message_type = data.get("type")
            if message_type == "run_command":
                command = data.get("command", "")
                request_id = data.get("request_id")
                asyncio.create_task(_ws_handle_run_command(websocket, command, request_id))
            elif message_type == "execute":
                instruction = data.get("instruction", "")
                request_id = data.get("request_id")
                asyncio.create_task(_ws_handle_run_command(websocket, instruction, request_id))
            elif message_type == "cognitive":
                if engine and hasattr(engine, "cognitive_network"):
                    cognitive_result = await engine.cognitive_network.process_with_emergence(data.get("instruction"))
                else:
                    cognitive_result = {"status": "unavailable"}
                await websocket.send_json({"type": "cognitive_result", "data": cognitive_result})
            elif message_type == "agent_coordinate":
                agent_results = {}
                for agent_name in data.get("agents", []):
                    agent_results[agent_name] = await _dispatch_agent(agent_name, data.get("instruction"), user_id)
                await websocket.send_json({"type": "agent_coordination_result", "data": agent_results})
            elif message_type == "ping":
                await websocket.send_json({"type": "pong", "timestamp": datetime.now().isoformat()})
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
    finally:
        if websocket in active_connections:
            active_connections.remove(websocket)
        logger.info(f"🔌 WebSocket fermé: {user_id}")


@app.get("/")
async def root():
    return HTMLResponse(get_dashboard_html())


def get_dashboard_html():
    return """
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>MOT-X v2 Dashboard</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); color: #e2e8f0; min-height: 100vh; }
            .container { max-width: 1200px; margin: 20px auto; padding: 20px; }
            header { background: rgba(15, 23, 42, 0.85); border-radius: 12px; padding: 20px; margin-bottom: 20px; border: 1px solid rgba(148, 163, 184, 0.2); }
            h1 { color: #f8fafc; font-size: 2em; margin-bottom: 10px; }
            p { color: #94a3b8; }
            .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 20px; }
            .card { background: rgba(15, 23, 42, 0.75); border-radius: 14px; padding: 18px; border: 1px solid rgba(148, 163, 184, 0.12); }
            .card h2 { color: #f8fafc; margin-bottom: 12px; }
            input, button { width: 100%; padding: 12px 14px; margin-top: 10px; border-radius: 10px; border: 1px solid rgba(148, 163, 184, 0.2); background: rgba(15, 23, 42, 0.55); color: #e2e8f0; }
            button { background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%); border: none; cursor: pointer; font-weight: 700; }
            button:hover { opacity: 0.95; }
            pre { background: rgba(15, 23, 42, 0.9); border-radius: 10px; padding: 14px; overflow-x: auto; color: #e2e8f0; }
        </style>
    </head>
    <body>
        <div class="container">
            <header>
                <h1>🤖 MOT-X v2 Dashboard</h1>
                <p>FastAPI + WebSocket + Multi-Agent orchestration</p>
            </header>
            <div class="grid">
                <div class="card">
                    <h2>⚡ Quick Execute</h2>
                    <input id="instruction" type="text" placeholder="Enter an instruction" />
                    <button onclick="executeInstruction()">Execute</button>
                    <pre id="result-execute"></pre>
                </div>
                <div class="card">
                    <h2>🧠 Cognitive Cycle</h2>
                    <input id="cognitive-instruction" type="text" placeholder="Enter cognitive instruction" />
                    <button onclick="cognitiveCycle()">Analyze</button>
                    <pre id="result-cognitive"></pre>
                </div>
                <div class="card">
                    <h2>📊 System Status</h2>
                    <button onclick="fetchStatus()">Refresh Status</button>
                    <pre id="status-content"></pre>
                </div>
                <div class="card">
                    <h2>🤝 Agent Coordination</h2>
                    <button onclick="coordinateAgents()">Load Agent Status</button>
                    <pre id="agents-content"></pre>
                </div>
            </div>
        </div>
        <script>
            const API_URL = window.location.origin;
            async function executeInstruction() {
                const instruction = document.getElementById('instruction').value;
                if (!instruction) return alert('Enter instruction');
                const res = await fetch(`${API_URL}/api/execute`, {
                    method: 'POST', headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({instruction, user_id: 'web-user'})
                });
                document.getElementById('result-execute').textContent = JSON.stringify(await res.json(), null, 2);
            }
            async function cognitiveCycle() {
                const instruction = document.getElementById('cognitive-instruction').value;
                if (!instruction) return alert('Enter instruction');
                const res = await fetch(`${API_URL}/api/cognitive`, {
                    method: 'POST', headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({instruction, user_id: 'web-user'})
                });
                document.getElementById('result-cognitive').textContent = JSON.stringify(await res.json(), null, 2);
            }
            async function fetchStatus() {
                const res = await fetch(`${API_URL}/api/status`);
                document.getElementById('status-content').textContent = JSON.stringify(await res.json(), null, 2);
            }
            async function coordinateAgents() {
                const res = await fetch(`${API_URL}/api/agents/status`);
                document.getElementById('agents-content').textContent = JSON.stringify(await res.json(), null, 2);
            }
            setInterval(fetchStatus, 5000);
        </script>
    </body>
    </html>
    """


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
