from chromadb.utils import embedding_functions

class EmbeddingModel:
    """
    Encapsulates the embedding model logic for RAG.
    """
    def __init__(self):
        # Use sentence-transformers all-MiniLM-L6-v2 model as requested
        self.ef = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )
        
    def get_embedding_function(self):
        """
        Returns the instantiated embedding function for ChromaDB to use.
        """
        return self.ef
