"""
Database Models pour MOT-X - Utilise SQLite avec SQLAlchemy
"""
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os
from pathlib import Path

# Configuration
DB_PATH = Path(__file__).resolve().parent.parent.parent / "motx_database.db"
DATABASE_URL = f"sqlite:///{DB_PATH}"

Base = declarative_base()
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class User(Base):
    """Modèle utilisateur"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)
    
    # Relations
    profile = relationship("UserProfile", back_populates="user", uselist=False)
    achievements = relationship("Achievement", back_populates="user")
    executions = relationship("ExecutionHistory", back_populates="user")
    cognitive_states = relationship("CognitiveState", back_populates="user")


class UserProfile(Base):
    """Profil joueur gamification"""
    __tablename__ = "user_profiles"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    level = Column(Integer, default=1)
    experience_points = Column(Integer, default=0)
    streak_count = Column(Integer, default=0)
    total_automations = Column(Integer, default=0)
    success_rate = Column(Float, default=0.0)
    total_time_saved_minutes = Column(Float, default=0.0)
    insights_generated = Column(Integer, default=0)
    last_updated = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="profile")


class Badge(Base):
    """Badge/Achievement"""
    __tablename__ = "badges"
    
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    description = Column(String)
    icon = Column(String)
    rarity = Column(String)  # common, rare, epic, legendary
    lore = Column(String)
    unlock_condition = Column(JSON)  # Condition pour débloquer
    
    user_achievements = relationship("Achievement", back_populates="badge")


class Achievement(Base):
    """Achievements débloqués par utilisateur"""
    __tablename__ = "achievements"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    badge_id = Column(Integer, ForeignKey("badges.id"))
    unlocked_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="achievements")
    badge = relationship("Badge", back_populates="user_achievements")


class DailyChallenge(Base):
    """Quêtes/Défis quotidiens"""
    __tablename__ = "daily_challenges"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    challenge_id = Column(String)
    name = Column(String)
    description = Column(String)
    reward_xp = Column(Integer)
    progress = Column(Integer, default=0)
    target = Column(Integer)
    completed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)


class ExecutionHistory(Base):
    """Historique des exécutions"""
    __tablename__ = "execution_history"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    instruction = Column(String)
    status = Column(String)  # success, error, blocked
    duration_seconds = Column(Float)
    tasks_executed = Column(Integer, default=0)
    tasks_failed = Column(Integer, default=0)
    tasks_blocked = Column(Integer, default=0)
    result_data = Column(JSON)
    executed_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="executions")


class CognitiveNode(Base):
    """État des nœuds cognitifs"""
    __tablename__ = "cognitive_nodes"
    
    id = Column(Integer, primary_key=True)
    node_id = Column(String, unique=True)
    specialty = Column(String)
    confidence = Column(Float, default=0.7)
    insight_count = Column(Integer, default=0)
    last_activated = Column(DateTime)


class CognitiveState(Base):
    """État cognitif actuel de l'utilisateur"""
    __tablename__ = "cognitive_states"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    consensus_score = Column(Float, default=0.0)
    emergent_insights = Column(Integer, default=0)
    dominant_style = Column(String)
    last_updated = Column(DateTime, default=datetime.utcnow)
    state_data = Column(JSON)
    
    user = relationship("User", back_populates="cognitive_states")


class AnalyticMetric(Base):
    """Métriques analytiques"""
    __tablename__ = "analytic_metrics"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    metric_name = Column(String)
    value = Column(Float)
    recorded_at = Column(DateTime, default=datetime.utcnow)
    metadata = Column(JSON)


# Créer les tables
def init_db():
    """Initialise la base de données"""
    Base.metadata.create_all(bind=engine)
    print(f"✅ Base de données initialisée: {DB_PATH}")


def get_db():
    """Obtenir une session DB"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


if __name__ == "__main__":
    init_db()
