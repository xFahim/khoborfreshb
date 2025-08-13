import json
import asyncio
import os
from datetime import datetime
from typing import Dict, Any, List, Union
from app.services.mistral_service import MistralService

# Initialize Mistral service
openai_service = MistralService()


def save_news_json(data: Dict[str, Any], source_name: str) -> str:
    """
    Save news data to JSON file with timestamp

    Args:
        data: The news data to save
        source_name: Name of the news source (e.g., 'dailystar', 'prothomalo')

    Returns:
        str: Path to the saved file
    """
    # Create data directory if it doesn't exist
    data_dir = "data"
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    # Generate filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{source_name}_news_{timestamp}.json"
    filepath = os.path.join(data_dir, filename)

    # Save the data
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"✅ News data saved to: {filepath}")
    return filepath


async def generate_embeddings_for_articles(
    articles: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """
    Generate embeddings for title + summary of each article

    Args:
        articles: List of news articles

    Returns:
        List[Dict[str, Any]]: Articles with embeddings added
    """
    if not articles:
        return articles

    # Prepare texts for embedding (title + summary)
    texts_for_embedding = []
    for article in articles:
        title = article.get("title", "")
        summary = article.get("summary", "")
        combined_text = f"{title} {summary}".strip()
        texts_for_embedding.append(combined_text)

    print(f"Generating embeddings for {len(texts_for_embedding)} articles...")

    # Get embeddings from Mistral AI
    embeddings_result = await openai_service.get_embeddings(texts_for_embedding)

    if embeddings_result.get("success"):
        embeddings_data = embeddings_result["embeddings"]

        # Add embeddings to articles
        for i, article in enumerate(articles):
            if i < len(embeddings_data):
                article["embedding"] = embeddings_data[i].embedding
                article["embedding_model"] = "mistral-embed"
            else:
                article["embedding"] = None
                article["embedding_model"] = None

        print(f"✅ Embeddings generated successfully for {len(articles)} articles")
    else:
        print(f"❌ Failed to generate embeddings: {embeddings_result.get('error')}")
        # Add None embeddings if generation failed
        for article in articles:
            article["embedding"] = None
            article["embedding_model"] = None

    return articles


def split_markdown_into_chunks(
    markdown_content: str, chunk_size: int = 3000
) -> List[str]:
    """
    Split large markdown content into smaller chunks for processing

    Args:
        markdown_content (str): The full markdown content
        chunk_size (int): Maximum size of each chunk

    Returns:
        List[str]: List of markdown chunks
    """
    if len(markdown_content) <= chunk_size:
        return [markdown_content]

    chunks = []
    current_chunk = ""

    # Split by lines to avoid breaking in the middle of content
    lines = markdown_content.split("\n")

    for line in lines:
        # If adding this line would exceed chunk size, save current chunk and start new one
        if len(current_chunk) + len(line) + 1 > chunk_size and current_chunk:
            chunks.append(current_chunk.strip())
            current_chunk = line + "\n"
        else:
            current_chunk += line + "\n"

    # Add the last chunk if it has content
    if current_chunk.strip():
        chunks.append(current_chunk.strip())

    return chunks


async def preprocess_data(
    data: Any, max_chunks: int = 3, source_name: str = "dailystar"
) -> Dict[str, Any]:
    """
    Preprocess scraped data using Mistral to clean and structure it into a news format

    Args:
        data: Raw scraped data from the scraping service
        max_chunks: Maximum number of chunks to process (default: 3)
        source_name: Name of the news source for file naming (default: "dailystar")

    Returns:
        Dict[str, Any]: Cleaned and structured news data
    """
    try:
        # Convert data to dict format - handle different types gracefully
        try:
            if hasattr(data, "dict") and callable(getattr(data, "dict")):
                data_dict = data.dict()
            elif isinstance(data, dict):
                data_dict = data
            else:
                data_dict = {"content": str(data)}
        except Exception:
            data_dict = {"content": str(data)}

        # Extract the markdown content from the scraped data
        markdown_content = data_dict.get("markdown", "")
        original_url = data_dict.get("url", "")

        if not markdown_content:
            return {
                "success": False,
                "error": "No markdown content found in scraped data",
                "original_data": data_dict,
            }

        # Split markdown into chunks (keep small for reliability)
        chunks = split_markdown_into_chunks(markdown_content, chunk_size=3000)

        # Process chunks based on max_chunks parameter, but don't exceed available chunks
        chunks_to_process = min(max_chunks, len(chunks))
        if chunks_to_process == 0:
            return {
                "success": False,
                "error": "No chunks available to process",
                "original_data": {"total_content_length": len(markdown_content)},
            }

        print(
            f"Processing {chunks_to_process} chunks out of {len(chunks)} total chunks (max requested: {max_chunks})"
        )

        all_articles: List[Dict[str, Any]] = []
        processed_chunks = 0
        model_used = None

        for i in range(chunks_to_process):
            current_chunk = chunks[i]
            print(f"\n--- Processing Chunk {i+1}/{chunks_to_process} ---")
            print(f"Chunk length: {len(current_chunk)} characters")
            print(f"Chunk preview: {current_chunk[:300]}...")

            # Create prompt for current chunk with URL extraction
            preprocessing_prompt = f"""
            Analyze this news content and extract news articles in JSON format.

            Content to analyze (Chunk {i+1} of {chunks_to_process}):
            {current_chunk}

            Return ONLY a valid JSON object with this structure:
            {{
                "news_articles": [
                    {{
                        "title": "Article title",
                        "summary": "Brief summary",
                        "category": "News category if available",
                        "url": "Full URL to the news article if found in content, otherwise null"
                    }}
                ]
            }}

            Important: 
            - Return ONLY the JSON object, no additional text
            - Extract URLs from the content if they point to full articles
            - If no specific article URL is found, set url to null
            """

            print(f"Sending chunk {i+1} to Mistral AI...")

            # Use Mistral AI service to preprocess the current chunk
            result = await openai_service.preprocess_content(preprocessing_prompt)

            print(
                f"Mistral response meta for chunk {i+1}: success={result.get('success')}"
            )

            if result.get("success"):
                try:
                    response_text = result["response"]
                    model_used = result.get("model", model_used)

                    # Mistral should return clean JSON (response_format json_object). Still, be defensive.
                    json_text = response_text
                    if isinstance(
                        response_text, str
                    ) and response_text.lstrip().startswith("```"):
                        # Extract JSON from fenced block if present
                        start_tag = "```json"
                        start = response_text.find(start_tag)
                        if start != -1:
                            start += len(start_tag)
                            end = response_text.find("```", start)
                            if end == -1:
                                end = len(response_text)
                            json_text = response_text[start:end].strip()
                        else:
                            # Remove generic fences
                            json_text = response_text.strip().strip("`")

                    print(
                        f"Extracted JSON sample (first 200 chars): {json_text[:200]}..."
                    )

                    chunk_data = json.loads(json_text)
                    chunk_articles = chunk_data.get("news_articles", [])

                    # Process each article to add missing fields and chunk source
                    for article in chunk_articles:
                        # Add chunk source
                        article["chunk_source"] = f"chunk_{i+1}"

                        # Ensure URL field exists and handle null values
                        if "url" not in article or article["url"] is None:
                            article["url"] = None

                        # Add original source URL if article URL is missing
                        if not article["url"] and original_url:
                            article["source_url"] = original_url

                        # Ensure all required fields exist
                        if "title" not in article:
                            article["title"] = "Untitled Article"
                        if "summary" not in article:
                            article["summary"] = "No summary available"
                        if "category" not in article:
                            article["category"] = "general"

                    all_articles.extend(chunk_articles)
                    processed_chunks += 1
                    print(
                        f"✅ Chunk {i+1} processed successfully - {len(chunk_articles)} articles found"
                    )
                except Exception as e:
                    print(f"❌ Failed to parse chunk {i+1} JSON: {str(e)}")
                    response = result.get("response")
                    if isinstance(response, str):
                        print(f"Raw response (first 200): {response[:200]}...")
                    else:
                        print(f"Raw response: {response}")
            else:
                print(f"❌ Chunk {i+1} processing failed: {result.get('error')}")

            # Light delay to avoid rate limits
            if i < chunks_to_process - 1:
                await asyncio.sleep(0.75)

        # Combine all articles into final response
        combined_data = {
            "news_articles": all_articles,
            "total_articles": len(all_articles),
            "source": f"{source_name.title()} News",
            "processing_summary": f"Processed {processed_chunks} chunks out of {len(chunks)} total chunks (max requested: {max_chunks})",
            "chunks_processed": processed_chunks,
            "total_chunks": len(chunks),
            "chunk_size": 3000,
            "max_chunks_requested": max_chunks,
        }

        # Generate embeddings for all articles
        print("\n--- Generating Embeddings ---")
        articles_with_embeddings = await generate_embeddings_for_articles(all_articles)
        combined_data["news_articles"] = articles_with_embeddings

        # Save the processed data to JSON
        print("\n--- Saving Data ---")
        saved_filepath = save_news_json(combined_data, source_name)

        return {
            "success": True,
            "preprocessed_data": {
                "structured_news": combined_data,
                "chunks_processed": processed_chunks,
                "total_chunks": len(chunks),
                "chunk_size": 3000,
            },
            "original_data": {
                "total_content_length": len(markdown_content),
                "chunks_available": len(chunks),
                "original_url": original_url,
            },
            "processing_info": {
                "model_used": model_used or "mistral-large-latest",
                "chunks_processed": processed_chunks,
                "max_chunks_requested": max_chunks,
            },
            "saved_file": saved_filepath,
        }

    except Exception as e:
        return {
            "success": False,
            "error": f"Preprocessing error: {str(e)}",
            "original_data": str(data) if data else "No data",
        }
