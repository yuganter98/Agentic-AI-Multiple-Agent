from chromadb.utils import embedding_functions

class EmbeddingModel:
    """
    Encapsulates the embedding model logic for RAG.
    Uses ChromaDB's built-in ONNX embedding (fast, lightweight, no large downloads).
    """
    def __init__(self):
        # DefaultEmbeddingFunction uses a tiny built-in ONNX model (~30MB vs 500MB sentence-transformers)
        self.ef = embedding_functions.DefaultEmbeddingFunction()
        
    def get_embedding_function(self):
        """
        Returns the instantiated embedding function for ChromaDB to use.
        """
        return self.ef
