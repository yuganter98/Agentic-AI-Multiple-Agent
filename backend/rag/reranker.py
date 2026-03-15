class Reranker:
    """
    Rescores a list of chunks regarding a specific query.
    Uses a simple score-passthrough approach compatible with Render free tier
    (no sentence_transformers required).
    """
    def __init__(self, model_name: str = None):
        # No heavy model needed - we use the existing vector similarity scores
        pass
        
    def rerank(self, query: str, documents: list[dict], top_k: int = 3) -> list[dict]:
        """
        Reranks retrieved chunk list based on existing similarity scores.
        """
        if not documents:
            return []
        
        # Sort by existing score (set by HybridRetriever)
        sorted_docs = sorted(
            documents,
            key=lambda x: x.get("score", 0) if isinstance(x, dict) else 0,
            reverse=True
        )
        
        return sorted_docs[:top_k]
