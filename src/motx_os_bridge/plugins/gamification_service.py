"""
Gamification Service avec Persistance SQLite
"""
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Dict, List, Any
import logging

from ..utils.database import SessionLocal, User, UserProfile, Badge, Achievement, DailyChallenge, ExecutionHistory
from .gamification_engine import GamificationEngine

logger = logging.getLogger(__name__)


class GamificationService:
    """Service de gamification avec persistance DB"""
    
    def __init__(self):
        self.db = SessionLocal()
        self.engine = GamificationEngine()
    
    def get_or_create_user(self, username: str, email: str = None) -> User:
        """Obtient ou crée un utilisateur"""
        user = self.db.query(User).filter(User.username == username).first()
        
        if not user:
            user = User(username=username, email=email)
            self.db.add(user)
            
            # Créer le profil
            profile = UserProfile(user=user)
            self.db.add(profile)
            
            self.db.commit()
            logger.info(f"✅ Nouvel utilisateur créé: {username}")
        
        return user
    
    def get_user_profile(self, user_id: int) -> Dict[str, Any]:
        """Récupère le profil complet de l'utilisateur"""
        profile = self.db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
        
        if not profile:
            return None
        
        achievements = self.db.query(Achievement).filter(Achievement.user_id == user_id).all()
        challenges = self.db.query(DailyChallenge).filter(
            DailyChallenge.user_id == user_id,
            DailyChallenge.completed == False
        ).all()
        
        return {
            "level": profile.level,
            "experience_points": profile.experience_points,
            "streak": profile.streak_count,
            "total_automations": profile.total_automations,
            "success_rate": profile.success_rate,
            "time_saved_minutes": profile.total_time_saved_minutes,
            "insights": profile.insights_generated,
            "badges": [
                {
                    "id": ach.badge.id,
                    "name": ach.badge.name,
                    "icon": ach.badge.icon,
                    "rarity": ach.badge.rarity,
                    "unlocked_at": ach.unlocked_at.isoformat()
                }
                for ach in achievements
            ],
            "daily_challenges": [
                {
                    "id": ch.challenge_id,
                    "name": ch.name,
                    "progress": ch.progress,
                    "target": ch.target,
                    "completed": ch.completed,
                    "reward_xp": ch.reward_xp
                }
                for ch in challenges
            ]
        }
    
    def add_experience(self, user_id: int, amount: int, source: str = "automation") -> Dict[str, Any]:
        """Ajoute de l'expérience et gère la progression"""
        profile = self.db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
        
        if not profile:
            return {"error": "User not found"}
        
        old_level = profile.level
        profile.experience_points += amount
        
        # Vérifier les niveaux (100 XP par niveau)
        new_level = 1 + (profile.experience_points // 100)
        level_up = new_level > old_level
        
        if level_up:
            profile.level = new_level
            logger.info(f"🎉 Level UP! Utilisateur {user_id} est au niveau {new_level}")
        
        profile.last_updated = datetime.utcnow()
        self.db.commit()
        
        # Vérifier les achievements
        unlocked = self._check_achievements(user_id, profile)
        
        return {
            "xp_gained": amount,
            "source": source,
            "new_total_xp": profile.experience_points,
            "current_level": profile.level,
            "level_up": level_up,
            "achievements_unlocked": unlocked,
            "progress_to_next_level": profile.experience_points % 100
        }
    
    def record_execution(self, user_id: int, instruction: str, result: Dict[str, Any]) -> None:
        """Enregistre une exécution"""
        execution = ExecutionHistory(
            user_id=user_id,
            instruction=instruction,
            status=result.get("status", "unknown"),
            duration_seconds=result.get("duration", 0),
            tasks_executed=len(result.get("results", [])),
            tasks_failed=result.get("failed_count", 0),
            tasks_blocked=result.get("blocked_count", 0),
            result_data=result
        )
        
        self.db.add(execution)
        
        # Mettre à jour le profil
        profile = self.db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
        if profile:
            profile.total_automations += 1
            
            # Calculer le taux de succès
            success_count = len(result.get("results", []))
            if success_count > 0:
                success_rate = success_count / len(result.get("results", []))
                profile.success_rate = (profile.success_rate + success_rate) / 2
            
            # Ajouter du temps sauvegardé (estimation)
            profile.total_time_saved_minutes += len(result.get("results", [])) * 0.5
        
        self.db.commit()
    
    def complete_challenge(self, user_id: int, challenge_id: str) -> Dict[str, Any]:
        """Complète une quête"""
        challenge = self.db.query(DailyChallenge).filter(
            DailyChallenge.user_id == user_id,
            DailyChallenge.challenge_id == challenge_id
        ).first()
        
        if not challenge:
            return {"status": "error", "message": "Challenge not found"}
        
        if challenge.progress < challenge.target:
            return {"status": "error", "message": "Challenge not completed"}
        
        challenge.completed = True
        challenge.completed_at = datetime.utcnow()
        
        # Ajouter l'XP
        reward = self.add_experience(user_id, challenge.reward_xp, f"challenge_{challenge_id}")
        
        self.db.commit()
        
        return {
            "status": "completed",
            "challenge": challenge.name,
            "reward": reward
        }
    
    def _check_achievements(self, user_id: int, profile: UserProfile) -> List[Dict]:
        """Vérifie les achievements débloqués"""
        unlocked = []
        
        # Achievements standards
        achievements_to_check = [
            ("first_automation", "1 automation", lambda: profile.total_automations >= 1),
            ("perfect_execution", "10 success streak", lambda: profile.streak_count >= 10),
            ("level_10", "Reach level 10", lambda: profile.level >= 10),
            ("100_automations", "100 automations", lambda: profile.total_automations >= 100),
            ("99_percent_success", "99% success rate", lambda: profile.success_rate >= 0.99),
        ]
        
        for badge_name, desc, condition in achievements_to_check:
            if condition():
                # Vérifier si pas déjà débloqué
                existing = self.db.query(Achievement).filter(
                    Achievement.user_id == user_id,
                    Achievement.badge.has(Badge.name == badge_name)
                ).first()
                
                if not existing:
                    badge = self.db.query(Badge).filter(Badge.name == badge_name).first()
                    if badge:
                        achievement = Achievement(user_id=user_id, badge_id=badge.id)
                        self.db.add(achievement)
                        self.db.commit()
                        
                        unlocked.append({
                            "name": badge.name,
                            "icon": badge.icon,
                            "rarity": badge.rarity
                        })
        
        return unlocked
    
    def get_leaderboard(self, limit: int = 10) -> List[Dict]:
        """Obtient le leaderboard"""
        profiles = self.db.query(UserProfile).order_by(
            UserProfile.level.desc(),
            UserProfile.experience_points.desc()
        ).limit(limit).all()
        
        leaderboard = []
        for i, profile in enumerate(profiles):
            user = self.db.query(User).filter(User.id == profile.user_id).first()
            leaderboard.append({
                "rank": i + 1,
                "username": user.username if user else "Unknown",
                "level": profile.level,
                "xp": profile.experience_points,
                "automations": profile.total_automations,
                "success_rate": profile.success_rate
            })
        
        return leaderboard
    
    def update_cognitive_state(self, user_id: int, state_data: Dict[str, Any]) -> None:
        """Met à jour l'état cognitif"""
        from ..utils.database import CognitiveState
        
        cog_state = self.db.query(CognitiveState).filter(CognitiveState.user_id == user_id).first()
        
        if not cog_state:
            cog_state = CognitiveState(user_id=user_id)
            self.db.add(cog_state)
        
        cog_state.consensus_score = state_data.get("consensus_score", 0)
        cog_state.emergent_insights = state_data.get("emergent_insights", 0)
        cog_state.dominant_style = state_data.get("dominant_style", "balanced")
        cog_state.state_data = state_data
        cog_state.last_updated = datetime.utcnow()
        
        self.db.commit()


# Singleton
_gamification_service = None


def get_gamification_service() -> GamificationService:
    """Obtient l'instance du service de gamification"""
    global _gamification_service
    if _gamification_service is None:
        _gamification_service = GamificationService()
    return _gamification_service
