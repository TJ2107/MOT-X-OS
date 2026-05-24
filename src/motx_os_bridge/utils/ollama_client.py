"""
Ollama Client - Client pour LLM local via Ollama.
"""

import requests
import json
from typing import Optional, Dict, Any, List


class OllamaClient:
    """Client pour interagir avec Ollama (LLM local)."""
    
    def __init__(self, host: str = "localhost", port: int = 11434, model: str = "llama2"):
        """
        Initialise le client Ollama.
        
        Args:
            host: Hôte Ollama (défaut: localhost)
            port: Port Ollama (défaut: 11434)
            model: Modèle à utiliser (défaut: llama2)
        """
        self.base_url = f"http://{host}:{port}"
        self.model = model
        self.timeout = 30
        self._check_connection()
    
    def _check_connection(self):
        """Vérifie la connexion avec Ollama."""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                print(f"✅ Connecté à Ollama sur {self.base_url}")
                models = response.json().get("models", [])
                if models:
                    available_models = [m["name"] for m in models]
                    print(f"   Modèles disponibles: {', '.join(available_models)}")
                    resolved_model = self._resolve_model_alias(self.model, available_models)
                    if resolved_model != self.model:
                        print(f"⚠️ Modèle '{self.model}' non trouvé, utilisation de '{resolved_model}'")
                        self.model = resolved_model
            else:
                print(f"⚠️ Ollama répond mais avec un code {response.status_code}")
        except requests.exceptions.ConnectionError:
            print(f"⚠️ Impossible de connecter à Ollama sur {self.base_url}")
            print("   Assurez-vous que Ollama est installé et démarré:")
            print("   - Installation: https://ollama.ai")
            print("   - Démarrage: ollama serve")
        except Exception as e:
            print(f"⚠️ Erreur de connexion Ollama: {str(e)}")

    def _resolve_model_alias(self, requested_model: str, available_models: List[str]) -> str:
        """Resolve a requested Ollama model alias against available model names."""
        model_lower = requested_model.lower()
        if requested_model in available_models:
            return requested_model
        if model_lower == "llama2":
            for model in available_models:
                if model.lower().startswith("llama2"):
                    return model
        if model_lower.endswith(":latest"):
            for model in available_models:
                if model.lower() == model_lower:
                    return model
        for model in available_models:
            if model_lower in model.lower():
                return model
        return available_models[0]
    
    def generate(self, prompt: str, max_tokens: int = 512, temperature: float = 0.7, 
                 stream: bool = False) -> str:
        """
        Génère une réponse via Ollama.
        
        Args:
            prompt: Prompt à envoyer
            max_tokens: Nombre maximum de tokens
            temperature: Température de génération
            stream: Si True, utilise le streaming
            
        Returns:
            Texte généré
        """
        try:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": stream,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens
                }
            }
            
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                if stream:
                    # Streaming response
                    full_response = ""
                    for line in response.iter_lines():
                        if line:
                            json_response = json.loads(line)
                            if "response" in json_response:
                                full_response += json_response["response"]
                    return full_response
                else:
                    # Single response
                    data = response.json()
                    return data.get("response", "")
            else:
                error_msg = f"Erreur Ollama: {response.status_code}"
                try:
                    error_data = response.json()
                    error_msg += f" - {error_data.get('error', '')}"
                except:
                    pass
                return f"[LLM Error] {error_msg}"
                
        except requests.exceptions.Timeout:
            return "[LLM Error] Timeout Ollama"
        except requests.exceptions.ConnectionError:
            return "[LLM Error] Impossible de connecter à Ollama"
        except Exception as e:
            return f"[LLM Error] {str(e)}"
    
    def chat(self, messages: List[Dict[str, str]], max_tokens: int = 512, 
             temperature: float = 0.7) -> str:
        """
        Génère une réponse via Ollama en mode chat.
        
        Args:
            messages: Liste de messages (role: system/user/assistant, content)
            max_tokens: Nombre maximum de tokens
            temperature: Température de génération
            
        Returns:
            Texte généré
        """
        try:
            payload = {
                "model": self.model,
                "messages": messages,
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens
                }
            }
            
            response = requests.post(
                f"{self.base_url}/api/chat",
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get("message", {}).get("content", "")
            else:
                return f"[LLM Error] HTTP {response.status_code}"
                
        except Exception as e:
            return f"[LLM Error] {str(e)}"
    
    def list_models(self) -> List[str]:
        """Liste les modèles disponibles."""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get("models", [])
                return [m["name"] for m in models]
            return []
        except Exception:
            return []
    
    def set_model(self, model: str):
        """Change le modèle utilisé."""
        available_models = self.list_models()
        if model in available_models:
            self.model = model
            print(f"✅ Modèle changé pour: {model}")
        else:
            print(f"⚠️ Modèle '{model}' non disponible")
            print(f"   Modèles disponibles: {', '.join(available_models)}")
    
    def pull_model(self, model: str) -> bool:
        """
        Télécharge un modèle depuis Ollama.
        
        Args:
            model: Nom du modèle à télécharger
            
        Returns:
            True si succès, False sinon
        """
        try:
            print(f"📥 Téléchargement du modèle {model}...")
            response = requests.post(
                f"{self.base_url}/api/pull",
                json={"name": model},
                stream=True,
                timeout=300
            )
            
            if response.status_code == 200:
                for line in response.iter_lines():
                    if line:
                        json_response = json.loads(line)
                        status = json_response.get("status", "")
                        if status:
                            print(f"   {status}")
                print(f"✅ Modèle {model} téléchargé avec succès")
                return True
            else:
                print(f"❌ Erreur téléchargement: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Erreur téléchargement: {str(e)}")
            return False
    
    def get_model_info(self, model: Optional[str] = None) -> Dict[str, Any]:
        """
        Récupère les informations sur un modèle.
        
        Args:
            model: Nom du modèle (si None, utilise le modèle actuel)
            
        Returns:
            Dictionnaire avec les informations du modèle
        """
        model = model or self.model
        try:
            response = requests.post(
                f"{self.base_url}/api/show",
                json={"name": model},
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            return {}
        except Exception:
            return {}
    
    def is_available(self) -> bool:
        """Vérifie si Ollama est disponible."""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=2)
            return response.status_code == 200
        except:
            return False


# Fonction utilitaire pour créer un client Ollama
def create_ollama_client(config: Optional[Dict[str, Any]] = None) -> Optional[OllamaClient]:
    """
    Crée un client Ollama à partir de la configuration.
    
    Args:
        config: Dictionnaire de configuration (host, port, model)
        
    Returns:
        Instance OllamaClient ou None si non disponible
    """
    if config is None:
        config = {}
    
    host = config.get("host", "localhost")
    port = config.get("port", 11434)
    model = config.get("model", "llama2")
    
    client = OllamaClient(host=host, port=port, model=model)
    
    if client.is_available():
        return client
    else:
        print("⚠️ Ollama non disponible, utilisation du fallback")
        return None
