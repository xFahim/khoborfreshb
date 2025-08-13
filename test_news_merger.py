"""
Test script to demonstrate news merging and deduplication functionality
"""

from app.services.news_merger_service import NewsMergerService


def test_news_merger():
    """Test the news merger service"""

    print("Testing News Merger Service...")
    print("=" * 50)

    # Initialize the service
    merger = NewsMergerService()

    # Test merging news sources
    print("🔄 Merging news from both sources...")
    result = merger.merge_news_sources()

    if result.get("success"):
        print("✅ News merging successful!")

        merged_data = result["merged_data"]
        dedup_stats = result["deduplication_summary"]

        print(f"\n📊 Merging Results:")
        print(f"Sources loaded: {merged_data.get('sources_loaded', [])}")
        print(f"Original articles: {dedup_stats['original']}")
        print(f"Duplicates removed: {dedup_stats['duplicates_removed']}")
        print(f"Final unique articles: {dedup_stats['final']}")

        print(f"\n📰 Sample Articles:")
        articles = merged_data.get("news_articles", [])
        for i, article in enumerate(articles[:3]):  # Show first 3 articles
            print(f"\nArticle {i+1}:")
            print(f"  Title: {article.get('title', 'N/A')[:60]}...")
            print(f"  Source: {article.get('source_name', 'N/A')}")
            print(f"  Category: {article.get('category', 'N/A')}")
            print(f"  Has embedding: {'Yes' if article.get('embedding') else 'No'}")

        print(f"\n💾 Saved to: {result.get('saved_file', 'N/A')}")

    else:
        print("❌ News merging failed!")
        print(f"Error: {result.get('error')}")


if __name__ == "__main__":
    test_news_merger()
