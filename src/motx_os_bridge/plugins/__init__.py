"""Plugins for MOT-X automation bridge."""

from .advanced_filesystem import AdvancedFileSystemPlugin
from .browser import BrowserPlugin
from .communication import CommunicationPlugin
from .filesystem import FileSystemPlugin
from .llm import LLMPlugin
from .logger import MacrosPlugin as LoggerPlugin
from .macros import MacrosPlugin
from .monitor import MonitorPlugin
from .notes import NotesPlugin
from .scheduler import SchedulerPlugin
from .scripts import ScriptsPlugin
from .shell import ShellPlugin
from .system_info import SystemInfoPlugin
from .translation import TranslationPlugin
from .vision import take_screenshot, ocr_image, screenshot_to_text
from .web import WebPlugin

# Revolutionary Innovations
from .cognitive_emergence import CognitiveNetwork
from .immersive_interface import ImmersiveInterface, WebSocketVisualization
from .gamification_engine import GamificationEngine
from .predictive_intelligence import PredictiveIntelligence
from .multi_user_collaboration import CollaborationEngine
from .narrative_engine import NarrativeEngine
from .advanced_analytics import AdvancedAnalytics
from .enhanced_engine import EnhancedMOTXEngine

__all__ = [
    "AdvancedFileSystemPlugin",
    "BrowserPlugin",
    "CommunicationPlugin",
    "FileSystemPlugin",
    "LLMPlugin",
    "LoggerPlugin",
    "MacrosPlugin",
    "MonitorPlugin",
    "NotesPlugin",
    "SchedulerPlugin",
    "ScriptsPlugin",
    "ShellPlugin",
    "SystemInfoPlugin",
    "TranslationPlugin",
    "take_screenshot",
    "ocr_image",
    "screenshot_to_text",
    "WebPlugin",
    # Revolutionary Innovations
    "CognitiveNetwork",
    "ImmersiveInterface",
    "WebSocketVisualization",
    "GamificationEngine",
    "PredictiveIntelligence",
    "CollaborationEngine",
    "NarrativeEngine",
    "AdvancedAnalytics",
    "EnhancedMOTXEngine",
]
