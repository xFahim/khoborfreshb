import json
import os
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
from firecrawl import AsyncFirecrawlApp
from dotenv import load_dotenv
from app.services.mistral_service import MistralService
from app.services.supabase_service import SupabaseService

load_dotenv()


class DetailedNewsService:
    def __init__(self):
        self.openai_service = MistralService()
        self.firecrawl_api_key = os.getenv("FIRECRAWL_API_KEY")
        self.supabase_service = SupabaseService()

    async def scrape_article_content(self, url: str) -> Dict[str, Any]:
        """
        Scrape individual article content using Firecrawl

        Args:
            url: Article URL to scrape

        Returns:
            Dict[str, Any]: Scraped content
        """
        try:
            if not self.firecrawl_api_key:
                return {"success": False, "error": "FIRECRAWL_API_KEY not set"}

            firecrawl_app = AsyncFirecrawlApp(api_key=self.firecrawl_api_key)

            print(f"🔍 Scraping article: {url}")
            response = await firecrawl_app.scrape_url(
                url=url,
                formats=["markdown"],
                only_main_content=True,
                parse_pdf=False,
                max_age=14400000,
            )

            return {"success": True, "content": response, "url": url}

        except Exception as e:
            return {"success": False, "error": str(e), "url": url}

    async def process_article_with_mistral(
        self, article_content: str, article_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process article content with Mistral AI to extract structured information

        Args:
            article_content: Raw article content from Firecrawl
            article_info: Basic article info (title, summary, etc.)

        Returns:
            Dict[str, Any]: Processed article data
        """
        try:
            # Create prompt for Mistral AI
            prompt = f"""
            You are a news analysis expert. Analyze the following article content and extract structured information.
            
            Article Title: {article_info.get('title', 'N/A')}
            Article Summary: {article_info.get('summary', 'N/A')}
            
            Article Content:
            {article_content[:8000]}  # Limit content for processing
            
            Please extract and return the following information in JSON format:
            {{
                "title": "Article title (TEXT, NOT NULL)",
                "summary": "Article summary (TEXT)",
                "full_text": "Full article content, cleaned and formatted (TEXT, NOT NULL)",
                "category": "News category (TEXT)",
                "sentiment": "Sentiment analysis (positive/negative/neutral) (TEXT)",
                "importance_level": "Importance level 1-10 (INT)",
                "keywords": ["keyword1", "keyword2", "keyword3"] (TEXT array),
                "date_time": "Article date/time if found (ISO format string)",
                "location": "Geographic location mentioned (TEXT)",
                "named_entities": {{
                    "people": ["person1", "person2"],
                    "organizations": ["org1", "org2"],
                    "locations": ["location1", "location2"]
                }} (JSONB),
                "source_name": "{article_info.get('source_name', 'Unknown')}",
                "source_url": "{article_info.get('url', 'N/A')}",
                "thumbnail_url": "Thumbnail URL if available (TEXT)",
                "language": "Article language (TEXT)"
            }}
            
            Ensure all required fields are present and properly formatted.
            """

            # Process with Mistral AI
            print(
                f"🤖 Processing article with Mistral AI: {article_info.get('title', 'N/A')[:50]}..."
            )
            result = await self.openai_service.preprocess_content(prompt)

            if result.get("success"):
                try:
                    # Parse the JSON response
                    processed_data = json.loads(result.get("response", "{}"))

                    # Add original article info
                    processed_data["original_title"] = article_info.get("title")
                    processed_data["original_summary"] = article_info.get("summary")
                    processed_data["chunk_source"] = article_info.get(
                        "chunk_source", "unknown"
                    )

                    return {"success": True, "processed_data": processed_data}

                except json.JSONDecodeError as e:
                    return {
                        "success": False,
                        "error": f"Failed to parse Mistral response: {e}",
                    }
            else:
                return {
                    "success": False,
                    "error": f"Mistral processing failed: {result.get('error')}",
                }

        except Exception as e:
            return {"success": False, "error": f"Error processing article: {str(e)}"}

    async def generate_article_embedding(
        self, article_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate embedding for the article using title + summary + full_text

        Args:
            article_data: Processed article data

        Returns:
            Dict[str, Any]: Article data with embedding
        """
        try:
            # Combine text for embedding
            title = article_data.get("title", "")
            summary = article_data.get("summary", "")
            full_text = article_data.get("full_text", "")

            # Use title + summary for embedding (full_text might be too long)
            embedding_text = f"{title} {summary}".strip()

            if not embedding_text:
                embedding_text = full_text[
                    :1000
                ]  # Fallback to first 1000 chars of full text

            # Generate embedding
            embedding_result = await self.openai_service.get_embeddings(
                [embedding_text]
            )

            if embedding_result.get("success") and embedding_result.get("embeddings"):
                # Add embedding to article data
                article_data["embedding"] = embedding_result["embeddings"][0].embedding
                article_data["embedding_model"] = "mistral-embed"
                article_data["embedding_dimension"] = len(
                    embedding_result["embeddings"][0].embedding
                )

                return {"success": True, "article_data": article_data}
            else:
                return {
                    "success": False,
                    "error": "Failed to generate embedding",
                    "article_data": article_data,
                }

        except Exception as e:
            return {
                "success": False,
                "error": f"Error generating embedding: {str(e)}",
                "article_data": article_data,
            }

    async def process_merged_news_batch(self, batch_number: int) -> Dict[str, Any]:
        """
        Process a specific batch of merged news articles

        Args:
            batch_number: Batch number (1, 2, 3, or 4)

        Returns:
            Dict[str, Any]: Detailed news processing results for the batch
        """
        try:
            if batch_number not in [1, 2, 3, 4]:
                return {"success": False, "error": "Batch number must be 1, 2, 3, or 4"}

            # Load the latest merged news file
            from app.services.news_merger_service import NewsMergerService

            merger = NewsMergerService()

            # First merge the news to get the latest articles
            merge_result = merger.merge_news_sources()
            if not merge_result.get("success"):
                return {"success": False, "error": "Failed to merge news sources"}

            merged_data = merge_result["merged_data"]
            all_articles = merged_data.get("news_articles", [])

            if not all_articles:
                return {"success": False, "error": "No articles found to process"}

            total_articles = len(all_articles)
            articles_per_batch = (
                total_articles + 3
            ) // 4  # Ceiling division to ensure all articles are covered

            # Calculate batch boundaries
            start_idx = (batch_number - 1) * articles_per_batch
            end_idx = min(start_idx + articles_per_batch, total_articles)

            # Get articles for this batch
            batch_articles = all_articles[start_idx:end_idx]

            print(
                f"📰 Processing Batch {batch_number}: Articles {start_idx + 1}-{end_idx} of {total_articles}"
            )
            print(f"📊 Batch size: {len(batch_articles)} articles")

            detailed_articles = []
            processing_stats = {
                "batch_number": batch_number,
                "total_articles": len(batch_articles),
                "successful": 0,
                "failed": 0,
                "errors": [],
                "batch_boundaries": {
                    "start_index": start_idx,
                    "end_index": end_idx,
                    "total_available": total_articles,
                },
            }

            # Process each article in the batch
            for i, article in enumerate(batch_articles):
                global_article_num = start_idx + i + 1
                print(
                    f"\n--- Processing Article {global_article_num}/{total_articles} (Batch {batch_number}) ---"
                )
                print(f"Title: {article.get('title', 'N/A')[:60]}...")

                url = article.get("url") or article.get("source_url")
                if not url:
                    print(f"❌ No URL found for article {global_article_num}")
                    processing_stats["failed"] += 1
                    processing_stats["errors"].append(
                        f"Article {global_article_num}: No URL found"
                    )
                    continue

                # Scrape article content
                scrape_result = await self.scrape_article_content(url)
                if not scrape_result.get("success"):
                    print(
                        f"❌ Failed to scrape article {global_article_num}: {scrape_result.get('error')}"
                    )
                    processing_stats["failed"] += 1
                    processing_stats["errors"].append(
                        f"Article {global_article_num}: Scraping failed - {scrape_result.get('error')}"
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
                        f"Article {global_article_num}: Markdown extraction failed - {e}"
                    )
                    continue

                # Process with Mistral AI
                mistral_result = await self.process_article_with_mistral(
                    markdown_content, article
                )
                if not mistral_result.get("success"):
                    print(
                        f"❌ Mistral processing failed for article {global_article_num}: {mistral_result.get('error')}"
                    )
                    processing_stats["failed"] += 1
                    processing_stats["errors"].append(
                        f"Article {global_article_num}: Mistral processing failed - {mistral_result.get('error')}"
                    )
                    continue

                # Generate embedding
                embedding_result = await self.generate_article_embedding(
                    mistral_result["processed_data"]
                )
                if not embedding_result.get("success"):
                    print(
                        f"⚠️ Embedding generation failed for article {global_article_num}: {embedding_result.get('error')}"
                    )
                    # Continue without embedding
                    detailed_article = embedding_result["article_data"]
                else:
                    detailed_article = embedding_result["article_data"]

                # Add processing metadata
                detailed_article["processing_timestamp"] = datetime.now().isoformat()
                detailed_article["processing_status"] = "completed"
                detailed_article["batch_number"] = batch_number
                detailed_article["global_article_number"] = global_article_num

                detailed_articles.append(detailed_article)
                processing_stats["successful"] += 1

                print(f"✅ Article {global_article_num} processed successfully")

                # Add delay to avoid overwhelming APIs
                await asyncio.sleep(1)

            # Create final output
            detailed_news_data = {
                "batch_info": {
                    "batch_number": batch_number,
                    "batch_size": len(batch_articles),
                    "total_batches": 4,
                    "articles_per_batch": articles_per_batch,
                },
                "detailed_articles": detailed_articles,
                "total_articles": len(detailed_articles),
                "processing_stats": processing_stats,
                "processing_timestamp": datetime.now().isoformat(),
                "source_files": {"merged_news": merge_result.get("saved_file", "N/A")},
            }

            # Save detailed news data for this batch
            saved_filepath = self.save_detailed_news_batch_json(
                detailed_news_data, batch_number
            )

            # Upload to Supabase
            supabase_upload_result = self.supabase_service.upsert_articles(
                detailed_articles
            )

            return {
                "success": True,
                "detailed_news_data": detailed_news_data,
                "saved_file": saved_filepath,
                "supabase_upload": supabase_upload_result,
                "processing_summary": {
                    "batch_number": batch_number,
                    "total_requested": len(batch_articles),
                    "successful": processing_stats["successful"],
                    "failed": processing_stats["failed"],
                    "success_rate": f"{(processing_stats['successful'] / len(batch_articles)) * 100:.1f}%",
                    "batch_progress": f"Batch {batch_number}/4 completed",
                },
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"Error processing batch {batch_number}: {str(e)}",
            }

    def save_detailed_news_batch_json(
        self, data: Dict[str, Any], batch_number: int
    ) -> str:
        """
        Save detailed news batch data to JSON file

        Args:
            data: Detailed news data to save
            batch_number: Batch number for filename

        Returns:
            str: Filepath where data was saved
        """
        try:
            data_dir = "data"
            if not os.path.exists(data_dir):
                os.makedirs(data_dir)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"detailed_news_batch{batch_number}_{timestamp}.json"
            filepath = os.path.join(data_dir, filename)

            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            print(f"✅ Batch {batch_number} detailed news data saved to: {filepath}")
            return filepath

        except Exception as e:
            print(f"❌ Error saving batch {batch_number} detailed news data: {e}")
            return "N/A"

    def save_detailed_news_all_json(self, data: Dict[str, Any]) -> str:
        """
        Save detailed news data for all batches combined to JSON file

        Args:
            data: Detailed news data to save

        Returns:
            str: Filepath where data was saved
        """
        try:
            data_dir = "data"
            if not os.path.exists(data_dir):
                os.makedirs(data_dir)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"detailed_news_all_batches_{timestamp}.json"
            filepath = os.path.join(data_dir, filename)

            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            print(f"✅ All batches detailed news data saved to: {filepath}")
            return filepath

        except Exception as e:
            print(f"❌ Error saving all batches detailed news data: {e}")
            return "N/A"
