from rag.vector_store import KnowledgeVectorStore

class VectorRetriever:
    """
    Handles similarity-based vector retrieval using ChromaDB.
    """
    def __init__(self, vector_store: KnowledgeVectorStore = None):
        self.vector_store = vector_store or KnowledgeVectorStore()

    def retrieve(self, query: str, top_k: int = 10) -> list[str]:
        """
        Returns top semantic matches for the query.
        """
        return self.vector_store.search_similar(query=query, n_results=top_k)
