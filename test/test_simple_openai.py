"""
Simple test script to check if OpenAI service is working
"""

import asyncio
from app.services.mistral_service import MistralService


async def test_simple_openai():
    """Test basic OpenAI functionality"""

    print("Testing basic OpenAI service...")
    print("=" * 40)

    # Initialize service
    service = MistralService()

    # Test 1: Simple completion
    print("\n1. Testing simple completion...")
    try:
        result = await service.get_completion("Say hello in one word")
        print(f"Result: {result}")
    except Exception as e:
        print(f"Error: {e}")

    # Test 2: Preprocessing
    print("\n2. Testing preprocessing...")
    try:
        result = await service.preprocess_content(
            "Extract news from: Breaking news: Test article"
        )
        print(f"Result: {result}")
    except Exception as e:
        print(f"Error: {e}")

    # Test 3: Ping
    print("\n3. Testing ping...")
    try:
        result = await service.ping()
        print(f"Result: {result}")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    asyncio.run(test_simple_openai())
