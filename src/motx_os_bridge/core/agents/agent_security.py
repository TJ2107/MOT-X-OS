"""
Agent Security - Agent spécialisé pour la sécurité et les audits.
"""

import asyncio
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from pathlib import Path
import json
import hashlib
import re


@dataclass
class SecurityEvent:
    """Représente un événement de sécurité."""
    event_type: str
    severity: str  # low, medium, high, critical
    description: str
    timestamp: str
    source: str
    details: Dict[str, Any]


class AgentSecurity:
    """Agent spécialisé pour la sécurité et les audits."""
    
    def __init__(self):
        self.security_events: List[SecurityEvent] = []
        self.security_policies: Dict[str, Any] = {}
        self.blocked_actions: List[str] = []
        self.whitelist: List[str] = []
        
        self._load_default_policies()
    
    def _load_default_policies(self):
        """Charge les politiques de sécurité par défaut."""
        self.security_policies = {
            "file_operations": {
                "allowed_paths": ["C:\\Users", "D:\\"],
                "blocked_paths": ["C:\\Windows", "C:\\Program Files"],
                "require_confirmation": True
            },
            "network_operations": {
                "allowed_domains": ["*.local", "localhost"],
                "blocked_domains": ["malware.com", "phishing.net"],
                "require_confirmation": True
            },
            "system_operations": {
                "require_confirmation": True,
                "blocked_commands": ["format", "del /f", "rm -rf"]
            },
            "script_execution": {
                "allowed_extensions": [".py", ".ps1"],
                "require_confirmation": True
            }
        }
    
    async def validate_action(self, action: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """Valide une action selon les politiques de sécurité."""
        action_type = action.get("type", "")
        
        # Vérification des actions bloquées
        if action_type in self.blocked_actions:
            event = SecurityEvent(
                event_type="action_blocked",
                severity="high",
                description=f"Action bloquée: {action_type}",
                timestamp=self._get_timestamp(),
                source="AgentSecurity",
                details={"action": action}
            )
            self.security_events.append(event)
            return False, f"Action {action_type} bloquée par politique de sécurité"
        
        # Validation selon le type d'action
        if action_type.startswith("FILE_"):
            return await self._validate_file_operation(action)
        elif action_type.startswith("EXECUTE_"):
            return await self._validate_script_execution(action)
        elif action_type in ["OPEN_URL", "DOWNLOAD_FILE"]:
            return await self._validate_network_operation(action)
        elif action_type in ["RESTART_PC", "SHUTDOWN_PC"]:
            return await self._validate_system_operation(action)
        
        return True, None
    
    async def _validate_file_operation(self, action: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """Valide une opération de fichier."""
        path = action.get("path") or action.get("source") or action.get("target")
        
        if not path:
            return True, None
        
        # Vérification des chemins bloqués
        for blocked in self.security_policies["file_operations"]["blocked_paths"]:
            if path.lower().startswith(blocked.lower()):
                event = SecurityEvent(
                    event_type="file_operation_blocked",
                    severity="high",
                    description=f"Opération fichier bloquée: {path}",
                    timestamp=self._get_timestamp(),
                    source="AgentSecurity",
                    details={"path": path, "blocked_pattern": blocked}
                )
                self.security_events.append(event)
                return False, f"Chemin {path} bloqué par politique de sécurité"
        
        return True, None
    
    async def _validate_script_execution(self, action: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """Valide l'exécution d'un script."""
        script = action.get("script") or action.get("command")
        
        if not script:
            return True, None
        
        # Vérification des commandes dangereuses
        for blocked_cmd in self.security_policies["system_operations"]["blocked_commands"]:
            if blocked_cmd.lower() in script.lower():
                event = SecurityEvent(
                    event_type="script_execution_blocked",
                    severity="critical",
                    description=f"Exécution script bloquée: {script}",
                    timestamp=self._get_timestamp(),
                    source="AgentSecurity",
                    details={"script": script, "blocked_pattern": blocked_cmd}
                )
                self.security_events.append(event)
                return False, f"Commande bloquée: {blocked_cmd}"
        
        return True, None
    
    async def _validate_network_operation(self, action: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """Valide une opération réseau."""
        url = action.get("url") or action.get("target")
        
        if not url:
            return True, None
        
        # Vérification des domaines bloqués
        for blocked in self.security_policies["network_operations"]["blocked_domains"]:
            if blocked in url.lower():
                event = SecurityEvent(
                    event_type="network_operation_blocked",
                    severity="high",
                    description=f"Opération réseau bloquée: {url}",
                    timestamp=self._get_timestamp(),
                    source="AgentSecurity",
                    details={"url": url, "blocked_domain": blocked}
                )
                self.security_events.append(event)
                return False, f"Domaine {blocked} bloqué par politique de sécurité"
        
        return True, None
    
    async def _validate_system_operation(self, action: Dict[str, Any]) -> tuple[bool, Optional[str]]:
        """Valide une opération système."""
        if self.security_policies["system_operations"]["require_confirmation"]:
            return True, "Confirmation requise pour opération système"
        
        return True, None
    
    async def audit_system(self) -> Dict[str, Any]:
        """Effectue un audit de sécurité du système."""
        audit_results = {
            "timestamp": self._get_timestamp(),
            "security_events_count": len(self.security_events),
            "high_severity_events": len([e for e in self.security_events if e.severity in ["high", "critical"]]),
            "blocked_actions_count": len(self.blocked_actions),
            "policies_active": len(self.security_policies),
            "recommendations": []
        }
        
        # Analyse des événements pour générer des recommandations
        high_severity_events = [e for e in self.security_events if e.severity in ["high", "critical"]]
        if len(high_severity_events) > 5:
            audit_results["recommendations"].append("Nombre élevé d'événements de haute sévérité détectés")
        
        if audit_results["blocked_actions_count"] > 10:
            audit_results["recommendations"].append("Considérer la révision des politiques de blocage")
        
        return audit_results
    
    async def scan_files(self, directory: str) -> List[Dict[str, Any]]:
        """Scan un répertoire pour détecter les fichiers suspects."""
        suspicious_files = []
        
        try:
            from pathlib import Path
            dir_path = Path(directory)
            
            if not dir_path.exists():
                return suspicious_files
            
            # Patterns suspects
            suspicious_patterns = [
                r"\.exe$",
                r"\.bat$",
                r"\.scr$",
                r"\.vbs$",
                r"\.js$",
                r"password",
                r"secret",
                r"key",
                r"hack"
            ]
            
            for file_path in dir_path.rglob("*"):
                if file_path.is_file():
                    file_name = file_path.name.lower()
                    
                    for pattern in suspicious_patterns:
                        if re.search(pattern, file_name):
                            suspicious_files.append({
                                "path": str(file_path),
                                "pattern_matched": pattern,
                                "size": file_path.stat().st_size
                            })
                            break
            
            return suspicious_files
            
        except Exception as e:
            raise Exception(f"Erreur scan fichiers: {str(e)}")
    
    async def check_password_strength(self, password: str) -> Dict[str, Any]:
        """Vérifie la force d'un mot de passe."""
        strength_score = 0
        issues = []
        
        # Longueur
        if len(password) >= 12:
            strength_score += 2
        elif len(password) >= 8:
            strength_score += 1
        else:
            issues.append("Mot de passe trop court (minimum 8 caractères)")
        
        # Complexité
        if re.search(r"[A-Z]", password):
            strength_score += 1
        else:
            issues.append("Pas de majuscules")
        
        if re.search(r"[a-z]", password):
            strength_score += 1
        else:
            issues.append("Pas de minuscules")
        
        if re.search(r"\d", password):
            strength_score += 1
        else:
            issues.append("Pas de chiffres")
        
        if re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            strength_score += 1
        else:
            issues.append("Pas de caractères spéciaux")
        
        # Évaluation
        if strength_score >= 5:
            strength = "very_strong"
        elif strength_score >= 4:
            strength = "strong"
        elif strength_score >= 3:
            strength = "moderate"
        elif strength_score >= 2:
            strength = "weak"
        else:
            strength = "very_weak"
        
        return {
            "strength": strength,
            "score": strength_score,
            "issues": issues
        }
    
    async def encrypt_data(self, data: str, key: str) -> str:
        """Chiffre des données avec une clé."""
        try:
            # Simple XOR encryption (pour démonstration)
            # En production, utiliser cryptography ou PyCryptodome
            key_bytes = key.encode()
            data_bytes = data.encode()
            
            encrypted = bytes([b ^ key_bytes[i % len(key_bytes)] for i, b in enumerate(data_bytes)])
            return encrypted.hex()
            
        except Exception as e:
            raise Exception(f"Erreur chiffrement: {str(e)}")
    
    async def decrypt_data(self, encrypted_hex: str, key: str) -> str:
        """Déchiffre des données avec une clé."""
        try:
            key_bytes = key.encode()
            encrypted_bytes = bytes.fromhex(encrypted_hex)
            
            decrypted = bytes([b ^ key_bytes[i % len(key_bytes)] for i, b in enumerate(encrypted_bytes)])
            return decrypted.decode()
            
        except Exception as e:
            raise Exception(f"Erreur déchiffrement: {str(e)}")
    
    def add_to_whitelist(self, item: str):
        """Ajoute un élément à la liste blanche."""
        if item not in self.whitelist:
            self.whitelist.append(item)
    
    def add_to_blocked_actions(self, action: str):
        """Ajoute une action à la liste des actions bloquées."""
        if action not in self.blocked_actions:
            self.blocked_actions.append(action)
    
    def get_security_events(self, severity: Optional[str] = None) -> List[SecurityEvent]:
        """Retourne les événements de sécurité, filtrés par sévérité."""
        if severity:
            return [e for e in self.security_events if e.severity == severity]
        return self.security_events
    
    def clear_security_events(self):
        """Efface les événements de sécurité."""
        self.security_events.clear()
    
    def _get_timestamp(self) -> str:
        """Retourne l'horodatage actuel."""
        from datetime import datetime
        return datetime.now().isoformat()
