"""
Life Graph - Carte automatique projets, personnes, tâches, documents, réunions
Vision globale instantanée.
"""

from typing import Dict, List, Any, Set
from datetime import datetime
import json
from pathlib import Path
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)


class LifeGraph:
    """
    Crée automatiquement une carte connectée de tous les éléments de la vie numérique
    """
    
    def __init__(self):
        self.projects = {}
        self.people = {}
        self.tasks = {}
        self.documents = {}
        self.meetings = {}
        self.connections = defaultdict(set)
        self.data_path = Path(__file__).parent.parent.parent / "config" / "life_graph_data.json"
        self._load_data()
    
    def _load_data(self):
        """Charge les données du Life Graph"""
        try:
            if self.data_path.exists():
                with open(self.data_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.projects = data.get("projects", {})
                    self.people = data.get("people", {})
                    self.tasks = data.get("tasks", {})
                    self.documents = data.get("documents", {})
                    self.meetings = data.get("meetings", {})
                    self.connections = defaultdict(set, {k: set(v) for k, v in data.get("connections", {}).items()})
        except Exception as e:
            logger.warning(f"Erreur chargement données Life Graph: {e}")
    
    def _save_data(self):
        """Sauvegarde les données du Life Graph"""
        try:
            self.data_path.parent.mkdir(parents=True, exist_ok=True)
            data = {
                "projects": self.projects,
                "people": self.people,
                "tasks": self.tasks,
                "documents": self.documents,
                "meetings": self.meetings,
                "connections": {k: list(v) for k, v in self.connections.items()}
            }
            with open(self.data_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.warning(f"Erreur sauvegarde données Life Graph: {e}")
    
    def add_project(self, project_id: str, name: str, metadata: Dict[str, Any] = None):
        """Ajoute un projet au graphe"""
        self.projects[project_id] = {
            "name": name,
            "metadata": metadata or {},
            "created_at": datetime.now().isoformat(),
            "last_accessed": datetime.now().isoformat()
        }
        self._save_data()
    
    def add_person(self, person_id: str, name: str, metadata: Dict[str, Any] = None):
        """Ajoute une personne au graphe"""
        self.people[person_id] = {
            "name": name,
            "metadata": metadata or {},
            "created_at": datetime.now().isoformat(),
            "last_contact": datetime.now().isoformat()
        }
        self._save_data()
    
    def add_task(self, task_id: str, title: str, project_id: str = None, metadata: Dict[str, Any] = None):
        """Ajoute une tâche au graphe"""
        self.tasks[task_id] = {
            "title": title,
            "project_id": project_id,
            "metadata": metadata or {},
            "created_at": datetime.now().isoformat(),
            "status": "pending"
        }
        
        # Créer la connexion avec le projet
        if project_id:
            self.connections[task_id].add(project_id)
            self.connections[project_id].add(task_id)
        
        self._save_data()
    
    def add_document(self, doc_id: str, path: str, project_id: str = None, metadata: Dict[str, Any] = None):
        """Ajoute un document au graphe"""
        self.documents[doc_id] = {
            "path": path,
            "project_id": project_id,
            "metadata": metadata or {},
            "created_at": datetime.now().isoformat(),
            "last_accessed": datetime.now().isoformat()
        }
        
        # Créer la connexion avec le projet
        if project_id:
            self.connections[doc_id].add(project_id)
            self.connections[project_id].add(doc_id)
        
        self._save_data()
    
    def add_meeting(self, meeting_id: str, title: str, participants: List[str], project_id: str = None, metadata: Dict[str, Any] = None):
        """Ajoute une réunion au graphe"""
        self.meetings[meeting_id] = {
            "title": title,
            "participants": participants,
            "project_id": project_id,
            "metadata": metadata or {},
            "created_at": datetime.now().isoformat()
        }
        
        # Créer les connexions avec les participants
        for person_id in participants:
            self.connections[meeting_id].add(person_id)
            self.connections[person_id].add(meeting_id)
        
        # Créer la connexion avec le projet
        if project_id:
            self.connections[meeting_id].add(project_id)
            self.connections[project_id].add(meeting_id)
        
        self._save_data()
    
    def connect_elements(self, element_id_1: str, element_id_2: str, connection_type: str = "related"):
        """Connecte deux éléments du graphe"""
        self.connections[element_id_1].add(element_id_2)
        self.connections[element_id_2].add(element_id_1)
        self._save_data()
    
    def get_project_context(self, project_id: str) -> Dict[str, Any]:
        """Retourne le contexte complet d'un projet"""
        if project_id not in self.projects:
            return {"error": "Project not found"}
        
        # Récupérer tous les éléments connectés au projet
        connected_elements = self.connections.get(project_id, set())
        
        context = {
            "project": self.projects[project_id],
            "tasks": [],
            "documents": [],
            "meetings": [],
            "people": []
        }
        
        for element_id in connected_elements:
            if element_id in self.tasks:
                context["tasks"].append(self.tasks[element_id])
            elif element_id in self.documents:
                context["documents"].append(self.documents[element_id])
            elif element_id in self.meetings:
                context["meetings"].append(self.meetings[element_id])
            elif element_id in self.people:
                context["people"].append(self.people[element_id])
        
        return context
    
    def get_person_context(self, person_id: str) -> Dict[str, Any]:
        """Retourne le contexte complet d'une personne"""
        if person_id not in self.people:
            return {"error": "Person not found"}
        
        # Récupérer tous les éléments connectés à la personne
        connected_elements = self.connections.get(person_id, set())
        
        context = {
            "person": self.people[person_id],
            "projects": [],
            "meetings": [],
            "tasks": []
        }
        
        for element_id in connected_elements:
            if element_id in self.projects:
                context["projects"].append(self.projects[element_id])
            elif element_id in self.meetings:
                context["meetings"].append(self.meetings[element_id])
            elif element_id in self.tasks:
                context["tasks"].append(self.tasks[element_id])
        
        return context
    
    def get_global_overview(self) -> Dict[str, Any]:
        """Retourne une vue globale du graphe"""
        return {
            "projects_count": len(self.projects),
            "people_count": len(self.people),
            "tasks_count": len(self.tasks),
            "documents_count": len(self.documents),
            "meetings_count": len(self.meetings),
            "connections_count": sum(len(v) for v in self.connections.values()) // 2,  # Divisé par 2 car les connexions sont bidirectionnelles
            "projects": list(self.projects.values()),
            "recent_activity": self._get_recent_activity()
        }
    
    def _get_recent_activity(self) -> List[Dict[str, Any]]:
        """Retourne l'activité récente"""
        activities = []
        
        # Ajouter les projets récents
        for project_id, project in self.projects.items():
            activities.append({
                "type": "project",
                "id": project_id,
                "name": project["name"],
                "timestamp": project["created_at"]
            })
        
        # Ajouter les tâches récentes
        for task_id, task in self.tasks.items():
            activities.append({
                "type": "task",
                "id": task_id,
                "title": task["title"],
                "timestamp": task["created_at"]
            })
        
        # Trier par timestamp et retourner les 10 plus récents
        activities.sort(key=lambda x: x["timestamp"], reverse=True)
        return activities[:10]
