import re
from typing import List
from rag.vector_store import KnowledgeVectorStore

class KeywordRetriever:
    """
    Handles simple exact-match and keyword-based retrieval across all documents.
    """
    def __init__(self, vector_store: KnowledgeVectorStore = None):
        self.vector_store = vector_store or KnowledgeVectorStore()

    def retrieve(self, query: str) -> List[str]:
        """
        Returns chunks containing simple query keywords.
        """
        all_docs = self.vector_store.get_all_documents()
        if not all_docs:
            return []

        # Simple keyword extraction (ignore case and punctuation)
        keywords = set(re.findall(r'\b\w+\b', query.lower()))
        
        # Stopwords to ignore
        stopwords = {"the", "a", "an", "is", "in", "it", "to", "and", "of", "for", "on", "with", "what", "where", "how", "why"}
        keywords = {k for k in keywords if k not in stopwords}

        if not keywords:
            return []

        matched_chunks = []
        for doc in all_docs:
            doc_lower = doc.lower()
            # Basic scoring: how many unique keywords are present in the chunk
            match_count = sum(1 for kw in keywords if kw in doc_lower)
            if match_count > 0:
                matched_chunks.append((match_count, doc))

        # Sort by most keyword matches matches
        matched_chunks.sort(key=lambda x: x[0], reverse=True)
        
        # Return matched documents
        return [doc for _, doc in matched_chunks]
