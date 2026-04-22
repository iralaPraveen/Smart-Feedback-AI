import requests
import logging

logger = logging.getLogger(__name__)


class LocalLLMService:
    def __init__(self, model="phi3:mini"):
        self.model = model
        self.url = "http://localhost:11434/api/generate"

    def generate(self, prompt: str) -> str | None:
        """
        Call local LLM (Ollama) to generate response
        """
        try:
            response = requests.post(
                self.url,
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False
                },
            
            )

            if response.status_code != 200:
                logger.error(f"Local LLM HTTP error: {response.status_code}")
                return None

            data = response.json()
            return data.get("response", None)

        except Exception as e:
            logger.error(f"Local LLM failed: {e}")
            return None