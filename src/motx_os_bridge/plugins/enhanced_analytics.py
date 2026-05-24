import logging
from collections import defaultdict
from datetime import datetime, timedelta

import numpy as np

logger = logging.getLogger(__name__)


class EnhancedAnalytics:
    """Analytics avancées avec prédictions."""

    def __init__(self):
        self.events = []
        self.metrics = defaultdict(list)

    def record_event(self, event_type: str, data: dict):
        self.events.append({
            "type": event_type,
            "data": data,
            "timestamp": datetime.now().isoformat()
        })

    def get_overview(self) -> dict:
        total = len(self.events)
        success = len([e for e in self.events if e["data"].get("status") == "success"])
        return {
            "total_events": total,
            "success_count": success,
            "success_rate": round((success / total * 100), 2) if total > 0 else 0,
            "last_24h": len([
                e for e in self.events
                if datetime.fromisoformat(e["timestamp"]) > datetime.now() - timedelta(days=1)
            ])
        }

    def get_performance_metrics(self) -> dict:
        execution_times = [e["data"].get("execution_time") for e in self.events if "execution_time" in e["data"]]
        if not execution_times:
            return {}
        return {
            "average_time": float(np.mean(execution_times)),
            "min_time": float(np.min(execution_times)),
            "max_time": float(np.max(execution_times)),
            "p95_time": float(np.percentile(execution_times, 95))
        }

    def get_trends(self) -> dict:
        return {
            "hourly_trend": self._calculate_hourly_trend(),
            "daily_trend": self._calculate_daily_trend()
        }

    def get_predictions(self) -> dict:
        recent = self.events[-10:] if len(self.events) > 10 else self.events
        avg_success = len([e for e in recent if e["data"].get("status") == "success"]) / len(recent) if recent else 0
        return {
            "predicted_success_rate": round(avg_success * 100, 2),
            "estimated_next_failure": "Low" if avg_success > 0.8 else "Medium",
            "recommended_action": "Continue current pattern" if avg_success > 0.8 else "Review failures"
        }

    def get_summary(self) -> dict:
        return {
            "overview": self.get_overview(),
            "performance": self.get_performance_metrics(),
            "trends": self.get_trends(),
            "predictions": self.get_predictions()
        }

    def _calculate_hourly_trend(self):
        return []

    def _calculate_daily_trend(self):
        return []
