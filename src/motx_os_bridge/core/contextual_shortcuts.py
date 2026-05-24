"""
Contextual Natural Language Shortcuts - Sélection globale + raccourci clavier.
"""

import asyncio
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from datetime import datetime
import pyperclip
import re


@dataclass
class ShortcutAction:
    """Représente une action de raccourci."""
    action_id: str
    name: str
    description: str
    trigger_hotkey: str
    command_pattern: str
    created_at: str


@dataclass
class ContextualCommand:
    """Représente une commande contextuelle exécutée."""
    command_id: str
    selected_text: str
    command: str
    executed_at: str
    result: Optional[str] = None
    success: bool = False


class ContextualShortcuts:
    """Gestionnaire de raccourcis contextuels avec sélection globale."""
    
    def __init__(self):
        self.shortcuts: List[ShortcutAction] = []
        self.command_history: List[ContextualCommand] = []
        self.is_listening = False
        self.global_hotkey = "ctrl+space"
        
        # Patterns de commandes courantes
        self.command_patterns = {
            "translate": ["traduis", "translate", "traduction"],
            "summarize": ["résume", "summarize", "résumé"],
            "email": ["envoie par mail", "send email", "email à"],
            "save": ["sauvegarde", "save", "enregistre"],
            "create_file": ["crée un fichier", "create file", "nouveau fichier"],
            "search": ["cherche", "search", "recherche"],
            "format": ["formate", "format", "mise en forme"]
        }
        
        # Initialiser les raccourcis par défaut
        self._initialize_default_shortcuts()
    
    def _initialize_default_shortcuts(self):
        """Initialise les raccourcis par défaut."""
        default_shortcuts = [
            ShortcutAction(
                action_id="translate_selection",
                name="Traduire la sélection",
                description="Traduit le texte sélectionné en français",
                trigger_hotkey="ctrl+shift+t",
                command_pattern="traduis ça",
                created_at=datetime.now().isoformat()
            ),
            ShortcutAction(
                action_id="summarize_selection",
                name="Résumer la sélection",
                description="Génère un résumé du texte sélectionné",
                trigger_hotkey="ctrl+shift+s",
                command_pattern="résume ça",
                created_at=datetime.now().isoformat()
            ),
            ShortcutAction(
                action_id="save_to_file",
                name="Sauvegarder dans un fichier",
                description="Sauvegarde le texte sélectionné dans un fichier",
                trigger_hotkey="ctrl+shift+f",
                command_pattern="sauvegarde ça",
                created_at=datetime.now().isoformat()
            )
        ]
        
        self.shortcuts = default_shortcuts
    
    async def start_listening(self, callback: Optional[Callable] = None):
        """Démarre l'écoute des raccourcis globaux."""
        self.is_listening = True
        
        try:
            import keyboard
            
            print(f"🎧 Écoute des raccourcis activée (Hotkey: {self.global_hotkey})")
            
            while self.is_listening:
                # Attendre le hotkey global
                keyboard.wait(self.global_hotkey)
                
                # Capturer le texte sélectionné
                selected_text = self._get_selected_text()
                
                if selected_text:
                    print(f"\n📝 Texte sélectionné: {selected_text[:50]}...")
                    print("💬 Entrez votre commande (ou 'cancel' pour annuler):")
                    
                    # En mode réel, on afficherait une UI ici
                    # Pour l'instant, on simule avec input
                    command = input("Commande: ").strip()
                    
                    if command.lower() != "cancel":
                        result = await self.execute_contextual_command(selected_text, command)
                        if callback:
                            await callback(result)
                
        except ImportError:
            print("⚠️ keyboard non installé - Raccourcis globaux non disponibles")
            await self._fallback_listening()
        except Exception as e:
            print(f"⚠️ Erreur écoute raccourcis: {str(e)}")
    
    async def _fallback_listening(self):
        """Mode d'écoute fallback sans keyboard."""
        print("📋 Mode fallback: Utilisez Ctrl+C pour copier, puis entrez 'paste' pour traiter")
        
        while self.is_listening:
            await asyncio.sleep(1)
    
    def _get_selected_text(self) -> str:
        """Récupère le texte sélectionné via le presse-papiers."""
        try:
            # Simuler Ctrl+C pour copier la sélection
            import pyautogui
            pyautogui.hotkey('ctrl', 'c')
            asyncio.sleep(0.1)  # Attendre que la copie se fasse
            
            # Récupérer le texte du presse-papiers
            selected_text = pyperclip.paste()
            
            return selected_text if selected_text else ""
            
        except Exception as e:
            print(f"⚠️ Erreur récupération sélection: {str(e)}")
            return ""
    
    async def execute_contextual_command(self, selected_text: str, command: str) -> ContextualCommand:
        """Exécute une commande contextuelle sur le texte sélectionné."""
        command_id = f"cmd_{len(self.command_history)}"
        
        # Analyser la commande
        parsed_command = self._parse_command(command)
        
        try:
            result = await self._execute_action(selected_text, parsed_command)
            
            contextual_command = ContextualCommand(
                command_id=command_id,
                selected_text=selected_text,
                command=command,
                executed_at=datetime.now().isoformat(),
                result=result,
                success=True
            )
            
            self.command_history.append(contextual_command)
            
            return contextual_command
            
        except Exception as e:
            contextual_command = ContextualCommand(
                command_id=command_id,
                selected_text=selected_text,
                command=command,
                executed_at=datetime.now().isoformat(),
                result=str(e),
                success=False
            )
            
            self.command_history.append(contextual_command)
            
            return contextual_command
    
    def _parse_command(self, command: str) -> Dict[str, Any]:
        """Analyse une commande en langage naturel."""
        command_lower = command.lower()
        
        parsed = {
            "action": "unknown",
            "parameters": {}
        }
        
        # Détecter l'action
        for action, keywords in self.command_patterns.items():
            if any(kw in command_lower for kw in keywords):
                parsed["action"] = action
                break
        
        # Extraire les paramètres
        # Email
        email_match = re.search(r'à\s+(\w+)|to\s+(\w+)', command_lower)
        if email_match:
            parsed["parameters"]["recipient"] = email_match.group(1) or email_match.group(2)
        
        # Fichier
        file_match = re.search(r'"([^"]+)"|\'([^\']+)\'', command)
        if file_match:
            parsed["parameters"]["filename"] = file_match.group(1) or file_match.group(2)
        
        # Langue
        lang_match = re.search(r"(en\s+(\w+)|in\s+(\w+))", command_lower)
        if lang_match:
            parsed["parameters"]["language"] = lang_match.group(1) or lang_match.group(2)
        
        return parsed
    
    async def _execute_action(self, text: str, parsed_command: Dict[str, Any]) -> str:
        """Exécute l'action correspondant à la commande."""
        action = parsed_command["action"]
        parameters = parsed_command["parameters"]
        
        if action == "translate":
            return await self._translate_text(text, parameters.get("language", "french"))
        elif action == "summarize":
            return await self._summarize_text(text)
        elif action == "email":
            return await self._send_email(text, parameters.get("recipient"))
        elif action == "save":
            return await self._save_to_file(text, parameters.get("filename", "output.txt"))
        elif action == "create_file":
            return await self._create_file_with_content(text, parameters.get("filename", "output.txt"))
        elif action == "search":
            return await self._search_text(text)
        elif action == "format":
            return await self._format_text(text)
        else:
            return f"Action non reconnue: {action}"
    
    async def _translate_text(self, text: str, target_language: str) -> str:
        """Traduit le texte."""
        try:
            from ..plugins.translation import translate_to_french
            if target_language == "french":
                return translate_to_french(text)
            else:
                return f"Traduction vers {target_language} non implémentée"
        except Exception as e:
            return f"Erreur traduction: {str(e)}"
    
    async def _summarize_text(self, text: str) -> str:
        """Génère un résumé du texte."""
        # Résumé basique (nombre de mots, phrases)
        words = text.split()
        sentences = text.split('.')
        
        summary = f"Texte de {len(words)} mots et {len(sentences)} phrases. "
        summary += f"Premiers mots: {' '.join(words[:10])}..."
        
        return summary
    
    async def _send_email(self, text: str, recipient: Optional[str]) -> str:
        """Envoie le texte par email."""
        if not recipient:
            return "Destinataire non spécifié"
        return f"Email simulé envoyé à {recipient} avec le texte: {text[:50]}..."
    
    async def _save_to_file(self, text: str, filename: str) -> str:
        """Sauvegarde le texte dans un fichier."""
        try:
            from pathlib import Path
            file_path = Path(filename)
            file_path.write_text(text, encoding='utf-8')
            return f"Texte sauvegardé dans {filename}"
        except Exception as e:
            return f"Erreur sauvegarde: {str(e)}"
    
    async def _create_file_with_content(self, text: str, filename: str) -> str:
        """Crée un fichier avec le contenu."""
        return await self._save_to_file(text, filename)
    
    async def _search_text(self, text: str) -> str:
        """Recherche des informations dans le texte."""
        return f"Recherche simulée dans le texte: {text[:50]}..."
    
    async def _format_text(self, text: str) -> str:
        """Formate le texte."""
        # Formatage basique: nettoyer les espaces multiples
        formatted = re.sub(r'\s+', ' ', text).strip()
        return f"Texte formaté: {formatted[:50]}..."
    
    def add_custom_shortcut(self, name: str, description: str, hotkey: str, 
                           command_pattern: str) -> ShortcutAction:
        """Ajoute un raccourci personnalisé."""
        shortcut = ShortcutAction(
            action_id=f"custom_{len(self.shortcuts)}",
            name=name,
            description=description,
            trigger_hotkey=hotkey,
            command_pattern=command_pattern,
            created_at=datetime.now().isoformat()
        )
        
        self.shortcuts.append(shortcut)
        return shortcut
    
    def remove_shortcut(self, action_id: str) -> bool:
        """Supprime un raccourci."""
        for i, shortcut in enumerate(self.shortcuts):
            if shortcut.action_id == action_id:
                self.shortcuts.pop(i)
                return True
        return False
    
    def get_shortcuts(self) -> List[ShortcutAction]:
        """Retourne la liste des raccourcis."""
        return self.shortcuts
    
    def get_command_history(self, limit: int = 10) -> List[ContextualCommand]:
        """Retourne l'historique des commandes."""
        return self.command_history[-limit:]
    
    def stop_listening(self):
        """Arrête l'écoute des raccourcis."""
        self.is_listening = False
    
    def get_usage_statistics(self) -> Dict[str, Any]:
        """Retourne les statistiques d'utilisation."""
        if not self.command_history:
            return {"status": "no_data"}
        
        # Distribution des actions
        action_distribution = {}
        for cmd in self.command_history:
            action = cmd.command.split()[0] if cmd.command else "unknown"
            action_distribution[action] = action_distribution.get(action, 0) + 1
        
        # Taux de succès
        successful = sum(1 for cmd in self.command_history if cmd.success)
        success_rate = successful / len(self.command_history) if self.command_history else 0
        
        return {
            "total_commands": len(self.command_history),
            "successful_commands": successful,
            "success_rate": success_rate,
            "action_distribution": action_distribution,
            "total_shortcuts": len(self.shortcuts)
        }
