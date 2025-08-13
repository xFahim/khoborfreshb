from firecrawl import AsyncFirecrawlApp
from dotenv import load_dotenv
import os
from app.utils.preprocessing import preprocess_data

load_dotenv()


async def scrape_dailystar():
    api_key = os.getenv("FIRECRAWL_API_KEY")
    if not api_key:
        return {"error": "FIRECRAWL_API_KEY not set in environment"}

    firecrawl_app = AsyncFirecrawlApp(api_key=api_key)
    response = await firecrawl_app.scrape_url(
        url="https://bangla.thedailystar.net/todays-news",
        formats=["markdown"],
        only_main_content=True,
        parse_pdf=False,
        max_age=14400000,
    )

    # Preprocess the response using OpenAI
    preprocessed_data = await preprocess_data(
        response, max_chunks=3, source_name="dailystar"
    )

    return preprocessed_data
