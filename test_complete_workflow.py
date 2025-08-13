"""
Test script to demonstrate the complete news processing workflow
"""

import asyncio
import time
from app.services.scrape_service import scrape_dailystar
from app.services.prothomalo_service import scrape_prothomalo
from app.services.news_merger_service import NewsMergerService
from app.services.detailed_news_service import DetailedNewsService


async def test_complete_workflow():
    """Test the complete news processing workflow"""

    print("🚀 Testing Complete News Processing Workflow")
    print("=" * 80)

    start_time = time.time()

    # Step 1: Scrape both sources
    print("\n📰 STEP 1: Scraping News Sources")
    print("-" * 50)

    print("🔍 Scraping Daily Star Bangladesh...")
    dailystar_result = await scrape_dailystar()
    if dailystar_result.get("success"):
        print("✅ Daily Star scraping completed successfully")
        print(
            f"   Articles found: {dailystar_result.get('preprocessed_data', {}).get('structured_news', {}).get('total_articles', 'N/A')}"
        )
    else:
        print("❌ Daily Star scraping failed")
        return

    print("\n🔍 Scraping Prothom Alo...")
    prothomalo_result = await scrape_prothomalo()
    if prothomalo_result.get("success"):
        print("✅ Prothom Alo scraping completed successfully")
        print(
            f"   Articles found: {prothomalo_result.get('preprocessed_data', {}).get('structured_news', {}).get('total_articles', 'N/A')}"
        )
    else:
        print("❌ Prothom Alo scraping failed")
        return

    # Step 2: Merge and deduplicate
    print("\n🔄 STEP 2: Merging and Deduplicating News")
    print("-" * 50)

    merger = NewsMergerService()
    merge_result = merger.merge_news_sources()  # This is not async

    if merge_result.get("success"):
        print("✅ News merging completed successfully")
        dedup_summary = merge_result.get("deduplication_summary", {})
        print(f"   Original articles: {dedup_summary.get('original', 'N/A')}")
        print(
            f"   Duplicates removed: {dedup_summary.get('duplicates_removed', 'N/A')}"
        )
        print(f"   Final unique articles: {dedup_summary.get('final', 'N/A')}")
        print(f"   Saved to: {merge_result.get('saved_file', 'N/A')}")
    else:
        print("❌ News merging failed")
        print(f"   Error: {merge_result.get('error')}")
        return

    # Step 3: Process detailed news in batches
    print("\n🤖 STEP 3: Detailed News Processing (4 Batches)")
    print("-" * 50)

    detailed_service = DetailedNewsService()
    batch_results = []

    for batch_num in range(1, 5):
        print(f"\n📦 Processing Batch {batch_num}/4...")
        batch_start = time.time()

        batch_result = await detailed_service.process_merged_news_batch(batch_num)

        if batch_result.get("success"):
            processing_summary = batch_result.get("processing_summary", {})
            print(f"✅ Batch {batch_num} completed successfully")
            print(
                f"   Articles processed: {processing_summary.get('successful', 'N/A')}/{processing_summary.get('total_requested', 'N/A')}"
            )
            print(f"   Success rate: {processing_summary.get('success_rate', 'N/A')}")
            print(f"   Saved to: {batch_result.get('saved_file', 'N/A')}")

            batch_results.append(
                {
                    "batch": batch_num,
                    "success": True,
                    "articles_processed": processing_summary.get("successful", 0),
                    "file": batch_result.get("saved_file", "N/A"),
                }
            )
        else:
            print(f"❌ Batch {batch_num} failed")
            print(f"   Error: {batch_result.get('error')}")
            batch_results.append(
                {
                    "batch": batch_num,
                    "success": False,
                    "error": batch_result.get("error", "Unknown error"),
                }
            )

        batch_time = time.time() - batch_start
        print(f"   Batch {batch_num} processing time: {batch_time:.1f} seconds")

        # Add delay between batches
        if batch_num < 4:
            print("   ⏳ Waiting 3 seconds before next batch...")
            await asyncio.sleep(3)

    # Summary
    total_time = time.time() - start_time
    successful_batches = sum(1 for r in batch_results if r["success"])
    total_articles_processed = sum(
        r.get("articles_processed", 0) for r in batch_results if r["success"]
    )

    print(f"\n{'='*80}")
    print("🎉 WORKFLOW COMPLETION SUMMARY")
    print("=" * 80)
    print(
        f"⏱️  Total workflow time: {total_time:.1f} seconds ({total_time/60:.1f} minutes)"
    )
    print(f"📰 Sources scraped: 2 (Daily Star + Prothom Alo)")
    print(f"🔄 Merging: ✅ Completed")
    print(f"🤖 Batch processing: {successful_batches}/4 batches completed")
    print(f"📊 Total articles processed: {total_articles_processed}")

    print(f"\n📁 Generated Files:")
    print(f"   Merged news: {merge_result.get('saved_file', 'N/A')}")
    for result in batch_results:
        if result["success"]:
            print(f"   Batch {result['batch']}: {result['file']}")
        else:
            print(f"   Batch {result['batch']}: ❌ Failed - {result['error']}")

    print(f"\n🎯 Next Steps:")
    print(f"   1. Check the data/ folder for all generated files")
    print(f"   2. Review processing statistics in each file")
    print(f"   3. Use embeddings for semantic search and analysis")
    print(f"   4. Monitor for any failed articles and re-process if needed")


if __name__ == "__main__":
    asyncio.run(test_complete_workflow())
