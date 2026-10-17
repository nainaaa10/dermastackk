"""
Dermastack Database Management & Persistence Layer.

Supports MongoDB via PyMongo with index management, and provides an in-memory
mock repository fallback when MongoDB is offline or in local demo mode.
"""

from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timezone
import asyncio
from bson import ObjectId
from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

from backend.app.core.config import settings
from backend.app.core.logging import logger


def serialize_doc(doc: Dict[str, Any]) -> Dict[str, Any]:
    """Recursively converts MongoDB ObjectIds and datetimes to JSON-serializable types."""
    if not isinstance(doc, dict):
        return doc
    clean = {}
    for k, v in doc.items():
        if k == "_id" and isinstance(v, ObjectId):
            clean["id"] = str(v)
        elif isinstance(v, ObjectId):
            clean[k] = str(v)
        elif isinstance(v, datetime):
            clean[k] = v.isoformat()
        elif isinstance(v, dict):
            clean[k] = serialize_doc(v)
        elif isinstance(v, list):
            clean[k] = [serialize_doc(item) if isinstance(item, dict) else item for item in v]
        else:
            clean[k] = v
    return clean


class DatabaseManager:
    """Manages MongoDB connection lifecycle and in-memory demo fallback."""

    def __init__(self):
        self.client: Optional[MongoClient] = None
        self.db = None
        self.is_connected: bool = False
        self.db_type: str = "in_memory_demo"

        # In-memory storage for demo mode or when MongoDB is unavailable
        self._in_memory_reports: Dict[str, Dict[str, Any]] = {}
        self._in_memory_ingredients: Dict[str, Dict[str, Any]] = {}

    def connect(self) -> bool:
        """
        Attempts to connect to MongoDB with a short timeout.
        Falls back to in-memory demo repository if unreachable.
        """
        try:
            logger.info("Attempting connection to MongoDB at %s ...", settings.MONGODB_URI)
            self.client = MongoClient(
                settings.MONGODB_URI,
                serverSelectionTimeoutMS=settings.MONGODB_TIMEOUT_MS,
                connectTimeoutMS=settings.MONGODB_TIMEOUT_MS
            )
            # Force server roundtrip check
            self.client.admin.command("ping")
            self.db = self.client[settings.MONGODB_DB_NAME]
            self.is_connected = True
            self.db_type = "mongodb"

            # Create Indexes
            self._ensure_indexes()
            logger.info("Successfully connected to MongoDB database '%s'.", settings.MONGODB_DB_NAME)
            return True
        except (ConnectionFailure, ServerSelectionTimeoutError, Exception) as e:
            self.is_connected = False
            self.db_type = "in_memory_demo"
            self.client = None
            self.db = None
            logger.warning(
                "MongoDB connection unavailable (%s). Falling back to In-Memory Demo persistence layer.",
                str(e)
            )
            return False

    def close(self):
        """Closes MongoDB connection if active."""
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed.")
        self.is_connected = False

    def _ensure_indexes(self):
        """Creates required indexes on MongoDB collections."""
        try:
            if self.db is not None:
                self.db.reports.create_index([("report_id", ASCENDING)], unique=True)
                self.db.reports.create_index([("created_at", DESCENDING)])
                self.db.ingredients.create_index([("key", ASCENDING)], unique=True)
                self.db.ingredients.create_index([("name", ASCENDING)])
                logger.info("Database indexes verified.")
        except Exception as e:
            logger.error("Failed to create database indexes: %s", str(e))

    async def save_report(self, report_dict: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Persists an analysis report to MongoDB or the in-memory fallback.
        Returns (success: bool, storage_type: str).
        """
        report_id = report_dict["report_id"]
        doc = dict(report_dict)
        doc["saved_at"] = datetime.now(timezone.utc).isoformat()

        if self.is_connected and self.db is not None:
            try:
                await asyncio.to_thread(self.db.reports.replace_one, {"report_id": report_id}, doc, upsert=True)
                return True, "mongodb"
            except Exception as e:
                logger.error("Failed to save report to MongoDB: %s", str(e))
                self._in_memory_reports[report_id] = doc
                return True, "in_memory_fallback"
        else:
            self._in_memory_reports[report_id] = doc
            return True, "in_memory_demo"

    async def get_report(self, report_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves a single report by unique report_id."""
        if self.is_connected and self.db is not None:
            try:
                doc = await asyncio.to_thread(self.db.reports.find_one, {"report_id": report_id})
                if doc:
                    return serialize_doc(doc)
            except Exception as e:
                logger.error("Error retrieving report from MongoDB: %s", str(e))

        doc = self._in_memory_reports.get(report_id)
        if doc:
            return serialize_doc(dict(doc))
        return None

    async def list_reports(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Lists recent analysis reports sorted newest first."""
        results = []
        if self.is_connected and self.db is not None:
            try:
                def _fetch():
                    cursor = self.db.reports.find({}, {"gradcam_heatmap": 0}).sort("created_at", DESCENDING).limit(limit)
                    return [serialize_doc(doc) for doc in cursor]

                results = await asyncio.to_thread(_fetch)
                return results
            except Exception as e:
                logger.error("Error listing reports from MongoDB: %s", str(e))

        sorted_reports = sorted(
            self._in_memory_reports.values(),
            key=lambda r: r.get("created_at", ""),
            reverse=True
        )[:limit]
        
        for r in sorted_reports:
            summary = dict(r)
            if "gradcam_heatmap" in summary and summary["gradcam_heatmap"]:
                summary["has_heatmap"] = True
                del summary["gradcam_heatmap"]
            results.append(serialize_doc(summary))
        return results

    def seed_ingredients(self, ingredients_list: List[Dict[str, Any]]):
        """Populates starter ingredients into MongoDB or in-memory dictionary."""
        for item in ingredients_list:
            key = item["key"].lower().strip()
            self._in_memory_ingredients[key] = item

            if self.is_connected and self.db is not None:
                try:
                    self.db.ingredients.replace_one({"key": key}, item, upsert=True)
                except Exception:
                    pass

    async def find_ingredient(self, query_key: str) -> Optional[Dict[str, Any]]:
        """Finds an ingredient by normalized key, exact name, or synonym."""
        query_norm = query_key.lower().strip()
        
        # 1. Exact key match
        if query_norm in self._in_memory_ingredients:
            return self._in_memory_ingredients[query_norm]

        # 2. Check names and synonyms in in-memory
        for item in self._in_memory_ingredients.values():
            if item.get("name", "").lower().strip() == query_norm:
                return item
            synonyms = [s.lower().strip() for s in item.get("synonyms", [])]
            if query_norm in synonyms:
                return item

        # 3. Substring/token match (e.g. "Fragrance / Parfum" -> matches "fragrance" or "parfum")
        for item in self._in_memory_ingredients.values():
            synonyms = [s.lower().strip() for s in item.get("synonyms", [])]
            for part in query_norm.replace("/", " ").replace("-", " ").split():
                if len(part) >= 4 and (part == item["key"] or part in synonyms):
                    return item

        # 4. Check MongoDB if connected
        if self.is_connected and self.db is not None:
            try:
                doc = await asyncio.to_thread(
                    self.db.ingredients.find_one,
                    {"$or": [{"key": query_norm}, {"name": {"$regex": f"^{query_norm}$", "$options": "i"}}, {"synonyms": query_norm}]}
                )
                if doc:
                    return serialize_doc(doc)
            except Exception as e:
                logger.error("Error querying ingredient in MongoDB: %s", str(e))

        return None

    async def list_all_ingredients(self) -> List[Dict[str, Any]]:
        """Returns all registered ingredients."""
        return list(self._in_memory_ingredients.values())


# Global database instance
db_manager = DatabaseManager()
