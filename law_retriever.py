"""
Tool 2 — Law Retriever
Input : dispute_type, state
Output: list[LawDocument]

Current: MongoDB find() with state → category fallback
Upgrade path: swap _find_laws() with vector_search() from mongodb.py
"""

import logging
from typing import Optional

from pydantic import BaseModel
from dotenv import load_dotenv

from mongodb import get_database

load_dotenv()

logger = logging.getLogger(__name__)

# ── Pydantic model ─────────────────────────────────────────────────────────

class LawDocument(BaseModel):
    title: str
    state: str
    category: str
    content: str


# ── Internal query helpers ─────────────────────────────────────────────────

def _find_laws(query: dict, limit: int) -> list[dict]:
    """
    Raw MongoDB find. Single place to swap for vector_search() later.

    To upgrade to Atlas Vector Search:
      1. Generate query embedding: genai.embed_content(dispute_text)
      2. Replace this function body with: return vector_search(embedding, dispute_type)
    """
    db = get_database()
    cursor = db.laws.find(query, {"_id": 0}).limit(limit)
    return list(cursor)


# ── Main function ──────────────────────────────────────────────────────────

def get_relevant_laws(
    dispute_type: str,
    state: Optional[str] = None,
    limit: int = 5,
) -> list[LawDocument]:
    """
    Retrieve relevant laws from MongoDB.

    Strategy:
      Pass 1 — category + state match (state-specific laws first)
      Pass 2 — category only fallback (central acts, e.g. Consumer Protection Act 2019)

    Args:
        dispute_type : "tenant" or "consumer"
        state        : Indian state name, e.g. "Gujarat". None = skip Pass 1.
        limit        : Max laws to return.

    Returns:
        List of LawDocument. Empty list if nothing found.

    Raises:
        RuntimeError: On MongoDB connection failure.
    """
    if not dispute_type:
        raise ValueError("dispute_type cannot be empty.")

    results: list[dict] = []

    try:
        # Pass 1: state-specific laws
        if state and state.strip():
            logger.info(f"Law retrieval Pass 1 — category={dispute_type!r}, state={state!r}")
            results = _find_laws(
                {"category": dispute_type, "state": state.strip()},
                limit,
            )
            logger.info(f"Pass 1 found {len(results)} result(s).")

        # Pass 2: fallback to central/national laws if Pass 1 empty or state not given
        if not results:
            logger.info(f"Law retrieval Pass 2 — category={dispute_type!r}, no state filter.")
            results = _find_laws(
                {"category": dispute_type},
                limit,
            )
            logger.info(f"Pass 2 found {len(results)} result(s).")

        if not results:
            logger.warning(f"No laws found for dispute_type={dispute_type!r}, state={state!r}.")
            return []

        return [LawDocument(**doc) for doc in results]

    except Exception as e:
        logger.error(f"Law retrieval failed: {e}")
        raise RuntimeError(f"Law retrieval failed: {e}") from e


# ── Test ───────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s | %(name)s | %(message)s",
    )

    from app.db.mongodb import get_database

    db = get_database()

    # Seed test data (idempotent — clears before inserting)
    db.laws.delete_many({"_test": True})
    db.laws.insert_many([
        {
            "title": "Gujarat Rent Control Act, 1947",
            "state": "Gujarat",
            "category": "tenant",
            "content": "Section 12: Landlord must return security deposit within 30 days of vacating.",
            "_test": True,
        },
        {
            "title": "Transfer of Property Act, 1882",
            "state": "India",
            "category": "tenant",
            "content": "Section 108: Tenant rights and obligations under lease agreements.",
            "_test": True,
        },
        {
            "title": "Consumer Protection Act, 2019",
            "state": "India",
            "category": "consumer",
            "content": "Section 35: Complaint can be filed for defective goods or deficient services.",
            "_test": True,
        },
        {
            "title": "Maharashtra Rent Control Act, 1999",
            "state": "Maharashtra",
            "category": "tenant",
            "content": "Section 7: Tenant protections against unlawful eviction.",
            "_test": True,
        },
    ])
    print("Test data seeded.\n")

    # Test 1: state-specific hit
    print("Test 1 — tenant + Gujarat (should return Gujarat act first)")
    laws = get_relevant_laws("tenant", "Gujarat")
    for law in laws:
        print(f"  [{law.state}] {law.title}")

    # Test 2: state with no specific law → fallback
    print("\nTest 2 — tenant + Rajasthan (no state law → fallback to central)")
    laws = get_relevant_laws("tenant", "Rajasthan")
    for law in laws:
        print(f"  [{law.state}] {law.title}")

    # Test 3: consumer, no state
    print("\nTest 3 — consumer, no state")
    laws = get_relevant_laws("consumer", None)
    for law in laws:
        print(f"  [{law.state}] {law.title}")

    # Test 4: unknown category
    print("\nTest 4 — unknown category (should return empty list)")
    laws = get_relevant_laws("criminal", "Gujarat")
    print(f"  Returned {len(laws)} laws (expected 0)")

    # Cleanup
    db.laws.delete_many({"_test": True})
    print("\nTest data cleaned up.")
    print("\nAll tests passed.")
