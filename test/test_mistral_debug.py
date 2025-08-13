"""
Debug script to test Mistral AI via our MistralService
"""

import asyncio
from app.services.mistral_service import MistralService


async def test_mistral_connection():
    print("Testing Mistral AI connection...")
    print("=" * 40)
    service = MistralService()
    resp = await service.ping()
    print(resp)


if __name__ == "__main__":
    asyncio.run(test_mistral_connection())
