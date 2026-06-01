"""
Friction Detector - Détecte tâches répétitives, clics inutiles, routines chronophages
Automatisation continue.
"""

from typing import Dict, List, Any
from datetime import datetime, timedelta
import json
from pathlib import Path
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)


class FrictionDetector:
    """
    Détecte les frictions dans le workflow de l'utilisateur et suggère des automatisations
    """
    
    def __init__(self):
        self.action_log = []
        self.repetitive_tasks = defaultdict(list)
        self.time_wasters = defaultdict(float)
        self.automation_suggestions = []
        self.data_path = Path(__file__).parent.parent.parent / "config" / "friction_detector_data.json"
        self._load_data()
    
    def _load_data(self):
        """Charge les données de détection de friction"""
        try:
            if self.data_path.exists():
                with open(self.data_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.action_log = data.get("action_log", [])
                    self.repetitive_tasks = defaultdict(list, data.get("repetitive_tasks", {}))
                    self.time_wasters = defaultdict(float, data.get("time_wasters", {}))
                    self.automation_suggestions = data.get("automation_suggestions", [])
        except Exception as e:
            logger.warning(f"Erreur chargement données Friction Detector: {e}")
    
    def _save_data(self):
        """Sauvegarde les données de détection de friction"""
        try:
            self.data_path.parent.mkdir(parents=True, exist_ok=True)
            data = {
                "action_log": self.action_log[-500],  # Garder les 500 dernières actions
                "repetitive_tasks": dict(self.repetitive_tasks),
                "time_wasters": dict(self.time_wasters),
                "automation_suggestions": self.automation_suggestions
            }
            with open(self.data_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.warning(f"Erreur sauvegarde données Friction Detector: {e}")
    
    def log_action(self, action_type: str, details: Dict[str, Any], duration: float = 0.0):
        """
        Enregistre une action pour l'analyse de friction
        """
        action_record = {
            "timestamp": datetime.now().isoformat(),
            "action_type": action_type,
            "details": details,
            "duration": duration
        }
        self.action_log.append(action_record)
        
        # Détecter les tâches répétitives
        task_key = self._generate_task_key(action_type, details)
        self.repetitive_tasks[task_key].append({
            "timestamp": action_record["timestamp"],
            "duration": duration
        })
        
        # Calculer le temps perdu
        if duration > 5.0:  # Actions prenant plus de 5 secondes
            self.time_wasters[task_key] += duration
        
        # Sauvegarder périodiquement
        if len(self.action_log) % 20 == 0:
            self._save_data()
    
    def _generate_task_key(self, action_type: str, details: Dict[str, Any]) -> str:
        """Génère une clé unique pour identifier une tâche"""
        key_parts = [action_type]
        if "app" in details:
            key_parts.append(details["app"])
        if "file" in details:
            key_parts.append(details["file"])
        if "folder" in details:
            key_parts.append(details["folder"])
        return "_".join(key_parts)
    
    def detect_repetitive_tasks(self, threshold: int = 5) -> List[Dict[str, Any]]:
        """
        Détecte les tâches répétitives
        """
        repetitive = []
        
        for task_key, occurrences in self.repetitive_tasks.items():
            if len(occurrences) >= threshold:
                total_time = sum(o["duration"] for o in occurrences)
                avg_time = total_time / len(occurrences)
                
                repetitive.append({
                    "task": task_key,
                    "occurrences": len(occurrences),
                    "total_time": total_time,
                    "avg_time": avg_time,
                    "potential_savings": total_time * 0.8,  # 80% d'économie potentielle
                    "automation_priority": "high" if len(occurrences) > 10 else "medium"
                })
        
        # Trier par nombre d'occurrences
        repetitive.sort(key=lambda x: x["occurrences"], reverse=True)
        
        return repetitive
    
    def detect_time_wasters(self, threshold: float = 30.0) -> List[Dict[str, Any]]:
        """
        Détecte les routines chronophages
        """
        wasters = []
        
        for task_key, total_time in self.time_wasters.items():
            if total_time >= threshold:
                occurrences = len(self.repetitive_tasks.get(task_key, []))
                avg_time = total_time / occurrences if occurrences > 0 else total_time
                
                wasters.append({
                    "task": task_key,
                    "total_time": total_time,
                    "occurrences": occurrences,
                    "avg_time": avg_time,
                    "priority": "high" if total_time > 60 else "medium"
                })
        
        # Trier par temps total
        wasters.sort(key=lambda x: x["total_time"], reverse=True)
        
        return wasters
    
    def suggest_automations(self) -> List[Dict[str, Any]]:
        """
        Suggère des automatisations basées sur les frictions détectées
        """
        suggestions = []
        
        # Analyser les tâches répétitives
        repetitive = self.detect_repetitive_tasks()
        for task in repetitive[:5]:
            suggestions.append({
                "type": "automation",
                "task": task["task"],
                "reason": f"Tâche répétée {task['occurrences']} fois",
                "potential_savings": f"{task['potential_savings']:.1f} secondes",
                "suggestion": f"Créer un workflow pour automatiser {task['task']}",
                "priority": task["automation_priority"]
            })
        
        # Analyser les routines chronophages
        wasters = self.detect_time_wasters()
        for waster in wasters[:5]:
            suggestions.append({
                "type": "optimization",
                "task": waster["task"],
                "reason": f"Routine chronophage ({waster['total_time']:.1f}s total)",
                "potential_savings": f"{waster['total_time'] * 0.5:.1f} secondes",
                "suggestion": f"Optimiser ou automatiser {waster['task']}",
                "priority": waster["priority"]
            })
        
        # Trier par priorité
        suggestions.sort(key=lambda x: 0 if x["priority"] == "high" else 1)
        
        self.automation_suggestions = suggestions
        self._save_data()
        
        return suggestions
    
    def get_friction_summary(self) -> Dict[str, Any]:
        """
        Retourne un résumé des frictions détectées
        """
        repetitive = self.detect_repetitive_tasks()
        wasters = self.detect_time_wasters()
        
        total_potential_savings = sum(t["potential_savings"] for t in repetitive)
        total_time_wasted = sum(w["total_time"] for w in wasters)
        
        return {
            "repetitive_tasks_detected": len(repetitive),
            "time_wasters_detected": len(wasters),
            "total_potential_savings_seconds": total_potential_savings,
            "total_time_wasted_seconds": total_time_wasted,
            "automation_suggestions_count": len(self.automation_suggestions),
            "estimated_daily_savings": f"{total_potential_savings / 60:.1f} minutes"
        }
