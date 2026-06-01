"""
Infinite Memory - Mémorisation documents, réunions, web, conversations
Recherche par sens et non par nom.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import json
from pathlib import Path
import logging
from collections import defaultdict
import hashlib

logger = logging.getLogger(__name__)


class InfiniteMemory:
    """
    Mémoire épisodique qui mémorise tout et permet la recherche par sens
    """
    
    def __init__(self):
        self.documents = {}
        self.meetings = {}
        self.web_pages = {}
        self.conversations = {}
        self.images = {}
        self.semantic_index = defaultdict(list)
        self.data_path = Path(__file__).parent.parent.parent / "config" / "infinite_memory_data.json"
        self._load_data()
    
    def _load_data(self):
        """Charge les données de mémoire"""
        try:
            if self.data_path.exists():
                with open(self.data_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.documents = data.get("documents", {})
                    self.meetings = data.get("meetings", {})
                    self.web_pages = data.get("web_pages", {})
                    self.conversations = data.get("conversations", {})
                    self.images = data.get("images", {})
                    self.semantic_index = defaultdict(list, data.get("semantic_index", {}))
        except Exception as e:
            logger.warning(f"Erreur chargement données Infinite Memory: {e}")
    
    def _save_data(self):
        """Sauvegarde les données de mémoire"""
        try:
            self.data_path.parent.mkdir(parents=True, exist_ok=True)
            data = {
                "documents": self.documents,
                "meetings": self.meetings,
                "web_pages": self.web_pages,
                "conversations": self.conversations,
                "images": self.images,
                "semantic_index": dict(self.semantic_index)
            }
            with open(self.data_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.warning(f"Erreur sauvegarde données Infinite Memory: {e}")
    
    def _generate_id(self, content: str) -> str:
        """Génère un ID unique basé sur le contenu"""
        return hashlib.md5(content.encode()).hexdigest()[:16]
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extrait les mots-clés pour l'indexation sémantique"""
        # Simplification: extraction basique de mots
        words = text.lower().split()
        # Filtrer les mots courts et les articles
        keywords = [w for w in words if len(w) > 3]
        return keywords[:10]  # Limiter à 10 mots-clés
    
    def store_document(self, path: str, content: str, metadata: Dict[str, Any] = None):
        """
        Mémorise un document
        """
        doc_id = self._generate_id(content)
        self.documents[doc_id] = {
            "path": path,
            "content": content,
            "metadata": metadata or {},
            "stored_at": datetime.now().isoformat(),
            "access_count": 0
        }
        
        # Indexer sémantiquement
        keywords = self._extract_keywords(content)
        for keyword in keywords:
            self.semantic_index[keyword].append(("document", doc_id))
        
        self._save_data()
        return doc_id
    
    def store_meeting(self, title: str, content: str, metadata: Dict[str, Any] = None):
        """
        Mémorise une réunion
        """
        meeting_id = self._generate_id(content)
        self.meetings[meeting_id] = {
            "title": title,
            "content": content,
            "metadata": metadata or {},
            "stored_at": datetime.now().isoformat(),
            "access_count": 0
        }
        
        # Indexer sémantiquement
        keywords = self._extract_keywords(content)
        for keyword in keywords:
            self.semantic_index[keyword].append(("meeting", meeting_id))
        
        self._save_data()
        return meeting_id
    
    def store_web_page(self, url: str, content: str, metadata: Dict[str, Any] = None):
        """
        Mémorise une page web
        """
        page_id = self._generate_id(content)
        self.web_pages[page_id] = {
            "url": url,
            "content": content,
            "metadata": metadata or {},
            "stored_at": datetime.now().isoformat(),
            "access_count": 0
        }
        
        # Indexer sémantiquement
        keywords = self._extract_keywords(content)
        for keyword in keywords:
            self.semantic_index[keyword].append(("web", page_id))
        
        self._save_data()
        return page_id
    
    def store_conversation(self, participants: List[str], content: str, metadata: Dict[str, Any] = None):
        """
        Mémorise une conversation
        """
        conv_id = self._generate_id(content)
        self.conversations[conv_id] = {
            "participants": participants,
            "content": content,
            "metadata": metadata or {},
            "stored_at": datetime.now().isoformat(),
            "access_count": 0
        }
        
        # Indexer sémantiquement
        keywords = self._extract_keywords(content)
        for keyword in keywords:
            self.semantic_index[keyword].append(("conversation", conv_id))
        
        self._save_data()
        return conv_id
    
    def store_image(self, path: str, description: str, metadata: Dict[str, Any] = None):
        """
        Mémorise une image avec sa description
        """
        img_id = self._generate_id(description)
        self.images[img_id] = {
            "path": path,
            "description": description,
            "metadata": metadata or {},
            "stored_at": datetime.now().isoformat(),
            "access_count": 0
        }
        
        # Indexer sémantiquement
        keywords = self._extract_keywords(description)
        for keyword in keywords:
            self.semantic_index[keyword].append(("image", img_id))
        
        self._save_data()
        return img_id
    
    def search_by_sense(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Recherche par sens (mots-clés)
        """
        keywords = self._extract_keywords(query)
        results = []
        
        for keyword in keywords:
            if keyword in self.semantic_index:
                for item_type, item_id in self.semantic_index[keyword]:
                    if item_type == "document" and item_id in self.documents:
                        doc = self.documents[item_id]
                        doc["access_count"] += 1
                        results.append({
                            "type": "document",
                            "id": item_id,
                            "path": doc["path"],
                            "relevance": 1.0,
                            "snippet": doc["content"][:200] + "..."
                        })
                    elif item_type == "meeting" and item_id in self.meetings:
                        meeting = self.meetings[item_id]
                        meeting["access_count"] += 1
                        results.append({
                            "type": "meeting",
                            "id": item_id,
                            "title": meeting["title"],
                            "relevance": 1.0,
                            "snippet": meeting["content"][:200] + "..."
                        })
                    elif item_type == "web" and item_id in self.web_pages:
                        page = self.web_pages[item_id]
                        page["access_count"] += 1
                        results.append({
                            "type": "web",
                            "id": item_id,
                            "url": page["url"],
                            "relevance": 1.0,
                            "snippet": page["content"][:200] + "..."
                        })
                    elif item_type == "conversation" and item_id in self.conversations:
                        conv = self.conversations[item_id]
                        conv["access_count"] += 1
                        results.append({
                            "type": "conversation",
                            "id": item_id,
                            "participants": conv["participants"],
                            "relevance": 1.0,
                            "snippet": conv["content"][:200] + "..."
                        })
                    elif item_type == "image" and item_id in self.images:
                        img = self.images[item_id]
                        img["access_count"] += 1
                        results.append({
                            "type": "image",
                            "id": item_id,
                            "path": img["path"],
                            "relevance": 1.0,
                            "description": img["description"]
                        })
        
        # Dédupliquer et trier
        unique_results = {}
        for result in results:
            key = f"{result['type']}_{result['id']}"
            if key not in unique_results:
                unique_results[key] = result
        
        return list(unique_results.values())[:limit]
    
    def get_memory_summary(self) -> Dict[str, Any]:
        """
        Retourne un résumé de la mémoire
        """
        return {
            "documents_stored": len(self.documents),
            "meetings_stored": len(self.meetings),
            "web_pages_stored": len(self.web_pages),
            "conversations_stored": len(self.conversations),
            "images_stored": len(self.images),
            "semantic_index_size": len(self.semantic_index),
            "total_items": len(self.documents) + len(self.meetings) + len(self.web_pages) + len(self.conversations) + len(self.images)
        }
