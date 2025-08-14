from fastapi import APIRouter, Query
from app.services.scrape_service import scrape_dailystar
from app.services.prothomalo_service import scrape_prothomalo
from app.services.news_merger_service import NewsMergerService
from app.services.detailed_news_service import DetailedNewsService
from app.services.mistral_service import MistralService
from app.services.supabase_service import SupabaseService

import os
import glob
import json
from typing import Optional
from datetime import datetime
import asyncio

router = APIRouter()

# Initialize services
openai_service = MistralService()
news_merger_service = NewsMergerService()
detailed_news_service = DetailedNewsService()


@router.get("/scrape/dailystar")
async def scrape_dailystar_endpoint():
    return await scrape_dailystar()


@router.get("/scrape/prothomalo")
async def scrape_prothomalo_endpoint():
    return await scrape_prothomalo()


@router.get("/merge/news")
async def merge_news_endpoint():
    """
    Merge news from both sources and remove duplicates using cosine similarity
    """
    return news_merger_service.merge_news_sources()


@router.get("/news/detailed/batch1")
async def detailed_news_batch1_endpoint():
    """
    Process Batch 1 of detailed news (approximately articles 1-11)
    """
    return await detailed_news_service.process_merged_news_batch(1)


@router.get("/news/detailed/batch2")
async def detailed_news_batch2_endpoint():
    """
    Process Batch 2 of detailed news (approximately articles 12-22)
    """
    return await detailed_news_service.process_merged_news_batch(2)


@router.get("/news/detailed/batch3")
async def detailed_news_batch3_endpoint():
    """
    Process Batch 3 of detailed news (approximately articles 23-33)
    """
    return await detailed_news_service.process_merged_news_batch(3)


@router.get("/news/detailed/batch4")
async def detailed_news_batch4_endpoint():
    """
    Process Batch 4 of detailed news (approximately articles 34-42)
    """
    return await detailed_news_service.process_merged_news_batch(4)


@router.post("/upload/batch1")
@router.get("/upload/batch1")
async def upload_batch1_to_supabase():
    """
    Upload the latest saved detailed batch1 JSON to Supabase.
    Uses SUPABASE_URL and SUPABASE_KEY from .env via SupabaseService.
    """
    try:
        data_dir = "data"
        pattern = os.path.join(data_dir, "detailed_news_batch1_*.json")
        files = glob.glob(pattern)
        if not files:
            return {"success": False, "error": "No batch1 files found"}

        latest_file = max(files, key=os.path.getctime)
        with open(latest_file, "r", encoding="utf-8") as f:
            payload = json.load(f)

        articles = payload.get("detailed_news_data", {}).get("detailed_articles")
        if articles is None:
            # Try direct top-level
            articles = payload.get("detailed_articles", [])
        if not articles:
            return {
                "success": False,
                "error": "No detailed articles found in file",
                "file": latest_file,
            }

        # Use .env-configured client; no keys in code
        supa = SupabaseService()

        # Use upsert to handle potential duplicates gracefully
        upload_result = supa.upsert_articles(articles)
        return {
            "success": upload_result.get("success", False),
            "file": latest_file,
            "inserted_count": upload_result.get("count", 0),
            "upload_result": upload_result,
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.post("/upload/all")
@router.get("/upload/all")
async def upload_all_batches_to_supabase():
    """
    Upload all detailed news to Supabase.
    Prioritizes the complete all_batches file if present, otherwise falls back to individual batch files.
    Uses SUPABASE_URL and SUPABASE_KEY from .env via SupabaseService.
    """
    try:
        data_dir = "data"
        all_batches = []
        seen_urls = set()  # Track unique URLs to avoid duplicates

        # First check if complete all_batches file exists
        all_batches_pattern = os.path.join(data_dir, "detailed_news_all_batches_*.json")
        all_batches_files = glob.glob(all_batches_pattern)

        if all_batches_files:
            # Use the complete all_batches file
            latest_all_batches_file = max(all_batches_files, key=os.path.getctime)
            print(f"📁 Found complete all_batches file: {latest_all_batches_file}")

            with open(latest_all_batches_file, "r", encoding="utf-8") as f:
                payload = json.load(f)

            articles = payload.get("detailed_articles", [])
            if articles:
                print(
                    f"✅ Loaded {len(articles)} articles from complete all_batches file"
                )
                # Deduplicate articles based on source_url to avoid Supabase conflicts
                unique_articles = []
                seen_urls = set()
                seen_titles = set()  # Also check for duplicate titles as backup

                for article in articles:
                    source_url = article.get("source_url") or article.get("url")
                    title = article.get("title", "").strip()

                    # Check both URL and title for duplicates
                    is_duplicate = False
                    if source_url and source_url in seen_urls:
                        print(f"⚠️ Skipping duplicate article with URL: {source_url}")
                        is_duplicate = True
                    elif title and title in seen_titles:
                        print(
                            f"⚠️ Skipping duplicate article with title: {title[:50]}..."
                        )
                        is_duplicate = True

                    if not is_duplicate:
                        if source_url:
                            seen_urls.add(source_url)
                        if title:
                            seen_titles.add(title)
                        unique_articles.append(article)

                all_batches = unique_articles
                print(
                    f"📊 Deduplicated: {len(articles)} → {len(unique_articles)} articles"
                )
                print(f"   - Unique URLs: {len(seen_urls)}")
                print(f"   - Unique titles: {len(seen_titles)}")
            else:
                print(
                    "⚠️ No articles found in all_batches file, falling back to individual batches"
                )
                all_batches = []
                seen_urls = set()

        # If no complete file or no articles found, fall back to individual batch files
        if not all_batches:
            print("📁 Processing individual batch files...")
            # Initialize deduplication sets for individual batch processing
            seen_titles = set()
            # Process all 4 batches
            for batch_num in range(1, 5):
                pattern = os.path.join(
                    data_dir, f"detailed_news_batch{batch_num}_*.json"
                )
                files = glob.glob(pattern)
                if not files:
                    continue

                latest_file = max(files, key=os.path.getctime)
                with open(latest_file, "r", encoding="utf-8") as f:
                    payload = json.load(f)

                articles = payload.get("detailed_news_data", {}).get(
                    "detailed_articles"
                )
                if articles is None:
                    # Try direct top-level
                    articles = payload.get("detailed_articles", [])

                if articles:
                    # Filter out duplicates based on source_url and title
                    for article in articles:
                        source_url = article.get("source_url") or article.get("url")
                        title = article.get("title", "").strip()

                        # Check both URL and title for duplicates
                        is_duplicate = False
                        if source_url and source_url in seen_urls:
                            print(
                                f"⚠️ Skipping duplicate article with URL: {source_url}"
                            )
                            is_duplicate = True
                        elif title and title in seen_titles:
                            print(
                                f"⚠️ Skipping duplicate article with title: {title[:50]}..."
                            )
                            is_duplicate = True

                        if not is_duplicate:
                            if source_url:
                                seen_urls.add(source_url)
                            if title:
                                seen_titles.add(title)
                            all_batches.append(article)

        if not all_batches:
            return {
                "success": False,
                "error": "No detailed articles found in any batch files or complete all_batches file",
            }

        print(f"📊 Final deduplication summary:")
        print(f"   - Total unique articles: {len(all_batches)}")
        print(f"   - Unique URLs tracked: {len(seen_urls)}")

        # Debug: Check embedding information
        embedding_info = {
            "total_articles": len(all_batches),
            "articles_with_embeddings": 0,
            "articles_without_embeddings": 0,
            "embedding_dimensions": set(),
        }

        for article in all_batches:
            embedding = article.get("embedding")
            if embedding:
                embedding_info["articles_with_embeddings"] += 1
                embedding_info["embedding_dimensions"].add(len(embedding))
            else:
                embedding_info["articles_without_embeddings"] += 1

        # Use .env-configured client; no keys in code
        supa = SupabaseService()

        # Use upsert to handle potential duplicates gracefully
        upload_result = supa.upsert_articles(all_batches)
        return {
            "success": upload_result.get("success", False),
            "total_articles": len(all_batches),
            "unique_articles": len(seen_urls),
            "inserted_count": upload_result.get("count", 0),
            "deduplication_info": {
                "original_count": len(all_batches),
                "final_count": len(all_batches),
                "duplicates_removed": 0,  # Will be calculated if we track original count
            },
            "embedding_debug": embedding_info,
            "upload_result": upload_result,
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.get("/news/detailed/all")
async def detailed_news_all_batches_endpoint():
    """
    Process ALL batches of detailed news at once.
    Goes through all URLs in merged articles and gets detailed information for each one.
    """
    try:
        # First merge the news to get the latest articles
        merge_result = news_merger_service.merge_news_sources()
        if not merge_result.get("success"):
            return {"success": False, "error": "Failed to merge news sources"}

        merged_data = merge_result["merged_data"]
        all_articles = merged_data.get("news_articles", [])

        if not all_articles:
            return {"success": False, "error": "No articles found to process"}

        total_articles = len(all_articles)
        print(f"📰 Processing ALL {total_articles} articles in one batch")

        detailed_articles = []
        processing_stats = {
            "total_articles": total_articles,
            "successful": 0,
            "failed": 0,
            "errors": [],
            "processing_start": datetime.now().isoformat(),
        }

        # Process each article
        for i, article in enumerate(all_articles):
            article_num = i + 1
            print(f"\n--- Processing Article {article_num}/{total_articles} ---")
            print(f"Title: {article.get('title', 'N/A')[:60]}...")

            url = article.get("url") or article.get("source_url")
            if not url:
                print(f"❌ No URL found for article {article_num}")
                processing_stats["failed"] += 1
                processing_stats["errors"].append(
                    f"Article {article_num}: No URL found"
                )
                continue

            # Scrape article content
            scrape_result = await detailed_news_service.scrape_article_content(url)
            if not scrape_result.get("success"):
                print(
                    f"❌ Failed to scrape article {article_num}: {scrape_result.get('error')}"
                )
                processing_stats["failed"] += 1
                processing_stats["errors"].append(
                    f"Article {article_num}: Scraping failed - {scrape_result.get('error')}"
                )
                continue

            # Extract markdown content
            markdown_content = ""
            try:
                if hasattr(scrape_result["content"], "markdown"):
                    markdown_content = scrape_result["content"].markdown
                elif hasattr(scrape_result["content"], "dict"):
                    markdown_content = (
                        scrape_result["content"].dict().get("markdown", "")
                    )
                else:
                    markdown_content = str(scrape_result["content"])
            except Exception as e:
                print(f"❌ Error extracting markdown: {e}")
                processing_stats["failed"] += 1
                processing_stats["errors"].append(
                    f"Article {article_num}: Markdown extraction failed - {e}"
                )
                continue

            # Process with Mistral AI
            mistral_result = await detailed_news_service.process_article_with_mistral(
                markdown_content, article
            )
            if not mistral_result.get("success"):
                print(
                    f"❌ Mistral processing failed for article {article_num}: {mistral_result.get('error')}"
                )
                processing_stats["failed"] += 1
                processing_stats["errors"].append(
                    f"Article {article_num}: Mistral processing failed - {mistral_result.get('error')}"
                )
                continue

            # Generate embedding
            embedding_result = await detailed_news_service.generate_article_embedding(
                mistral_result["processed_data"]
            )
            if not embedding_result.get("success"):
                print(
                    f"⚠️ Embedding generation failed for article {article_num}: {embedding_result.get('error')}"
                )
                # Continue without embedding
                detailed_article = embedding_result["article_data"]
            else:
                detailed_article = embedding_result["article_data"]

            # Add processing metadata
            detailed_article["processing_timestamp"] = datetime.now().isoformat()
            detailed_article["processing_status"] = "completed"
            detailed_article["global_article_number"] = article_num

            detailed_articles.append(detailed_article)
            processing_stats["successful"] += 1

            print(f"✅ Article {article_num} processed successfully")

            # Add delay to avoid overwhelming APIs
            await asyncio.sleep(1)

        # Create final output
        detailed_news_data = {
            "batch_info": {
                "batch_type": "all_batches_combined",
                "total_articles": total_articles,
                "processing_mode": "single_batch_all_articles",
            },
            "detailed_articles": detailed_articles,
            "total_articles": len(detailed_articles),
            "processing_stats": processing_stats,
            "processing_timestamp": datetime.now().isoformat(),
            "source_files": {"merged_news": merge_result.get("saved_file", "N/A")},
        }

        # Save detailed news data
        saved_filepath = detailed_news_service.save_detailed_news_all_json(
            detailed_news_data
        )

        # Upload to Supabase
        supabase_upload_result = detailed_news_service.supabase_service.upsert_articles(
            detailed_articles
        )

        return {
            "success": True,
            "detailed_news_data": detailed_news_data,
            "saved_file": saved_filepath,
            "supabase_upload": supabase_upload_result,
            "processing_summary": {
                "total_requested": total_articles,
                "successful": processing_stats["successful"],
                "failed": processing_stats["failed"],
                "success_rate": f"{(processing_stats['successful'] / total_articles) * 100:.1f}%",
                "processing_time": f"Started: {processing_stats['processing_start']}, Completed: {datetime.now().isoformat()}",
            },
        }

    except Exception as e:
        return {
            "success": False,
            "error": f"Error processing all batches: {str(e)}",
        }


@router.get("/check/existing")
async def check_existing_articles():
    """
    Check if the database table exists and return basic info.
    Useful for debugging connection issues.
    """
    try:
        supa = SupabaseService()
        # Just check if we can access the table
        response = supa.client.table(supa.table_name).select("*").limit(1).execute()

        return {
            "success": True,
            "table_name": supa.table_name,
            "connection_status": "Connected to Supabase",
            "table_accessible": True,
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.get("/check/embedding-config")
async def check_embedding_config():
    """
    Check the current embedding dimension configuration.
    Useful for debugging embedding issues.
    """
    try:
        supa = SupabaseService()
        return {
            "success": True,
            "required_vector_dimension": supa.required_vector_dimension,
            "table_name": supa.table_name,
            "embedding_dim_env": os.getenv(
                "EMBEDDING_DIM", "Not set (using default 1024)"
            ),
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.delete("/delete/previous-data")
@router.post("/delete/previous-data")
async def delete_previous_data():
    """
    Delete all previous data files to avoid duplicate uploads.
    This will clear the data folder of all JSON files.
    """
    try:
        data_dir = "data"
        if not os.path.exists(data_dir):
            return {"success": False, "error": "Data directory does not exist"}

        # Find all JSON files in the data directory
        json_pattern = os.path.join(data_dir, "*.json")
        json_files = glob.glob(json_pattern)

        if not json_files:
            return {
                "success": True,
                "message": "No JSON files found to delete",
                "deleted_count": 0,
            }

        deleted_files = []
        deleted_count = 0

        for file_path in json_files:
            try:
                os.remove(file_path)
                deleted_files.append(os.path.basename(file_path))
                deleted_count += 1
                print(f"🗑️ Deleted: {os.path.basename(file_path)}")
            except Exception as e:
                print(f"❌ Failed to delete {file_path}: {e}")

        return {
            "success": True,
            "message": f"Successfully deleted {deleted_count} data files",
            "deleted_count": deleted_count,
            "deleted_files": deleted_files,
            "data_directory": data_dir,
        }

    except Exception as e:
        return {"success": False, "error": f"Error deleting previous data: {str(e)}"}


@router.get("/openai/ping")
async def openai_ping():
    """
    Ping endpoint to test OpenAI service connectivity
    """
    return await openai_service.ping()
