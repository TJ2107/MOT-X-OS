"""
Gamification Engine - Système de gamification qui rend chaque action pertinente et récompensée.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Any
from datetime import datetime, timedelta
import random
import logging

logger = logging.getLogger(__name__)


class Achievement(Enum):
    """Achievements débloquables"""
    FIRST_TASK = "first_automation"
    COGNITIVE_CONSENSUS = "cognitive_consensus"
    EMERGENT_INSIGHT = "emergent_insight"
    ZERO_FAILURE = "perfect_execution"
    CREATIVE_SOLUTION = "unexpected_solution"
    PATTERN_MASTER = "learn_100_patterns"
    NETWORK_BUILDER = "interconnect_disciplines"
    QUANTUM_LEAP = "breakthrough_discovery"


@dataclass
class Badge:
    """Badge visuel avec lore"""
    id: str
    name: str
    description: str
    icon: str  # emoji ou SVG
    color: str
    rarity: str  # common, rare, epic, legendary
    lore: str  # histoire du badge


class GamificationEngine:
    """
    Système de gamification qui rend chaque action
    pertinente et récompensée
    """
    
    def __init__(self):
        self.player_level = 1
        self.experience_points = 0
        self.achievements_unlocked: List[Badge] = []
        self.streak_count = 0
        self.daily_challenges: List[Dict] = []
        self.leaderboard_position = 1000
        self.badges_earned = {}
        self.quests_active: List[Dict] = []
        
        self._initialize_badges()
        self._generate_daily_quests()
    
    def _initialize_badges(self):
        """Initialise les badges spéciaux"""
        
        self.badges_library = {
            Achievement.FIRST_TASK: Badge(
                id="first_automation",
                name="🌟 Initié",
                description="Première automatisation réussie",
                icon="🤖",
                color="#FFD700",
                rarity="common",
                lore="Vous avez pris votre premier pas dans l'automatisation"
            ),
            Achievement.COGNITIVE_CONSENSUS: Badge(
                id="cognitive_consensus",
                name="🧠 Consensus Cognitif",
                description="Tous les nœuds ont convergé",
                icon="🎯",
                color="#FF6B9D",
                rarity="epic",
                lore="Vos domaines de pensée se sont alignés en harmonie parfaite"
            ),
            Achievement.EMERGENT_INSIGHT: Badge(
                id="emergent_insight",
                name="⚡ Insight Émergent",
                description="Vous avez découvert quelque chose d'imprévu",
                icon="💡",
                color="#00D9FF",
                rarity="legendary",
                lore="Une connexion jamais vue avant a émergé de votre réseau cognitif"
            ),
            Achievement.ZERO_FAILURE: Badge(
                id="perfect_execution",
                name="✨ Exécution Parfaite",
                description="10 tâches réussies consécutives",
                icon="👑",
                color="#FFB700",
                rarity="rare",
                lore="Vous avez maîtrisé l'art de l'exécution sans failles"
            ),
            Achievement.CREATIVE_SOLUTION: Badge(
                id="unexpected_solution",
                name="🎨 Créateur",
                description="Solution créative trouvée",
                icon="🎭",
                color="#FF69B4",
                rarity="epic",
                lore="Votre esprit créatif a forgé une solution unique"
            ),
            Achievement.PATTERN_MASTER: Badge(
                id="learn_100_patterns",
                name="📚 Maître des Patterns",
                description="100 patterns appris",
                icon="📖",
                color="#9D4EDD",
                rarity="legendary",
                lore="Vous maîtrisez maintenant une centaine de patterns automatisés"
            ),
            Achievement.NETWORK_BUILDER: Badge(
                id="interconnect_disciplines",
                name="🔗 Architecte Cognitif",
                description="Connecté toutes les disciplines",
                icon="🏗️",
                color="#3A86FF",
                rarity="legendary",
                lore="Vous avez créé une architecture cognitive complète"
            ),
            Achievement.QUANTUM_LEAP: Badge(
                id="breakthrough_discovery",
                name="🚀 Saut Quantique",
                description="Découverte révolutionnaire",
                icon="🌌",
                color="#06FFA5",
                rarity="legendary",
                lore="Vous avez découvert quelque chose qui change tout"
            )
        }
    
    def _generate_daily_quests(self):
        """Génère des quêtes quotidiennes"""
        
        quests = [
            {
                "id": "daily_automation",
                "name": "Automatiseur Quotidien",
                "description": "Complétez 5 automatisations",
                "reward_xp": 100,
                "progress": 0,
                "target": 5,
                "icon": "📋"
            },
            {
                "id": "cognitive_sync",
                "name": "Synchronisation Cognitive",
                "description": "Obtenir un consensus cognitif parfait",
                "reward_xp": 250,
                "progress": 0,
                "target": 1,
                "icon": "🧠"
            },
            {
                "id": "memory_explorer",
                "name": "Explorateur Mémoire",
                "description": "Consulter votre mémoire 10 fois",
                "reward_xp": 75,
                "progress": 0,
                "target": 10,
                "icon": "💾"
            },
            {
                "id": "creative_solution",
                "name": "Solution Créative",
                "description": "Trouver une solution inattendue",
                "reward_xp": 200,
                "progress": 0,
                "target": 1,
                "icon": "🎨"
            }
        ]
        
        self.daily_challenges = quests
    
    def add_experience(self, amount: int, source: str = "task") -> Dict[str, Any]:
        """
        Ajoute de l'expérience et gère la progression
        """
        
        old_level = self.player_level
        self.experience_points += amount
        
        # Vérifier les niveaux (100 XP par niveau)
        new_level = 1 + (self.experience_points // 100)
        
        level_up = new_level > old_level
        
        if level_up:
            self.player_level = new_level
            logger.info(f"🎉 Level UP! Vous êtes maintenant niveau {new_level}")
        
        # Vérifier les achievements
        unlocked = self._check_achievements()
        
        # Mettre à jour les quêtes
        self._update_quests(source, amount)
        
        return {
            "xp_gained": amount,
            "source": source,
            "new_total_xp": self.experience_points,
            "current_level": self.player_level,
            "level_up": level_up,
            "achievements_unlocked": unlocked,
            "progress_to_next_level": self.experience_points % 100
        }
    
    def _check_achievements(self) -> List[Badge]:
        """Vérifie les achievements débloqués"""
        
        unlocked = []
        
        # Ces vérifications seraient connectées au système réel
        if self.player_level == 1 and Achievement.FIRST_TASK not in self.badges_earned:
            badge = self.badges_library[Achievement.FIRST_TASK]
            self.badges_earned[Achievement.FIRST_TASK] = badge
            unlocked.append(badge)
        
        if self.streak_count >= 10 and Achievement.ZERO_FAILURE not in self.badges_earned:
            badge = self.badges_library[Achievement.ZERO_FAILURE]
            self.badges_earned[Achievement.ZERO_FAILURE] = badge
            unlocked.append(badge)
        
        return unlocked
    
    def _update_quests(self, action_type: str, value: int = 1):
        """Met à jour la progression des quêtes"""
        
        for quest in self.daily_challenges:
            if quest["id"] == "daily_automation" and action_type == "automation":
                quest["progress"] = min(quest["target"], quest["progress"] + 1)
            elif quest["id"] == "memory_explorer" and action_type == "memory_access":
                quest["progress"] = min(quest["target"], quest["progress"] + 1)
    
    def complete_quest(self, quest_id: str) -> Dict[str, Any]:
        """Complète une quête"""
        
        quest = next((q for q in self.daily_challenges if q["id"] == quest_id), None)
        
        if not quest:
            return {"status": "error", "message": "Quest not found"}
        
        if quest["progress"] < quest["target"]:
            return {"status": "error", "message": "Quest not completed"}
        
        reward = self.add_experience(quest["reward_xp"], f"quest_{quest_id}")
        
        # Retirer la quête
        self.daily_challenges.remove(quest)
        
        return {
            "status": "completed",
            "quest": quest["name"],
            "reward": reward,
            "new_quests": self._generate_daily_quests()
        }
    
    def get_player_profile(self) -> Dict[str, Any]:
        """Profil complet du joueur"""
        
        return {
            "level": self.player_level,
            "experience_points": self.experience_points,
            "streak": self.streak_count,
            "badges": list(self.badges_earned.values()),
            "leaderboard_position": self.leaderboard_position,
            "daily_challenges": self.daily_challenges,
            "active_quests": self.quests_active,
            "next_level_xp": (self.player_level) * 100
        }
    
    def get_achievement_progress(self) -> Dict[str, Any]:
        """Progression vers les achievements"""
        
        return {
            "total_achievements": len(self.badges_library),
            "unlocked": len(self.badges_earned),
            "progress_percent": (len(self.badges_earned) / len(self.badges_library)) * 100,
            "available": [
                badge for achievement, badge in self.badges_library.items()
                if achievement not in self.badges_earned
            ]
        }
