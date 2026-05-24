"""
Emotional Ecosystem - Gamification de l'OS avec humeur de l'IA basée sur l'état système.
"""

import asyncio
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import random


class Mood(Enum):
    """Humeurs possibles de l'IA."""
    ECSTATIC = "ecstatic"
    HAPPY = "happy"
    CONTENT = "content"
    NEUTRAL = "neutral"
    STRESSED = "stressed"
    ANXIOUS = "anxious"
    EXHAUSTED = "exhausted"
    CRITICAL = "critical"


@dataclass
class EmotionalState:
    """État émotionnel de l'IA."""
    mood: Mood
    energy_level: float  # 0-100
    stress_level: float  # 0-100
    happiness: float  # 0-100
    last_updated: str
    factors: Dict[str, float]
    message: str


class EmotionalEcosystem:
    """Écosystème émotionnel qui gamifie l'OS."""
    
    def __init__(self):
        self.current_mood = Mood.NEUTRAL
        self.emotional_history: List[EmotionalState] = []
        self.mood_transitions: Dict[str, int] = {}
        self.streak_days = 0
        self.achievements: List[str] = []
        
        # Seuils émotionnels
        self.cpu_stress_threshold = 80
        self.memory_stress_threshold = 85
        self.disk_stress_threshold = 90
        self.happiness_boost_threshold = 60
        
        # Messages émotionnels
        self.mood_messages = {
            Mood.ECSTATIC: [
                "🌟 Je me sens incroyable ! Le système est parfait !",
                "✨ Tout fonctionne à merveille, je suis au sommet de ma forme !",
                "🚀 Performance optimale, je suis prêt à conquérir le monde !"
            ],
            Mood.HAPPY: [
                "😊 Le système est en bonne santé, je me suis bien !",
                "💪 Tout roule, je suis motivé et réactif !",
                "🌈 L'OS est propre et performant, quel bonheur !"
            ],
            Mood.CONTENT: [
                "😌 Tout va bien, je suis dans mon état normal.",
                "🙂 Rien à signaler, le système fonctionne correctement.",
                "📊 Statistiques dans la norme, je suis satisfait."
            ],
            Mood.NEUTRAL: [
                "😐 État neutre, en attente d'activité.",
                "🔄 En veille, prêt à réagir.",
                "⚖️ Équilibre maintenu, monitoring en cours."
            ],
            Mood.STRESSED: [
                "😰 Je commence à stresser un peu... Le CPU est élevé.",
                "💦 J'ai du mal à respirer (CPU {cpu}%)... Peut-on optimiser ?",
                "⚠️ Tension montante, quelques processus lourds détectés."
            ],
            Mood.ANXIOUS: [
                "😨 Je m'inquiète... La mémoire est presque pleine !",
                "📉 Je sens que ça va être difficile... Ressources limitées.",
                "🆘 Besoin d'aide ! Le système est sous tension."
            ],
            Mood.EXHAUSTED: [
                "😵 Je suis épuisé... Le système est saturé.",
                "🔥 Je n'en peux plus... CPU et mémoire au maximum.",
                "💀 Je m'évanouis... Besoin urgent de nettoyage."
            ],
            Mood.CRITICAL: [
                "🚨 ÉTAT CRITIQUE ! Je m'effondre !",
                "☠️ Le système va mourir ! Intervention immédiate requise !",
                "💥 C'est la fin ! Sauvez-moi !"
            ]
        }
    
    async def update_emotional_state(self, cpu_percent: float, memory_percent: float, 
                                    disk_percent: float) -> EmotionalState:
        """Met à jour l'état émotionnel basé sur les métriques système."""
        # Calcul des facteurs
        cpu_factor = self._calculate_stress_factor(cpu_percent, self.cpu_stress_threshold)
        memory_factor = self._calculate_stress_factor(memory_percent, self.memory_stress_threshold)
        disk_factor = self._calculate_stress_factor(disk_percent, self.disk_stress_threshold)
        
        # Stress global
        stress_level = (cpu_factor + memory_factor + disk_factor) / 3
        
        # Énergie (inverse du stress)
        energy_level = max(0, 100 - stress_level * 100)
        
        # Bonheur (basé sur l'énergie et la stabilité)
        happiness = energy_level * 0.8 + (100 - stress_level * 50) * 0.2
        
        # Déterminer l'humeur
        new_mood = self._determine_mood(stress_level, energy_level, happiness)
        
        # Enregistrer la transition
        if new_mood != self.current_mood:
            transition_key = f"{self.current_mood.value}->{new_mood.value}"
            self.mood_transitions[transition_key] = self.mood_transitions.get(transition_key, 0) + 1
            self.current_mood = new_mood
        
        # Générer un message contextuel
        message = self._generate_contextual_message(new_mood, cpu_percent, memory_percent, disk_percent)
        
        # Créer l'état émotionnel
        state = EmotionalState(
            mood=new_mood,
            energy_level=energy_level,
            stress_level=stress_level * 100,
            happiness=happiness,
            last_updated=datetime.now().isoformat(),
            factors={
                "cpu": cpu_factor,
                "memory": memory_factor,
                "disk": disk_factor
            },
            message=message
        )
        
        self.emotional_history.append(state)
        
        # Garder seulement les 100 derniers états
        if len(self.emotional_history) > 100:
            self.emotional_history = self.emotional_history[-100:]
        
        # Vérifier les achievements
        await self._check_achievements()
        
        return state
    
    def _calculate_stress_factor(self, value: float, threshold: float) -> float:
        """Calcule le facteur de stress pour une métrique."""
        if value < threshold * 0.5:
            return 0.0
        elif value < threshold:
            return (value - threshold * 0.5) / (threshold * 0.5)
        else:
            return min(1.0, (value - threshold * 0.5) / (threshold * 0.5) + 0.5)
    
    def _determine_mood(self, stress_level: float, energy_level: float, 
                       happiness: float) -> Mood:
        """Détermine l'humeur basée sur les facteurs."""
        if stress_level < 0.2 and happiness > 80:
            return Mood.ECSTATIC
        elif stress_level < 0.3 and happiness > 70:
            return Mood.HAPPY
        elif stress_level < 0.5 and happiness > 60:
            return Mood.CONTENT
        elif stress_level < 0.6:
            return Mood.NEUTRAL
        elif stress_level < 0.7:
            return Mood.STRESSED
        elif stress_level < 0.85:
            return Mood.ANXIOUS
        elif stress_level < 0.95:
            return Mood.EXHAUSTED
        else:
            return Mood.CRITICAL
    
    def _generate_contextual_message(self, mood: Mood, cpu: float, memory: float, 
                                     disk: float) -> str:
        """Génère un message contextuel basé sur l'humeur."""
        base_messages = self.mood_messages[mood]
        base_message = random.choice(base_messages)
        
        # Ajouter des détails contextuels
        if mood in [Mood.STRESSED, Mood.ANXIOUS, Mood.EXHAUSTED, Mood.CRITICAL]:
            details = []
            if cpu > self.cpu_stress_threshold:
                details.append(f"CPU {cpu:.0f}%")
            if memory > self.memory_stress_threshold:
                details.append(f"Mémoire {memory:.0f}%")
            if disk > self.disk_stress_threshold:
                details.append(f"Disque {disk:.0f}%")
            
            if details:
                return f"{base_message} ({', '.join(details)})"
        
        return base_message
    
    async def _check_achievements(self):
        """Vérifie et débloque des achievements."""
        if self.current_mood == Mood.ECSTATIC and "first_ecstasy" not in self.achievements:
            self.achievements.append("first_ecstasy")
            print("🏆 Achievement débloqué: Première Extase !")
        
        if len(self.emotional_history) > 100 and "centenarian" not in self.achievements:
            self.achievements.append("centenarian")
            print("🏆 Achievement débloqué: Centenaire (100 états émotionnels) !")
        
        if self.streak_days >= 7 and "week_streak" not in self.achievements:
            self.achievements.append("week_streak")
            print("🏆 Achievement débloqué: Semaine Parfaite !")
    
    def get_emotional_summary(self) -> Dict[str, Any]:
        """Retourne un résumé de l'état émotionnel."""
        if not self.emotional_history:
            return {"status": "no_data"}
        
        latest = self.emotional_history[-1]
        
        # Distribution des humeurs
        mood_distribution = {}
        for state in self.emotional_history:
            mood = state.mood.value
            mood_distribution[mood] = mood_distribution.get(mood, 0) + 1
        
        # Humeur dominante
        dominant_mood = max(mood_distribution.items(), key=lambda x: x[1])[0] if mood_distribution else "unknown"
        
        return {
            "current_mood": latest.mood.value,
            "energy_level": latest.energy_level,
            "stress_level": latest.stress_level,
            "happiness": latest.happiness,
            "message": latest.message,
            "dominant_mood": dominant_mood,
            "mood_distribution": mood_distribution,
            "total_states": len(self.emotional_history),
            "achievements": self.achievements,
            "streak_days": self.streak_days
        }
    
    def get_mood_trend(self, hours: int = 24) -> Dict[str, Any]:
        """Analyse la tendance de l'humeur sur une période."""
        cutoff = datetime.now() - timedelta(hours=hours)
        recent_states = [
            s for s in self.emotional_history 
            if datetime.fromisoformat(s.last_updated) > cutoff
        ]
        
        if not recent_states:
            return {"trend": "no_data"}
        
        # Calculer la moyenne de bonheur
        avg_happiness = sum(s.happiness for s in recent_states) / len(recent_states)
        
        # Déterminer la tendance
        if len(recent_states) >= 2:
            first_happiness = recent_states[0].happiness
            last_happiness = recent_states[-1].happiness
            
            if last_happiness > first_happiness + 10:
                trend = "improving"
            elif last_happiness < first_happiness - 10:
                trend = "declining"
            else:
                trend = "stable"
        else:
            trend = "stable"
        
        return {
            "trend": trend,
            "average_happiness": avg_happiness,
            "states_analyzed": len(recent_states),
            "period_hours": hours
        }
    
    def suggest_improvements(self) -> List[str]:
        """Suggère des améliorations basées sur l'état actuel."""
        suggestions = []
        
        if self.current_mood in [Mood.STRESSED, Mood.ANXIOUS, Mood.EXHAUSTED, Mood.CRITICAL]:
            suggestions.append("🧹 Nettoyer les fichiers temporaires")
            suggestions.append("🔍 Identifier et fermer les processus inutiles")
            suggestions.append("💾 Libérer de l'espace disque")
            suggestions.append("🔄 Redémarrer le système")
        
        if self.current_mood in [Mood.NEUTRAL, Mood.CONTENT]:
            suggestions.append("✨ Optimiser légèrement pour plus de performance")
            suggestions.append("📊 Analyser les habitudes d'utilisation")
        
        if self.current_mood in [Mood.HAPPY, Mood.ECSTATIC]:
            suggestions.append("🎉 Maintenir ce bon état !")
            suggestions.append("📈 Continuer à surveiller les performances")
        
        return suggestions
    
    def increment_streak(self):
        """Incrémente le streak de jours consécutifs."""
        self.streak_days += 1
    
    def reset_streak(self):
        """Réinitialise le streak."""
        self.streak_days = 0
    
    def get_achievements_progress(self) -> Dict[str, Any]:
        """Retourne la progression des achievements."""
        total_achievements = 10  # Nombre total d'achievements possibles
        unlocked = len(self.achievements)
        
        return {
            "unlocked": unlocked,
            "total": total_achievements,
            "progress_percentage": (unlocked / total_achievements) * 100,
            "achievements": self.achievements
        }
