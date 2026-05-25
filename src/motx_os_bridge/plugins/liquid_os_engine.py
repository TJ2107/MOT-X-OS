import logging
import asyncio
from typing import Dict, List, Any
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)

class CognitiveState(Enum):
    FOCUS = "focus"
    CREATIVE = "creative"
    SOCIAL = "social"
    LEARNING = "learning"
    RELAXATION = "relaxation"
    ANALYSIS = "analysis"
    WRITING = "writing"
    CODING = "coding"
    MEETING = "meeting"

class LiquidOSEngine:
    """
    L'OS se transforme physiquement selon l'état cognitif
    """
    
    def __init__(self):
        self.current_state = CognitiveState.FOCUS
        self.environment_config = {}
        self.active_transformations = []
        self.last_snapshot: Dict = {}
    
    async def detect_cognitive_state(self, user_activity: Dict | None = None) -> CognitiveState:
        from .activity_detector import collect_activity_snapshot, infer_cognitive_state_id

        snapshot = collect_activity_snapshot()
        if user_activity:
            snapshot.update({k: v for k, v in user_activity.items() if v is not None})

        state_key = snapshot.get("cognitive_state_backend") or snapshot.get("cognitive_state", "focus")
        if isinstance(state_key, str) and state_key.isupper():
            state_key = state_key.lower()

        try:
            detected_state = CognitiveState(state_key)
        except ValueError:
            fg = snapshot.get("foreground_process")
            ui_id, _ = infer_cognitive_state_id(fg)
            mapping = {
                "CODING": CognitiveState.CODING,
                "CREATIVE": CognitiveState.CREATIVE,
                "MEETING": CognitiveState.MEETING,
                "RELAXATION": CognitiveState.RELAXATION,
                "FOCUS": CognitiveState.FOCUS,
            }
            detected_state = mapping.get(ui_id, CognitiveState.FOCUS)

        self.last_snapshot = snapshot
        if detected_state != self.current_state:
            logger.info(f"🧠 Cognitive state change: {self.current_state.value} → {detected_state.value}")
            await self.transform_environment(detected_state)
            self.current_state = detected_state
        return detected_state

    async def get_activity_snapshot(self) -> Dict:
        from .activity_detector import collect_activity_snapshot

        snapshot = collect_activity_snapshot()
        self.last_snapshot = snapshot
        return snapshot
    
    async def transform_environment(self, target_state: CognitiveState) -> Dict:
        logger.info(f"🌀 Transforming environment for {target_state.value}...")
        
        transformations = {
            CognitiveState.CODING: {
                "color_scheme": "Dark Pro",
                "message": "💻 Mode Coding activé. Distractions minimisées."
            },
            CognitiveState.CREATIVE: {
                "color_scheme": "Vibrant",
                "message": "🎨 Mode Créatif activé. Flexibilité maximale."
            },
            CognitiveState.FOCUS: {
                "color_scheme": "Monochrome Focus",
                "message": "🎯 Mode Focus activé. AUCUNE distraction."
            }
        }
        
        config = transformations.get(target_state, {"color_scheme": "Default", "message": "Mode Standard"})
        
        await self._apply_visual_changes(config)
        self.environment_config = config
        self.active_transformations.append({
            "state": target_state.value,
            "timestamp": datetime.now().isoformat(),
            "config": config
        })
        
        return {
            "status": "transformed",
            "state": target_state.value,
            "message": config.get("message")
        }
    
    async def smooth_transition(self, from_state: CognitiveState, to_state: CognitiveState) -> None:
        logger.info(f"🌊 Smooth transition: {from_state.value} → {to_state.value}")
        await asyncio.sleep(0.5)
        await self.transform_environment(to_state)
        await asyncio.sleep(0.5)
    
    async def _apply_visual_changes(self, config: Dict) -> None:
        logger.info(f"🎨 Applying visual changes: {config.get('color_scheme')}")
    
    async def _match_activity_to_state(self, activity: Dict) -> CognitiveState:
        return await self.detect_cognitive_state(activity)
