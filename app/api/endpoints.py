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

        # Insert (no upsert) to match user's request; will error if duplicates exist
        upload_result = supa.insert_articles(articles)
        return {
            "success": upload_result.get("success", False),
            "file": latest_file,
            "inserted_count": upload_result.get("count", 0),
            "upload_result": upload_result,
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


@router.get("/openai/ping")
async def openai_ping():
    """
    Ping endpoint to test OpenAI service connectivity
    """
    return await openai_service.ping()
