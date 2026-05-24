"""
Voice Interface - Commandes vocales et synthèse vocale.
"""

import asyncio
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from pathlib import Path
import json


@dataclass
class VoiceCommand:
    """Représente une commande vocale reconnue."""
    text: str
    confidence: float
    intent: str
    parameters: Dict[str, Any]


class VoiceInterface:
    """Interface vocale pour commandes et synthèse."""
    
    def __init__(self):
        self.is_listening = False
        self.commands_history: List[VoiceCommand] = []
        self.language = "fr-FR"
        
        # Vérification des dépendances
        self._check_dependencies()
    
    def _check_dependencies(self):
        """Vérifie si les dépendances nécessaires sont disponibles."""
        self.has_speech_recognition = self._try_import('speech_recognition')
        self.has_pyaudio = self._try_import('pyaudio')
        self.has_pyttsx3 = self._try_import('pyttsx3')
        self.has_openai = self._try_import('openai')
        
        if not self.has_speech_recognition:
            print("⚠️ SpeechRecognition non installé - Reconnaissance vocale non disponible")
        if not self.has_pyaudio:
            print("⚠️ PyAudio non installé - Entrée micro non disponible")
        if not self.has_pyttsx3:
            print("⚠️ pyttsx3 non installé - Synthèse vocale non disponible")
    
    def _try_import(self, module_name: str) -> bool:
        """Tente d'importer un module."""
        try:
            __import__(module_name)
            return True
        except ImportError:
            return False
    
    async def listen_command(self, timeout: int = 5) -> VoiceCommand:
        """Écoute et reconnaît une commande vocale."""
        if not self.has_speech_recognition or not self.has_pyaudio:
            raise Exception("Dépendances vocales non installées")
        
        try:
            import speech_recognition as sr
            
            recognizer = sr.Recognizer()
            
            with sr.Microphone() as source:
                print("🎤 Écoute...")
                recognizer.adjust_for_ambient_noise(source, duration=0.5)
                
                try:
                    audio = recognizer.listen(source, timeout=timeout)
                    text = recognizer.recognize_google(audio, language=self.language)
                    
                    command = VoiceCommand(
                        text=text,
                        confidence=0.8,  # Google ne fournit pas toujours la confiance
                        intent=self._extract_intent(text),
                        parameters=self._extract_parameters(text)
                    )
                    
                    self.commands_history.append(command)
                    return command
                    
                except sr.WaitTimeoutError:
                    raise Exception("Timeout - Aucune commande détectée")
                except sr.UnknownValueError:
                    raise Exception("Impossible de reconnaître la commande")
                except sr.RequestError:
                    raise Exception("Erreur service reconnaissance vocale")
                    
        except Exception as e:
            raise Exception(f"Erreur écoute: {str(e)}")
    
    def _extract_intent(self, text: str) -> str:
        """Extrait l'intention de la commande."""
        text_lower = text.lower()
        
        intents = {
            "ouvrir": ["ouvre", "ouvrir", "open", "lance", "lancer"],
            "fermer": ["ferme", "fermer", "close", "quitte", "quitter"],
            "créer": ["crée", "créer", "create", "nouveau", "new"],
            "supprimer": ["supprime", "supprimer", "delete", "effacer"],
            "chercher": ["cherche", "chercher", "search", "recherche"],
            "écrire": ["écris", "écrire", "write", "tape"],
            "lire": ["lis", "lire", "read"],
            "envoyer": ["envoie", "envoyer", "send"],
            "télécharger": ["télécharge", "télécharger", "download"],
            "info": ["info", "information", "status", "état"],
            "aide": ["aide", "help", "assistant"]
        }
        
        for intent, keywords in intents.items():
            if any(kw in text_lower for kw in keywords):
                return intent
        
        return "general"
    
    def _extract_parameters(self, text: str) -> Dict[str, Any]:
        """Extrait les paramètres de la commande."""
        import re
        
        parameters = {}
        
        # Extraction entre guillemets
        quoted = re.findall(r'"([^"]+)"', text)
        if quoted:
            parameters["quoted_text"] = quoted[0]
        
        # Extraction de nombres
        numbers = re.findall(r'\d+', text)
        if numbers:
            parameters["numbers"] = [int(n) for n in numbers]
        
        # Extraction d'URLs
        urls = re.findall(r'https?://[^\s]+', text)
        if urls:
            parameters["urls"] = urls
        
        # Extraction de chemins Windows
        paths = re.findall(r'[a-zA-Z]:\\[^\s]+', text)
        if paths:
            parameters["paths"] = paths
        
        return parameters
    
    async def speak(self, text: str, rate: int = 150, volume: float = 0.9) -> bool:
        """Synthétise et prononce du texte."""
        if not self.has_pyttsx3:
            print(f"🔊 (TTS non disponible): {text}")
            return False
        
        try:
            import pyttsx3
            
            engine = pyttsx3.init()
            engine.setProperty('rate', rate)
            engine.setProperty('volume', volume)
            
            # Configuration de la voix française si disponible
            voices = engine.getProperty('voices')
            for voice in voices:
                if 'french' in voice.languages[0].lower() or 'fr' in voice.languages[0].lower():
                    engine.setProperty('voice', voice.id)
                    break
            
            engine.say(text)
            engine.runAndWait()
            
            return True
            
        except Exception as e:
            print(f"⚠️ Erreur synthèse: {str(e)}")
            return False
    
    async def speak_async(self, text: str, rate: int = 150, volume: float = 0.9):
        """Synthèse vocale asynchrone."""
        await asyncio.get_event_loop().run_in_executor(
            None, self.speak, text, rate, volume
        )
    
    async def start_continuous_listening(self, callback):
        """Démarre l'écoute continue avec callback."""
        if not self.has_speech_recognition or not self.has_pyaudio:
            raise Exception("Dépendances vocales non installées")
        
        self.is_listening = True
        
        try:
            import speech_recognition as sr
            
            recognizer = sr.Recognizer()
            
            with sr.Microphone() as source:
                recognizer.adjust_for_ambient_noise(source, duration=1)
                
                while self.is_listening:
                    try:
                        audio = recognizer.listen(source, timeout=1, phrase_time_limit=5)
                        text = recognizer.recognize_google(audio, language=self.language)
                        
                        command = VoiceCommand(
                            text=text,
                            confidence=0.8,
                            intent=self._extract_intent(text),
                            parameters=self._extract_parameters(text)
                        )
                        
                        self.commands_history.append(command)
                        await callback(command)
                        
                    except sr.WaitTimeoutError:
                        continue
                    except sr.UnknownValueError:
                        continue
                    except Exception as e:
                        print(f"Erreur écoute continue: {str(e)}")
                        break
                        
        except Exception as e:
            raise Exception(f"Erreur démarrage écoute: {str(e)}")
    
    def stop_listening(self):
        """Arrête l'écoute continue."""
        self.is_listening = False
    
    def set_language(self, language: str):
        """Définit la langue pour la reconnaissance."""
        self.language = language
    
    def get_commands_history(self) -> List[VoiceCommand]:
        """Retourne l'historique des commandes."""
        return self.commands_history
    
    def clear_history(self):
        """Efface l'historique des commandes."""
        self.commands_history.clear()
