"""
Test script to demonstrate detailed news batch processing functionality
"""

import asyncio
from app.services.detailed_news_service import DetailedNewsService


async def test_detailed_news_batches():
    """Test the detailed news batch processing"""

    print("Testing Detailed News Batch Processing...")
    print("=" * 70)

    # Initialize the service
    detailed_service = DetailedNewsService()

    # Test all 4 batches
    for batch_num in range(1, 5):
        print(f"\n{'='*20} Testing Batch {batch_num} {'='*20}")

        result = await detailed_service.process_merged_news_batch(batch_num)

        if result.get("success"):
            print(f"✅ Batch {batch_num} processing successful!")

            detailed_data = result["detailed_news_data"]
            processing_summary = result["processing_summary"]
            batch_info = detailed_data.get("batch_info", {})

            print(f"\n📊 Batch {batch_num} Results:")
            print(f"Batch size: {batch_info.get('batch_size', 'N/A')} articles")
            print(f"Articles requested: {processing_summary['total_requested']}")
            print(f"Successfully processed: {processing_summary['successful']}")
            print(f"Failed: {processing_summary['failed']}")
            print(f"Success rate: {processing_summary['success_rate']}")
            print(f"Progress: {processing_summary['batch_progress']}")

            # Show sample articles from this batch
            articles = detailed_data.get("detailed_articles", [])
            if articles:
                print(f"\n📰 Sample Articles from Batch {batch_num}:")
                for i, article in enumerate(articles[:2]):  # Show first 2 articles
                    print(f"\nArticle {i+1}:")
                    print(f"  Title: {article.get('title', 'N/A')[:60]}...")
                    print(f"  Category: {article.get('category', 'N/A')}")
                    print(f"  Sentiment: {article.get('sentiment', 'N/A')}")
                    print(f"  Importance: {article.get('importance_level', 'N/A')}/10")
                    print(f"  Global #: {article.get('global_article_number', 'N/A')}")
                    print(
                        f"  Has embedding: {'Yes' if article.get('embedding') else 'No'}"
                    )
                    if article.get("embedding"):
                        print(
                            f"  Embedding dimension: {article.get('embedding_dimension', 'N/A')}"
                        )

            print(f"\n💾 Saved to: {result.get('saved_file', 'N/A')}")

            # Show processing stats
            processing_stats = detailed_data.get("processing_stats", {})
            if processing_stats.get("errors"):
                print(f"\n⚠️ Processing Errors in Batch {batch_num}:")
                for error in processing_stats["errors"][:2]:  # Show first 2 errors
                    print(f"  - {error}")

            # Add delay between batches
            if batch_num < 4:
                print(f"\n⏳ Waiting 2 seconds before next batch...")
                await asyncio.sleep(2)

        else:
            print(f"❌ Batch {batch_num} processing failed!")
            print(f"Error: {result.get('error')}")

    print(f"\n{'='*70}")
    print("🎉 All batch testing completed!")
    print("Check the data/ folder for generated files.")


if __name__ == "__main__":
    asyncio.run(test_detailed_news_batches())
