# KhoborFreshB

A FastAPI-based news aggregation system that scrapes, processes, and analyzes Bengali news from Daily Star Bangladesh and Prothom Alo using AI-powered content analysis.

## Setup

1. **Clone the repository:**

   ```bash
   git clone <repository-url>
   cd khoborfreshb
   ```

2. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   Create a `.env` file with:

   ```bash
   MISTRAL_API_KEY=your_mistral_api_key_here
   FIRECRAWL_API_KEY=your_firecrawl_api_key_here
   SUPABASE_URL=your_supabase_url
   SUPABASE_KEY=your_supabase_key
   ```

4. **Run the application:**
   ```bash
   uvicorn main:app --reload
   ```

## Important: Endpoint Sequence

**The endpoints must be called in the correct sequence for the system to work properly:**

1. **`GET /scrape/dailystar`** - Scrape Daily Star Bangladesh news
2. **`GET /scrape/prothomalo`** - Scrape Prothom Alo news
3. **`GET /merge/news`** - Merge and deduplicate news from both sources
4. **`GET /news/detailed/batch1`** - Process detailed analysis for batch 1
5. **`GET /news/detailed/batch2`** - Process detailed analysis for batch 2
6. **`GET /news/detailed/batch3`** - Process detailed analysis for batch 3
7. **`GET /news/detailed/batch4`** - Process detailed analysis for batch 4
8. **`GET /upload/all`** - Upload all 4 batches to Supabase (handles duplicates automatically)
9. **`GET /check/existing`** - Check database connection and table accessibility

**Note:** Each step depends on the previous one. Skipping steps will cause errors. The `/upload/all` endpoint automatically handles duplicate articles using upsert.
