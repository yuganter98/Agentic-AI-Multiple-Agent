from sentence_transformers import CrossEncoder

class Reranker:
    """
    Rescores a list of chunks regarding a specific query using a cross-encoder model.
    """
    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"):
        self.model = CrossEncoder(model_name)
        
    def rerank(self, query: str, documents: list[dict], top_k: int = 3) -> list[dict]:
        """
        Reranks retrieved chunk list based on relevance scores, outputting normalized scores.
        """
        if not documents:
            return []
            
        import math
        def sigmoid(x):
            return 1 / (1 + math.exp(-x))
            
        # CrossEncoder scoring pairs the query and each document text
        texts = [doc["text"] if isinstance(doc, dict) else doc for doc in documents]
        pairs = [[query, text] for text in texts]
        
        # Get raw scores
        raw_scores = self.model.predict(pairs)
        
        # Zip documents with normalized 0.0-1.0 scores
        doc_score_pairs = [
            {"text": text, "score": round(sigmoid(float(score)), 4)} 
            for text, score in zip(texts, raw_scores)
        ]
        
        # Sort by descending score
        doc_score_pairs.sort(key=lambda x: x["score"], reverse=True)
        
        # Extract the top_k documents
        return doc_score_pairs[:top_k]
