"""
Test suite pour la Cognitive Operating Layer
"""

import pytest
from src.motx_os_bridge.core.cognitive_layer import (
    DisciplinaryGenerator,
    TransdisciplinaryReasoner,
    OptimizationV2,
    CognitiveOperatingLayer
)


def test_disciplinary_generator_rejects_unknown_domain():
    gen = DisciplinaryGenerator()
    result = gen.generate("unknown_domain", "test query")
    assert "non reconnu" in result


def test_disciplinary_generator_supports_known_domains():
    gen = DisciplinaryGenerator()
    known_domains = ["code", "analysis", "planning", "documentation", "security"]
    for domain in known_domains:
        assert domain in gen.domains


def test_transdisciplinary_reasoner_cross_domain_reasoning():
    reasoner = TransdisciplinaryReasoner()
    reasoning = reasoner.reason(
        "Optimize a Python script for performance",
        ["code", "analysis", "optimization"]
    )
    
    assert "analysis" in reasoning or isinstance(reasoning.get("analysis"), str)
    assert isinstance(reasoning.get("cross_domain_insights"), list)


def test_transdisciplinary_reasoner_memory():
    reasoner = TransdisciplinaryReasoner()
    reasoner.store_knowledge("domain_x", "key_y", "value_z")
    retrieved = reasoner.retrieve_knowledge("domain_x", "key_y")
    
    assert retrieved == "value_z"


def test_optimization_v2_analyze_execution(tmp_path):
    optimizer = OptimizationV2(history_file=tmp_path / "opt.json")
    
    task = {"type": "FILE_COPY", "source": "a.txt", "destination": "b.txt"}
    result = "File copied successfully"
    metrics = {"time_ms": 250, "bytes_copied": 1024}
    
    optimization = optimizer.analyze_execution(task, result, metrics)
    
    assert "performance_score" in optimization
    assert "bottlenecks" in optimization
    assert "optimizations" in optimization


def test_optimization_v2_get_optimization_for_task(tmp_path):
    optimizer = OptimizationV2(history_file=tmp_path / "opt.json")
    
    task = {"type": "EXECUTE_PYTHON", "script": "print('hello')"}
    first_analysis = optimizer.analyze_execution(task, "success", {"time_ms": 100})
    
    retrieved = optimizer.get_optimization_for_task(task)
    assert retrieved is not None
    assert retrieved["performance_score"] == first_analysis["performance_score"]


@pytest.mark.asyncio
async def test_cognitive_operating_layer_analyze():
    col = CognitiveOperatingLayer()
    analysis = await col.analyze("Ouvre notepad et crée un dossier")
    
    assert "instruction" in analysis
    assert "analysis_type" in analysis
    assert "relevant_domains" in analysis
    assert "complexity" in analysis


@pytest.mark.asyncio
async def test_cognitive_operating_layer_decide():
    col = CognitiveOperatingLayer()
    analysis = await col.analyze("Ouvre notepad")
    decision = await col.decide(analysis)
    
    assert "approach" in decision
    assert "cross_domain_insights" in decision
    assert "confidence" in decision
    assert 0 <= decision["confidence"] <= 1


@pytest.mark.asyncio
async def test_cognitive_operating_layer_plan():
    col = CognitiveOperatingLayer()
    analysis = await col.analyze("Crée un dossier test")
    decision = await col.decide(analysis)
    plan = await col.plan(decision)
    
    assert isinstance(plan, list)


def test_cognitive_operating_layer_detect_analysis_type():
    col = CognitiveOperatingLayer()
    
    assert col._detect_analysis_type("exécute ce script") == "automation"
    assert col._detect_analysis_type("analyse les données") == "analysis"
    assert col._detect_analysis_type("crée un rapport") == "generation"


def test_cognitive_operating_layer_extract_domains():
    col = CognitiveOperatingLayer()
    
    domains = col._extract_domains("Écris du code Python sécurisé")
    assert "code" in domains
    assert "security" in domains


def test_cognitive_operating_layer_estimate_complexity():
    col = CognitiveOperatingLayer()
    
    assert col._estimate_complexity("ouvre notepad") == "simple"
    assert col._estimate_complexity("fais ceci et cela et aussi autre chose") == "complex"


def test_cognitive_operating_layer_calculate_confidence():
    col = CognitiveOperatingLayer()
    
    reasoning_low = {"cross_domain_insights": [], "domains_used": []}
    reasoning_high = {"cross_domain_insights": ["i1", "i2", "i3"], "domains_used": ["d1", "d2"]}
    
    conf_low = col._calculate_confidence(reasoning_low)
    conf_high = col._calculate_confidence(reasoning_high)
    
    assert conf_low < conf_high
    assert conf_low >= 0.7 and conf_low <= 1.0
    assert conf_high >= 0.7 and conf_high <= 1.0
