# src/motx_os_bridge/plugins/voice_engine_enhanced.py

import asyncio
import logging
from typing import Optional, Dict
import numpy as np

logger = logging.getLogger(__name__)

class EnhancedVoiceEngine:
    """
    Intégration vocale: transcription + compréhension d'intention
    """
    
    def __init__(self):
        self.is_listening = False
        self.last_transcript = None
        self.voice_model = None
        self.commands_processed = 0
    
    async def initialize(self) -> Dict:
        """Initialise le moteur vocal"""
        
        logger.info("🎤 Initializing Voice Engine...")
        
        try:
            # Essayer d'utiliser Whisper (OpenAI) ou SpeechRecognition
            try:
                import whisper
                self.voice_model = whisper.load_model("base")
                provider = "Whisper (OpenAI)"
            except ImportError:
                try:
                    import speech_recognition as sr
                    self.recognizer = sr.Recognizer()
                    provider = "SpeechRecognition"
                except ImportError:
                    return {
                        "status": "warning",
                        "message": "No voice provider available",
                        "install": "pip install openai-whisper OR pip install SpeechRecognition"
                    }
            
            self.is_listening = True
            asyncio.create_task(self._voice_listening_loop())
            
            return {
                "status": "initialized",
                "provider": provider,
                "message": "🎤 Voice input ready"
            }
        
        except Exception as e:
            logger.error(f"Voice initialization error: {str(e)}")
            return {"status": "error", "error": str(e)}
    
    async def _voice_listening_loop(self) -> None:
        """Écoute en continu"""
        
        try:
            import speech_recognition as sr
        except ImportError:
            logger.warning("speech_recognition not installed. Voice loop stopped.")
            self.is_listening = False
            return
        
        recognizer = sr.Recognizer()
        
        try:
            source = sr.Microphone()
        except Exception as e:
            logger.warning(f"Could not open microphone: {str(e)}. Voice loop stopped.")
            self.is_listening = False
            return
            
        with source:
            recognizer.adjust_for_ambient_noise(source)
            
            while self.is_listening:
                try:
                    logger.debug("🎤 Listening...")
                    audio = recognizer.listen(source, timeout=5)
                    
                    # Transcrire
                    try:
                        if self.voice_model:
                            # Whisper
                            import tempfile
                            import os
                            # Utiliser un fichier temporaire
                            fd, tmp_path = tempfile.mkstemp(suffix=".wav")
                            try:
                                with os.fdopen(fd, "wb") as f:
                                    f.write(audio.get_wav_data())
                                result = self.voice_model.transcribe(tmp_path)
                                transcript = result["text"]
                            finally:
                                os.remove(tmp_path)
                        else:
                            # SpeechRecognition
                            transcript = recognizer.recognize_google(audio)
                        
                        logger.info(f"🎤 Transcript: {transcript}")
                        self.last_transcript = transcript
                        
                        # Dispatcher le transcript
                        await self._process_voice_command(transcript)
                    
                    except sr.UnknownValueError:
                        logger.debug("Could not understand audio")
                    except sr.RequestError as e:
                        logger.error(f"Speech recognition error: {str(e)}")
                
                except Exception as e:
                    logger.debug(f"Microphone timeout or error, continuing: {str(e)}")
                    await asyncio.sleep(0.5)
    
    async def _process_voice_command(self, transcript: str) -> None:
        """Traite une commande vocale"""
        self.commands_processed += 1
        logger.info(f"Processing voice command: '{transcript}'")
        
        # À connecter avec look_and_do.process_multimodal_command()
        # On peut essayer d'importer LookAndDoEngine dynamiquement ou utiliser un callback
        try:
            from motx_os_bridge.api.fastapi_server import look_and_do
            if look_and_do:
                asyncio.create_task(look_and_do._process_multimodal_command(transcript))
        except Exception:
            pass
