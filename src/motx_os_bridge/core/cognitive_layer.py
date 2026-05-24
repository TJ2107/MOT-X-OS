"""
Cognitive Operating Layer (COL)

Articulation de :
  - Génération disciplinaire
  - Raisonnement transdisciplinaire
  - Optimisation V2
  - Automatisation OS
"""

import json
from pathlib import Path
from typing import Any

from ..core.engine import MOTXAutomationEngine
from ..core.planner import TaskPlanner
from ..core.security import SecurityManager
from ..utils.llm_client import LocalLLMClient


class DisciplinaryGenerator:
    """Génère du contenu/code spécialisé par domaine."""
    
    def __init__(self):
        self.llm_client = LocalLLMClient()
        self.domains = {
            "code": "Générer du code Python, JavaScript, PowerShell selon le contexte.",
            "analysis": "Analyser des données, fichiers, logs et extraire des insights.",
            "planning": "Planifier des workflows, projets et séquences d'actions.",
            "documentation": "Générer de la documentation technique et des rapports.",
            "security": "Suggérer des mesures de sécurité et audits."
        }
    
    def generate(self, domain: str, query: str, context: dict | None = None) -> str:
        """Génère du contenu disciplinaire."""
        if domain not in self.domains:
            return f"Domaine '{domain}' non reconnu. Disponibles: {list(self.domains.keys())}"
        
        prompt = f"""Tu es un expert en {domain}.
Domaine description: {self.domains[domain]}
Query: {query}
Context: {json.dumps(context or {})}

Réponds de manière concise et actionnable."""
        
        response = self.llm_client.generate(prompt, max_tokens=512)
        return response


class TransdisciplinaryReasoner:
    """Raisonnement cross-domain pour connecter les savoirs."""
    
    def __init__(self):
        self.llm_client = LocalLLMClient()
        self.knowledge_base = {}
    
    def reason(self, query: str, relevant_domains: list[str]) -> dict:
        """Raisonne sur une question en croisant plusieurs domaines."""
        domains_context = "\n".join([f"- {d}" for d in relevant_domains])
        
        prompt = f"""Tu es un système de raisonnement transdisciplinaire.
Domaines pertinents:
{domains_context}

Raisonne sur cette question en connectant les concepts de ces domaines:
{query}

Réponds au format JSON avec:
{{
  "analysis": "Analyse du problème",
  "cross_domain_insights": ["insight1", "insight2", ...],
  "recommended_approach": "Approche recommandée",
  "domains_used": ["domain1", "domain2", ...]
}}"""
        
        response = self.llm_client.generate(prompt, max_tokens=1024)
        try:
            reasoning = json.loads(response)
        except json.JSONDecodeError:
            reasoning = {
                "analysis": response,
                "cross_domain_insights": [],
                "recommended_approach": "Voir analyse",
                "domains_used": relevant_domains
            }
        reasoning["raw_response"] = response
        return reasoning
    
    def store_knowledge(self, domain: str, key: str, value: Any):
        """Mémorise une connaissance."""
        if domain not in self.knowledge_base:
            self.knowledge_base[domain] = {}
        self.knowledge_base[domain][key] = value
    
    def retrieve_knowledge(self, domain: str, key: str) -> Any:
        """Récupère une connaissance."""
        return self.knowledge_base.get(domain, {}).get(key)


class OptimizationV2:
    """Optimisation itérative avec apprentissage."""
    
    def __init__(self, history_file: Path | None = None):
        self.llm_client = LocalLLMClient()
        self.history_file = history_file or Path("cognitive_optimizations.json")
        self.optimizations = self._load_optimizations()
    
    def _load_optimizations(self) -> dict:
        if self.history_file.exists():
            return json.loads(self.history_file.read_text(encoding="utf-8"))
        return {}
    
    def _save_optimizations(self):
        self.history_file.write_text(json.dumps(self.optimizations, indent=2, ensure_ascii=False), encoding="utf-8")
    
    def analyze_execution(self, task: dict, result: Any, metrics: dict | None = None) -> dict:
        """Analyse une exécution et propose des optimisations."""
        prompt = f"""Analyse cette exécution de tâche et propose des optimisations:

Tâche: {json.dumps(task)}
Résultat: {result}
Métriques: {json.dumps(metrics or {})}

Réponds au format JSON:
{{
  "performance_score": 0.0-1.0,
  "bottlenecks": ["problème1", "problème2"],
  "optimizations": ["optimisation1", "optimisation2"],
  "estimated_improvement": "X% faster/better"
}}"""
        
        response = self.llm_client.generate(prompt, max_tokens=512)
        try:
            optimization = json.loads(response)
        except json.JSONDecodeError:
            optimization = {
                "performance_score": 0.5,
                "bottlenecks": [],
                "optimizations": [response],
                "estimated_improvement": "À évaluer"
            }
        
        task_id = f"{task.get('type')}_{hash(str(task)) % 10000}"
        self.optimizations[task_id] = optimization
        self._save_optimizations()
        
        return optimization
    
    def get_optimization_for_task(self, task: dict) -> dict | None:
        """Récupère une optimisation appliquée précédemment."""
        task_id = f"{task.get('type')}_{hash(str(task)) % 10000}"
        return self.optimizations.get(task_id)


class CognitiveOperatingLayer:
    """
    Couche d'exploitation cognitive : articule l'analyse, la décision, la planification et l'action.
    """
    
    def __init__(self):
        self.engine = MOTXAutomationEngine(interactive=True)
        self.planner = TaskPlanner()
        self.security = SecurityManager()
        
        # Composants cognitifs
        self.disciplinary_gen = DisciplinaryGenerator()
        self.transdisciplinary_reasoner = TransdisciplinaryReasoner()
        self.optimizer = OptimizationV2()
        
        self.execution_log = []
    
    async def analyze(self, instruction: str) -> dict:
        """Phase 1 : Analyse la demande."""
        analysis = {
            "instruction": instruction,
            "analysis_type": self._detect_analysis_type(instruction),
            "relevant_domains": self._extract_domains(instruction),
            "complexity": self._estimate_complexity(instruction)
        }
        return analysis
    
    async def decide(self, analysis: dict) -> dict:
        """Phase 2 : Prend des décisions basées sur l'analyse."""
        reasoning = self.transdisciplinary_reasoner.reason(
            query=analysis["instruction"],
            relevant_domains=analysis["relevant_domains"]
        )
        
        decision = {
            "approach": reasoning.get("recommended_approach"),
            "cross_domain_insights": reasoning.get("cross_domain_insights", []),
            "reasoning": reasoning,
            "confidence": self._calculate_confidence(reasoning)
        }
        return decision
    
    async def plan(self, decision: dict) -> list[dict]:
        """Phase 3 : Planifie les actions."""
        plan = self.planner.build_plan(decision["approach"])
        
        # Enrichit le plan avec des optimisations précédentes
        enriched_plan = []
        for task in plan:
            optimization = self.optimizer.get_optimization_for_task(task)
            task_with_opt = {
                **task,
                "optimization_hint": optimization
            }
            enriched_plan.append(task_with_opt)
        
        return enriched_plan
    
    async def act(self, plan: list[dict]) -> dict:
        """Phase 4 : Exécute le plan et collecte les résultats."""
        results = {
            "tasks_executed": 0,
            "tasks_blocked": 0,
            "tasks_failed": 0,
            "execution_details": []
        }
        
        for task in plan:
            # Valide la sécurité
            allowed, reason, needs_confirmation = self.security.validate(task)
            
            if not allowed and needs_confirmation and self.engine.interactive:
                confirmed = self.engine.confirm_task(task, reason)
                if not confirmed:
                    results["tasks_blocked"] += 1
                    results["execution_details"].append({
                        "task": task,
                        "status": "blocked_by_user",
                        "reason": reason
                    })
                    continue
            
            if not allowed:
                results["tasks_blocked"] += 1
                results["execution_details"].append({
                    "task": task,
                    "status": "blocked",
                    "reason": reason
                })
                continue
            
            # Exécute la tâche
            try:
                if self.engine.dry_run:
                    print(f"✅ [DRY-RUN] Exécution simulée de : {task.get('type')}")
                    result = {"status": "success", "simulated": True}
                else:
                    result = await self.engine.executor.execute(task)
                
                self.engine.memory.store(task, result)
                results["tasks_executed"] += 1
                
                # Détermination de succès (pour éviter d'optimiser les erreurs brutales)
                is_error = False
                if isinstance(result, str) and any(err_kw in result.lower() for err_kw in ["erreur", "error", "exception", "failed", "échec"]):
                    is_error = True
                
                # Analyse pour optimisation
                if not is_error:
                    optimization = self.optimizer.analyze_execution(task, result)
                else:
                    optimization = {"status": "skipped", "reason": "Tâche en échec, optimisation ignorée"}
                
                results["execution_details"].append({
                    "task": task,
                    "status": "executed",
                    "result": result,
                    "optimization": optimization
                })
            except Exception as e:
                results["tasks_failed"] += 1
                results["execution_details"].append({
                    "task": task,
                    "status": "failed",
                    "error": str(e)
                })
        
        return results
    
    async def execute_cognitive_cycle(self, instruction: str) -> dict:
        """Exécute le cycle complet : Analyser → Décider → Planifier → Agir."""
        print("\n" + "="*60)
        print("🧠 COGNITIVE OPERATING LAYER")
        print("="*60)
        
        # Phase 1 : Analyse
        print("\n📊 Phase 1 : Analyse...")
        analysis = await self.analyze(instruction)
        print(f"  Type: {analysis['analysis_type']}")
        print(f"  Domaines pertinents: {', '.join(analysis['relevant_domains'])}")
        print(f"  Complexité: {analysis['complexity']}")
        
        # Phase 2 : Décision
        print("\n🤔 Phase 2 : Décision...")
        decision = await self.decide(analysis)
        print(f"  Approche: {decision['approach']}")
        print(f"  Confiance: {decision['confidence']:.0%}")
        print(f"  Insights transdisciplinaires: {len(decision['cross_domain_insights'])} insights")
        
        # Phase 3 : Planification
        print("\n📋 Phase 3 : Planification...")
        plan = await self.plan(decision)
        print(f"  Tâches planifiées: {len(plan)}")
        for i, task in enumerate(plan, 1):
            print(f"    {i}. {task['type']}")
        
        # Phase 4 : Action
        print("\n⚡ Phase 4 : Exécution...")
        results = await self.act(plan)
        print(f"  ✓ Exécutées: {results['tasks_executed']}")
        print(f"  ⊘ Bloquées: {results['tasks_blocked']}")
        print(f"  ✗ Échouées: {results['tasks_failed']}")
        
        self.execution_log.append({
            "instruction": instruction,
            "analysis": analysis,
            "decision": decision,
            "plan": plan,
            "results": results
        })
        
        print("\n" + "="*60)
        return {
            "analysis": analysis,
            "decision": decision,
            "plan": plan,
            "results": results,
            "cycle_complete": True
        }
    
    def _detect_analysis_type(self, instruction: str) -> str:
        keywords = {
            "automation": ["exécute", "lance", "automatise", "fais"],
            "analysis": ["analyse", "évalue", "examine", "regarde"],
            "generation": ["crée", "génère", "écris", "produis"],
            "optimization": ["optimise", "accélère", "améliore"],
            "learning": ["apprend", "mémorize", "enregistre"]
        }
        
        instruction_lower = instruction.lower()
        for analysis_type, keywords_list in keywords.items():
            if any(kw in instruction_lower for kw in keywords_list):
                return analysis_type
        
        return "general"
    
    def _extract_domains(self, instruction: str) -> list[str]:
        domain_keywords = {
            "code": ["code", "script", "python", "powershell"],
            "analysis": ["analyse", "évalue", "examine", "données"],
            "planning": ["plan", "workflow", "séquence", "étapes"],
            "security": ["sécurité", "sécurise", "sécurisé", "protège"],
            "documentation": ["document", "écris", "rapport"]
        }
        
        instruction_lower = instruction.lower()
        relevant_domains = []
        for domain, keywords in domain_keywords.items():
            if any(kw in instruction_lower for kw in keywords):
                relevant_domains.append(domain)
        
        return relevant_domains or ["general"]
    
    def _estimate_complexity(self, instruction: str) -> str:
        word_count = len(instruction.split())
        keyword_count = sum(1 for kw in ["et", "puis", "ensuite", "aussi"] if kw in instruction.lower())
        
        if keyword_count >= 2 and word_count >= 6:
            return "complex"

        complexity_score = word_count + (keyword_count * 3)

        if complexity_score < 12:
            return "simple"
        elif complexity_score < 30:
            return "moderate"
        else:
            return "complex"
    
    def _calculate_confidence(self, reasoning: dict) -> float:
        insights_count = len(reasoning.get("cross_domain_insights", []))
        domains_count = len(reasoning.get("domains_used", []))
        
        base_confidence = 0.7
        confidence = min(0.95, base_confidence + (insights_count * 0.05) + (domains_count * 0.05))
        
        return confidence
