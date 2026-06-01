"""
Focus Guardian Pro - Détecte distractions, fatigue, surcharge cognitive
Protection du temps de concentration.
"""

from typing import Dict, List, Any
from datetime import datetime, timedelta
import json
from pathlib import Path
import logging
from collections import defaultdict
import psutil

logger = logging.getLogger(__name__)


class FocusGuardianPro:
    """
    Protège le temps de concentration en détectant et bloquant les distractions
    """
    
    def __init__(self):
        self.focus_sessions = []
        self.distractions_detected = []
        self.fatigue_indicators = []
        self.cognitive_load_history = []
        self.current_focus_session = None
        self.data_path = Path(__file__).parent.parent.parent / "config" / "focus_guardian_data.json"
        self._load_data()
    
    def _load_data(self):
        """Charge les données du Focus Guardian"""
        try:
            if self.data_path.exists():
                with open(self.data_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.focus_sessions = data.get("focus_sessions", [])
                    self.distractions_detected = data.get("distractions_detected", [])
                    self.fatigue_indicators = data.get("fatigue_indicators", [])
                    self.cognitive_load_history = data.get("cognitive_load_history", [])
        except Exception as e:
            logger.warning(f"Erreur chargement données Focus Guardian: {e}")
    
    def _save_data(self):
        """Sauvegarde les données du Focus Guardian"""
        try:
            self.data_path.parent.mkdir(parents=True, exist_ok=True)
            data = {
                "focus_sessions": self.focus_sessions,
                "distractions_detected": self.distractions_detected[-100],
                "fatigue_indicators": self.fatigue_indicators[-100],
                "cognitive_load_history": self.cognitive_load_history[-100]
            }
            with open(self.data_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.warning(f"Erreur sauvegarde données Focus Guardian: {e}")
    
    def start_focus_session(self, task: str, duration_minutes: int = 25) -> Dict[str, Any]:
        """
        Démarre une session de focus (Pomodoro)
        """
        session_id = f"focus_{datetime.now().timestamp()}"
        self.current_focus_session = {
            "id": session_id,
            "task": task,
            "start_time": datetime.now().isoformat(),
            "duration_minutes": duration_minutes,
            "distractions_blocked": 0,
            "status": "active"
        }
        
        return {
            "status": "focus_session_started",
            "session_id": session_id,
            "task": task,
            "duration_minutes": duration_minutes,
            "message": f"Session de focus démarrée pour {duration_minutes} minutes"
        }
    
    def end_focus_session(self) -> Dict[str, Any]:
        """
        Termine la session de focus actuelle
        """
        if not self.current_focus_session:
            return {"status": "error", "message": "No active focus session"}
        
        self.current_focus_session["end_time"] = datetime.now().isoformat()
        self.current_focus_session["status"] = "completed"
        
        # Calculer la durée réelle
        start = datetime.fromisoformat(self.current_focus_session["start_time"])
        end = datetime.fromisoformat(self.current_focus_session["end_time"])
        actual_duration = (end - start).total_seconds() / 60
        
        self.current_focus_session["actual_duration_minutes"] = actual_duration
        
        self.focus_sessions.append(self.current_focus_session)
        self.current_focus_session = None
        
        self._save_data()
        
        return {
            "status": "focus_session_ended",
            "session": self.focus_sessions[-1],
            "message": f"Session terminée après {actual_duration:.1f} minutes"
        }
    
    def detect_distraction(self, distraction_type: str, details: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Détecte et enregistre une distraction
        """
        distraction = {
            "timestamp": datetime.now().isoformat(),
            "type": distraction_type,
            "details": details or {},
            "blocked": False
        }
        
        # Si une session de focus est active, bloquer la distraction
        if self.current_focus_session and self.current_focus_session["status"] == "active":
            distraction["blocked"] = True
            self.current_focus_session["distractions_blocked"] += 1
        
        self.distractions_detected.append(distraction)
        self._save_data()
        
        return {
            "status": "distraction_detected",
            "distraction": distraction,
            "blocked": distraction["blocked"],
            "message": "Distraction bloquée" if distraction["blocked"] else "Distraction détectée"
        }
    
    def measure_fatigue(self) -> Dict[str, Any]:
        """
        Mesure les indicateurs de fatigue
        """
        # Indicateurs basés sur le temps de travail et l'activité système
        current_hour = datetime.now().hour
        
        # Fatigue basée sur l'heure
        hour_fatigue = 0.0
        if 2 <= current_hour <= 6:  # Nuit profonde
            hour_fatigue = 0.9
        elif 22 <= current_hour <= 23 or current_hour == 1:  # Soir/tard
            hour_fatigue = 0.7
        elif 13 <= current_hour <= 15:  # Après-midi (creux post-déjeuner)
            hour_fatigue = 0.5
        elif 9 <= current_hour <= 11 or 16 <= current_hour <= 18:  # Heures de productivité
            hour_fatigue = 0.2
        
        # Fatigue basée sur l'utilisation CPU (indicateur d'activité intense)
        cpu_usage = psutil.cpu_percent(interval=1)
        cpu_fatigue = min(cpu_usage / 100, 1.0) * 0.3
        
        # Fatigue basée sur les sessions de focus récentes
        recent_sessions = [s for s in self.focus_sessions if datetime.fromisoformat(s["start_time"]) > datetime.now() - timedelta(hours=4)]
        session_fatigue = min(len(recent_sessions) / 8, 1.0) * 0.4
        
        total_fatigue = hour_fatigue + cpu_fatigue + session_fatigue
        total_fatigue = min(total_fatigue, 1.0)
        
        fatigue_indicator = {
            "timestamp": datetime.now().isoformat(),
            "hour_fatigue": hour_fatigue,
            "cpu_fatigue": cpu_fatigue,
            "session_fatigue": session_fatigue,
            "total_fatigue": total_fatigue,
            "level": "high" if total_fatigue > 0.7 else "medium" if total_fatigue > 0.4 else "low"
        }
        
        self.fatigue_indicators.append(fatigue_indicator)
        self._save_data()
        
        return fatigue_indicator
    
    def measure_cognitive_load(self) -> Dict[str, Any]:
        """
        Mesure la surcharge cognitive
        """
        # Indicateurs de surcharge cognitive
        current_hour = datetime.now().hour
        
        # Surcharge basée sur le nombre d'applications ouvertes
        try:
            process_count = len(psutil.pids())
            process_load = min(process_count / 200, 1.0) * 0.3
        except:
            process_load = 0.3
        
        # Surcharge basée sur l'utilisation mémoire
        memory_usage = psutil.virtual_memory().percent
        memory_load = min(memory_usage / 100, 1.0) * 0.3
        
        # Surcharge basée sur les distractions récentes
        recent_distractions = [d for d in self.distractions_detected if datetime.fromisoformat(d["timestamp"]) > datetime.now() - timedelta(hours=1)]
        distraction_load = min(len(recent_distractions) / 20, 1.0) * 0.4
        
        total_load = process_load + memory_load + distraction_load
        total_load = min(total_load, 1.0)
        
        cognitive_load = {
            "timestamp": datetime.now().isoformat(),
            "process_load": process_load,
            "memory_load": memory_load,
            "distraction_load": distraction_load,
            "total_load": total_load,
            "level": "high" if total_load > 0.7 else "medium" if total_load > 0.4 else "low"
        }
        
        self.cognitive_load_history.append(cognitive_load)
        self._save_data()
        
        return cognitive_load
    
    def get_focus_summary(self) -> Dict[str, Any]:
        """
        Retourne un résumé du focus et de la santé cognitive
        """
        total_focus_time = sum(s.get("actual_duration_minutes", s["duration_minutes"]) for s in self.focus_sessions)
        total_distractions = len(self.distractions_detected)
        blocked_distractions = sum(1 for d in self.distractions_detected if d.get("blocked", False))
        
        # Fatigue moyenne récente
        recent_fatigue = self.fatigue_indicators[-10:] if self.fatigue_indicators else []
        avg_fatigue = sum(f["total_fatigue"] for f in recent_fatigue) / len(recent_fatigue) if recent_fatigue else 0.0
        
        # Charge cognitive moyenne récente
        recent_load = self.cognitive_load_history[-10:] if self.cognitive_load_history else []
        avg_load = sum(l["total_load"] for l in recent_load) / len(recent_load) if recent_load else 0.0
        
        return {
            "total_focus_sessions": len(self.focus_sessions),
            "total_focus_time_minutes": total_focus_time,
            "total_distractions_detected": total_distractions,
            "distractions_blocked": blocked_distractions,
            "distraction_block_rate": blocked_distractions / total_distractions if total_distractions > 0 else 0.0,
            "current_fatigue_level": avg_fatigue,
            "current_cognitive_load": avg_load,
            "recommendation": self._generate_recommendation(avg_fatigue, avg_load)
        }
    
    def _generate_recommendation(self, fatigue: float, cognitive_load: float) -> str:
        """Génère une recommandation basée sur l'état actuel"""
        if fatigue > 0.7 and cognitive_load > 0.7:
            return "Faites une pause de 15-20 minutes. Votre cerveau a besoin de récupérer."
        elif fatigue > 0.7:
            return "Vous êtes fatigué. Considérez une courte pause ou une tâche moins exigeante."
        elif cognitive_load > 0.7:
            return "Surcharge cognitive détectée. Réduisez le nombre d'applications ouvertes."
        elif fatigue > 0.4:
            return "Fatigue modérée. Une courte pause pourrait être bénéfique."
        else:
            return "État optimal pour le travail concentré."
