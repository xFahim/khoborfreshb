from mistralai import Mistral
from typing import Dict, Any, List
import os


class MistralService:
    def __init__(self):
        api_key = os.getenv("MISTRAL_API_KEY", "uRLI2qONfZ2BlLMvtX0gKrL7p8JXwvOZ")
        self.client = Mistral(api_key=api_key)

    async def get_completion(
        self, message: str, model: str = "mistral-small-2506"
    ) -> Dict[str, Any]:
        try:
            chat_response = self.client.chat.complete(
                model=model,
                messages=[{"role": "user", "content": message}],
                response_format={"type": "json_object"},
            )
            return {
                "success": True,
                "response": chat_response.choices[0].message.content,
                "model": model,
                "usage": None,
            }
        except Exception as e:
            return {"success": False, "error": str(e), "model": model}

    async def preprocess_content(
        self, prompt: str, model: str = "mistral-small-2506"
    ) -> Dict[str, Any]:
        try:
            chat_response = self.client.chat.complete(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a data preprocessing expert. Your task is to clean, structure, and format raw data according to specific instructions. When asked for JSON, provide ONLY valid JSON without any additional text or explanations.",
                    },
                    {"role": "user", "content": prompt},
                ],
                response_format={"type": "json_object"},
            )
            return {
                "success": True,
                "response": chat_response.choices[0].message.content,
                "model": model,
                "usage": None,
            }
        except Exception as e:
            return {"success": False, "error": str(e), "model": model}

    async def ping(self) -> Dict[str, Any]:
        try:
            chat_response = self.client.chat.complete(
                model="mistral-large-latest",
                messages=[{"role": "user", "content": "Hello! hows is life'"}],
                response_format={"type": "json_object"},
            )
            return {
                "success": True,
                "message": "Mistral AI service is working!",
                "response": chat_response.choices[0].message.content,
                "status": "connected",
            }
        except Exception as e:
            return {"success": False, "error": str(e), "status": "disconnected"}

    async def get_embeddings(self, texts: List[str]) -> Dict[str, Any]:
        try:
            embeddings_response = self.client.embeddings.create(
                model="mistral-embed",
                inputs=texts,
            )
            return {
                "success": True,
                "embeddings": embeddings_response.data,
                "model": "mistral-embed",
            }
        except Exception as e:
            return {"success": False, "error": str(e), "model": "mistral-embed"}
