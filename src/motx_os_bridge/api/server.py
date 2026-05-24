from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import asyncio
from pathlib import Path
from datetime import datetime

from ..utils.config_loader import load_settings
from ..core.cognitive_layer import CognitiveOperatingLayer


class MOTXRequestHandler(BaseHTTPRequestHandler):
    engine = None
    api_token = None
    cognitive_layer = None
    multi_agent_system = None
    audit_log = []
    max_audit_entries = 200

    def _apply_security_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("Cache-Control", "no-store")

    def _log_audit(self, code: int, path: str, method: str, payload=None):
        if not isinstance(self.audit_log, list):
            self.audit_log = []

        entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "method": method,
            "path": path,
            "status": code,
            "client": self.client_address[0] if hasattr(self, "client_address") else "unknown",
            "payload": payload if isinstance(payload, (dict, list, str, int, float, bool, type(None))) else str(payload)
        }
        self.audit_log.append(entry)
        if len(self.audit_log) > self.max_audit_entries:
            self.audit_log.pop(0)

    def _send_json(self, payload, code=200):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self._apply_security_headers()
        self.end_headers()
        self.wfile.write(json.dumps(payload).encode("utf-8"))
        self._log_audit(code, self.path, self.command, payload)

    def _check_auth(self):
        if not self.api_token:
            return True
        auth_header = self.headers.get("Authorization", "")
        if auth_header.startswith("Bearer ") and auth_header[7:].strip() == self.api_token:
            return True
        return False

    def _load_json_payload(self):
        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length).decode("utf-8") if length else ""
        if not body:
            return {}
        try:
            return json.loads(body)
        except json.JSONDecodeError:
            self._send_json({"error": "Invalid JSON payload"}, code=400)
            return None

    def _fetch_gamification_profile(self):
        if self.engine and hasattr(self.engine, "get_gamification_state"):
            try:
                return asyncio.run(self.engine.get_gamification_state())
            except Exception:
                pass

        if self.engine and hasattr(self.engine, "gamification") and hasattr(self.engine.gamification, "get_player_profile"):
            return self.engine.gamification.get_player_profile()

        return {
            "level": 1,
            "experience_points": 0,
            "streak": 0,
            "badges": [],
            "daily_challenges": []
        }

    def _fetch_analytics_dashboard(self):
        if self.engine and hasattr(self.engine, "get_analytics"):
            try:
                return asyncio.run(self.engine.get_analytics())
            except Exception:
                pass

        return {
            "overview": {
                "total_automations": 0,
                "success_rate": 0.0,
                "total_tasks_executed": 0,
                "time_saved_estimate": "0 minutes",
                "insight_generated": 0
            },
            "performance_metrics": {
                "average_execution_time": 0,
                "fastest_execution": 0,
                "slowest_execution": 0,
                "performance_trend": "stable"
            },
            "execution_timeline": [],
            "discipline_impact": {},
            "predictions": {
                "predicted_next_action": "Automation Ready",
                "estimated_success_probability": 0.5,
                "recommended_next_step": "Execute your first automation"
            },
            "recommendations": []
        }

    def _augment_agent_status(self, status: dict) -> dict:
        if not self.engine:
            return status

        engine_metrics = {}
        try:
            if hasattr(self.engine, "get_full_dashboard"):
                engine_metrics["full_dashboard"] = asyncio.run(self.engine.get_full_dashboard())
            else:
                if hasattr(self.engine, "get_analytics"):
                    engine_metrics["analytics"] = asyncio.run(self.engine.get_analytics())
                if hasattr(self.engine, "get_gamification_state"):
                    engine_metrics["gamification"] = asyncio.run(self.engine.get_gamification_state())
                if hasattr(self.engine, "get_cognitive_state"):
                    engine_metrics["cognitive"] = asyncio.run(self.engine.get_cognitive_state())
                if hasattr(self.engine, "get_narrative_state"):
                    engine_metrics["narrative"] = asyncio.run(self.engine.get_narrative_state())
        except Exception:
            engine_metrics = {}

        if engine_metrics:
            status = dict(status)
            status["engine_metrics"] = engine_metrics
        return status

    def _augment_coordinate_result(self, result: dict) -> dict:
        if not self.engine:
            return result

        engine_metrics = {}
        try:
            if hasattr(self.engine, "get_full_dashboard"):
                engine_metrics["full_dashboard"] = asyncio.run(self.engine.get_full_dashboard())
            else:
                if hasattr(self.engine, "get_analytics"):
                    engine_metrics["analytics"] = asyncio.run(self.engine.get_analytics())
                if hasattr(self.engine, "get_gamification_state"):
                    engine_metrics["gamification"] = asyncio.run(self.engine.get_gamification_state())
                if hasattr(self.engine, "get_cognitive_state"):
                    engine_metrics["cognitive"] = asyncio.run(self.engine.get_cognitive_state())
                if hasattr(self.engine, "get_narrative_state"):
                    engine_metrics["narrative"] = asyncio.run(self.engine.get_narrative_state())
        except Exception:
            engine_metrics = {}

        if engine_metrics:
            result = dict(result)
            result["engine_metrics"] = engine_metrics
        return result

    def _send_html(self, html: str, code: int = 200):
        self.send_response(code)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self._apply_security_headers()
        self.end_headers()
        self.wfile.write(html.encode("utf-8"))
        self._log_audit(code, self.path, self.command)

    def _send_dashboard(self):
        dashboard_path = Path(__file__).resolve().parent / "dashboard.html"
        if not dashboard_path.exists():
            return self._send_json({"error": "Dashboard unavailable"}, code=404)
        return self._send_html(dashboard_path.read_text(encoding="utf-8"))

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()

    def do_GET(self):
        if not self._check_auth():
            return self._send_json({"error": "Unauthorized"}, code=401)

        path = self.path.split("?", 1)[0].rstrip("/") or "/"
        normalized = path.lower()
        if normalized.startswith("/api"):
            normalized = normalized[4:]
            if not normalized:
                normalized = "/"

        if normalized == "/status" or normalized == "/health":
            return self._send_json({"status": "ok", "service": "MOT-X OS API"})

        if normalized == "/config":
            config = load_settings()
            if isinstance(config, dict):
                config = {k: v for k, v in config.items() if k != "secrets"}
            return self._send_json({"config": config})

        if normalized == "/tasks":
            supported_tasks = [
                "OPEN_APP", "CREATE_FOLDER", "MONITOR_CPU", "FILE_COPY", "FILE_MOVE", "FILE_RENAME", "FILE_DELETE",
                "FILE_LIST", "FILE_COMPRESS", "EXECUTE_PYTHON", "EXECUTE_POWERSHELL", "EXECUTE_BATCH",
                "SYSTEM_INFO", "RESTART_PC", "SHUTDOWN_PC", "OPEN_URL", "SEARCH_GOOGLE", "SEARCH_BING",
                "DOWNLOAD_FILE", "SEND_EMAIL", "SEND_NOTIFICATION", "PLAY_SOUND", "CREATE_NOTE", "LIST_NOTES",
                "DELETE_NOTE", "CREATE_MACRO", "EXECUTE_MACRO", "LIST_MACROS", "TRANSLATE_TO_FRENCH"
            ]
            return self._send_json({"supported_tasks": supported_tasks})

        if normalized == "/dashboard":
            return self._send_dashboard()

        if normalized.startswith("/history") or normalized.startswith("/commands"):
            history = []
            if self.engine and hasattr(self.engine, "memory"):
                history = self.engine.memory.get_history()
            return self._send_json({"history": history})

        if normalized == "/agents/status":
            if not self.multi_agent_system:
                return self._send_json({"error": "Multi-agent system not initialized"}, code=500)
            status = self.multi_agent_system.get_agent_status()
            return self._send_json(self._augment_agent_status(status))

        if normalized == "/agents/coordinate":
            if not self.multi_agent_system:
                return self._send_json({"error": "Multi-agent system not initialized"}, code=500)
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length).decode("utf-8")
            try:
                payload = json.loads(body) if body else {}
            except json.JSONDecodeError:
                return self._send_json({"error": "Invalid JSON payload"}, code=400)
            
            instruction = payload.get("instruction")
            if not instruction:
                return self._send_json({"error": "Missing 'instruction' field"}, code=400)
            
            try:
                result = asyncio.run(self.multi_agent_system.coordinate_agents(instruction))
                return self._send_json(self._augment_coordinate_result(result))
            except Exception as exc:
                return self._send_json({"error": str(exc)}, code=500)

        if normalized == "/gamification/profile":
            return self._send_json(self._fetch_gamification_profile())

        if normalized == "/analytics/dashboard":
            return self._send_json(self._fetch_analytics_dashboard())

        if normalized == "/audit/logs":
            return self._send_json({"audit_logs": self.audit_log})

        return self._send_json({"error": "Not Found", "original_path": self.path, "normalized_path": normalized}, code=404)

    def do_POST(self):
        if not self._check_auth():
            return self._send_json({"error": "Unauthorized"}, code=401)

        path = self.path.split("?", 1)[0].rstrip("/") or "/"
        normalized = path.lower()
        if normalized.startswith("/api"):
            normalized = normalized[4:]
            if not normalized:
                normalized = "/"

        if normalized == "/execute":
            payload = self._load_json_payload()
            if payload is None:
                return

            instruction = payload.get("instruction") or payload.get("command")
            if not instruction:
                return self._send_json({"error": "Missing 'instruction' field"}, code=400)

            if not self.engine:
                return self._send_json({"error": "Engine not initialized"}, code=500)

            try:
                if hasattr(self.engine, "execute_enhanced"):
                    results = asyncio.run(self.engine.execute_enhanced(instruction))
                    return self._send_json({"results": results})

                results = asyncio.run(self.engine.process_instruction(instruction))
                return self._send_json({"results": results})
            except Exception as exc:
                return self._send_json({"error": str(exc)}, code=500)

        elif normalized == "/cognitive":
            payload = self._load_json_payload()
            if payload is None:
                return

            instruction = payload.get("instruction") or payload.get("command")
            if not instruction:
                return self._send_json({"error": "Missing 'instruction' field"}, code=400)

            if not self.cognitive_layer:
                return self._send_json({"error": "Cognitive layer not initialized"}, code=500)

            try:
                result = asyncio.run(self.cognitive_layer.execute_cognitive_cycle(instruction))
                response_payload = {
                    "cycle_complete": True,
                    "analysis": result.get("analysis"),
                    "decision_confidence": result.get("decision", {}).get("confidence"),
                    "decision": {
                        "approach": result.get("decision", {}).get("approach"),
                        "confidence": result.get("decision", {}).get("confidence"),
                        "reasoning": result.get("decision", {}).get("reasoning")
                    },
                    "tasks_executed": result.get("results", {}).get("tasks_executed"),
                    "tasks_blocked": result.get("results", {}).get("tasks_blocked"),
                    "tasks_failed": result.get("results", {}).get("tasks_failed")
                }
                if isinstance(result.get("decision", {}).get("reasoning"), dict):
                    response_payload["decision"]["raw_reasoning"] = result["decision"]["reasoning"].get("raw_response")
                return self._send_json(response_payload)
            except Exception as exc:
                return self._send_json({"error": str(exc)}, code=500)

        elif normalized == "/agents/coordinate":
            payload = self._load_json_payload()
            if payload is None:
                return

            instruction = payload.get("instruction")
            if not instruction:
                return self._send_json({"error": "Missing 'instruction' field"}, code=400)

            try:
                result = asyncio.run(self.multi_agent_system.coordinate_agents(instruction))
                return self._send_json(self._augment_coordinate_result(result))
            except Exception as exc:
                return self._send_json({"error": str(exc)}, code=500)

        elif normalized == "/gamification/profile":
            return self._send_json(self._fetch_gamification_profile())

        elif normalized == "/analytics/dashboard":
            return self._send_json(self._fetch_analytics_dashboard())

        elif normalized == "/vision/ocr":
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length).decode("utf-8")
            try:
                payload = json.loads(body) if body else {}
            except json.JSONDecodeError:
                self.send_response(400)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": "Invalid JSON payload"}).encode("utf-8"))
                return

            # payload options: { "path": "/path/to/image.png", "lang": "fra" }
            img_path = payload.get("path")
            lang = payload.get("lang", "eng")

            try:
                from ..plugins import vision
            except Exception as e:
                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": f"Vision plugin not available: {e}"}).encode("utf-8"))
                return

            try:
                if img_path:
                    text = vision.ocr_image(path=img_path, lang=lang)
                    result = {"text": text, "path": img_path}
                else:
                    saved = None
                    try:
                        saved = vision.take_screenshot()
                    except Exception:
                        # try without saving path if ImageGrab unsupported
                        pass
                    text = vision.screenshot_to_text(saved) if saved else vision.screenshot_to_text()
                    result = {"text": text, "path": saved}

                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(result).encode("utf-8"))
            except Exception as exc:
                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(exc)}).encode("utf-8"))
            return

        else:
            self._send_json({"error": "Not Found", "path": self.path}, code=404)


def run_server(host: str = "127.0.0.1", port: int = 8000, engine=None):
    if engine is None:
        from ..core.engine import MOTXAutomationEngine
        engine = MOTXAutomationEngine()

    try:
        from ..plugins.enhanced_engine import EnhancedMOTXEngine
        if not hasattr(engine, "execute_enhanced"):
            engine = EnhancedMOTXEngine(engine)
            print("🚀 Enhanced MOT-X Engine integrated")
    except Exception as e:
        print(f"⚠️ Enhanced engine not available: {e}")

    MOTXRequestHandler.engine = engine
    MOTXRequestHandler.cognitive_layer = CognitiveOperatingLayer()
    
    # Initialize multi-agent system
    try:
        from ..core.multi_agent_system import MultiAgentSystem
        MOTXRequestHandler.multi_agent_system = MultiAgentSystem()
        print("🤖 Multi-Agent System initialized")
    except Exception as e:
        print(f"⚠️ Failed to initialize Multi-Agent System: {e}")
    
    settings = load_settings()
    api_settings = settings.get("api", {}) if isinstance(settings, dict) else {}
    MOTXRequestHandler.api_token = api_settings.get("token")

    server = HTTPServer((host, port), MOTXRequestHandler)
    print(f"Serving MOT-X OS API on http://{host}:{port}")
    if MOTXRequestHandler.api_token:
        print("🔒 API token authentication is enabled")
    server.serve_forever()
