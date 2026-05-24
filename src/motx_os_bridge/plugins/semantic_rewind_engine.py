import logging
import asyncio
from typing import Dict, List, Any
from datetime import datetime, timedelta
import os
import json

logger = logging.getLogger(__name__)

class SemanticRewindEngine:
    """
    MOT-X crée une Mémoire Épisodique complète persistante.
    Chercher par association d'idées, pas par chemins de fichiers.
    """
    
    def __init__(self):
        # Initialiser le client persistant ChromaDB
        db_path = os.path.expanduser("~/.motx/chroma_db")
        os.makedirs(db_path, exist_ok=True)
        try:
            import chromadb
            self.chroma_client = chromadb.PersistentClient(path=db_path)
            self.collection = self.chroma_client.get_or_create_collection(
                name="episodic_memory_v2",
                metadata={"hnsw:space": "cosine"}
            )
        except Exception as e:
            self.chroma_client = None
            self.collection = None
            logger.warning(f"⚠️ ChromaDB initialization failed for SemanticRewindEngine: {e}")

        # Charger le modèle d'embedding réel (all-MiniLM-L6-v2)
        self.model = None
        try:
            logger.info("🧠 Loading sentence-transformers model (all-MiniLM-L6-v2)...")
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
            logger.info("🧠 Model loaded successfully!")
        except Exception as e:
            self.model = None
            logger.warning(f"⚠️ SentenceTransformer failed to load for SemanticRewindEngine: {e}")
        self.contextual_metadata = {}
    
    @property
    def episodic_memory(self) -> List[str]:
        try:
            return self.collection.get()["ids"]
        except Exception:
            return []
    
    async def record_episode(self, episode_data: Dict) -> Dict:
        episode_id = f"episode_{datetime.now().timestamp()}"
        timestamp = datetime.now().isoformat()
        
        content = {
            "screen_state": episode_data.get("screen"),
            "active_app": episode_data.get("app"),
            "ocr_text": episode_data.get("text"),
            "open_files": episode_data.get("files"),
            "applications": episode_data.get("apps")
        }
        
        context = {
            "weather": await self._get_weather(),
            "time_of_day": self._get_time_of_day(),
            "user_mood": episode_data.get("mood", "neutral"),
            "music_playing": episode_data.get("music"),
            "external_events": episode_data.get("events", [])
        }
        
        vector_embedding = await self._vectorize_episode(episode_data)
        
        episode_doc = json.dumps({
            "id": episode_id,
            "timestamp": timestamp,
            "content": content,
            "context": context
        })
        
        metadata = {
            "timestamp": timestamp,
            "active_app": content["active_app"] or "unknown",
            "user_mood": context["user_mood"]
        }
        
        self.collection.add(
            ids=[episode_id],
            embeddings=[vector_embedding],
            documents=[episode_doc],
            metadatas=[metadata]
        )
        
        logger.debug(f"📝 Episode enregistré: {episode_id}")
        return {"status": "recorded", "episode_id": episode_id}
    
    async def semantic_search(self, query: str) -> List[Dict]:
        logger.info(f"🔍 Semantic search: '{query}'")
        try:
            query_vector = await self._vectorize_query(query)
            
            query_results = self.collection.query(
                query_embeddings=[query_vector],
                n_results=5
            )
            
            results = []
            if query_results and "ids" in query_results and len(query_results["ids"]) > 0:
                ids = query_results["ids"][0]
                distances = query_results["distances"][0] if "distances" in query_results and query_results["distances"] else [0.0] * len(ids)
                documents = query_results["documents"][0] if "documents" in query_results and query_results["documents"] else ["{}"] * len(ids)
                
                for i in range(len(ids)):
                    distance = distances[i]
                    # En espace cosinus: distance = 1 - cosine_similarity
                    # Donc similarity = 1.0 - distance (bornée entre 0 et 1)
                    similarity = 1.0 - distance
                    if similarity < 0.0:
                        similarity = 0.0
                    
                    try:
                        episode_data = json.loads(documents[i])
                        results.append({
                            "episode_id": ids[i],
                            "timestamp": episode_data.get("timestamp"),
                            "similarity_score": round(similarity, 2),
                            "content_preview": episode_data.get("content"),
                            "context": episode_data.get("context"),
                            "can_recover": True
                        })
                    except Exception as e:
                        logger.error(f"Error parsing episode document: {e}")
                        
            return results
        except Exception as e:
            logger.error(f"Semantic search error: {str(e)}")
            return []
    
    async def recover_episode(self, episode_id: str) -> Dict:
        try:
            query_res = self.collection.get(ids=[episode_id])
            if not query_res or not query_res["ids"]:
                return {"status": "error", "message": "Episode not found"}
            
            episode = json.loads(query_res["documents"][0])
            
            return {
                "status": "success",
                "episode": episode,
                "recovery_actions": await self._generate_recovery_actions(episode),
                "message": f"🔄 Je peux restaurer l'état d'il y a {self._time_ago(episode['timestamp'])}"
            }
        except Exception as e:
            logger.error(f"Recover episode error: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    async def _vectorize_episode(self, episode: Dict) -> List[float]:
        # Formater l'épisode sous forme de texte descriptif pour de meilleures performances sémantiques
        parts = []
        if episode.get("app"):
            parts.append(f"Application active: {episode['app']}.")
        if episode.get("text"):
            parts.append(f"Texte affiché à l'écran: {episode['text']}.")
        if episode.get("files"):
            files_str = ", ".join(episode["files"])
            parts.append(f"Fichiers ouverts: {files_str}.")
        if episode.get("mood"):
            parts.append(f"État ou humeur détectée de l'utilisateur: {episode['mood']}.")
        
        text = " ".join(parts)
        if not text.strip():
            text = "Épisode d'activité MOT-X OS"
            
        return self.model.encode(text).tolist()
    
    async def _vectorize_query(self, query: str) -> List[float]:
        if not query.strip():
            return [0.0] * 384
        return self.model.encode(query).tolist()
    
    async def _get_weather(self) -> str: return "Rainy"
    
    def _get_time_of_day(self) -> str:
        hour = datetime.now().hour
        if hour < 12: return "Morning"
        elif hour < 17: return "Afternoon"
        else: return "Evening"
    
    async def _generate_recovery_actions(self, episode: Dict) -> List[str]:
        actions = []
        content = episode.get("content", {})
        if content.get("active_app"):
            actions.append(f"Ouvrir {content['active_app']}")
        if content.get("open_files"):
            for file in content["open_files"]:
                actions.append(f"Restaurer {file}")
        return actions
    
    def _time_ago(self, timestamp: str) -> str:
        try:
            episode_time = datetime.fromisoformat(timestamp)
            diff = datetime.now() - episode_time
            if diff < timedelta(hours=1): return f"{int(diff.total_seconds()/60)} minutes"
            elif diff < timedelta(days=1): return f"{int(diff.total_seconds()/3600)} heures"
            else: return f"{int(diff.total_seconds()/86400)} jours"
        except Exception:
            return "quelques instants"
