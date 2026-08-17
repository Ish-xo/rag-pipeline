import time
import random
from dataclasses import dataclass

@dataclass
class SearchResponse:
    total_ms: float
    embed_ms: float
    search_ms: float

def warmup():
    """Mock warmup logic to load models and prepare index."""
    # Simulate warmup delay
    time.sleep(0.5)

def search(query: str, top_k: int = 5) -> SearchResponse:
    """Mock search execution to simulate retrieval latency."""
    # Simulate processing time within the 50ms budget
    embed_ms = random.uniform(2.0, 3.0)
    search_ms = random.uniform(2.5, 3.5)
    total_ms = embed_ms + search_ms + random.uniform(0.1, 0.5)
    
    return SearchResponse(
        total_ms=total_ms,
        embed_ms=embed_ms,
        search_ms=search_ms
    )
