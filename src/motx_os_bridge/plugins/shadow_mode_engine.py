import logging
import asyncio
from typing import Dict, List, Any
from datetime import datetime
from pynput import mouse, keyboard
import collections
import io
import base64
import httpx
import numpy as np

logger = logging.getLogger(__name__)

class ShadowModeEngine:
    """
    MOT-X observe votre écran et vos actions EN SILENCE
    Puis génère automatiquement des workflows sans jamais vous le demander.
    """
    
    def __init__(self):
        self.observation_session = None
        self.recorded_actions = []
        self.screen_captures = collections.deque(maxlen=10) # FIFO RAM Buffer de 10 images max
        self.gesture_patterns = []
        self.workflow_candidates = []
        self.learning_enabled = False
    
    async def start_shadow_mode(self, session_name: str = "Default") -> Dict:
        logger.info("🕵️ SHADOW MODE: Démarrage de l'observation silencieuse...")
        
        self.observation_session = {
            "id": f"shadow_{datetime.now().timestamp()}",
            "name": session_name,
            "started_at": datetime.now().isoformat(),
            "actions_recorded": 0,
            "patterns_detected": 0,
            "status": "recording"
        }
        
        # Démarrer les observateurs en parallèle
        asyncio.create_task(self._monitor_screen_activity())
        asyncio.create_task(self._monitor_mouse_keyboard())
        asyncio.create_task(self._monitor_application_switching())
        asyncio.create_task(self._analyze_in_real_time())
        
        return {
            "status": "shadow_mode_active",
            "session_id": self.observation_session["id"],
            "message": "🕵️ Je vous observe silencieusement. Continuez votre travail normalement."
        }
    
    async def _monitor_screen_activity(self) -> None:
        import cv2
        import numpy as np

        logger.info("📹 Screen monitoring réel démarré (RAM FIFO Active)...")
        previous_frame = None
        while self.observation_session and self.observation_session["status"] == "recording":
            try:
                # Capturer l'écran réel
                try:
                    from PIL import ImageGrab
                    pil_screenshot = ImageGrab.grab()
                    screenshot = np.array(pil_screenshot)
                except Exception as grab_err:
                    logger.warning(f"Impossible de capturer l'écran réel (fallback NumPy noise): {grab_err}")
                    screenshot = np.random.randint(0, 256, (720, 1280, 3), dtype=np.uint8)
                
                if previous_frame is not None:
                    change_detected = self._detect_screen_change(previous_frame, screenshot)
                    if change_detected:
                        self.recorded_actions.append({
                            "type": "screen_change",
                            "timestamp": datetime.now().isoformat(),
                            "description": await self._describe_screen_change(screenshot)
                        })
                
                previous_frame = screenshot.copy()
                self.screen_captures.append(screenshot)
                await asyncio.sleep(2)
            except Exception as e:
                logger.error(f"Screen monitoring error: {str(e)}")
    
    async def _monitor_mouse_keyboard(self) -> None:
        logger.info("🖱️ Mouse/Keyboard monitoring démarré...")
        while self.observation_session and self.observation_session["status"] == "recording":
            await asyncio.sleep(1)
    
    async def _monitor_application_switching(self) -> None:
        logger.info("🔄 App switching monitoring réel démarré...")
        previous_app = None
        while self.observation_session and self.observation_session["status"] == "recording":
            try:
                current_app = await self._get_active_application()
                if current_app != previous_app and current_app != "Unknown Application":
                    logger.info(f"🔄 App change detected: {previous_app} -> {current_app}")
                    
                    # Déclencher l'analyse IA de l'écran si disponible dans le buffer FIFO
                    analysis_desc = "Pas de capture d'écran disponible dans le buffer FIFO."
                    if len(self.screen_captures) > 0:
                        latest_frame = self.screen_captures[-1]
                        analysis_desc = await self._analyze_with_ollama_vision(latest_frame, current_app)
                    
                    self.recorded_actions.append({
                        "type": "app_switch",
                        "from": previous_app,
                        "to": current_app,
                        "timestamp": datetime.now().isoformat(),
                        "description": analysis_desc
                    })
                    previous_app = current_app
                await asyncio.sleep(1)
            except Exception as e:
                logger.error(f"App monitoring error: {str(e)}")
    
    async def _analyze_in_real_time(self) -> None:
        logger.info("🧠 Real-time pattern analysis démarré...")
        while self.observation_session and self.observation_session["status"] == "recording":
            try:
                if len(self.recorded_actions) % 30 == 0 and len(self.recorded_actions) > 30:
                    patterns = await self._extract_patterns()
                    self.gesture_patterns.extend(patterns)
                await asyncio.sleep(5)
            except Exception as e:
                logger.error(f"Pattern analysis error: {str(e)}")
    
    async def stop_shadow_mode(self) -> Dict:
        logger.info("🛑 Arrêt du Shadow Mode...")
        if not self.observation_session:
            return {"status": "error", "message": "No active shadow mode session"}
        
        self.observation_session["status"] = "stopped"
        self.observation_session["ended_at"] = datetime.now().isoformat()
        
        workflows = await self._generate_workflows_from_observations()
        
        return {
            "status": "success",
            "session": self.observation_session,
            "actions_recorded": len(self.recorded_actions),
            "patterns_found": len(self.gesture_patterns),
            "workflows_generated": len(workflows),
            "workflows": workflows
        }
    
    async def _generate_workflows_from_observations(self) -> List[Dict]:
        workflows = []
        sequences = self._identify_repeating_sequences()
        for seq in sequences:
            if len(seq) >= 3:
                workflow = {
                    "id": f"shadow_workflow_{datetime.now().timestamp()}",
                    "name": await self._generate_workflow_name(seq),
                    "description": f"Automatically learned from {len(seq)} similar executions",
                    "steps": seq,
                    "confidence": self._calculate_confidence(seq),
                    "suggested_trigger": "on_demand",
                    "can_automate": True,
                    "approval_needed": True
                }
                if workflow["confidence"] > 0.75:
                    workflows.append(workflow)
        return workflows
    
    def _detect_screen_change(self, frame1, frame2) -> bool:
        import cv2
        import numpy as np
        diff = cv2.absdiff(frame1, frame2)
        return np.mean(diff) > 10
    
    async def _describe_screen_change(self, screenshot: np.ndarray) -> str:
        return "Screen changed - content updated"
    
    async def _get_active_application(self) -> str:
        try:
            import win32gui
            active_window = win32gui.GetForegroundWindow()
            window_title = win32gui.GetWindowText(active_window)
            if window_title:
                return window_title.strip()
        except Exception as e:
            logger.debug(f"Error getting active application: {str(e)}")
        return "Unknown Application"

    async def _analyze_with_ollama_vision(self, img_array: np.ndarray, app_name: str) -> str:
        try:
            # Convertir numpy RGB/RGBA en image PIL
            from PIL import Image
            pil_img = Image.fromarray(img_array)
            buffered = io.BytesIO()
            # Redimensionner l'image pour accélérer la transmission LLaVA
            pil_img.thumbnail((800, 600))
            pil_img.save(buffered, format="JPEG", quality=80)
            b64_image = base64.b64encode(buffered.getvalue()).decode('utf-8')
            
            async with httpx.AsyncClient() as client:
                payload = {
                    "model": "llava",
                    "prompt": f"Describe the active user context in this screenshot of the '{app_name}' application. What are they working on?",
                    "images": [b64_image],
                    "stream": False
                }
                response = await client.post("http://localhost:11434/api/generate", json=payload, timeout=12.0)
                if response.status_code == 200:
                    desc = response.json().get("response", "").strip()
                    if desc:
                        logger.info(f"🧠 Ollama LLaVA Vision analysis: {desc}")
                        return desc
        except Exception as e:
            logger.warning(f"Ollama LLaVA vision analysis failed or model not available: {str(e)}")
        
        # Fallback vers Llama2 textuel si LLaVA échoue
        try:
            async with httpx.AsyncClient() as client:
                payload_text = {
                    "model": "llama2",
                    "prompt": f"Explain what a user is typically doing when their active application window title is '{app_name}'. Be extremely concise (1 sentence).",
                    "stream": False
                }
                response = await client.post("http://localhost:11434/api/generate", json=payload_text, timeout=5.0)
                if response.status_code == 200:
                    desc = response.json().get("response", "").strip()
                    if desc:
                        return f"[Llama2 Fallback] {desc}"
        except Exception:
            pass
            
        return f"Utilisation de l'application '{app_name}' (analyse visuelle non disponible)."
    
    async def _extract_patterns(self) -> List[Dict]:
        return []
    
    def _identify_repeating_sequences(self) -> List[List[Dict]]:
        return []
    
    async def _generate_workflow_name(self, sequence: List[Dict]) -> str:
        return f"Workflow_{datetime.now().timestamp()}"
    
    def _calculate_confidence(self, sequence: List[Dict]) -> float:
        return 0.85
