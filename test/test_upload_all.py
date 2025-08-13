#!/usr/bin/env python3
"""
Test script for the /upload/all endpoint
"""

import requests
import json

BASE_URL = "http://127.0.0.1:8000"


def test_check_existing():
    """Test the check existing endpoint"""
    print("Testing /check/existing...")
    try:
        response = requests.get(f"{BASE_URL}/check/existing")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {e}")


def test_embedding_info():
    """Test to check embedding information in batch files"""
    print("\nChecking embedding information...")
    try:
        import json
        import glob
        import os
        
        data_dir = "data"
        embedding_info = {}
        
        for batch_num in range(1, 5):
            pattern = os.path.join(data_dir, f"detailed_news_batch{batch_num}_*.json")
            files = glob.glob(pattern)
            if files:
                latest_file = max(files, key=os.path.getctime)
                with open(latest_file, "r", encoding="utf-8") as f:
                    payload = json.load(f)
                
                articles = payload.get("detailed_news_data", {}).get("detailed_articles")
                if articles is None:
                    articles = payload.get("detailed_articles", [])
                
                if articles:
                    batch_info = {
                        "file": latest_file,
                        "total_articles": len(articles),
                        "articles_with_embeddings": 0,
                        "articles_without_embeddings": 0,
                        "embedding_dimensions": set()
                    }
                    
                    for article in articles:
                        embedding = article.get("embedding")
                        if embedding:
                            batch_info["articles_with_embeddings"] += 1
                            batch_info["embedding_dimensions"].add(len(embedding))
                        else:
                            batch_info["articles_without_embeddings"] += 1
                    
                    # Convert set to list for JSON serialization
                    batch_info["embedding_dimensions"] = list(batch_info["embedding_dimensions"])
                    embedding_info[f"batch_{batch_num}"] = batch_info
        
        print("Embedding Analysis:")
        print(json.dumps(embedding_info, indent=2))
        
    except Exception as e:
        print(f"Error analyzing embeddings: {e}")


def test_upload_all():
    """Test the upload all endpoint"""
    print("\nTesting /upload/all...")
    try:
        response = requests.get(f"{BASE_URL}/upload/all")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    print("Testing new upload endpoints...")
    test_check_existing()
    test_embedding_info()
    test_upload_all()
