import chromadb
from chromadb.utils import embedding_functions

class VectorStore:
    """
    Handles interactions with the ChromaDB vector database.
    """
    def __init__(self):
        # Initialize an in-memory or persisted ChromaDB client
        self.client = chromadb.PersistentClient(path="./chroma_db")
        
        # Use sentence-transformers exactly as requested
        self.sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )
        
        # Get or create the memory collection using the specified embedding function
        self.collection = self.client.get_or_create_collection(
            name="research_memory",
            embedding_function=self.sentence_transformer_ef
        )

    def store_document(self, text: str, doc_id: str):
        """
        Embeds and stores the text document in the database.
        """
        try:
            # We use doc_id to ensure uniqueness in the collection
            self.collection.upsert(
                documents=[text],
                ids=[doc_id]
            )
        except Exception as e:
            print(f"Error storing document: {e}")

    def search_similar(self, query: str, n_results: int = 3) -> list[str]:
        """
        Searches the DB for documents similar to the query and returns the top n_results.
        """
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=min(n_results, self.collection.count()) 
                if self.collection.count() > 0 else 0
            )
            
            if results and results.get("documents"):
                # chroma returns a list of lists of documents
                return results["documents"][0]
            return []
        except Exception as e:
            print(f"Error searching similar documents: {e}")
            return []
