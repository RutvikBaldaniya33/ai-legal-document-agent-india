import os
import uuid
from datetime import datetime, timezone
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from dotenv import load_dotenv

load_dotenv()

_client = None

def get_client():
    global _client
    if _client is None:
        uri = os.getenv("MONGODB_URI")
        if not uri:
            raise ValueError("MONGODB_URI not set in .env")
        _client = MongoClient(uri)
        # Verify connection
        _client.admin.command("ping")
        print("MongoDB connected.")
    return _client

def get_database():
    client = get_client()
    db_name = os.getenv("DB_NAME", "legal_agent")
    return client[db_name]


# ── Cases ──────────────────────────────────────────────────────────────────

def save_case(case_data: dict) -> str:
    """Insert a case document. Returns the generated case_id."""
    db = get_database()
    case_id = str(uuid.uuid4())
    doc = {
        "case_id": case_id,
        "created_at": datetime.now(timezone.utc),
        **case_data,
    }
    db.cases.insert_one(doc)
    return case_id

def get_case(case_id: str) -> dict | None:
    """Retrieve a case by case_id. Returns None if not found."""
    db = get_database()
    doc = db.cases.find_one({"case_id": case_id}, {"_id": 0})
    return doc


# ── Laws ───────────────────────────────────────────────────────────────────

def insert_law(law_data: dict) -> str:
    """Insert a law chunk. Returns inserted MongoDB _id as string."""
    db = get_database()
    result = db.laws.insert_one(law_data)
    return str(result.inserted_id)

def vector_search(query_embedding: list[float], dispute_type: str = None, top_k: int = 5) -> list[dict]:
    """
    Semantic search over laws collection using Atlas Vector Search.

    Requires an Atlas Search index named 'laws_vector_index' on the
    `embedding` field (cosine similarity, 768 dimensions for Gemini embeddings).

    Falls back to empty list if index not yet created.
    """
    db = get_database()

    pipeline = [
        {
            "$vectorSearch": {
                "index": "laws_vector_index",
                "path": "embedding",
                "queryVector": query_embedding,
                "numCandidates": top_k * 10,
                "limit": top_k,
            }
        },
        {
            "$project": {
                "_id": 0,
                "title": 1,
                "state": 1,
                "category": 1,
                "content": 1,
                "score": {"$meta": "vectorSearchScore"},
            }
        },
    ]

    if dispute_type:
        pipeline.insert(1, {"$match": {"category": dispute_type}})

    try:
        results = list(db.laws.aggregate(pipeline))
        return results
    except Exception as e:
        print(f"Vector search failed (index may not exist yet): {e}")
        return []


# ── Health check ───────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("Testing MongoDB connection...")
    db = get_database()

    # Test save_case
    test_id = save_case({
        "dispute_type": "tenant",
        "jurisdiction": "Gujarat",
        "user_input": "Landlord not returning deposit",
        "case_strength": 74,
    })
    print(f"save_case OK — case_id: {test_id}")

    # Test get_case
    fetched = get_case(test_id)
    print(f"get_case OK — dispute_type: {fetched['dispute_type']}")

    # Test insert_law
    law_id = insert_law({
        "title": "Gujarat Rent Control Act",
        "state": "Gujarat",
        "category": "tenant",
        "content": "Section 12: Landlord must return deposit within 30 days of vacating.",
        "embedding": [0.0] * 768,  # dummy embedding for test
    })
    print(f"insert_law OK — _id: {law_id}")

    print("\nAll tests passed.")
