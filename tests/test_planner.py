from src.motx_os_bridge.core.planner import TaskPlanner


class DummyLLMClient:
    def generate(self, prompt: str, max_tokens: int = 512) -> str:
        return '[{"type":"FILE_LIST","directory":"C:/temp"}]'


class StubLLMClient:
    def generate(self, prompt: str, max_tokens: int = 512) -> str:
        return "[LLM stub] fallback"


def test_planner_uses_llm_prediction_when_available(monkeypatch):
    planner = TaskPlanner()
    monkeypatch.setattr(planner, "llm_client", DummyLLMClient())
    plan = planner.build_plan("lister le dossier temporaire")

    assert len(plan) == 1
    assert plan[0]["type"] == "FILE_LIST"
    assert plan[0]["directory"] == "C:/temp"


def test_planner_falls_back_to_rules_when_llm_returns_stub(monkeypatch):
    planner = TaskPlanner()
    monkeypatch.setattr(planner, "llm_client", StubLLMClient())
    plan = planner.build_plan("ouvrir notepad")

    assert any(task["type"] == "OPEN_APP" for task in plan)
