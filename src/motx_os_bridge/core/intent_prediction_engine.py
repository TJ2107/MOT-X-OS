"""
Intent Prediction Engine - Anticipe les prochaines actions
Ouvre automatiquement les documents pertinents, prépare les mails, précharge les applications.
"""

from typing import Dict, List, Any
from datetime import datetime, timedelta
import json
from pathlib import Path
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)


class IntentPredictionEngine:
    """
    Anticipe les prochaines actions de l'utilisateur pour réduire les micro-actions inutiles
    """
    
    def __init__(self):
        self.action_history = []
        self.context_patterns = defaultdict(list)
        self.predictions_cache = {}
        self.data_path = Path(__file__).parent.parent.parent / "config" / "intent_prediction_data.json"
        self._load_data()
    
    def _load_data(self):
        """Charge les données de prédiction"""
        try:
            if self.data_path.exists():
                with open(self.data_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.action_history = data.get("action_history", [])
                    self.context_patterns = defaultdict(list, data.get("context_patterns", {}))
        except Exception as e:
            logger.warning(f"Erreur chargement données Intent Prediction: {e}")
    
    def _save_data(self):
        """Sauvegarde les données de prédiction"""
        try:
            self.data_path.parent.mkdir(parents=True, exist_ok=True)
            data = {
                "action_history": self.action_history[-1000],  # Garder les 1000 dernières actions
                "context_patterns": dict(self.context_patterns)
            }
            with open(self.data_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.warning(f"Erreur sauvegarde données Intent Prediction: {e}")
    
    def record_action(self, action_type: str, context: Dict[str, Any]):
        """
        Enregistre une action avec son contexte
        """
        action_record = {
            "timestamp": datetime.now().isoformat(),
            "action_type": action_type,
            "context": context
        }
        self.action_history.append(action_record)
        
        # Enregistrer le pattern de contexte
        context_key = self._generate_context_key(context)
        self.context_patterns[context_key].append(action_type)
        
        # Sauvegarder périodiquement
        if len(self.action_history) % 10 == 0:
            self._save_data()
    
    def _generate_context_key(self, context: Dict[str, Any]) -> str:
        """Génère une clé unique pour le contexte"""
        hour = datetime.now().hour
        day = datetime.now().weekday()
        app = context.get("app", "unknown")
        project = context.get("project", "unknown")
        return f"{hour}_{day}_{app}_{project}"
    
    def predict_next_actions(self, current_context: Dict[str, Any], limit: int = 5) -> List[Dict[str, Any]]:
        """
        Prédit les prochaines actions basées sur le contexte actuel
        """
        context_key = self._generate_context_key(current_context)
        
        if context_key in self.context_patterns:
            recent_actions = self.context_patterns[context_key][-20]
            action_counts = defaultdict(int)
            
            for action in recent_actions:
                action_counts[action] += 1
            
            predictions = []
            for action, count in sorted(action_counts.items(), key=lambda x: x[1], reverse=True):
                confidence = min(count / len(recent_actions), 1.0)
                predictions.append({
                    "action": action,
                    "confidence": confidence,
                    "reason": f"Pattern détecté dans le contexte {context_key}"
                })
            
            return predictions[:limit]
        
        # Fallback: analyser l'historique global
        return self._predict_from_history(current_context, limit)
    
    def _predict_from_history(self, context: Dict[str, Any], limit: int = 5) -> List[Dict[str, Any]]:
        """Prédit depuis l'historique global"""
        recent_history = self.action_history[-100]
        action_counts = defaultdict(int)
        
        for record in recent_history:
            action_counts[record["action_type"]] += 1
        
        predictions = []
        for action, count in sorted(action_counts.items(), key=lambda x: x[1], reverse=True):
            confidence = min(count / len(recent_history), 1.0)
            predictions.append({
                "action": action,
                "confidence": confidence * 0.5,  # Réduire la confiance pour le fallback
                "reason": "Basé sur l'historique global"
            })
        
        return predictions[:limit]
    
    def suggest_documents(self, current_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Suggère les documents pertinents à ouvrir
        """
        project = current_context.get("project")
        if project:
            # Chercher les documents récemment ouverts pour ce projet
            project_docs = []
            for record in self.action_history[-50]:
                if record.get("context", {}).get("project") == project:
                    if "document" in record.get("context", {}):
                        project_docs.append(record["context"]["document"])
            
            # Retourner les documents uniques
            unique_docs = list(set(project_docs))
            return [
                {
                    "path": doc,
                    "reason": f"Document récent du projet {project}",
                    "confidence": 0.8
                }
                for doc in unique_docs[:5]
            ]
        
        return []
    
    def suggest_emails(self, current_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Suggère les emails à préparer
        """
        # Analyser les patterns d'envoi d'emails
        email_actions = [
            record for record in self.action_history[-100]
            if record["action_type"] == "send_email"
        ]
        
        if email_actions:
            # Extraire les destinataires fréquents
            recipients = defaultdict(int)
            for record in email_actions:
                recipient = record.get("context", {}).get("recipient")
                if recipient:
                    recipients[recipient] += 1
            
            suggestions = []
            for recipient, count in sorted(recipients.items(), key=lambda x: x[1], reverse=True)[:3]:
                suggestions.append({
                    "recipient": recipient,
                    "reason": f"Contact fréquent ({count} emails)",
                    "confidence": min(count / len(email_actions), 1.0)
                })
            
            return suggestions
        
        return []
    
    def suggest_applications(self, current_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Suggère les applications à précharger
        """
        current_hour = datetime.now().hour
        current_day = datetime.now().weekday()
        
        # Analyser les applications utilisées à cet horaire
        hour_apps = defaultdict(int)
        for record in self.action_history[-200]:
            record_time = datetime.fromisoformat(record["timestamp"])
            if record_time.hour == current_hour and record_time.weekday() == current_day:
                app = record.get("context", {}).get("app")
                if app:
                    hour_apps[app] += 1
        
        suggestions = []
        for app, count in sorted(hour_apps.items(), key=lambda x: x[1], reverse=True)[:5]:
            suggestions.append({
                "application": app,
                "reason": f"Utilisation fréquente à cette heure ({count} fois)",
                "confidence": min(count / 10, 1.0)
            })
        
        return suggestions
    
    def get_prediction_summary(self) -> Dict[str, Any]:
        """
        Retourne un résumé des prédictions
        """
        total_actions = len(self.action_history)
        unique_contexts = len(self.context_patterns)
        
        return {
            "total_actions_recorded": total_actions,
            "unique_context_patterns": unique_contexts,
            "prediction_accuracy": 0.75,  # Placeholder - à calculer avec les résultats réels
            "time_saved_estimate": f"{total_actions * 0.5} secondes",  # Estimation
            "decisions_reduced": f"{total_actions * 0.8} décisions"
        }
