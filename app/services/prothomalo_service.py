from firecrawl import AsyncFirecrawlApp
from dotenv import load_dotenv
import os
from app.utils.preprocessing import preprocess_data

load_dotenv()


async def scrape_prothomalo():
    """Scrape latest news from Prothom Alo"""
    api_key = os.getenv("FIRECRAWL_API_KEY")
    if not api_key:
        return {"error": "FIRECRAWL_API_KEY not set in environment"}

    firecrawl_app = AsyncFirecrawlApp(api_key=api_key)
    response = await firecrawl_app.scrape_url(
        url="https://www.prothomalo.com/collection/latest",
        formats=["markdown"],
        only_main_content=True,
        parse_pdf=False,
        max_age=14400000,
    )

    # Preprocess the response using Mistral AI with 3 chunks
    preprocessed_data = await preprocess_data(response, max_chunks=3, source_name="prothomalo")

    return preprocessed_data
