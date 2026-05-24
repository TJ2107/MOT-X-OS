"""
Enhanced Engine - MOT-X avec toutes les innovations intégrées.
"""

import asyncio
import json
import logging
import time
from typing import Dict, Any

logger = logging.getLogger(__name__)


class EnhancedMOTXEngine:
    """
    MOT-X avec toutes les innovations intégrées
    """
    
    def __init__(self, base_engine):
        self.base_engine = base_engine
        
        # Importer les nouveaux systèmes
        from .cognitive_emergence import CognitiveNetwork
        from .immersive_interface import ImmersiveInterface, WebSocketVisualization
        from .gamification_engine import GamificationEngine
        from .predictive_intelligence import PredictiveIntelligence
        from .multi_user_collaboration import CollaborationEngine
        from .narrative_engine import NarrativeEngine
        from .advanced_analytics import AdvancedAnalytics
        
        # Initialiser les systèmes
        self.cognitive_network = CognitiveNetwork()
        self.immersive_ui = ImmersiveInterface()
        self.gamification = GamificationEngine()
        self.predictive_ai = PredictiveIntelligence()
        self.collaboration = CollaborationEngine()
        self.narrative = NarrativeEngine()
        self.analytics = AdvancedAnalytics()
        self.ws_viz = WebSocketVisualization()
        
        self.execution_history = []
        
        logger.info("🚀 MOT-X Enhanced Edition initialisé")
    
    async def execute_enhanced(self, instruction: str, user_id: str = "default") -> Dict[str, Any]:
        """Exécution améliorée avec tous les systèmes"""
        
        logger.info(f"🎯 Exécution enhanced: {instruction}")
        
        # 1. Exécution standard via le moteur de base
        try:
            try:
                result = await self.base_engine.process_instruction(instruction, user_id)
            except TypeError:
                result = await self.base_engine.process_instruction(instruction)
        except Exception as e:
            result = {
                "status": "error",
                "error": str(e),
                "instruction": instruction
            }

        result = self._normalize_execution_result(result, instruction)
        
        # Enregistrer dans l'historique
        execution_record = {
            "instruction": instruction,
            "results": result.get("results", []),
            "status": result.get("status"),
            "timestamp": time.time()
        }
        self.execution_history.append(execution_record)
        
        # 2. Analyse cognitive émergente
        cognitive_analysis = await self.cognitive_network.process_with_emergence(instruction)
        
        # 3. Ajouter contexte narratif
        narrative = self.narrative.generate_narrative_context(result)
        
        # 4. Ajouter XP et achievements
        xp_reward = self.gamification.add_experience(
            50 if result.get("status") == "success" else 20,
            "automation"
        )
        
        # 5. Prédictions
        predictions = self.predictive_ai.analyze_user_behavior(self.execution_history)
        
        # 6. Visualisations
        cognitive_viz = self.immersive_ui.render_cognitive_network(cognitive_analysis.get("individual_analyses", {}))
        execution_viz = self.immersive_ui.render_real_time_execution({"tasks": result.get("results", [])})
        
        # 7. Analytiques
        dashboard = self.analytics.generate_comprehensive_dashboard(self.execution_history)
        
        # Retour complet
        return {
            "execution_result": result,
            "cognitive_analysis": cognitive_analysis,
            "narrative_context": narrative,
            "gamification": {
                "xp_earned": xp_reward["xp_gained"],
                "new_level": xp_reward["level_up"],
                "achievements": xp_reward["achievements_unlocked"]
            },
            "predictions": predictions,
            "visualizations": {
                "cognitive_network": cognitive_viz,
                "execution_flow": execution_viz
            },
            "analytics_dashboard": dashboard,
            "player_profile": self.gamification.get_player_profile()
        }

    def _normalize_execution_result(self, result: Any, instruction: str) -> Dict[str, Any]:
        if isinstance(result, list):
            return {
                "results": result,
                "status": "success" if result else "error",
                "instruction": instruction
            }

        if isinstance(result, dict):
            normalized = dict(result)
            if "results" not in normalized:
                normalized["results"] = [normalized.copy()]
            if "status" not in normalized:
                normalized["status"] = "success"
            return normalized

        return {
            "results": [],
            "status": "error",
            "instruction": instruction
        }
    
    async def get_cognitive_state(self) -> Dict[str, Any]:
        """Retourne l'état cognitif actuel"""
        return {
            "nodes": len(self.cognitive_network.nodes),
            "collective_insights": len(self.cognitive_network.collective_insights),
            "emergence_patterns": len(self.cognitive_network.emergence_patterns)
        }
    
    async def get_gamification_state(self) -> Dict[str, Any]:
        """Retourne l'état de gamification"""
        return self.gamification.get_player_profile()
    
    async def get_predictions(self) -> Dict[str, Any]:
        """Retourne les prédictions actuelles"""
        return self.predictive_ai.analyze_user_behavior(self.execution_history)
    
    async def get_analytics(self) -> Dict[str, Any]:
        """Retourne les analytiques"""
        return self.analytics.generate_comprehensive_dashboard(self.execution_history)
    
    async def get_narrative_state(self) -> Dict[str, Any]:
        """Retourne l'état narratif"""
        return {
            "current_arc": getattr(getattr(self.narrative, "current_arc", None), "value", "unknown"),
            "story_events": len(getattr(self.narrative, "story_events", []))
        }
    
    async def get_full_dashboard(self) -> Dict[str, Any]:
        """Dashboard complet de tous les systèmes"""
        return {
            "cognitive": await self.get_cognitive_state(),
            "gamification": await self.get_gamification_state(),
            "predictions": await self.get_predictions(),
            "analytics": await self.get_analytics(),
            "narrative": await self.get_narrative_state(),
            "execution_history_count": len(self.execution_history)
        }
