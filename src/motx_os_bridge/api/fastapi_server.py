import logging
import asyncio
from datetime import datetime
import requests
from fastapi import FastAPI, WebSocket, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from motx_os_bridge.utils.config_loader import load_settings

logger = logging.getLogger(__name__)

from starlette.websockets import WebSocketDisconnect

from motx_os_bridge.core.engine import MOTXAutomationEngine
from motx_os_bridge.core.cognitive_layer import CognitiveOperatingLayer
from motx_os_bridge.core.multi_agent_system import MultiAgentSystem

app = FastAPI(title="MOT-X Ambient Intelligence")

shadow_mode = None
look_and_do = None
semantic_rewind = None
liquid_os = None
black_hole = None
eye_tracking = None
voice_engine = None


def get_shadow_mode():
    global shadow_mode
    if shadow_mode is None:
        from motx_os_bridge.plugins.shadow_mode_engine import ShadowModeEngine
        shadow_mode = ShadowModeEngine()
    return shadow_mode


def get_look_and_do():
    global look_and_do
    if look_and_do is None:
        from motx_os_bridge.plugins.look_and_do_engine import LookAndDoEngine
        look_and_do = LookAndDoEngine()
    return look_and_do


def get_semantic_rewind():
    global semantic_rewind
    if semantic_rewind is None:
        from motx_os_bridge.plugins.semantic_rewind_engine import SemanticRewindEngine
        semantic_rewind = SemanticRewindEngine()
    return semantic_rewind


def get_liquid_os():
    global liquid_os
    if liquid_os is None:
        from motx_os_bridge.plugins.liquid_os_engine import LiquidOSEngine
        liquid_os = LiquidOSEngine()
    return liquid_os


def get_black_hole():
    global black_hole
    if black_hole is None:
        from motx_os_bridge.plugins.black_hole_folder import BlackHoleFolder
        black_hole = BlackHoleFolder()
    return black_hole


def get_eye_tracking():
    global eye_tracking
    if eye_tracking is None:
        from motx_os_bridge.plugins.eye_tracking_integrated import IntegratedEyeTracking
        eye_tracking = IntegratedEyeTracking()
    return eye_tracking


def get_voice_engine():
    global voice_engine
    if voice_engine is None:
        from motx_os_bridge.plugins.voice_engine_enhanced import EnhancedVoiceEngine
        voice_engine = EnhancedVoiceEngine()
    return voice_engine


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

_engine = None
_cognitive_layer = None
_multi_agent = None

# Active websockets for generic broadcasts (set of WebSocket)
active_websockets = set()

def get_engine():
    global _engine
    if _engine is None:
        _engine = MOTXAutomationEngine(interactive=False)
    return _engine

def get_cognitive_layer():
    global _cognitive_layer
    if _cognitive_layer is None:
        _cognitive_layer = CognitiveOperatingLayer()
    return _cognitive_layer

def get_multi_agent():
    global _multi_agent
    if _multi_agent is None:
        _multi_agent = MultiAgentSystem()
    return _multi_agent


def _is_chroma_available(plugin) -> bool:
    return getattr(plugin, "chroma_available", False) and getattr(plugin, "collection", None) is not None


def _get_chroma_status() -> dict:
    bh = get_black_hole()
    sr = get_semantic_rewind()
    black_hole_status = {
        "service": "black_hole",
        "status": "ok" if _is_chroma_available(bh) else "error",
        "message": getattr(bh, "chroma_error", "")
    }
    rewind_status = {
        "service": "semantic_rewind",
        "status": "ok" if _is_chroma_available(sr) else "error",
        "message": getattr(sr, "chroma_error", "")
    }
    overall = "ok" if black_hole_status["status"] == "ok" or rewind_status["status"] == "ok" else "error"
    return {
        "status": overall,
        "details": [black_hole_status, rewind_status]
    }


def _get_ollama_status() -> dict:
    settings = load_settings()
    llm_settings = settings.get("llm", {}) if isinstance(settings, dict) else {}
    host = llm_settings.get("ollama_host", "localhost")
    port = llm_settings.get("ollama_port", 11434)
    model = llm_settings.get("model", "llama2")
    url = f"http://{host}:{port}/api/tags"
    try:
        response = requests.get(url, timeout=3)
        if response.status_code == 200:
            models = [m.get("name") for m in response.json().get("models", []) if isinstance(m, dict)]
            return {
                "status": "ok",
                "message": f"Ollama disponible ({host}:{port})",
                "model": model,
                "available_models": models
            }
        return {"status": "error", "message": f"Ollama HTTP {response.status_code}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


@app.on_event("startup")
async def startup_event():
    # Lancer le Black Hole Folder watcher dans la boucle asyncio de FastAPI
    asyncio.create_task(get_black_hole().watch_nexus_folder())
    # Background broadcaster for ChromaDB health pushed to connected websockets
    asyncio.create_task(_chroma_broadcaster())

@app.post("/api/shadow/start")
async def start_shadow_learning():
    return await get_shadow_mode().start_shadow_mode()

@app.post("/api/shadow/stop")
async def stop_shadow_learning():
    return await get_shadow_mode().stop_shadow_mode()

@app.post("/api/multimodal/voice")
async def handle_voice_command(data: dict):
    return await get_look_and_do()._process_multimodal_command(data.get("transcript"))

@app.get("/api/memory/search")
async def semantic_search(q: str):
    return await get_semantic_rewind().semantic_search(q)

@app.get("/api/memory/recover/{episode_id}")
async def recover_memory(episode_id: str):
    return await get_semantic_rewind().recover_episode(episode_id)

@app.post("/api/cognitive/state")
async def detect_state(activity: dict):
    state = await get_liquid_os().detect_cognitive_state(activity)
    return {"current_state": state.value}

@app.post("/api/nexus/upload")
async def upload_to_nexus(file: UploadFile):
    # Enregistrer temporairement puis passer le chemin
    # Note: dans une v2 on utiliserait File/Bytes
    contents = await file.read()
    import os, tempfile
    fd, temp_path = tempfile.mkstemp()
    with os.fdopen(fd, 'wb') as f:
        f.write(contents)
        
    result = await get_black_hole().ingest_file(temp_path, file.filename)
    os.remove(temp_path)
    return result

@app.get("/api/nexus/search")
async def search_nexus(q: str):
    return await get_black_hole().semantic_search_files(q)

@app.post("/api/nexus/recover/{file_id}")
async def recover_file(file_id: str):
    return await get_black_hole().retrieve_file(file_id)

@app.get("/api/nexus/rejected")
async def get_rejected_files():
    return get_black_hole().rejected_files

@app.websocket("/ws/{client_id}")
async def generic_websocket(websocket: WebSocket, client_id: str):
    # Generic websocket endpoint used for broadcasts from the server
    await websocket.accept()
    active_websockets.add(websocket)
    try:
        while True:
            try:
                # Wait for client messages to keep connection alive; ignore content
                _ = await websocket.receive_text()
            except WebSocketDisconnect:
                break
            except Exception:
                # small sleep to avoid tight loop on unexpected receive errors
                await asyncio.sleep(0.1)
    finally:
        try:
            active_websockets.discard(websocket)
        except Exception:
            pass

@app.websocket("/ws/ambient/{user_id}")
async def ambient_websocket(websocket: WebSocket, user_id: str):
    await websocket.accept()
    while True:
        try:
            update = {
                "type": "ambient_update",
                "cognitive_state": get_liquid_os().current_state.value,
                "active_workflows": len(get_shadow_mode().workflow_candidates),
                "memory_size": len(get_semantic_rewind().episodic_memory),
                "nexus_files": len(get_black_hole().ingested_files)
            }
            await websocket.send_json(update)
            await asyncio.sleep(5)
        except Exception:
            break


async def _chroma_broadcaster():
    # Periodically broadcast ChromaDB health to all connected generic websockets
    await asyncio.sleep(1)
    while True:
        try:
            status = _get_chroma_status()
            to_remove = []
            for ws in list(active_websockets):
                try:
                    await ws.send_json({"type": "chroma_status", "payload": status})
                except Exception:
                    try:
                        await ws.close()
                    except Exception:
                        pass
                    to_remove.append(ws)
            for ws in to_remove:
                active_websockets.discard(ws)
        except Exception:
            pass
        await asyncio.sleep(10)

# Routes de base
@app.get("/api/status")
@app.get("/status")
async def get_status():
    return {
        "status": "ok",
        "service": "MOT-X Ambient API (FastAPI)",
        "services": {
            "fastapi": {"status": "ok", "message": "FastAPI active"},
            "chroma": _get_chroma_status(),
            "ollama": _get_ollama_status()
        }
    }

@app.get("/api/analytics/dashboard")
async def get_analytics():
    engine = get_engine()
    multi = get_multi_agent()
    cognitive = get_cognitive_layer()

    total_executions = 0
    try:
        if hasattr(engine, "memory") and hasattr(engine.memory, "history"):
            total_executions = len(engine.memory.history)
    except Exception:
        total_executions = 0

    active_workflows = len(get_shadow_mode().workflow_candidates) if hasattr(get_shadow_mode(), 'workflow_candidates') else 0
    active_agents = len(multi.active_tasks) if multi and hasattr(multi, 'active_tasks') else 0

    return {
        "status": "ok",
        "analytics": {
            "total_executions": total_executions,
            "success_rate": 95.0,
            "average_speed_seconds": 0.85,
            "active_workflows": active_workflows,
            "active_agents": active_agents,
            "cognitive_load": getattr(cognitive, 'current_load', 0.0) if cognitive else 0.0,
            "trends": [10, 15, 8, 12, 20, 18, 25],
            "predictions": {
                "next_failure_chance": "2%",
                "suggested_optimization": "Compress log files"
            }
        }
    }


@app.get("/api/history")
async def get_history(limit: int = 10, user_id: str = "default"):
    engine = get_engine()
    history = []
    total = 0
    try:
        if hasattr(engine, "memory") and hasattr(engine.memory, "history"):
            history = engine.memory.history
            total = len(history)
    except Exception:
        history = []
        total = 0
    return {
        "history": history[:limit],
        "total": total,
        "user_id": user_id
    }

@app.post("/api/execute")
async def execute_instruction(data: dict):
    instruction = data.get("instruction")
    if not instruction:
        return {"status": "error", "message": "Instruction vide"}
    result = await get_engine().process_instruction(instruction)
    return {
        "status": "success",
        "timestamp": datetime.now().isoformat(),
        "data": result
    }

@app.post("/api/cognitive")
async def cognitive_cycle(data: dict):
    instruction = data.get("instruction")
    if not instruction:
        return {"status": "error", "message": "Instruction vide"}
    result = await get_cognitive_layer().execute_cognitive_cycle(instruction)
    return result

@app.get("/api/agents/status")
async def get_agents_status():
    multi = get_multi_agent()
    return {
        "agents": multi.get_agent_status() if multi else {},
        "active_tasks": len(multi.active_tasks) if multi else 0,
        "completed_tasks": [
            {
                "task_id": t.task_id,
                "agent_type": t.agent_type.value,
                "instruction": t.instruction,
                "status": t.status,
                "result": t.result,
                "error": t.error,
                "timestamp": t.timestamp
            } for t in multi.completed_tasks
        ] if multi else [],
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/vision/ocr")
async def ocr_vision(file: UploadFile = File(...)):
    contents = await file.read()
    return {
        "status": "success",
        "ocr_result": "Texte extrait de l'image de démonstration [Simulé]",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/demo/magic")
async def demo_magic():
    """
    Démo magique: Montre tout ce que MOT-X peut faire en 30 secondes
    """
    return {
        "demo": "MAGIC",
        "sequence": [
            "1. Vous jetez un PDF dans ~/MOT-X_Nexus",
            "2. MOT-X le fait disparaître ✨",
            "3. Vous dites: 'Retrouve-moi ce contrat'",
            "4. MOT-X: 'Voilà!' (retrouve par sémantique)",
            "5. Vous regardez le fichier",
            "6. Vous dites: 'Envoie ça à Sarah'",
            "7. MOT-X: 'Fait!' (eye-tracking + voice = zéro friction)",
            "8. Screen change: L'OS devient 'mode meeting'",
            "9. MOT-X génère un résumé automatiquement",
            "10. Vous: 'J'aurais pu faire ça? 👀'",
            "11. MOT-X: 'Vous l'avez déjà fait 3 fois cette semaine'"
        ],
        "total_time": "30 seconds",
        "friction_eliminated": "99%"
    }

# Routes d'Eye-Tracking spécifiées par l'utilisateur
@app.on_event("startup")
async def startup_eye_tracking():
    result = await get_eye_tracking().initialize()
    logger.info(f"Eye tracking: {result}")

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
        position = await get_eye_tracking().get_gaze_position()
        await websocket.send_json(position)
        await asyncio.sleep(0.05)  # 20 FPS

# Routes de reconnaissance vocale améliorée
@app.on_event("startup")
async def startup_voice_engine():
    result = await get_voice_engine().initialize()
    logger.info(f"Voice engine: {result}")

@app.get("/api/voice/status")
async def get_voice_status():
    engine = get_voice_engine()
    return {
        "is_listening": engine.is_listening,
        "last_transcript": engine.last_transcript,
        "initialized": engine.voice_model is not None or hasattr(engine, "recognizer")
    }

@app.options("/{full_path:path}")
async def options_handler(full_path: str):
    return {}
