import json
import os
import glob
from typing import Dict, Any, List, Tuple
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer


class NewsMergerService:
    def __init__(self):
        self.data_dir = "data"
        self.similarity_threshold = 0.85

    def load_latest_news_files(self) -> Tuple[str | None, str | None]:
        """Load the latest news files for both sources"""
        try:
            # Find latest dailystar file
            dailystar_pattern = os.path.join(self.data_dir, "dailystar_news_*.json")
            dailystar_files = glob.glob(dailystar_pattern)
            if not dailystar_files:
                return None, None

            latest_dailystar = max(dailystar_files, key=os.path.getctime)

            # Find latest prothomalo file
            prothomalo_pattern = os.path.join(self.data_dir, "prothomalo_news_*.json")
            prothomalo_files = glob.glob(prothomalo_pattern)
            if not prothomalo_files:
                return latest_dailystar, None

            latest_prothomalo = max(prothomalo_files, key=os.path.getctime)

            return latest_dailystar, latest_prothomalo

        except Exception as e:
            print(f"Error finding latest news files: {e}")
            return None, None

    def load_news_data(self, filepath: str) -> Dict[str, Any]:
        """Load news data from JSON file"""
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading file {filepath}: {e}")
            return {}

    def calculate_text_similarity(self, text1: str, text2: str) -> float:
        """Calculate cosine similarity between two texts using TF-IDF"""
        try:
            if not text1.strip() or not text2.strip():
                return 0.0

            vectorizer = TfidfVectorizer(
                stop_words=None, ngram_range=(1, 2), max_features=1000
            )

            tfidf_matrix = vectorizer.fit_transform([text1, text2])
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]

            return float(similarity)

        except Exception as e:
            print(f"Error calculating similarity: {e}")
            return 0.0

    def find_duplicates(
        self, articles: List[Dict[str, Any]]
    ) -> List[Tuple[int, int, float]]:
        """Find duplicate articles using cosine similarity"""
        duplicates = []

        for i in range(len(articles)):
            for j in range(i + 1, len(articles)):
                article1 = articles[i]
                article2 = articles[j]

                text1 = (
                    f"{article1.get('title', '')} {article1.get('summary', '')}".strip()
                )
                text2 = (
                    f"{article2.get('title', '')} {article2.get('summary', '')}".strip()
                )

                similarity = self.calculate_text_similarity(text1, text2)

                if similarity >= self.similarity_threshold:
                    duplicates.append((i, j, similarity))

        return duplicates

    def merge_news_sources(self) -> Dict[str, Any]:
        """Merge news from both sources and remove duplicates"""
        try:
            dailystar_file, prothomalo_file = self.load_latest_news_files()

            if not dailystar_file and not prothomalo_file:
                return {"success": False, "error": "No news files found"}

            all_articles = []
            sources_loaded = []

            # Load Daily Star news
            if dailystar_file:
                dailystar_data = self.load_news_data(dailystar_file)
                if dailystar_data and "news_articles" in dailystar_data:
                    articles = dailystar_data["news_articles"]
                    for article in articles:
                        article["source_file"] = "dailystar"
                        article["source_name"] = "Daily Star Bangladesh"
                    all_articles.extend(articles)
                    sources_loaded.append("dailystar")
                    print(f"✅ Loaded {len(articles)} articles from Daily Star")

            # Load Prothom Alo news
            if prothomalo_file:
                prothomalo_data = self.load_news_data(prothomalo_file)
                if prothomalo_data and "news_articles" in prothomalo_data:
                    articles = prothomalo_data["news_articles"]
                    for article in articles:
                        article["source_file"] = "prothomalo"
                        article["source_name"] = "Prothom Alo"
                    all_articles.extend(articles)
                    sources_loaded.append("prothomalo")
                    print(f"✅ Loaded {len(articles)} articles from Prothom Alo")

            if not all_articles:
                return {"success": False, "error": "No articles found"}

            print(
                f"--- Merging {len(all_articles)} articles from {len(sources_loaded)} sources ---"
            )

            # Find and remove duplicates
            duplicates = self.find_duplicates(all_articles)
            articles_to_remove = set()

            for i, j, similarity in duplicates:
                articles_to_remove.add(j)
                print(f"Duplicate: Articles {i} and {j} (similarity: {similarity:.3f})")

            unique_articles = [
                article
                for idx, article in enumerate(all_articles)
                if idx not in articles_to_remove
            ]

            print(f"📊 Results: {len(all_articles)} → {len(unique_articles)} articles")

            # Create merged response
            merged_data = {
                "news_articles": unique_articles,
                "total_articles": len(unique_articles),
                "sources_loaded": sources_loaded,
                "deduplication_stats": {
                    "original_count": len(all_articles),
                    "duplicates_found": len(duplicates),
                    "final_count": len(unique_articles),
                    "similarity_threshold": self.similarity_threshold,
                },
                "processing_timestamp": str(np.datetime64("now")),
            }

            # Save merged data
            merged_filename = f"merged_news_{len(sources_loaded)}sources_{len(unique_articles)}articles.json"
            merged_filepath = os.path.join(self.data_dir, merged_filename)

            with open(merged_filepath, "w", encoding="utf-8") as f:
                json.dump(merged_data, f, ensure_ascii=False, indent=2)

            print(f"✅ Merged news saved to: {merged_filepath}")

            return {
                "success": True,
                "merged_data": merged_data,
                "saved_file": merged_filepath,
                "deduplication_summary": {
                    "original": len(all_articles),
                    "duplicates_removed": len(duplicates),
                    "final": len(unique_articles),
                },
            }

        except Exception as e:
            return {"success": False, "error": f"Error merging news: {str(e)}"}
