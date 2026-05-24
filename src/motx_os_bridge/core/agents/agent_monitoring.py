"""
Agent Monitoring - Agent spécialisé pour le monitoring système.
"""

import asyncio
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime, timedelta
import json
import time


@dataclass
class SystemMetric:
    """Représente une métrique système."""
    name: str
    value: float
    unit: str
    timestamp: str
    threshold: Optional[float] = None
    status: str = "normal"  # normal, warning, critical


@dataclass
class Alert:
    """Représente une alerte système."""
    metric_name: str
    severity: str  # info, warning, critical
    message: str
    timestamp: str
    value: float
    threshold: float


class AgentMonitoring:
    """Agent spécialisé pour le monitoring système."""
    
    def __init__(self):
        self.metrics_history: List[SystemMetric] = []
        self.alerts: List[Alert] = []
        self.thresholds: Dict[str, float] = {
            "cpu_usage": 80.0,
            "memory_usage": 85.0,
            "disk_usage": 90.0,
            "temperature": 70.0
        }
        self.is_monitoring = False
        self.monitoring_interval = 5  # secondes
        
        # Vérification des dépendances
        self._check_dependencies()
    
    def _check_dependencies(self):
        """Vérifie les dépendances disponibles."""
        self.has_psutil = self._try_import('psutil')
        
        if not self.has_psutil:
            print("⚠️ psutil non installé - Monitoring système limité")
    
    def _try_import(self, module_name: str) -> bool:
        """Tente d'importer un module."""
        try:
            __import__(module_name)
            return True
        except ImportError:
            return False
    
    async def get_cpu_usage(self) -> SystemMetric:
        """Récupère l'utilisation CPU."""
        if not self.has_psutil:
            return SystemMetric(
                name="cpu_usage",
                value=0.0,
                unit="%",
                timestamp=datetime.now().isoformat(),
                status="unknown"
            )
        
        try:
            import psutil
            
            cpu_percent = psutil.cpu_percent(interval=1)
            threshold = self.thresholds["cpu_usage"]
            
            status = "normal"
            if cpu_percent >= threshold:
                status = "critical"
            elif cpu_percent >= threshold * 0.8:
                status = "warning"
            
            metric = SystemMetric(
                name="cpu_usage",
                value=cpu_percent,
                unit="%",
                timestamp=datetime.now().isoformat(),
                threshold=threshold,
                status=status
            )
            
            self.metrics_history.append(metric)
            await self._check_alert(metric)
            
            return metric
            
        except Exception as e:
            raise Exception(f"Erreur récupération CPU: {str(e)}")
    
    async def get_memory_usage(self) -> SystemMetric:
        """Récupère l'utilisation mémoire."""
        if not self.has_psutil:
            return SystemMetric(
                name="memory_usage",
                value=0.0,
                unit="%",
                timestamp=datetime.now().isoformat(),
                status="unknown"
            )
        
        try:
            import psutil
            
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            threshold = self.thresholds["memory_usage"]
            
            status = "normal"
            if memory_percent >= threshold:
                status = "critical"
            elif memory_percent >= threshold * 0.8:
                status = "warning"
            
            metric = SystemMetric(
                name="memory_usage",
                value=memory_percent,
                unit="%",
                timestamp=datetime.now().isoformat(),
                threshold=threshold,
                status=status
            )
            
            self.metrics_history.append(metric)
            await self._check_alert(metric)
            
            return metric
            
        except Exception as e:
            raise Exception(f"Erreur récupération mémoire: {str(e)}")
    
    async def get_disk_usage(self, path: str = "/") -> SystemMetric:
        """Récupère l'utilisation disque."""
        if not self.has_psutil:
            return SystemMetric(
                name="disk_usage",
                value=0.0,
                unit="%",
                timestamp=datetime.now().isoformat(),
                status="unknown"
            )
        
        try:
            import psutil
            
            disk = psutil.disk_usage(path)
            disk_percent = disk.percent
            threshold = self.thresholds["disk_usage"]
            
            status = "normal"
            if disk_percent >= threshold:
                status = "critical"
            elif disk_percent >= threshold * 0.8:
                status = "warning"
            
            metric = SystemMetric(
                name="disk_usage",
                value=disk_percent,
                unit="%",
                timestamp=datetime.now().isoformat(),
                threshold=threshold,
                status=status
            )
            
            self.metrics_history.append(metric)
            await self._check_alert(metric)
            
            return metric
            
        except Exception as e:
            raise Exception(f"Erreur récupération disque: {str(e)}")
    
    async def get_network_stats(self) -> Dict[str, Any]:
        """Récupère les statistiques réseau."""
        if not self.has_psutil:
            return {"error": "psutil non installé"}
        
        try:
            import psutil
            
            net_io = psutil.net_io_counters()
            net_connections = len(psutil.net_connections())
            
            return {
                "bytes_sent": net_io.bytes_sent,
                "bytes_recv": net_io.bytes_recv,
                "packets_sent": net_io.packets_sent,
                "packets_recv": net_io.packets_recv,
                "connections": net_connections,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            raise Exception(f"Erreur récupération réseau: {str(e)}")
    
    async def get_process_list(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Récupère la liste des processus."""
        if not self.has_psutil:
            return []
        
        try:
            import psutil
            
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    processes.append({
                        "pid": proc.info['pid'],
                        "name": proc.info['name'],
                        "cpu_percent": proc.info['cpu_percent'],
                        "memory_percent": proc.info['memory_percent']
                    })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # Trier par utilisation CPU
            processes.sort(key=lambda x: x['cpu_percent'] or 0, reverse=True)
            
            return processes[:limit]
            
        except Exception as e:
            raise Exception(f"Erreur récupération processus: {str(e)}")
    
    async def get_system_info(self) -> Dict[str, Any]:
        """Récupère les informations système complètes."""
        if not self.has_psutil:
            return {"error": "psutil non installé"}
        
        try:
            import psutil
            import platform
            
            return {
                "system": platform.system(),
                "node": platform.node(),
                "release": platform.release(),
                "version": platform.version(),
                "machine": platform.machine(),
                "processor": platform.processor(),
                "cpu_count": psutil.cpu_count(),
                "cpu_count_logical": psutil.cpu_count(logical=True),
                "memory_total": psutil.virtual_memory().total,
                "memory_available": psutil.virtual_memory().available,
                "boot_time": datetime.fromtimestamp(psutil.boot_time()).isoformat(),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            raise Exception(f"Erreur récupération infos système: {str(e)}")
    
    async def start_monitoring(self, duration: Optional[int] = None):
        """Démarre le monitoring continu."""
        self.is_monitoring = True
        start_time = time.time()
        
        while self.is_monitoring:
            if duration and (time.time() - start_time) > duration:
                break
            
            try:
                # Collecte des métriques
                await self.get_cpu_usage()
                await self.get_memory_usage()
                await self.get_disk_usage()
                
                await asyncio.sleep(self.monitoring_interval)
                
            except Exception as e:
                print(f"Erreur monitoring: {str(e)}")
                await asyncio.sleep(self.monitoring_interval)
    
    def stop_monitoring(self):
        """Arrête le monitoring continu."""
        self.is_monitoring = False
    
    async def _check_alert(self, metric: SystemMetric):
        """Vérifie si une alerte doit être générée."""
        if metric.status in ["warning", "critical"]:
            severity = metric.status
            
            alert = Alert(
                metric_name=metric.name,
                severity=severity,
                message=f"{metric.name} à {metric.value}{metric.unit} (seuil: {metric.threshold}{metric.unit})",
                timestamp=metric.timestamp,
                value=metric.value,
                threshold=metric.threshold or 0
            )
            
            self.alerts.append(alert)
            print(f"🚨 ALERTE [{severity.upper()}]: {alert.message}")
    
    def set_threshold(self, metric_name: str, threshold: float):
        """Définit un seuil pour une métrique."""
        self.thresholds[metric_name] = threshold
    
    def get_metrics_history(self, metric_name: Optional[str] = None, hours: int = 1) -> List[SystemMetric]:
        """Retourne l'historique des métriques."""
        cutoff = datetime.now() - timedelta(hours=hours)
        
        if metric_name:
            return [m for m in self.metrics_history 
                   if m.name == metric_name and datetime.fromisoformat(m.timestamp) > cutoff]
        
        return [m for m in self.metrics_history 
               if datetime.fromisoformat(m.timestamp) > cutoff]
    
    def get_alerts(self, severity: Optional[str] = None, hours: int = 24) -> List[Alert]:
        """Retourne les alertes."""
        cutoff = datetime.now() - timedelta(hours=hours)
        
        if severity:
            return [a for a in self.alerts 
                   if a.severity == severity and datetime.fromisoformat(a.timestamp) > cutoff]
        
        return [a for a in self.alerts 
               if datetime.fromisoformat(a.timestamp) > cutoff]
    
    def clear_alerts(self):
        """Efface les alertes."""
        self.alerts.clear()
    
    def clear_metrics_history(self):
        """Efface l'historique des métriques."""
        self.metrics_history.clear()
    
    async def generate_report(self) -> Dict[str, Any]:
        """Génère un rapport de monitoring."""
        cpu_metric = await self.get_cpu_usage()
        memory_metric = await self.get_memory_usage()
        disk_metric = await self.get_disk_usage()
        
        recent_alerts = self.get_alerts(hours=24)
        
        return {
            "timestamp": datetime.now().isoformat(),
            "current_metrics": {
                "cpu": {
                    "value": cpu_metric.value,
                    "unit": cpu_metric.unit,
                    "status": cpu_metric.status
                },
                "memory": {
                    "value": memory_metric.value,
                    "unit": memory_metric.unit,
                    "status": memory_metric.status
                },
                "disk": {
                    "value": disk_metric.value,
                    "unit": disk_metric.unit,
                    "status": disk_metric.status
                }
            },
            "alerts_count": len(recent_alerts),
            "critical_alerts": len([a for a in recent_alerts if a.severity == "critical"]),
            "warning_alerts": len([a for a in recent_alerts if a.severity == "warning"]),
            "monitoring_active": self.is_monitoring
        }
