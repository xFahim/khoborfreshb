# KhoborFreshB

A FastAPI-based news aggregation system that scrapes, processes, and analyzes Bengali news from Daily Star Bangladesh and Prothom Alo using AI-powered content analysis.

## Features

- **Multi-source scraping**: Daily Star Bangladesh and Prothom Alo
- **AI-powered analysis**: Uses Mistral AI for content processing and sentiment analysis
- **Smart deduplication**: Cosine similarity-based duplicate detection
- **Batch processing**: Process news in configurable batches or all at once
- **Vector embeddings**: Generate embeddings for semantic search
- **Supabase integration**: Store processed news with vector search capabilities
- **Comprehensive API**: RESTful endpoints for all operations

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

## API Endpoints

### 1. News Scraping Endpoints

#### `GET /scrape/dailystar`

Scrape news from Daily Star Bangladesh.

#### `GET /scrape/prothomalo`

Scrape news from Prothom Alo.

### 2. News Processing Endpoints

#### `GET /merge/news`

Merge and deduplicate news from both sources using cosine similarity.

#### `GET /news/detailed/batch1`

Process detailed analysis for batch 1 (articles 1-11 approximately).

#### `GET /news/detailed/batch2`

Process detailed analysis for batch 2 (articles 12-22 approximately).

#### `GET /news/detailed/batch3`

Process detailed analysis for batch 3 (articles 23-33 approximately).

#### `GET /news/detailed/batch4`

Process detailed analysis for batch 4 (articles 34-42 approximately).

#### `GET /news/detailed/all` ⭐ **NEW**

Process ALL articles at once in a single batch. This endpoint goes through all URLs in merged articles and gets detailed information for each one. **Recommended for processing all articles efficiently.**

### 3. Data Upload Endpoints

#### `GET /upload/batch1`

Upload batch 1 detailed news to Supabase.

#### `GET /upload/all`

Upload all detailed news to Supabase. **Smart prioritization**: If a complete `detailed_news_all_batches_*.json` file exists, it will use that instead of individual batch files. Otherwise, it falls back to processing individual batch files.

### 4. Data Management Endpoints

#### `DELETE /delete/previous-data` ⭐ **NEW**

Clear all previous data files from the data folder to avoid duplicate uploads. This is useful before running a fresh scraping session.

#### `POST /delete/previous-data`

Alternative method to clear previous data (same functionality as DELETE).

### 5. Utility & Debug Endpoints

#### `GET /check/existing`

Check database connection and table accessibility.

#### `GET /check/embedding-config`

Check the current embedding dimension configuration.

#### `GET /openai/ping`

Test Mistral AI service connectivity.

## Recommended Workflow

### Option 1: Batch Processing (Traditional)

```bash
# 1. Scrape news sources
curl http://127.0.0.1:8000/scrape/dailystar
curl http://127.0.0.1:8000/scrape/prothomalo

# 2. Merge news
curl http://127.0.0.1:8000/merge/news

# 3. Process in batches
curl http://127.0.0.1:8000/news/detailed/batch1
curl http://127.0.0.1:8000/news/detailed/batch2
curl http://127.0.0.1:8000/news/detailed/batch3
curl http://127.0.0.1:8000/news/detailed/batch4

# 4. Upload to Supabase
curl http://127.0.0.1:8000/upload/all
```

### Option 2: All-at-Once Processing (Recommended) ⭐

```bash
# 1. Scrape news sources
curl http://127.0.0.1:8000/scrape/dailystar
curl http://127.0.0.1:8000/scrape/prothomalo

# 2. Merge news
curl http://127.0.0.1:8000/merge/news

# 3. Process ALL articles at once
curl http://127.0.0.1:8000/news/detailed/all

# 4. Upload to Supabase
curl http://127.0.0.1:8000/upload/all
```

### Option 3: Fresh Start (Clear Previous Data)

```bash
# 1. Clear previous data to avoid duplicates
curl -X DELETE http://127.0.0.1:8000/delete/previous-data

# 2. Follow Option 1 or Option 2 above
```

## Important Notes

- **Endpoint Dependencies**: Each step depends on the previous one. Skipping steps will cause errors.
- **Smart Upload**: The `/upload/all` endpoint automatically detects and prioritizes complete all_batches files over individual batch files.
- **Duplicate Handling**: All upload endpoints use upsert to handle potential duplicates gracefully.
- **Rate Limiting**: The system includes delays between API calls to avoid overwhelming external services.
- **Error Handling**: Comprehensive error handling with detailed logging and fallback mechanisms.

## Data Structure

The system generates several types of JSON files:

- `dailystar_news_*.json` - Raw Daily Star news
- `prothomalo_news_*.json` - Raw Prothom Alo news
- `merged_news_*.json` - Merged and deduplicated news
- `detailed_news_batch*.json` - Individual batch detailed news
- `detailed_news_all_batches_*.json` - Complete detailed news for all articles

## Troubleshooting

- **Check database connection**: Use `/check/existing`
- **Verify embedding configuration**: Use `/check/embedding-config`
- **Test AI service**: Use `/openai/ping`
- **Clear data for fresh start**: Use `/delete/previous-data`
