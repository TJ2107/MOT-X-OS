from ..utils.llm_client import LocalLLMClient


class LLMPlugin:
    def __init__(self, model_path: str = None, backend: str = None):
        self.client = LocalLLMClient(model_path=model_path, backend=backend)

    def generate(self, prompt: str, max_tokens: int = 200) -> str:
        return self.client.generate(prompt, max_tokens=max_tokens)

    def translate_en_to_fr(self, text: str) -> str:
        prompt = f"Traduire en français:\n\n{text}\n\nTraduction:" 
        return self.generate(prompt, max_tokens=256)
