import json
import threading
from http.client import HTTPConnection
from http.server import HTTPServer

from src.motx_os_bridge.api.server import MOTXRequestHandler
from src.motx_os_bridge.core.engine import MOTXAutomationEngine
from src.motx_os_bridge.core.memory import MemoryManager


def _start_test_server(port=0, token=None, engine=None, multi_agent_system=None):
    MOTXRequestHandler.engine = engine or MOTXAutomationEngine()
    MOTXRequestHandler.api_token = token
    MOTXRequestHandler.multi_agent_system = multi_agent_system
    server = HTTPServer(("127.0.0.1", port), MOTXRequestHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, thread


def _request(method, path, body=None, headers=None, port=None):
    conn = HTTPConnection("127.0.0.1", port)
    if body is not None and isinstance(body, dict):
        body = json.dumps(body)
    conn.request(method, path, body=body, headers=headers or {})
    response = conn.getresponse()
    data = response.read().decode("utf-8")
    try:
        payload = json.loads(data)
    except json.JSONDecodeError:
        payload = data
    conn.close()
    return response.status, payload


class StubEnhancedEngine:
    async def process_instruction(self, instruction):
        return [{"type": "stub_task", "status": "success"}]

    async def get_gamification_state(self):
        return {
            "level": 2,
            "experience_points": 150,
            "streak": 2,
            "badges": [{"id": "first_automation", "name": "🌟 Initié"}],
            "daily_challenges": [{"id": "daily_automation", "name": "Automatiseur Quotidien", "progress": 1, "target": 5}]
        }

    async def get_analytics(self):
        return {
            "overview": {
                "total_automations": 1,
                "success_rate": 100.0,
                "total_tasks_executed": 1,
                "time_saved_estimate": "2.5 minutes",
                "insight_generated": 0
            },
            "performance_metrics": {
                "average_execution_time": 1.0,
                "fastest_execution": 1.0,
                "slowest_execution": 1.0,
                "performance_trend": "stable"
            },
            "execution_timeline": [],
            "discipline_impact": {},
            "predictions": {},
            "recommendations": []
        }

    async def get_predictions(self):
        return {
            "predicted_next_action": "Continue automating",
            "estimated_success_probability": 0.95,
            "recommended_next_step": "Review latest automation results"
        }

    async def get_full_dashboard(self):
        return {
            "cognitive": {"nodes": 3, "collective_insights": 1, "emergence_patterns": 1},
            "gamification": await self.get_gamification_state(),
            "predictions": await self.get_predictions(),
            "analytics": await self.get_analytics(),
            "narrative": {"current_arc": "intro", "story_events": 0},
            "execution_history_count": 1
        }


class StubMultiAgentSystem:
    def get_agent_status(self):
        return {
            "total_agents": 1,
            "available_agents": ["browser"],
            "active_tasks": 0,
            "completed_tasks": 0,
            "pending_tasks": 0
        }

    async def coordinate_agents(self, instruction):
        return {
            "instruction": instruction,
            "agents_used": ["browser"],
            "results": {
                "browser": {
                    "success": True,
                    "data": {"navigated": True},
                    "metadata": {"status": "completed"}
                }
            },
            "timestamp": "2025-01-01T00:00:00"
        }


def test_api_status_endpoint_returns_ok():
    server, thread = _start_test_server(port=0)
    port = server.server_address[1]
    status, payload = _request("GET", "/status", port=port)
    server.shutdown()
    thread.join(timeout=1)

    assert status == 200
    assert payload["status"] == "ok"
    assert payload["service"] == "MOT-X OS API"


def test_api_history_endpoint_returns_history():
    engine = MOTXAutomationEngine()
    engine.memory = MemoryManager()
    engine.memory.store({"type": "TEST"}, "ok")

    server, thread = _start_test_server(port=0, engine=engine)
    port = server.server_address[1]
    status, payload = _request("GET", "/history", port=port)
    server.shutdown()
    thread.join(timeout=1)

    assert status == 200
    assert isinstance(payload["history"], list)
    assert payload["history"][0]["task"]["type"] == "TEST"


def test_api_execute_requires_auth_when_token_is_set():
    server, thread = _start_test_server(port=0, token="secret-token")
    port = server.server_address[1]
    status, payload = _request("POST", "/execute", body={"instruction": "lister dossier ."}, port=port)
    server.shutdown()
    thread.join(timeout=1)

    assert status == 401
    assert payload["error"] == "Unauthorized"


def test_api_execute_with_auth_can_process_instruction():
    server, thread = _start_test_server(port=0, token="secret-token")
    port = server.server_address[1]
    headers = {"Authorization": "Bearer secret-token", "Content-Type": "application/json"}
    status, payload = _request("POST", "/execute", body={"instruction": "créer dossier test_api"}, headers=headers, port=port)
    server.shutdown()
    thread.join(timeout=1)

    assert status == 200
    assert isinstance(payload["results"], list)


def test_api_config_endpoint_returns_settings():
    server, thread = _start_test_server(port=0)
    port = server.server_address[1]
    status, payload = _request("GET", "/config", port=port)
    server.shutdown()
    thread.join(timeout=1)

    assert status == 200
    assert "config" in payload


def test_api_tasks_endpoint_returns_supported_list():
    server, thread = _start_test_server(port=0)
    port = server.server_address[1]
    status, payload = _request("GET", "/tasks", port=port)
    server.shutdown()
    thread.join(timeout=1)

    assert status == 200
    assert isinstance(payload.get("supported_tasks"), list)
    assert "OPEN_APP" in payload["supported_tasks"]


def test_api_dashboard_endpoint_returns_html():
    server, thread = _start_test_server(port=0)
    port = server.server_address[1]
    status, payload = _request("GET", "/dashboard", port=port)
    server.shutdown()
    thread.join(timeout=1)

    assert status == 200
    assert isinstance(payload, str)
    assert "MOT-X OS - Dashboard" in payload


def test_api_gamification_profile_returns_cached_user_data():
    server, thread = _start_test_server(port=0, engine=StubEnhancedEngine())
    port = server.server_address[1]
    status, payload = _request("GET", "/gamification/profile", port=port)
    server.shutdown()
    thread.join(timeout=1)

    assert status == 200
    assert payload["level"] == 2
    assert payload["experience_points"] == 150
    assert isinstance(payload.get("daily_challenges"), list)


def test_api_analytics_dashboard_returns_real_dashboard():
    server, thread = _start_test_server(port=0, engine=StubEnhancedEngine())
    port = server.server_address[1]
    status, payload = _request("GET", "/analytics/dashboard", port=port)
    server.shutdown()
    thread.join(timeout=1)

    assert status == 200
    assert payload["overview"]["total_automations"] == 1
    assert payload["overview"]["success_rate"] == 100.0
    assert "performance_metrics" in payload


def test_api_audit_logs_are_recorded():
    server, thread = _start_test_server(port=0)
    port = server.server_address[1]
    _request("GET", "/status", port=port)
    status, payload = _request("GET", "/audit/logs", port=port)
    server.shutdown()
    thread.join(timeout=1)

    assert status == 200
    assert isinstance(payload.get("audit_logs"), list)
    assert any(entry["path"] == "/status" for entry in payload["audit_logs"])


def test_api_agents_status_returns_enhanced_engine_metrics():
    engine = StubEnhancedEngine()
    multi_agent_system = StubMultiAgentSystem()
    server, thread = _start_test_server(port=0, engine=engine, multi_agent_system=multi_agent_system)
    port = server.server_address[1]

    status, payload = _request("GET", "/agents/status", port=port)
    server.shutdown()
    thread.join(timeout=1)

    assert status == 200
    assert payload["total_agents"] == 1
    assert payload["available_agents"] == ["browser"]
    assert "engine_metrics" in payload
    assert "full_dashboard" in payload["engine_metrics"]
    assert payload["engine_metrics"]["full_dashboard"]["gamification"]["level"] == 2


def test_api_agents_coordinate_returns_engine_metrics():
    engine = StubEnhancedEngine()
    multi_agent_system = StubMultiAgentSystem()
    server, thread = _start_test_server(port=0, engine=engine, multi_agent_system=multi_agent_system)
    port = server.server_address[1]

    headers = {"Content-Type": "application/json"}
    status, payload = _request("GET", "/agents/coordinate", body={"instruction": "navigate to homepage"}, headers=headers, port=port)
    server.shutdown()
    thread.join(timeout=1)

    assert status == 200
    assert payload["instruction"] == "navigate to homepage"
    assert payload["agents_used"] == ["browser"]
    assert payload["results"]["browser"]["success"] is True
    assert "engine_metrics" in payload
    assert payload["engine_metrics"]["full_dashboard"]["analytics"]["overview"]["total_automations"] == 1
