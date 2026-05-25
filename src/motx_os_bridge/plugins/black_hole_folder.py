import logging
import asyncio
from typing import Dict, List, Any
from datetime import datetime
import os

logger = logging.getLogger(__name__)

class BlackHoleFolder:
    """
    Le dossier où l'utilisateur jette tout sans classer.
    MOT-X ingère, vectorise sémantiquement dans ChromaDB, et supprime l'original.
    """
    
    def __init__(self):
        self.nexus_path = os.path.expanduser("~/MOT-X_Nexus")
        os.makedirs(self.nexus_path, exist_ok=True)
        
        # Initialiser le client persistant ChromaDB
        db_path = os.path.expanduser("~/.motx/chroma_db")
        os.makedirs(db_path, exist_ok=True)
        self.chroma_available = False
        self.chroma_error = None
        self.chroma_client = None
        self.collection = None
        try:
            import chromadb
            self.chroma_client = chromadb.PersistentClient(path=db_path)
            self.collection = self.chroma_client.get_or_create_collection(
                name="black_hole_files_v2",
                metadata={"hnsw:space": "cosine"}
            )
            self.chroma_available = True
        except Exception as e:
            self.chroma_error = str(e)
            logger.warning(f"⚠️ ChromaDB initialization failed for BlackHoleFolder: {self.chroma_error}")

        # Charger le modèle d'embedding réel (all-MiniLM-L6-v2)
        self.model = None
        try:
            logger.info("🧠 Loading sentence-transformers model (all-MiniLM-L6-v2)...")
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
            logger.info("🧠 Model loaded successfully!")
        except Exception as e:
            self.model = None
            logger.warning(f"⚠️ SentenceTransformer failed to load for BlackHoleFolder: {e}")

        self.rejected_files = [] # Historique RAM des fichiers rejetés par sécurité
        self.watching_enabled = False
        self.recovery_count = 0
        
    @property
    def ingested_files(self) -> List[str]:
        try:
            return self.collection.get()["ids"]
        except Exception:
            return []
    
    async def watch_nexus_folder(self) -> None:
        logger.info("👁️ Black Hole Folder watching started...")
        self.watching_enabled = True
        existing_files = set(os.listdir(self.nexus_path)) if os.path.exists(self.nexus_path) else set()
        
        while self.watching_enabled:
            try:
                current_files = set(os.listdir(self.nexus_path))
                new_files = current_files - existing_files
                
                for filename in new_files:
                    if filename.startswith('.'):
                        continue
                    
                    file_path = os.path.join(self.nexus_path, filename)
                    logger.info(f"🌀 New file detected: {filename}")
                    
                    # Vérification de sécurité strict (Safeguards)
                    is_safe, reason = self._is_safe_file(file_path)
                    if not is_safe:
                        logger.warning(f"⚠️ [BLACK HOLE SAFEGUARD] Rejet du fichier '{filename}' : {reason}")
                        self.rejected_files.append({
                            "filename": filename,
                            "timestamp": datetime.now().isoformat(),
                            "reason": reason
                        })
                        continue
                    
                    await self.ingest_file(file_path, filename)
                    
                    try:
                        os.remove(file_path)
                        logger.info(f"✨ File vanished: {filename}")
                    except Exception as e:
                        logger.error(f"Error removing file: {str(e)}")
                
                existing_files = current_files
                await asyncio.sleep(2)
            except Exception as e:
                logger.error(f"Folder watching error: {str(e)}")
                await asyncio.sleep(5)
    
    async def ingest_file(self, file_path: str, filename: str) -> Dict:
        if self.collection is None:
            message = "ChromaDB non disponible"
            logger.error(message)
            return {"status": "error", "error": message}

        logger.info(f"📥 Ingesting {filename}...")
        try:
            content = await self._read_file_content(file_path)
            metadata = self._extract_metadata(file_path)
            embedding = await self._vectorize_content(content)
            
            record_id = f"file_{datetime.now().timestamp()}"
            
            self.collection.add(
                ids=[record_id],
                embeddings=[embedding],
                documents=[content],
                metadatas=[{
                    "original_filename": filename,
                    "content_type": self._detect_content_type(file_path),
                    "size": metadata["size"],
                    "created": metadata["created"],
                    "ingested_at": datetime.now().isoformat()
                }]
            )
            
            return {
                "status": "ingested",
                "file_id": record_id,
                "filename": filename,
                "message": f"✨ '{filename}' a disparu. Je m'en souviendrai."
            }
        except Exception as e:
            logger.error(f"Ingestion error: {str(e)}")
            return {"status": "error", "error": str(e)}
    
    async def semantic_search_files(self, query: str) -> List[Dict]:
        logger.info(f"🔍 Semantic file search: '{query}'")
        if self.collection is None:
            logger.error("ChromaDB non disponible")
            return []

        if not (query or "").strip():
            try:
                stored = self.collection.get()
                ids = stored.get("ids") or []
                metadatas = stored.get("metadatas") or []
                documents = stored.get("documents") or []
                return [
                    {
                        "file_id": ids[i],
                        "filename": (metadatas[i] or {}).get("original_filename", "Unknown"),
                        "similarity": 1.0,
                        "preview": (documents[i] or "")[:500],
                        "can_retrieve": True,
                    }
                    for i in range(min(len(ids), 20))
                ]
            except Exception as e:
                logger.error(f"List nexus files error: {str(e)}")
                return []

        try:
            query_vector = await self._vectorize_content(query)
            
            query_results = self.collection.query(
                query_embeddings=[query_vector],
                n_results=10
            )
            
            results = []
            if query_results and "ids" in query_results and len(query_results["ids"]) > 0:
                ids = query_results["ids"][0]
                distances = query_results["distances"][0] if "distances" in query_results and query_results["distances"] else [0.0] * len(ids)
                metadatas = query_results["metadatas"][0] if "metadatas" in query_results and query_results["metadatas"] else [{}] * len(ids)
                documents = query_results["documents"][0] if "documents" in query_results and query_results["documents"] else [""] * len(ids)
                
                for i in range(len(ids)):
                    distance = distances[i]
                    # En espace cosinus: distance = 1 - cosine_similarity
                    # Donc similarity = 1.0 - distance (bornée entre 0 et 1)
                    similarity = 1.0 - distance
                    if similarity < 0.0:
                        similarity = 0.0
                    
                    meta = metadatas[i]
                    content = documents[i]
                    results.append({
                        "file_id": ids[i],
                        "filename": meta.get("original_filename", "Unknown"),
                        "similarity": round(similarity, 2),
                        "preview": content[:500],
                        "can_retrieve": True
                    })
            
            return results
        except Exception as e:
            logger.error(f"Semantic search error: {str(e)}")
            return []
    
    async def retrieve_file(self, file_id: str) -> Dict:
        try:
            query_res = self.collection.get(ids=[file_id])
            if not query_res or not query_res["ids"]:
                return {"status": "error", "message": "File not found"}
            
            content = query_res["documents"][0]
            metadata = query_res["metadatas"][0]
            original_name = metadata.get("original_filename", "restored_file.txt")
            
            restored_path = os.path.join(self.nexus_path, original_name)
            with open(restored_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"📤 File restored: {original_name}")
            
            return {
                "status": "restored",
                "file_id": file_id,
                "filename": original_name,
                "path": restored_path,
                "message": f"🎉 '{original_name}' a réapparu!"
            }
        except Exception as e:
            logger.error(f"Retrieve error: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    async def _read_file_content(self, file_path: str) -> str:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except:
            return ""
            
    def _extract_metadata(self, file_path: str) -> Dict:
        try:
            stat = os.stat(file_path)
            return {
                "size": stat.st_size,
                "created": datetime.fromtimestamp(stat.st_ctime).isoformat()
            }
        except Exception:
            return {"size": 0, "created": datetime.now().isoformat()}
    
    async def _vectorize_content(self, content: str) -> List[float]:
        if not content.strip() or self.model is None:
            return [0.0] * 384
        # Utiliser sentence-transformers pour encoder en 384D
        return self.model.encode(content).tolist()
    
    def _detect_content_type(self, file_path: str) -> str:
        _, ext = os.path.splitext(file_path)
        return ext.lower() if ext else "unknown"

    def _is_safe_file(self, file_path: str) -> tuple[bool, str]:
        # 1. Dossier de sécurité
        if os.path.isdir(file_path):
            return False, "Les dossiers ne sont pas supportés et sont préservés pour éviter toute corruption du système."
        
        # 2. Séparation de l'extension
        _, ext = os.path.splitext(file_path)
        ext = ext.lower()
        
        # 3. Interdire explicitement les exécutables et scripts système suspects
        if ext in {'.exe', '.app', '.lnk', '.bat', '.cmd', '.sys', '.dll', '.msi', '.com', '.vbs', '.scr', '.cpl', '.jar', '.sh'}:
            return False, f"Les fichiers exécutables ou de type système ({ext}) sont interdits pour des raisons de sécurité."
            
        # 4. Whitelist stricte d'extensions supportées
        safe_exts = {
            '.txt', '.pdf', '.docx', '.doc', '.csv', '.xlsx', '.xls', '.md', '.json', '.xml', '.ppt', '.pptx',
            '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg', '.py', '.js', '.html', '.css', '.ts', '.tsx', '.jsx'
        }
        
        if ext not in safe_exts:
            return False, f"Le type de fichier '{ext}' n'est pas supporté par le Black Hole. Seuls les documents, images et scripts sûrs sont autorisés."
            
        return True, "Fichier sûr et autorisé."
