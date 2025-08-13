# 🗞️ News Aggregation & Analysis System

A comprehensive FastAPI-based system for scraping, merging, and analyzing news from multiple Bengali news sources using advanced AI processing.

## 🚀 Features

- **Multi-source scraping** from Daily Star Bangladesh and Prothom Alo
- **Intelligent deduplication** using cosine similarity algorithms
- **AI-powered content analysis** with Mistral AI
- **Semantic embeddings** for advanced search capabilities
- **Batch processing** for efficient large-scale operations
- **Comprehensive data extraction** including sentiment, entities, and keywords

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Daily Star    │    │  Prothom Alo    │    │   Firecrawl     │
│   Scraping      │    │   Scraping      │    │   Web Scraper   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │   News Merger   │
                    │  (Deduplication)│
                    └─────────────────┘
                                 │
                    ┌─────────────────┐
                    │  Batch Processor│
                    │  (4 Batches)    │
                    └─────────────────┘
                                 │
                    ┌─────────────────┐
                    │   Mistral AI    │
                    │  (Content Analysis)│
                    └─────────────────┘
                                 │
                    ┌─────────────────┐
                    │   Embeddings    │
                    │  (Semantic Vectors)│
                    └─────────────────┘
```

## 📋 Prerequisites

- Python 3.8+
- FastAPI
- Mistral AI API key
- Firecrawl API key

## 🛠️ Installation

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

   ```bash
   # Create .env file
   MISTRAL_API_KEY=your_mistral_api_key_here
   FIRECRAWL_API_KEY=your_firecrawl_api_key_here
   ```

4. **Run the application:**
   ```bash
   uvicorn main:app --reload
   ```

## 🔌 API Endpoints

### 1. News Scraping Endpoints

#### `GET /scrape/dailystar`

Scrapes latest news from Daily Star Bangladesh homepage.

- **Purpose**: Collect raw news data from Daily Star
- **Output**: JSON with scraped news articles
- **Processing**: Basic preprocessing with Mistral AI

#### `GET /scrape/prothomalo`

Scrapes latest news from Prothom Alo latest collection.

- **Purpose**: Collect raw news data from Prothom Alo
- **Output**: JSON with scraped news articles
- **Processing**: Basic preprocessing with Mistral AI

### 2. News Merging Endpoint

#### `GET /merge/news`

Merges news from both sources and removes duplicates.

- **Purpose**: Combine and deduplicate news from multiple sources
- **Algorithm**: Cosine similarity with TF-IDF vectors
- **Output**: Merged news with duplicate removal statistics
- **File**: Saves `merged_news_2sources_Xarticles.json`

### 3. Detailed News Processing Endpoints

#### `GET /news/detailed/batch1`

Processes Batch 1 of detailed news analysis.

- **Articles**: Approximately 1-11
- **Purpose**: Full content scraping and AI analysis
- **Output**: Detailed news with embeddings

#### `GET /news/detailed/batch2`

Processes Batch 2 of detailed news analysis.

- **Articles**: Approximately 12-22
- **Purpose**: Full content scraping and AI analysis
- **Output**: Detailed news with embeddings

#### `GET /news/detailed/batch3`

Processes Batch 3 of detailed news analysis.

- **Articles**: Approximately 23-33
- **Purpose**: Full content scraping and AI analysis
- **Output**: Detailed news with embeddings

#### `GET /news/detailed/batch4`

Processes Batch 4 of detailed news analysis.

- **Articles**: Approximately 34-42
- **Purpose**: Full content scraping and AI analysis
- **Output**: Detailed news with embeddings

### 4. Utility Endpoints

#### `GET /openai/ping`

Tests connectivity with Mistral AI service.

- **Purpose**: Verify API key and service availability
- **Output**: Connection status

## 🔄 Complete Workflow

### Step 1: Initial Scraping

```bash
# Scrape Daily Star Bangladesh
GET /scrape/dailystar

# Scrape Prothom Alo
GET /scrape/prothomalo
```

**What happens:**

- Firecrawl scrapes news websites
- Basic preprocessing with Mistral AI
- News articles saved with title, summary, category, URL
- Embeddings generated for title + summary

**Expected output:**

- `dailystar_news_YYYYMMDD_HHMMSS.json`
- `prothomalo_news_YYYYMMDD_HHMMSS.json`

### Step 2: News Merging & Deduplication

```bash
GET /merge/news
```

**What happens:**

- Loads latest news files from both sources
- Combines all articles
- Removes duplicates using cosine similarity (threshold: 0.85)
- Saves merged results

**Expected output:**

- `merged_news_2sources_42articles.json` (approximately)
- Deduplication statistics
- Combined unique news collection

### Step 3: Detailed Processing (Batch by Batch)

```bash
# Process in sequence
GET /news/detailed/batch1
GET /news/detailed/batch2
GET /news/detailed/batch3
GET /news/detailed/batch4
```

**What happens for each batch:**

- Loads merged news file
- Processes 10-11 articles per batch
- Scrapes individual article URLs for full content
- AI analysis with Mistral for structured extraction
- Generates semantic embeddings
- Saves batch results

**Expected output per batch:**

- `detailed_news_batch1_YYYYMMDD_HHMMSS.json`
- `detailed_news_batch2_YYYYMMDD_HHMMSS.json`
- `detailed_news_batch3_YYYYMMDD_HHMMSS.json`
- `detailed_news_batch4_YYYYMMDD_HHMMSS.json`

## 📊 Data Structure

### Basic News Article (After Scraping)

```json
{
  "title": "Article title in Bengali",
  "summary": "Article summary",
  "category": "news category",
  "url": "article URL",
  "source_name": "Daily Star Bangladesh",
  "embedding": [0.123, -0.456, ...],
  "embedding_model": "mistral-embed"
}
```

### Detailed News Article (After Batch Processing)

```json
{
  "title": "Article title (TEXT, NOT NULL)",
  "summary": "Article summary (TEXT)",
  "full_text": "Full article content, cleaned and formatted (TEXT, NOT NULL)",
  "category": "News category (TEXT)",
  "sentiment": "Sentiment analysis (positive/negative/neutral) (TEXT)",
  "importance_level": "Importance level 1-10 (INT)",
  "keywords": ["keyword1", "keyword2", "keyword3"] (TEXT array),
  "date_time": "Article date/time if found (ISO format string)",
  "location": "Geographic location mentioned (TEXT)",
  "named_entities": {
    "people": ["person1", "person2"],
    "organizations": ["org1", "org2"],
    "locations": ["location1", "location2"]
  },
  "source_name": "Source name",
  "source_url": "Article URL",
  "thumbnail_url": "Thumbnail URL if available (TEXT)",
  "language": "Article language (TEXT)",
  "embedding": "VECTOR(1536) - Mistral embedding",
  "embedding_model": "mistral-embed",
  "embedding_dimension": 1536,
  "batch_number": 1,
  "global_article_number": 5,
  "processing_timestamp": "2024-01-31T10:30:00",
  "processing_status": "completed"
}
```

## 🎯 Batch Processing Strategy

### Why 4 Batches?

- **Load Distribution**: Prevents API rate limiting
- **Memory Management**: Efficient processing of large datasets
- **Error Isolation**: Batch failures don't affect other batches
- **Progress Tracking**: Clear progress indicators

### Batch Distribution (42 articles example)

- **Batch 1**: Articles 1-11 (11 articles)
- **Batch 2**: Articles 12-22 (11 articles)
- **Batch 3**: Articles 23-33 (11 articles)
- **Batch 4**: Articles 34-42 (9 articles)

### Processing Order

1. **Sequential Processing**: Process batches in order (1→2→3→4)
2. **Independent Execution**: Each batch can be run independently
3. **Progress Monitoring**: Track completion status per batch

## 🔧 Configuration

### Environment Variables

```bash
MISTRAL_API_KEY=your_mistral_api_key
FIRECRAWL_API_KEY=your_firecrawl_api_key
```

### Similarity Threshold

- **Default**: 0.85 (85% similarity for duplicate detection)
- **Location**: `app/services/news_merger_service.py`
- **Adjustment**: Modify `self.similarity_threshold` value

### Batch Size

- **Default**: Automatic calculation based on total articles
- **Formula**: `(total_articles + 3) // 4` (ceiling division)
- **Override**: Modify batch calculation logic in service

## 📁 File Structure

```
khoborfreshb/
├── app/
│   ├── api/
│   │   └── endpoints.py              # API route definitions
│   ├── services/
│   │   ├── scrape_service.py         # Daily Star scraping
│   │   ├── prothomalo_service.py     # Prothom Alo scraping
│   │   ├── news_merger_service.py    # News merging & deduplication
│   │   ├── detailed_news_service.py  # Detailed processing
│   │   └── openai_service.py         # Mistral AI integration
│   └── utils/
│       └── preprocessing.py           # Basic preprocessing
├── data/                              # Generated JSON files
├── main.py                            # FastAPI application
├── requirements.txt                   # Python dependencies
└── README.md                          # This file
```

## 🧪 Testing

### Test Scripts

```bash
# Test news merging
python test_news_merger.py

# Test detailed news processing
python test_detailed_news.py
```

### Manual Testing

```bash
# Start the server
uvicorn main:app --reload

# Test endpoints in sequence
curl http://localhost:8000/scrape/dailystar
curl http://localhost:8000/scrape/prothomalo
curl http://localhost:8000/merge/news
curl http://localhost:8000/news/detailed/batch1
```

## 🚨 Error Handling

### Common Issues

1. **API Key Errors**: Check environment variables
2. **Rate Limiting**: Built-in delays between API calls
3. **Scraping Failures**: Individual article failures don't stop batch processing
4. **AI Processing Errors**: Graceful degradation with error logging

### Error Recovery

- **Failed Articles**: Logged with detailed error messages
- **Partial Results**: Continue processing other articles
- **Batch Failures**: Can be re-run independently
- **Data Persistence**: Intermediate results saved automatically

## 📈 Performance Considerations

### Processing Time

- **Scraping**: ~1-2 seconds per article
- **AI Analysis**: ~2-3 seconds per article
- **Embedding Generation**: ~1 second per article
- **Total per batch**: ~5-10 minutes (10-11 articles)

### Rate Limiting

- **Built-in delays**: 1 second between API calls
- **Batch isolation**: Prevents overwhelming external APIs
- **Configurable**: Adjustable delays in service code

### Memory Usage

- **Batch processing**: Limits memory usage per batch
- **Content truncation**: Limits article content to 8000 chars for AI processing
- **Efficient storage**: JSON files with proper encoding

## 🔮 Future Enhancements

### Planned Features

- **Database Integration**: PostgreSQL with vector support
- **Real-time Processing**: WebSocket updates for progress
- **Advanced Analytics**: Trend analysis and reporting
- **API Rate Management**: Dynamic rate limiting
- **Content Caching**: Redis-based caching system

### Scalability Improvements

- **Worker Queues**: Background job processing
- **Load Balancing**: Multiple API instances
- **Content Delivery**: CDN integration for static files
- **Monitoring**: Prometheus metrics and Grafana dashboards

## 📞 Support

For issues, questions, or contributions:

- **Repository**: [GitHub Repository URL]
- **Issues**: [GitHub Issues URL]
- **Documentation**: [Documentation URL]

## 📄 License

[License Information]

---

**Happy News Processing! 🎉**
