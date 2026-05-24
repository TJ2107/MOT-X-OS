"""
Biomimetic System - Traite l'OS comme un organisme vivant.
"""

import asyncio
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from pathlib import Path
from datetime import datetime, timedelta
import json
import shutil
import re


@dataclass
class DeadCell:
    """Représente une 'cellule morte' (fichier inutilisé)."""
    path: str
    size_bytes: int
    last_accessed: str
    days_inactive: int
    cell_type: str
    recommendation: str


@dataclass
class HybridFolder:
    """Représente un 'dossier hybride' créé par pollinisation."""
    source_paths: List[str]
    hybrid_path: str
    created_at: str
    summaries: List[str]
    connections: List[str]


class BiomimeticSystem:
    """Système biomimétique qui traite l'OS comme un organisme vivant."""
    
    def __init__(self):
        self.dead_cells: List[DeadCell] = []
        self.hybrid_folders: List[HybridFolder] = []
        self.system_age_days = 0
        self.metabolism_rate = 0.5
        self.growth_factor = 1.0
        
        self.cell_death_threshold_days = 180
        self.organ_failure_threshold = 90
        self.auto_clean_interval_hours = 24
    
    async def scan_for_dead_cells(self, directory: str = "C:/Users") -> List[DeadCell]:
        """Scan pour détecter les 'cellules mortes' (fichiers inutilisés)."""
        dead_cells = []
        cutoff_date = datetime.now() - timedelta(days=self.cell_death_threshold_days)
        
        try:
            dir_path = Path(directory)
            if not dir_path.exists():
                return dead_cells
            
            for item in dir_path.rglob("*"):
                if item.is_file():
                    try:
                        stat = item.stat()
                        last_access = datetime.fromtimestamp(stat.st_atime)
                        
                        if last_access < cutoff_date:
                            days_inactive = (datetime.now() - last_access).days
                            
                            cell = DeadCell(
                                path=str(item),
                                size_bytes=stat.st_size,
                                last_accessed=last_access.isoformat(),
                                days_inactive=days_inactive,
                                cell_type="file",
                                recommendation=self._generate_recommendation(item, days_inactive)
                            )
                            dead_cells.append(cell)
                            
                    except (PermissionError, OSError):
                        continue
            
            self.dead_cells = dead_cells
            return dead_cells
            
        except Exception as e:
            raise Exception(f"Erreur scan cellules mortes: {str(e)}")
    
    def _generate_recommendation(self, path: Path, days_inactive: int) -> str:
        """Génère une recommandation pour une cellule morte."""
        size_mb = path.stat().st_size / (1024 * 1024)
        
        if size_mb > 100:
            return f"Archiver (gros fichier: {size_mb:.1f}MB)"
        elif days_inactive > 365:
            return "Supprimer ou archiver (inactif > 1 an)"
        else:
            return "Compresser et archiver"
    
    async def perform_excretion(self, archive_path: str = "C:/System_Archive") -> Dict[str, Any]:
        """Effectue l'excrétion (nettoyage) des cellules mortes."""
        archive_dir = Path(archive_path)
        archive_dir.mkdir(exist_ok=True)
        
        results = {
            "archived": 0,
            "deleted": 0,
            "freed_space_bytes": 0,
            "errors": []
        }
        
        for cell in self.dead_cells[:50]:  # Limiter à 50 par session
            try:
                file_path = Path(cell.path)
                if not file_path.exists():
                    continue
                
                if cell.recommendation.startswith("Supprimer"):
                    file_path.unlink()
                    results["deleted"] += 1
                else:
                    # Archiver
                    relative_path = file_path.relative_to(file_path.anchor)
                    archive_file = archive_dir / relative_path
                    archive_file.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(file_path, archive_file)
                    file_path.unlink()
                    results["archived"] += 1
                
                results["freed_space_bytes"] += cell.size_bytes
                
            except Exception as e:
                results["errors"].append(f"{cell.path}: {str(e)}")
        
        return results
    
    async def cross_pollination(self, source_directory: str, 
                               pattern: str = "*.txt") -> HybridFolder:
        """Effectue la pollinisation croisée (organisation intelligente)."""
        try:
            source_path = Path(source_directory)
            if not source_path.exists():
                raise Exception(f"Répertoire source non trouvé: {source_directory}")
            
            # Collecter les fichiers correspondants
            files = list(source_path.glob(pattern))
            
            if not files:
                raise Exception(f"Aucun fichier trouvé avec le pattern: {pattern}")
            
            # Créer le dossier hybride
            hybrid_name = f"Hybrid_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            hybrid_path = source_path.parent / hybrid_name
            hybrid_path.mkdir(exist_ok=True)
            
            # Analyser et créer des résumés
            summaries = []
            connections = []
            
            for file in files[:10]:  # Limiter à 10 fichiers
                try:
                    content = file.read_text(encoding='utf-8', errors='ignore')
                    
                    # Extraire des mots-clés
                    words = re.findall(r'\b\w+\b', content.lower())
                    word_freq = {}
                    for word in words:
                        if len(word) > 3:
                            word_freq[word] = word_freq.get(word, 0) + 1
                    
                    top_keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:5]
                    
                    # Créer un résumé
                    summary = f"{file.name}: {', '.join([k for k, v in top_keywords])}"
                    summaries.append(summary)
                    
                    # Copier le fichier
                    shutil.copy2(file, hybrid_path / file.name)
                    
                except Exception:
                    continue
            
            # Créer des connexions basées sur les mots-clés communs
            for i in range(len(summaries) - 1):
                connections.append(f"{summmaries[i]} -> {summaries[i+1]}")
            
            # Créer un fichier index
            index_file = hybrid_path / "_hybrid_index.json"
            index_data = {
                "created_at": datetime.now().isoformat(),
                "source_files": [f.name for f in files],
                "summaries": summaries,
                "connections": connections
            }
            index_file.write_text(json.dumps(index_data, indent=2, ensure_ascii=False))
            
            hybrid_folder = HybridFolder(
                source_paths=[str(f) for f in files],
                hybrid_path=str(hybrid_path),
                created_at=datetime.now().isoformat(),
                summaries=summaries,
                connections=connections
            )
            
            self.hybrid_folders.append(hybrid_folder)
            
            return hybrid_folder
            
        except Exception as e:
            raise Exception(f"Erreur pollinisation: {str(e)}")
    
    async def analyze_system_health(self) -> Dict[str, Any]:
        """Analyse la santé du système comme un organisme."""
        try:
            import psutil
            
            # Métriques système
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage("C:/")
            
            # Calcul de l'âge du système
            boot_time = datetime.fromtimestamp(psutil.boot_time())
            system_age = datetime.now() - boot_time
            self.system_age_days = system_age.days
            
            # Évaluation de la santé
            health_score = 100
            
            if cpu_percent > 80:
                health_score -= 20
            if memory.percent > 85:
                health_score -= 15
            if disk.percent > 90:
                health_score -= 25
            
            # Facteur de croissance basé sur l'activité
            self.growth_factor = min(2.0, 1.0 + (len(self.hybrid_folders) * 0.1))
            
            return {
                "health_score": health_score,
                "system_age_days": self.system_age_days,
                "metabolism_rate": self.metabolism_rate,
                "growth_factor": self.growth_factor,
                "vital_signs": {
                    "cpu": cpu_percent,
                    "memory": memory.percent,
                    "disk": disk.percent
                },
                "dead_cells_count": len(self.dead_cells),
                "hybrid_folders_count": len(self.hybrid_folders),
                "status": self._determine_organism_status(health_score)
            }
            
        except Exception as e:
            raise Exception(f"Erreur analyse santé: {str(e)}")
    
    def _determine_organism_status(self, health_score: int) -> str:
        """Détermine le statut de l'organisme."""
        if health_score >= 80:
            return "thriving"
        elif health_score >= 60:
            return "healthy"
        elif health_score >= 40:
            return "stressed"
        else:
            return "critical"
    
    async def auto_maintenance_cycle(self):
        """Cycle de maintenance automatique (métabolisme)."""
        while True:
            try:
                # Scanner les cellules mortes
                await self.scan_for_dead_cells()
                
                # Si trop de cellules mortes, effectuer l'excrétion
                if len(self.dead_cells) > 100:
                    await self.perform_excretion()
                
                # Analyser la santé
                health = await self.analyze_system_health()
                
                # Si le système est stressé, ajuster le métabolisme
                if health["status"] in ["stressed", "critical"]:
                    self.metabolism_rate = 0.8  # Augmenter le nettoyage
                else:
                    self.metabolism_rate = 0.5  # Normal
                
                # Attendre avant le prochain cycle
                await asyncio.sleep(self.auto_clean_interval_hours * 3600)
                
            except Exception as e:
                print(f"Erreur cycle maintenance: {str(e)}")
                await asyncio.sleep(3600)  # Attendre 1h en cas d'erreur
    
    def get_dead_cells_report(self) -> Dict[str, Any]:
        """Génère un rapport sur les cellules mortes."""
        total_size = sum(cell.size_bytes for cell in self.dead_cells)
        
        return {
            "total_dead_cells": len(self.dead_cells),
            "total_size_bytes": total_size,
            "total_size_mb": total_size / (1024 * 1024),
            "oldest_cell": max(self.dead_cells, key=lambda c: c.days_inactive) if self.dead_cells else None,
            "by_recommendation": self._group_by_recommendation()
        }
    
    def _group_by_recommendation(self) -> Dict[str, int]:
        """Groupe les cellules mortes par recommandation."""
        groups = {}
        for cell in self.dead_cells:
            rec = cell.recommendation
            groups[rec] = groups.get(rec, 0) + 1
        return groups
    
    def get_hybrid_folders_report(self) -> List[Dict[str, Any]]:
        """Génère un rapport sur les dossiers hybrides."""
        return [
            {
                "path": folder.hybrid_path,
                "created_at": folder.created_at,
                "source_count": len(folder.source_paths),
                "summaries_count": len(folder.summaries),
                "connections_count": len(folder.connections)
            }
            for folder in self.hybrid_folders
        ]
