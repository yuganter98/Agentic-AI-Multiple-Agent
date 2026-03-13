from typing import List
from rag.vector_retriever import VectorRetriever
from rag.keyword_retriever import KeywordRetriever
from rag.vector_store import KnowledgeVectorStore

class HybridRetriever:
    """
    Combines results from Vector retrieval and Keyword retrieval,
    removing duplicates to ensure diverse candidates.
    """
    def __init__(self, vector_store: KnowledgeVectorStore = None):
        self.vector_store = vector_store or KnowledgeVectorStore()
        self.vector_retriever = VectorRetriever(self.vector_store)
        self.keyword_retriever = KeywordRetriever(self.vector_store)

    def retrieve(self, query: str, top_k: int = 3) -> List[dict]:
        """
        Combines top vector results & top keyword results and removes duplicates.
        Returns up to top_k distinct results formatted as dicts.
        """
        vector_results = self.vector_retriever.retrieve(query, top_k=top_k)
        keyword_results = self.keyword_retriever.retrieve(query)
        
        combined = []
        seen = set()
        
        # Merge and assign base confidence scores to the struct
        max_len = max(len(vector_results), len(keyword_results))
        for i in range(max_len):
            if i < len(vector_results):
                doc = vector_results[i]
                if doc not in seen:
                    combined.append({"text": doc, "score": 0.8})
                    seen.add(doc)
                    
            if i < len(keyword_results):
                doc = keyword_results[i]
                if doc not in seen:
                    combined.append({"text": doc, "score": 0.5})
                    seen.add(doc)
                    
            if len(combined) >= top_k:
                break
                
        return combined[:top_k]
