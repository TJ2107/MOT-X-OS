from typing import Optional
import subprocess
import shutil

from .config_loader import load_settings
from .ollama_client import OllamaClient


class LocalLLMClient:
    """Minimal wrapper to call a local LLM backend if available.

    Tries these backends in order:
    - ollama_api (Ollama HTTP API - preferred)
    - ollama (Ollama CLI)
    - llama_cpp (python package `llama_cpp`)
    - transformers (HuggingFace pipeline)
    If none available, falls back to a simple echo/stub implementation.
    """

    def __init__(self, model_path: Optional[str] = None, backend: Optional[str] = None):
        settings = load_settings()
        llm_settings = settings.get("llm", {}) if isinstance(settings, dict) else {}

        self.model_path = model_path or llm_settings.get("model")
        self.backend = backend or llm_settings.get("backend")
        self.prompt_timeout = llm_settings.get("prompt_timeout", 60)
        self.ollama_host = llm_settings.get("ollama_host", "localhost")
        self.ollama_port = llm_settings.get("ollama_port", 11434)
        self._client = None
        self._detect_backend()

    def _detect_backend(self):
        # Prefer explicit backend if provided
        if self.backend == "ollama_api":
            model_name = self.model_path or "llama2"
            try:
                ollama_client = OllamaClient(
                    host=self.ollama_host,
                    port=self.ollama_port,
                    model=model_name
                )
                if ollama_client.is_available():
                    self._client = ("ollama_api", ollama_client)
                    return
            except Exception:
                pass
        if self.backend == "ollama":
            model_name = self.model_path or self._find_default_ollama_model()
            self._client = ("ollama", model_name)
            return
        if self.backend == "llama_cpp":
            try:
                from llama_cpp import Llama  # type: ignore[import]
                self._client = ("llama_cpp", Llama(model_path=self.model_path) if self.model_path else None)
                return
            except Exception:
                self._client = None
        if self.backend == "transformers":
            try:
                from transformers import pipeline  # type: ignore[import]
                self._client = ("transformers", pipeline("text-generation", model=self.model_path) if self.model_path else None)
                return
            except Exception:
                self._client = None

        # Ollama API detection (preferred when running local Ollama daemon)
        try:
            model_name = self.model_path or "llama2"
            ollama_client = OllamaClient(
                host=self.ollama_host,
                port=self.ollama_port,
                model=model_name
            )
            if ollama_client.is_available():
                self._client = ("ollama_api", ollama_client)
                return
        except Exception:
            pass

        # Ollama CLI detection (fallback)
        try:
            if shutil.which("ollama"):
                model_name = self.model_path or self._find_default_ollama_model()
                self._client = ("ollama", model_name)
                return
        except Exception:
            pass

        # Auto-detect
        try:
            from llama_cpp import Llama  # type: ignore[import]
            self._client = ("llama_cpp", Llama(model_path=self.model_path) if self.model_path else None)
            return
        except Exception:
            pass

        try:
            from transformers import pipeline  # type: ignore[import]
            self._client = ("transformers", pipeline("text-generation", model=self.model_path) if self.model_path else None)
            return
        except Exception:
            pass

        # Fallback stub
        self._client = ("stub", None)

    def _find_default_ollama_model(self) -> str:
        try:
            result = subprocess.run(["ollama", "list"], capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=10)
            if result.returncode == 0:
                for line in result.stdout.splitlines():
                    text = line.strip()
                    if not text:
                        continue
                    if text.startswith("NAME") or text.startswith("ID") or text.startswith("SIZE") or text.startswith("MODIFIED"):
                        continue
                    parts = text.split()
                    if parts:
                        return parts[0]
        except Exception:
            pass
        return ""

    def _choose_model_alias(self, alias: str, available_models: list[str]) -> str | None:
        """Return the best matching available model for a generic alias."""
        if not available_models:
            return None
        normalized = alias.lower()
        if normalized == "llama2":
            for model in available_models:
                if model.lower().startswith("llama2"):
                    return model
        if normalized.endswith(":latest"):
            for model in available_models:
                if model.lower() == normalized:
                    return model
        # Return the first model containing alias
        for model in available_models:
            if normalized in model.lower():
                return model
        return available_models[0]

    def generate(self, prompt: str, max_tokens: int = 200) -> str:
        kind, client = self._client
        if kind == "ollama_api":
            try:
                return client.generate(prompt, max_tokens=max_tokens)
            except Exception as e:
                return f"⚠️ Erreur Ollama API: {e}"
        if kind == "llama_cpp":
            try:
                resp = client.create(prompt=prompt, max_tokens=max_tokens)
                # llama_cpp returns dict-like with 'choices'
                return resp["choices"][0]["text"] if resp and "choices" in resp else str(resp)
            except Exception as e:
                return f"⚠️ Erreur llama_cpp: {e}"
        if kind == "transformers":
            try:
                outputs = client(prompt, max_length=max_tokens)
                if outputs and isinstance(outputs, list):
                    return outputs[0].get("generated_text", str(outputs[0]))
                return str(outputs)
            except Exception as e:
                return f"⚠️ Erreur transformers: {e}"
        if kind == "ollama":
            try:
                model_name = client or self._find_default_ollama_model()
                if not model_name:
                    return "⚠️ Aucun modèle Ollama trouvé. Spécifie un modèle avec model_path ou installe un modèle Ollama."
                cmd = ["ollama", "run", model_name, prompt]
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    timeout=self.prompt_timeout,
                )
                stdout = result.stdout.strip() if result.stdout else ""
                stderr = result.stderr.strip() if result.stderr else ""
                if result.returncode == 0:
                    return stdout or stderr or ""
                return f"⚠️ Ollama error: {stderr or stdout or 'unknown error'}"
            except Exception as e:
                return f"⚠️ Erreur Ollama: {e}"
        # stub
        return f"[LLM stub] {prompt}"
