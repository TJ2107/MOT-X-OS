"""
Life Twin Engine - Jumeau Cognitif
Apprend les habitudes de travail, comprend les projets, identifie les horaires de productivité.
"""

from typing import Dict, List, Any
from datetime import datetime, timedelta
import json
from pathlib import Path
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)


class LifeTwinEngine:
    """
    Jumeau Cognitif qui apprend et adapte l'environnement à l'utilisateur
    """
    
    def __init__(self):
        self.habits = defaultdict(list)
        self.projects = {}
        self.productivity_schedule = defaultdict(float)
        self.recurring_behaviors = defaultdict(int)
        self.environment_state = {}
        self.learning_data_path = Path(__file__).parent.parent.parent / "config" / "life_twin_data.json"
        self._load_learning_data()
    
    def _load_learning_data(self):
        """Charge les données d'apprentissage"""
        try:
            if self.learning_data_path.exists():
                with open(self.learning_data_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.habits = defaultdict(list, data.get("habits", {}))
                    self.projects = data.get("projects", {})
                    self.productivity_schedule = defaultdict(float, data.get("productivity_schedule", {}))
                    self.recurring_behaviors = defaultdict(int, data.get("recurring_behaviors", {}))
                    self.environment_state = data.get("environment_state", {})
        except Exception as e:
            logger.warning(f"Erreur chargement données Life Twin: {e}")
    
    def _save_learning_data(self):
        """Sauvegarde les données d'apprentissage"""
        try:
            self.learning_data_path.parent.mkdir(parents=True, exist_ok=True)
            data = {
                "habits": dict(self.habits),
                "projects": self.projects,
                "productivity_schedule": dict(self.productivity_schedule),
                "recurring_behaviors": dict(self.recurring_behaviors),
                "environment_state": self.environment_state
            }
            with open(self.learning_data_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.warning(f"Erreur sauvegarde données Life Twin: {e}")
    
    def record_action(self, action_type: str, details: Dict[str, Any]):
        """
        Enregistre une action pour l'apprentissage
        """
        timestamp = datetime.now()
        hour = timestamp.hour
        day_of_week = timestamp.weekday()
        
        # Enregistrer l'habitude
        habit_key = f"{action_type}_{hour}_{day_of_week}"
        self.habits[habit_key].append({
            "timestamp": timestamp.isoformat(),
            "details": details
        })
        
        # Mettre à jour l'horaire de productivité
        self.productivity_schedule[hour] += 1
        
        # Compter les comportements récurrents
        self.recurring_behaviors[action_type] += 1
        
        # Sauvegarder périodiquement
        if len(self.habits[habit_key]) % 10 == 0:
            self._save_learning_data()
    
    def learn_project_context(self, project_name: str, context: Dict[str, Any]):
        """
        Apprend le contexte d'un projet
        """
        self.projects[project_name] = {
            "learned_at": datetime.now().isoformat(),
            "context": context,
            "access_count": self.projects.get(project_name, {}).get("access_count", 0) + 1
        }
        self._save_learning_data()
    
    def predict_next_actions(self, current_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Prédit les prochaines actions basées sur l'horaire et le contexte
        """
        current_hour = datetime.now().hour
        current_day = datetime.now().weekday()
        
        predictions = []
        
        # Analyser les habitudes pour cet horaire
        for habit_key, habit_data in self.habits.items():
            if habit_key.startswith(f"{current_hour}_{current_day}"):
                if habit_data:
                    last_action = habit_data[-1]
                    predictions.append({
                        "action_type": habit_key.split("_")[0],
                        "confidence": min(len(habit_data) / 10, 1.0),
                        "suggested_details": last_action.get("details", {})
                    })
        
        # Trier par confiance
        predictions.sort(key=lambda x: x["confidence"], reverse=True)
        
        return predictions[:5]
    
    def prepare_environment(self, project_name: str = None) -> Dict[str, Any]:
        """
        Prépare l'environnement automatiquement
        """
        if project_name and project_name in self.projects:
            context = self.projects[project_name]["context"]
            return {
                "status": "environment_prepared",
                "project": project_name,
                "suggested_apps": context.get("apps", []),
                "suggested_documents": context.get("documents", []),
                "workspace_layout": context.get("layout", "default")
            }
        
        # Préparer l'environnement basé sur les habitudes actuelles
        current_hour = datetime.now().hour
        peak_hours = sorted(self.productivity_schedule.items(), key=lambda x: x[1], reverse=True)
        
        if peak_hours and peak_hours[0][0] == current_hour:
            return {
                "status": "peak_productivity_mode",
                "message": "Mode productivité maximale activé",
                "suggestions": self.predict_next_actions({})
            }
        
        return {
            "status": "standard_mode",
            "message": "Environnement standard"
        }
    
    def get_learning_summary(self) -> Dict[str, Any]:
        """
        Retourne un résumé de l'apprentissage
        """
        total_actions = sum(len(h) for h in self.habits.values())
        top_behaviors = sorted(self.recurring_behaviors.items(), key=lambda x: x[1], reverse=True)[:5]
        peak_hours = sorted(self.productivity_schedule.items(), key=lambda x: x[1], reverse=True)[:3]
        
        return {
            "total_actions_learned": total_actions,
            "projects_tracked": len(self.projects),
            "top_behaviors": [{"action": k, "count": v} for k, v in top_behaviors],
            "peak_productivity_hours": [{"hour": h, "score": s} for h, s in peak_hours],
            "learning_progress": min(total_actions / 1000, 1.0) * 100
        }
