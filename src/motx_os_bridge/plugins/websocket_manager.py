"""
WebSocket Server pour MOT-X - Updates en temps réel
"""
import asyncio
import json
import logging
import websockets
from typing import Set, Dict, Any
from datetime import datetime
from threading import Thread

logger = logging.getLogger(__name__)


class WebSocketManager:
    """Gère les connexions WebSocket"""
    
    def __init__(self):
        self.active_connections: Dict[str, Any] = {}
        self.broadcast_queue = asyncio.Queue()
        self.execution_listeners: Set[str] = set()
    
    def add_connection(self, client_id: str, websocket) -> None:
        """Ajoute une nouvelle connexion"""
        self.active_connections[client_id] = {
            "ws": websocket,
            "connected_at": datetime.utcnow(),
            "subscriptions": set()
        }
        logger.info(f"✅ Client connecté: {client_id}")
    
    def remove_connection(self, client_id: str) -> None:
        """Supprime une connexion"""
        if client_id in self.active_connections:
            del self.active_connections[client_id]
            logger.info(f"❌ Client déconnecté: {client_id}")
    
    async def broadcast_execution(self, execution_data: Dict[str, Any]) -> None:
        """Diffuse les données d'exécution en temps réel"""
        
        message = {
            "type": "execution_update",
            "data": execution_data,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        await self._broadcast(message)
    
    async def broadcast_cognitive_update(self, cognitive_data: Dict[str, Any]) -> None:
        """Diffuse les mises à jour cognitives"""
        
        message = {
            "type": "cognitive_update",
            "data": cognitive_data,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        await self._broadcast(message)
    
    async def broadcast_gamification_update(self, gamification_data: Dict[str, Any]) -> None:
        """Diffuse les mises à jour de gamification"""
        
        message = {
            "type": "gamification_update",
            "data": gamification_data,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        await self._broadcast(message)
    
    async def broadcast_analytics(self, analytics_data: Dict[str, Any]) -> None:
        """Diffuse les analytiques"""
        
        message = {
            "type": "analytics_update",
            "data": analytics_data,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        await self._broadcast(message)
    
    async def send_to_client(self, client_id: str, message: Dict[str, Any]) -> None:
        """Envoie un message à un client spécifique"""
        
        if client_id not in self.active_connections:
            return
        
        connection = self.active_connections[client_id]
        try:
            await connection["ws"].send(json.dumps(message))
        except Exception as e:
            logger.error(f"Erreur d'envoi à {client_id}: {e}")
            self.remove_connection(client_id)
    
    async def _broadcast(self, message: Dict[str, Any]) -> None:
        """Envoie un message à tous les clients"""
        
        disconnected = []
        for client_id, connection in self.active_connections.items():
            try:
                await connection["ws"].send(json.dumps(message))
            except Exception as e:
                logger.error(f"Erreur broadcast à {client_id}: {e}")
                disconnected.append(client_id)
        
        # Nettoyer les connexions mortes
        for client_id in disconnected:
            self.remove_connection(client_id)
    
    def subscribe_to_updates(self, client_id: str, channel: str) -> None:
        """Souscrit un client à un canal"""
        if client_id in self.active_connections:
            self.active_connections[client_id]["subscriptions"].add(channel)
    
    def unsubscribe_from_updates(self, client_id: str, channel: str) -> None:
        """Désabonne un client d'un canal"""
        if client_id in self.active_connections:
            self.active_connections[client_id]["subscriptions"].discard(channel)
    
    def get_connection_stats(self) -> Dict[str, Any]:
        """Retourne les statistiques de connexion"""
        return {
            "total_connections": len(self.active_connections),
            "connections": [
                {
                    "id": client_id,
                    "connected_since": conn["connected_at"].isoformat(),
                    "subscriptions": list(conn["subscriptions"])
                }
                for client_id, conn in self.active_connections.items()
            ]
        }

    async def handle_client(self, websocket):
        try:
            path = websocket.path
        except AttributeError:
            try:
                path = websocket.request.path
            except AttributeError:
                path = ""
                
        client_id = path.strip("/").split("/")[-1] if path else f"client_{id(websocket)}"
        if not client_id or client_id == "ws":
            client_id = f"client_{id(websocket)}"
            
        self.add_connection(client_id, websocket)
        try:
            async for message in websocket:
                pass
        except Exception:
            pass
        finally:
            self.remove_connection(client_id)

    async def start_server(self, host="127.0.0.1", port=8001):
        """Lance le serveur WebSocket en arrière-plan"""
        logger.info(f"🚀 Serveur WebSocket démarré sur ws://{host}:{port}")
        async with websockets.serve(self.handle_client, host, port):
            await asyncio.Future()  # run forever

# Instance globale
_ws_manager = None


def get_ws_manager() -> WebSocketManager:
    """Obtient le gestionnaire WebSocket"""
    global _ws_manager
    if _ws_manager is None:
        _ws_manager = WebSocketManager()
    return _ws_manager
