"""
Multi-User Collaboration - Permet à plusieurs utilisateurs de travailler ensemble.
"""

from typing import Dict, List, Any
from datetime import datetime
import asyncio
import logging

logger = logging.getLogger(__name__)


class CollaborationEngine:
    """
    Permet à plusieurs utilisateurs de travailler ensemble
    sur des automatisations et de partager les insights
    """
    
    def __init__(self):
        self.active_users: Dict[str, Dict] = {}
        self.shared_workflows: List[Dict] = []
        self.collaboration_sessions: List[Dict] = []
        self.idea_board: List[Dict] = []
    
    async def create_collaboration_session(
        self, 
        initiator_id: str,
        invited_users: List[str],
        theme: str
    ) -> Dict[str, Any]:
        """Crée une session collaborative"""
        
        session_id = f"collab_{datetime.now().timestamp()}"
        
        session = {
            "id": session_id,
            "initiator": initiator_id,
            "participants": [initiator_id] + invited_users,
            "theme": theme,
            "created_at": datetime.now().isoformat(),
            "shared_automations": [],
            "insights_board": [],
            "votes": {},
            "real_time_activity": []
        }
        
        self.collaboration_sessions.append(session)
        
        logger.info(f"🤝 Session collaborative créée: {session_id}")
        
        return session
    
    async def propose_shared_automation(
        self,
        session_id: str,
        proposer_id: str,
        automation_plan: Dict,
        description: str
    ) -> Dict[str, Any]:
        """Propose une automatisation à partager"""
        
        proposal = {
            "id": f"proposal_{datetime.now().timestamp()}",
            "session_id": session_id,
            "proposer": proposer_id,
            "plan": automation_plan,
            "description": description,
            "votes": {},
            "comments": [],
            "status": "pending",
            "created_at": datetime.now().isoformat()
        }
        
        session = next(
            (s for s in self.collaboration_sessions if s["id"] == session_id),
            None
        )
        
        if session:
            session["shared_automations"].append(proposal)
        
        return proposal
    
    async def vote_on_automation(
        self,
        session_id: str,
        automation_id: str,
        voter_id: str,
        vote: bool
    ) -> Dict[str, Any]:
        """Vote sur une automatisation partagée"""
        
        session = next(
            (s for s in self.collaboration_sessions if s["id"] == session_id),
            None
        )
        
        if not session:
            return {"status": "error", "message": "Session not found"}
        
        automation = next(
            (a for a in session["shared_automations"] 
             if a["id"] == automation_id),
            None
        )
        
        if not automation:
            return {"status": "error", "message": "Automation not found"}
        
        automation["votes"][voter_id] = vote
        
        total_votes = len(automation["votes"])
        positive_votes = sum(1 for v in automation["votes"].values() if v)
        approval_rate = positive_votes / total_votes if total_votes > 0 else 0
        
        # Approuver si > 70% de votes positifs
        if approval_rate > 0.7:
            automation["status"] = "approved"
        
        return {
            "status": "success",
            "automation_id": automation_id,
            "approval_rate": approval_rate,
            "automation_status": automation["status"]
        }
    
    async def share_insight(
        self,
        session_id: str,
        user_id: str,
        insight: str,
        type: str = "discovery"
    ) -> Dict[str, Any]:
        """Partage un insight avec le groupe"""
        
        insight_record = {
            "id": f"insight_{datetime.now().timestamp()}",
            "session_id": session_id,
            "author": user_id,
            "content": insight,
            "type": type,  # discovery, pattern, improvement
            "reactions": {},
            "created_at": datetime.now().isoformat()
        }
        
        session = next(
            (s for s in self.collaboration_sessions if s["id"] == session_id),
            None
        )
        
        if session:
            session["insights_board"].append(insight_record)
        
        logger.info(f"💡 Insight partagé par {user_id}")
        
        return insight_record
    
    async def get_collaboration_leaderboard(self) -> Dict[str, Any]:
        """Leaderboard des collaborateurs"""
        
        user_contributions = {}
        
        for session in self.collaboration_sessions:
            for automation in session["shared_automations"]:
                proposer = automation["proposer"]
                if proposer not in user_contributions:
                    user_contributions[proposer] = {
                        "proposals": 0,
                        "approvals": 0,
                        "insights": 0
                    }
                user_contributions[proposer]["proposals"] += 1
                
                if automation["status"] == "approved":
                    user_contributions[proposer]["approvals"] += 1
            
            for insight in session["insights_board"]:
                author = insight["author"]
                if author not in user_contributions:
                    user_contributions[author] = {
                        "proposals": 0,
                        "approvals": 0,
                        "insights": 0
                    }
                user_contributions[author]["insights"] += 1
        
        leaderboard = sorted(
            user_contributions.items(),
            key=lambda x: x[1]["approvals"] * 2 + x[1]["insights"],
            reverse=True
        )
        
        return {
            "leaderboard": [
                {
                    "rank": i + 1,
                    "user": user,
                    "score": stats["approvals"] * 2 + stats["insights"],
                    "proposals": stats["proposals"],
                    "approvals": stats["approvals"],
                    "insights": stats["insights"]
                }
                for i, (user, stats) in enumerate(leaderboard[:10])
            ]
        }
