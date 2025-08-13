"""
Test script to demonstrate the OpenAI preprocessing functionality with chunked data
"""

import asyncio
import json
from app.utils.preprocessing import preprocess_data


async def test_preprocessing():
    """Test the preprocessing functionality with sample chunked data"""

    # Sample scraped data (similar to what firecrawl would return)
    sample_data = {
        "markdown": """
        # Breaking News: New Development in Technology
        
        ## Technology News
        A new breakthrough in artificial intelligence has been announced today. 
        Researchers have developed a more efficient algorithm for natural language processing.
        This development could revolutionize how we interact with computers and AI systems.
        
        ## Business Update
        The stock market showed positive trends this week, with technology stocks leading the gains.
        Major tech companies reported strong quarterly earnings, driving market optimism.
        Analysts predict continued growth in the technology sector.
        
        ## Sports News
        The local football team won their match yesterday with a score of 3-1.
        The victory puts them in a strong position for the championship.
        Fans celebrated throughout the city after the win.
        
        ## Health Update
        New health guidelines have been released by the health department.
        The guidelines focus on preventive care and early detection.
        Experts recommend regular check-ups and healthy lifestyle choices.
        
        ## Entertainment
        A new movie has broken box office records this weekend.
        The film received critical acclaim and audience approval.
        Industry experts are calling it a game-changer for the genre.
        """,
        "url": "https://example.com/news",
        "timestamp": "2024-01-15T10:00:00Z",
    }

    print("Testing Mistral AI preprocessing with modular chunk processing...")
    print("=" * 70)

    # Test with different chunk counts
    chunk_counts = [1, 2, 3]

    for max_chunks in chunk_counts:
        print(f"\n{'='*20} Testing with max_chunks={max_chunks} {'='*20}")

        # Test the preprocessing
        result = await preprocess_data(sample_data, max_chunks=max_chunks)

        if result.get("success"):
            print("✅ Preprocessing successful!")

            print(f"\n📊 Processing Summary:")
            print(
                f"Chunks processed: {result['preprocessed_data']['chunks_processed']}"
            )
            print(
                f"Total chunks available: {result['preprocessed_data']['total_chunks']}"
            )
            print(
                f"Max chunks requested: {result['processing_info']['max_chunks_requested']}"
            )
            print(
                f"Chunk size processed: {result['preprocessed_data']['chunk_size']} characters"
            )

            print(f"\n📰 Structured News Data:")
            print("-" * 40)
            print(
                json.dumps(
                    result["preprocessed_data"]["structured_news"],
                    indent=2,
                    ensure_ascii=False,
                )
            )

            print(f"\n🔧 Processing Info:")
            print(f"Model used: {result['processing_info']['model_used']}")
            if result["processing_info"]["tokens_used"]:
                print(f"Tokens used: {result['processing_info']['tokens_used']}")

            print(f"\n📏 Original Data Info:")
            print(
                f"Total content length: {result['original_data']['total_content_length']} characters"
            )
            print(f"Chunks available: {result['original_data']['chunks_available']}")

        else:
            print("❌ Preprocessing failed!")
            print(f"Error: {result.get('error')}")
            print(f"Original data: {result.get('original_data')}")

        print("\n" + "-" * 60)


if __name__ == "__main__":
    asyncio.run(test_preprocessing())
