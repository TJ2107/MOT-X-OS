"""
Multi-Agent System - Orchestrateur des agents spécialisés.
"""

import asyncio
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum
import json


class AgentType(Enum):
    """Types d'agents disponibles."""
    BROWSER = "browser"
    VISION = "vision"
    VOICE = "voice"
    SECURITY = "security"
    RESEARCH = "research"
    DEVELOPMENT = "development"
    MONITORING = "monitoring"


@dataclass
class AgentTask:
    """Représente une tâche assignée à un agent."""
    task_id: str
    agent_type: AgentType
    instruction: str
    parameters: Dict[str, Any]
    status: str = "pending"  # pending, in_progress, completed, failed
    result: Optional[Any] = None
    error: Optional[str] = None
    timestamp: str = ""


@dataclass
class AgentResponse:
    """Représente une réponse d'un agent."""
    agent_type: AgentType
    task_id: str
    success: bool
    data: Any
    metadata: Dict[str, Any]
    timestamp: str


class MultiAgentSystem:
    """Système multi-agents pour l'orchestration des agents spécialisés."""
    
    def __init__(self):
        self.agents: Dict[AgentType, Any] = {}
        self.task_queue: List[AgentTask] = []
        self.completed_tasks: List[AgentTask] = []
        self.active_tasks: Dict[str, AgentTask] = {}
        
        # Initialisation des agents
        self._initialize_agents()
    
    def _initialize_agents(self):
        """Initialise tous les agents disponibles."""
        try:
            from .agents.agent_browser import AgentBrowser
            self.agents[AgentType.BROWSER] = AgentBrowser()
        except Exception as e:
            print(f"WARNING: Impossible d'initialiser Agent Browser: {e}")
        
        try:
            from .vision_engine import VisionEngine
            self.agents[AgentType.VISION] = VisionEngine()
        except Exception as e:
            print(f"WARNING: Impossible d'initialiser Vision Engine: {e}")
        
        try:
            from .voice_interface import VoiceInterface
            self.agents[AgentType.VOICE] = VoiceInterface()
        except Exception as e:
            print(f"WARNING: Impossible d'initialiser Voice Interface: {e}")
        
        try:
            from .agents.agent_security import AgentSecurity
            self.agents[AgentType.SECURITY] = AgentSecurity()
        except Exception as e:
            print(f"WARNING: Impossible d'initialiser Agent Security: {e}")
        
        try:
            from .agents.agent_research import AgentResearch
            self.agents[AgentType.RESEARCH] = AgentResearch()
        except Exception as e:
            print(f"WARNING: Impossible d'initialiser Agent Research: {e}")
        
        try:
            from .agents.agent_development import AgentDevelopment
            self.agents[AgentType.DEVELOPMENT] = AgentDevelopment()
        except Exception as e:
            print(f"WARNING: Impossible d'initialiser Agent Development: {e}")
        
        try:
            from .agents.agent_monitoring import AgentMonitoring
            self.agents[AgentType.MONITORING] = AgentMonitoring()
        except Exception as e:
            print(f"WARNING: Impossible d'initialiser Agent Monitoring: {e}")
        
        print(f"INFO: {len(self.agents)} agents initialises")
    
    async def dispatch_task(self, agent_type: AgentType, instruction: str, parameters: Dict[str, Any] = None) -> AgentResponse:
        """Dispatche une tâche à un agent spécifique."""
        if agent_type not in self.agents:
            return AgentResponse(
                agent_type=agent_type,
                task_id="",
                success=False,
                data=None,
                metadata={"error": f"Agent {agent_type} non disponible"},
                timestamp=self._get_timestamp()
            )
        
        agent = self.agents[agent_type]
        task_id = f"{agent_type.value}_{len(self.completed_tasks)}"
        
        task = AgentTask(
            task_id=task_id,
            agent_type=agent_type,
            instruction=instruction,
            parameters=parameters or {},
            timestamp=self._get_timestamp()
        )
        
        self.task_queue.append(task)
        self.active_tasks[task_id] = task
        
        try:
            task.status = "in_progress"
            result = await self._execute_agent_task(agent, agent_type, instruction, parameters)
            
            task.status = "completed"
            task.result = result
            self.completed_tasks.append(task)
            del self.active_tasks[task_id]
            
            return AgentResponse(
                agent_type=agent_type,
                task_id=task_id,
                success=True,
                data=result,
                metadata={"status": "completed"},
                timestamp=self._get_timestamp()
            )
            
        except Exception as e:
            task.status = "failed"
            task.error = str(e)
            self.completed_tasks.append(task)
            del self.active_tasks[task_id]
            
            return AgentResponse(
                agent_type=agent_type,
                task_id=task_id,
                success=False,
                data=None,
                metadata={"error": str(e)},
                timestamp=self._get_timestamp()
            )
    
    async def _execute_agent_task(self, agent: Any, agent_type: AgentType, instruction: str, parameters: Dict[str, Any]) -> Any:
        """Exécute une tâche sur un agent spécifique."""
        if agent_type == AgentType.BROWSER:
            return await self._execute_browser_task(agent, instruction, parameters)
        elif agent_type == AgentType.VISION:
            return await self._execute_vision_task(agent, instruction, parameters)
        elif agent_type == AgentType.VOICE:
            return await self._execute_voice_task(agent, instruction, parameters)
        elif agent_type == AgentType.SECURITY:
            return await self._execute_security_task(agent, instruction, parameters)
        elif agent_type == AgentType.RESEARCH:
            return await self._execute_research_task(agent, instruction, parameters)
        elif agent_type == AgentType.DEVELOPMENT:
            return await self._execute_development_task(agent, instruction, parameters)
        elif agent_type == AgentType.MONITORING:
            return await self._execute_monitoring_task(agent, instruction, parameters)
        else:
            raise Exception(f"Type d'agent non supporté: {agent_type}")
    
    async def _execute_browser_task(self, agent: Any, instruction: str, parameters: Dict[str, Any]) -> Any:
        """Exécute une tâche du navigateur."""
        action = parameters.get("action", "navigate")
        
        if action == "navigate":
            url = parameters.get("url")
            return await agent.navigate(url)
        elif action == "search":
            query = parameters.get("query")
            engine = parameters.get("engine", "google")
            return await agent.search(query, engine)
        elif action == "extract":
            selectors = parameters.get("selectors", {})
            return await agent.extract_data(selectors)
        elif action == "download":
            url = parameters.get("url")
            destination = parameters.get("destination")
            return await agent.download_file(url, destination)
        else:
            raise Exception(f"Action navigateur non supportée: {action}")
    
    async def _execute_vision_task(self, agent: Any, instruction: str, parameters: Dict[str, Any]) -> Any:
        """Exécute une tâche de vision."""
        action = parameters.get("action", "capture")
        
        if action == "capture":
            region = parameters.get("region")
            save_path = parameters.get("save_path")
            return await agent.capture_screen(region, save_path)
        elif action == "ocr":
            image_path = parameters.get("image_path")
            lang = parameters.get("lang", "eng")
            if image_path:
                return await agent.ocr_image(image_path, lang)
            else:
                return await agent.ocr_screen(parameters.get("region"), lang)
        elif action == "detect_ui":
            image_path = parameters.get("image_path")
            return await agent.detect_ui_elements(image_path)
        elif action == "find_text":
            text = parameters.get("text")
            region = parameters.get("region")
            return await agent.find_text_on_screen(text, region)
        elif action == "click":
            x = parameters.get("x")
            y = parameters.get("y")
            return await agent.click_at_position(x, y)
        else:
            raise Exception(f"Action vision non supportée: {action}")
    
    async def _execute_voice_task(self, agent: Any, instruction: str, parameters: Dict[str, Any]) -> Any:
        """Exécute une tâche vocale."""
        action = parameters.get("action", "listen")
        
        if action == "listen":
            timeout = parameters.get("timeout", 5)
            return await agent.listen_command(timeout)
        elif action == "speak":
            text = parameters.get("text")
            rate = parameters.get("rate", 150)
            volume = parameters.get("volume", 0.9)
            return await agent.speak(text, rate, volume)
        elif action == "start_listening":
            callback = parameters.get("callback")
            return await agent.start_continuous_listening(callback)
        elif action == "stop_listening":
            return agent.stop_listening()
        else:
            raise Exception(f"Action vocale non supportée: {action}")
    
    async def _execute_security_task(self, agent: Any, instruction: str, parameters: Dict[str, Any]) -> Any:
        """Exécute une tâche de sécurité."""
        action = parameters.get("action", "validate")
        
        if action == "validate":
            action_data = parameters.get("action_data", {})
            return await agent.validate_action(action_data)
        elif action == "audit":
            return await agent.audit_system()
        elif action == "scan":
            directory = parameters.get("directory")
            return await agent.scan_files(directory)
        elif action == "check_password":
            password = parameters.get("password")
            return await agent.check_password_strength(password)
        else:
            raise Exception(f"Action sécurité non supportée: {action}")
    
    async def _execute_research_task(self, agent: Any, instruction: str, parameters: Dict[str, Any]) -> Any:
        """Exécute une tâche de recherche."""
        action = parameters.get("action", "search")
        
        if action == "search":
            query = parameters.get("query")
            engine = parameters.get("engine", "google")
            max_results = parameters.get("max_results", 10)
            return await agent.search_web(query, engine, max_results)
        elif action == "deep_research":
            query = parameters.get("query")
            depth = parameters.get("depth", 2)
            return await agent.deep_research(query, depth)
        elif action == "analyze":
            data = parameters.get("data")
            analysis_type = parameters.get("analysis_type", "general")
            return await agent.analyze_data(data, analysis_type)
        elif action == "compare":
            sources = parameters.get("sources")
            return await agent.compare_sources(sources)
        else:
            raise Exception(f"Action recherche non supportée: {action}")
    
    async def _execute_development_task(self, agent: Any, instruction: str, parameters: Dict[str, Any]) -> Any:
        """Exécute une tâche de développement."""
        action = parameters.get("action", "analyze")
        
        if action == "analyze":
            file_path = parameters.get("file_path")
            return await agent.analyze_code(file_path)
        elif action == "generate":
            template_name = parameters.get("template_name")
            return await agent.generate_code(template_name, **parameters)
        elif action == "refactor":
            code = parameters.get("code")
            refactor_type = parameters.get("refactor_type", "cleanup")
            return await agent.refactor_code(code, refactor_type)
        elif action == "analyze_project":
            project_path = parameters.get("project_path")
            return await agent.analyze_project(project_path)
        elif action == "run_tests":
            project_path = parameters.get("project_path")
            return await agent.run_tests(project_path)
        elif action == "create_project":
            project_name = parameters.get("project_name")
            project_type = parameters.get("project_type", "python")
            return await agent.create_project_structure(project_name, project_type)
        else:
            raise Exception(f"Action développement non supportée: {action}")
    
    async def _execute_monitoring_task(self, agent: Any, instruction: str, parameters: Dict[str, Any]) -> Any:
        """Exécute une tâche de monitoring."""
        action = parameters.get("action", "get_cpu")
        
        if action == "get_cpu":
            return await agent.get_cpu_usage()
        elif action == "get_memory":
            return await agent.get_memory_usage()
        elif action == "get_disk":
            path = parameters.get("path", "/")
            return await agent.get_disk_usage(path)
        elif action == "get_network":
            return await agent.get_network_stats()
        elif action == "get_processes":
            limit = parameters.get("limit", 20)
            return await agent.get_process_list(limit)
        elif action == "get_system_info":
            return await agent.get_system_info()
        elif action == "start_monitoring":
            duration = parameters.get("duration")
            return await agent.start_monitoring(duration)
        elif action == "stop_monitoring":
            return agent.stop_monitoring()
        elif action == "generate_report":
            return await agent.generate_report()
        else:
            raise Exception(f"Action monitoring non supportée: {action}")
    
    async def coordinate_agents(self, instruction: str) -> Dict[str, Any]:
        """Coordonne plusieurs agents pour une instruction complexe."""
        # Analyse de l'instruction pour déterminer quels agents utiliser
        required_agents = self._determine_required_agents(instruction)
        
        if not required_agents:
            return {"error": "Aucun agent approprié trouvé"}
        
        results = {}
        
        # Exécution parallèle des tâches
        tasks = []
        for agent_type in required_agents:
            task = self.dispatch_task(agent_type, instruction, {"action": "auto"})
            tasks.append(task)
        
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        for i, response in enumerate(responses):
            if isinstance(response, Exception):
                results[required_agents[i].value] = {"error": str(response)}
            else:
                results[required_agents[i].value] = {
                    "success": response.success,
                    "data": response.data,
                    "metadata": response.metadata
                }
        
        return {
            "instruction": instruction,
            "agents_used": [a.value for a in required_agents],
            "results": results,
            "timestamp": self._get_timestamp()
        }
    
    def _determine_required_agents(self, instruction: str) -> List[AgentType]:
        """Détermine quels agents sont nécessaires pour une instruction."""
        instruction_lower = instruction.lower()
        required_agents = []
        
        # Mots-clés pour chaque agent
        agent_keywords = {
            AgentType.BROWSER: ["navigate", "web", "site", "url", "browser", "internet", "télécharger"],
            AgentType.VISION: ["ocr", "écran", "screen", "capture", "vision", "image", "reconnaissance"],
            AgentType.VOICE: ["vocal", "voice", "parole", "speak", "écoute", "micro", "tts"],
            AgentType.SECURITY: ["sécurité", "security", "audit", "scan", "vérifier", "protéger"],
            AgentType.RESEARCH: ["recherche", "research", "analyser", "étude", "enquête"],
            AgentType.DEVELOPMENT: ["code", "développement", "programme", "script", "test", "refactor"],
            AgentType.MONITORING: ["monitor", "surveillance", "cpu", "mémoire", "performance", "système"]
        }
        
        for agent_type, keywords in agent_keywords.items():
            if any(kw in instruction_lower for kw in keywords):
                required_agents.append(agent_type)
        
        return required_agents
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Retourne le statut de tous les agents."""
        status = {
            "total_agents": len(self.agents),
            "available_agents": [agent_type.value for agent_type in self.agents.keys()],
            "active_tasks": len(self.active_tasks),
            "completed_tasks": len(self.completed_tasks),
            "pending_tasks": len(self.task_queue)
        }
        
        return status
    
    def get_task_history(self, agent_type: Optional[AgentType] = None) -> List[AgentTask]:
        """Retourne l'historique des tâches."""
        if agent_type:
            return [t for t in self.completed_tasks if t.agent_type == agent_type]
        return self.completed_tasks
    
    def clear_task_history(self):
        """Efface l'historique des tâches."""
        self.completed_tasks.clear()
    
    def _get_timestamp(self) -> str:
        """Retourne l'horodatage actuel."""
        from datetime import datetime
        return datetime.now().isoformat()
