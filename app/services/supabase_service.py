import os
from typing import Any, Dict, List, Optional
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client, Client


class SupabaseService:
    def __init__(
        self,
        supabase_url: Optional[str] = None,
        api_key: Optional[str] = None,
        table_name: Optional[str] = None,
    ) -> None:
        load_dotenv()
        resolved_url = (
            supabase_url
            or os.getenv("SUPABASE_URL")
            or (
                f"https://{os.getenv('SUPABASE_PROJECT_ID', '')}.supabase.co"
                if os.getenv("SUPABASE_PROJECT_ID")
                else None
            )
        )
        resolved_key = (
            api_key or os.getenv("SUPABASE_KEY") or os.getenv("SUPABASE_SERVICE_KEY")
        )
        if not resolved_url or not resolved_key:
            raise ValueError(
                "SUPABASE_URL or SUPABASE_KEY not configured in environment"
            )
        self.client: Client = create_client(resolved_url, resolved_key)
        self.table_name: str = table_name or os.getenv("SUPABASE_TABLE", "articles_new")
        self.required_vector_dimension: int = int(os.getenv("EMBEDDING_DIM", "1536"))

    def _coerce_keywords(self, value: Any) -> Optional[List[str]]:
        if value is None:
            return None
        if isinstance(value, list):
            return [str(v) for v in value]
        if isinstance(value, str):
            parts = [p.strip() for p in value.split(",") if p.strip()]
            return parts or None
        return None

    def _coerce_int(self, value: Any) -> Optional[int]:
        if value is None:
            return None
        try:
            return int(value)
        except Exception:
            return None

    def _coerce_timestamp(self, value: Any) -> Optional[str]:
        if not value:
            return None
        if isinstance(value, str):
            return value
        if isinstance(value, datetime):
            return value.isoformat()
        return None

    def _coerce_embedding(self, value: Any) -> Optional[List[float]]:
        if not value:
            return None
        try:
            vec = [float(x) for x in value]
            if len(vec) != self.required_vector_dimension:
                return None
            return vec
        except Exception:
            return None

    def normalize_article_for_db(
        self, article: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Map an internal detailed article dict to DB row for 'articles_new'.
        Skips record if critical fields missing.
        """
        title: Optional[str] = article.get("title")
        full_text: Optional[str] = article.get("full_text")
        source_url: Optional[str] = article.get("source_url") or article.get("url")
        if not title or not full_text or not source_url:
            return None

        row: Dict[str, Any] = {
            "title": title,
            "full_text": full_text,
            "summary": article.get("summary"),
            "category": article.get("category"),
            "sentiment": article.get("sentiment"),
            "importance_level": self._coerce_int(article.get("importance_level")),
            "keywords": self._coerce_keywords(article.get("keywords")),
            "date_time": self._coerce_timestamp(article.get("date_time")),
            "location": article.get("location"),
            "named_entities": article.get("named_entities"),
            "source_name": article.get("source_name")
            or article.get("original_source_name"),
            "source_url": source_url,
            "thumbnail_url": article.get("thumbnail_url"),
            "language": article.get("language"),
        }

        embedding = self._coerce_embedding(article.get("embedding"))
        if embedding is not None:
            row["embedding"] = embedding

        return row

    def insert_articles(self, articles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Insert a list of articles into Supabase (no upsert)."""
        rows: List[Dict[str, Any]] = []
        for art in articles:
            row = self.normalize_article_for_db(art)
            if row is not None:
                rows.append(row)
        if not rows:
            return {"success": False, "error": "No valid rows to insert"}
        try:
            resp = self.client.table(self.table_name).insert(rows).execute()
            data = getattr(resp, "data", None)
            return {
                "success": True,
                "count": len(data) if data else 0,
                "response": data,
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def upsert_articles(self, articles: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Upsert a list of articles into Supabase using source_url as unique key."""
        rows: List[Dict[str, Any]] = []
        for art in articles:
            row = self.normalize_article_for_db(art)
            if row is not None:
                rows.append(row)

        if not rows:
            return {"success": False, "error": "No valid rows to upsert"}

        try:
            resp = (
                self.client.table(self.table_name)
                .upsert(rows, on_conflict="source_url")
                .execute()
            )
            return {
                "success": True,
                "count": len(rows),
                "response": getattr(resp, "data", None),
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
