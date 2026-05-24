"""
Proactive Symbiosis - Agent observateur qui propose des macros cognitives.
"""

import asyncio
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from pathlib import Path
from datetime import datetime, timedelta
import json
import re
from collections import defaultdict


@dataclass
class BehaviorPattern:
    """Représente un pattern de comportement détecté."""
    pattern_id: str
    pattern_type: str  # file_download, file_creation, app_usage, etc.
    frequency: int
    first_detected: str
    last_detected: str
    context: Dict[str, Any]
    suggested_macro: Optional[str] = None


@dataclass
class CognitiveMacro:
    """Représente une macro cognitive proposée."""
    macro_id: str
    name: str
    description: str
    trigger_pattern: str
    actions: List[Dict[str, Any]]
    confidence: float
    created_at: str
    user_feedback: Optional[str] = None  # approved, rejected, pending


class ProactiveSymbiosis:
    """Agent observateur proactif qui propose des macros cognitives."""
    
    def __init__(self):
        self.behavior_patterns: List[BehaviorPattern] = []
        self.cognitive_macros: List[CognitiveMacro] = []
        self.event_history: List[Dict[str, Any]] = []
        self.is_observing = False
        
        # Seuils de détection
        self.pattern_detection_threshold = 3  # Nombre d'occurrences pour détecter un pattern
        self.pattern_time_window_hours = 24  # Fenêtre temporelle pour les patterns
        self.notification_cooldown_minutes = 30
        
        # Patterns connus
        self.known_patterns = {
            "repeated_downloads": {
                "keywords": ["download", "téléchargement"],
                "file_types": [".pdf", ".doc", ".docx", ".xls", ".xlsx"],
                "suggested_macro": "auto_organize_downloads"
            },
            "repeated_file_creation": {
                "keywords": ["create", "créer", "new", "nouveau"],
                "file_types": [".txt", ".md", ".py"],
                "suggested_macro": "auto_organize_notes"
            },
            "repeated_app_launch": {
                "keywords": ["launch", "ouvrir", "open"],
                "apps": ["notepad", "chrome", "excel", "word"],
                "suggested_macro": "workspace_setup"
            }
        }
    
    async def start_observation(self, watch_directory: str = "C:/Users/*/Downloads"):
        """Démarre l'observation des événements système."""
        self.is_observing = True
        
        try:
            from watchdog.observers import Observer
            from watchdog.events import FileSystemEventHandler
            
            class MOTXEventHandler(FileSystemEventHandler):
                def __init__(self, symbiosis):
                    self.symbiosis = symbiosis
                
                def on_created(self, event):
                    if not event.is_directory:
                        asyncio.create_task(
                            self.symbiosis._record_event("file_created", str(event.src_path))
                        )
                
                def on_modified(self, event):
                    if not event.is_directory:
                        asyncio.create_task(
                            self.symbiosis._record_event("file_modified", str(event.src_path))
                        )
                
                def on_moved(self, event):
                    asyncio.create_task(
                        self.symbiosis._record_event("file_moved", {
                            "source": str(event.src_path),
                            "destination": str(event.dest_path)
                        })
                    )
            
            event_handler = MOTXEventHandler(self)
            observer = Observer()
            observer.schedule(event_handler, watch_directory, recursive=True)
            observer.start()
            
            print(f"👁️ Observation démarrée sur: {watch_directory}")
            
            # Boucle d'analyse des patterns
            while self.is_observing:
                await self._analyze_patterns()
                await asyncio.sleep(300)  # Analyser toutes les 5 minutes
            
            observer.stop()
            observer.join()
            
        except ImportError:
            print("⚠️ watchdog non installé - Observation limitée")
            await self._fallback_observation()
        except Exception as e:
            print(f"⚠️ Erreur observation: {str(e)}")
    
    async def _fallback_observation(self):
        """Mode d'observation fallback sans watchdog."""
        while self.is_observing:
            # Simulation d'observation basique
            await asyncio.sleep(600)
    
    async def _record_event(self, event_type: str, data: Any):
        """Enregistre un événement système."""
        event = {
            "type": event_type,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
        
        self.event_history.append(event)
        
        # Garder seulement les 1000 derniers événements
        if len(self.event_history) > 1000:
            self.event_history = self.event_history[-1000:]
    
    async def _analyze_patterns(self):
        """Analyse les événements pour détecter des patterns."""
        if len(self.event_history) < self.pattern_detection_threshold:
            return
        
        # Regrouper les événements par type
        events_by_type = defaultdict(list)
        for event in self.event_history:
            events_by_type[event["type"]].append(event)
        
        # Analyser chaque type d'événement
        for event_type, events in events_by_type.items():
            if len(events) >= self.pattern_detection_threshold:
                pattern = await self._detect_pattern(event_type, events)
                if pattern:
                    self.behavior_patterns.append(pattern)
                    await self._suggest_macro(pattern)
    
    async def _detect_pattern(self, event_type: str, events: List[Dict[str, Any]]) -> Optional[BehaviorPattern]:
        """Détecte un pattern dans les événements."""
        # Extraire les caractéristiques communes
        file_extensions = set()
        file_names = set()
        
        for event in events:
            if event_type == "file_created" or event_type == "file_modified":
                path = event["data"]
                ext = Path(path).suffix.lower()
                file_extensions.add(ext)
                file_names.add(Path(path).stem.lower())
        
        # Identifier le pattern
        pattern_id = f"{event_type}_{len(self.behavior_patterns)}"
        
        # Vérifier si cela correspond à un pattern connu
        for pattern_name, pattern_config in self.known_patterns.items():
            if any(ext in pattern_config.get("file_types", []) for ext in file_extensions):
                return BehaviorPattern(
                    pattern_id=pattern_id,
                    pattern_type=pattern_name,
                    frequency=len(events),
                    first_detected=events[0]["timestamp"],
                    last_detected=events[-1]["timestamp"],
                    context={
                        "file_types": list(file_extensions),
                        "file_names": list(file_names)[:5]
                    },
                    suggested_macro=pattern_config["suggested_macro"]
                )
        
        return None
    
    async def _suggest_macro(self, pattern: BehaviorPattern):
        """Suggère une macro cognitive basée sur le pattern."""
        if not pattern.suggested_macro:
            return
        
        # Vérifier si une macro similaire existe déjà
        for macro in self.cognitive_macros:
            if macro.trigger_pattern == pattern.pattern_type:
                return  # Macro déjà suggérée
        
        # Créer la macro suggérée
        macro = CognitiveMacro(
            macro_id=f"macro_{len(self.cognitive_macros)}",
            name=self._generate_macro_name(pattern),
            description=self._generate_macro_description(pattern),
            trigger_pattern=pattern.pattern_type,
            actions=self._generate_macro_actions(pattern),
            confidence=min(1.0, pattern.frequency / 10.0),
            created_at=datetime.now().isoformat(),
            user_feedback="pending"
        )
        
        self.cognitive_macros.append(macro)
        
        # Notifier l'utilisateur
        await self._notify_user(macro)
    
    def _generate_macro_name(self, pattern: BehaviorPattern) -> str:
        """Génère un nom pour la macro."""
        if pattern.pattern_type == "repeated_downloads":
            return "Organisation automatique des téléchargements"
        elif pattern.pattern_type == "repeated_file_creation":
            return "Organisation automatique des notes"
        elif pattern.pattern_type == "repeated_app_launch":
            return "Configuration automatique de l'espace de travail"
        else:
            return f"Macro {pattern.pattern_type}"
    
    def _generate_macro_description(self, pattern: BehaviorPattern) -> str:
        """Génère une description pour la macro."""
        file_types = ", ".join(pattern.context.get("file_types", []))
        return f"Détecté {pattern.frequency} fois. Organise automatiquement les fichiers {file_types}."
    
    def _generate_macro_actions(self, pattern: BehaviorPattern) -> List[Dict[str, Any]]:
        """Génère les actions pour la macro."""
        if pattern.pattern_type == "repeated_downloads":
            return [
                {"type": "FILE_MOVE", "source_pattern": "*.pdf", "destination": "Documents/Factures"},
                {"type": "FILE_RENAME", "pattern": "date", "format": "%Y-%m-%d"}
            ]
        elif pattern.pattern_type == "repeated_file_creation":
            return [
                {"type": "FILE_MOVE", "source_pattern": "*.txt", "destination": "Documents/Notes"},
                {"type": "CREATE_NOTE", "content": "Résumé automatique"}
            ]
        else:
            return [{"type": "LOG", "message": "Pattern détecté"}]
    
    async def _notify_user(self, macro: CognitiveMacro):
        """Notifie l'utilisateur de la macro suggérée."""
        print(f"\n💡 Suggestion de Macro Cognitive:")
        print(f"   Nom: {macro.name}")
        print(f"   Description: {macro.description}")
        print(f"   Confiance: {macro.confidence:.0%}")
        print(f"   Actions: {len(macro.actions)} action(s)")
        print(f"   Approuvez-vous cette macro? (y/n)")
    
    def approve_macro(self, macro_id: str, approved: bool):
        """Approuve ou rejette une macro."""
        for macro in self.cognitive_macros:
            if macro.macro_id == macro_id:
                macro.user_feedback = "approved" if approved else "rejected"
                return True
        return False
    
    def get_pending_macros(self) -> List[CognitiveMacro]:
        """Retourne les macros en attente d'approbation."""
        return [m for m in self.cognitive_macros if m.user_feedback == "pending"]
    
    def get_approved_macros(self) -> List[CognitiveMacro]:
        """Retourne les macros approuvées."""
        return [m for m in self.cognitive_macros if m.user_feedback == "approved"]
    
    async def execute_macro(self, macro_id: str) -> Dict[str, Any]:
        """Exécute une macro approuvée."""
        macro = next((m for m in self.cognitive_macros if m.macro_id == macro_id), None)
        
        if not macro:
            return {"error": "Macro non trouvée"}
        
        if macro.user_feedback != "approved":
            return {"error": "Macro non approuvée"}
        
        results = []
        
        for action in macro.actions:
            try:
                # Simulation de l'exécution
                result = {
                    "action": action["type"],
                    "status": "executed",
                    "timestamp": datetime.now().isoformat()
                }
                results.append(result)
            except Exception as e:
                results.append({
                    "action": action["type"],
                    "status": "failed",
                    "error": str(e)
                })
        
        return {
            "macro_id": macro_id,
            "macro_name": macro.name,
            "results": results,
            "executed_at": datetime.now().isoformat()
        }
    
    def stop_observation(self):
        """Arrête l'observation."""
        self.is_observing = False
    
    def get_behavior_report(self) -> Dict[str, Any]:
        """Génère un rapport sur les comportements détectés."""
        return {
            "total_patterns": len(self.behavior_patterns),
            "total_macros": len(self.cognitive_macros),
            "pending_macros": len(self.get_pending_macros()),
            "approved_macros": len(self.get_approved_macros()),
            "events_recorded": len(self.event_history),
            "is_observing": self.is_observing
        }
