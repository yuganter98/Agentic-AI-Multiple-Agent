import chromadb
from rag.embedding import EmbeddingModel

class KnowledgeVectorStore:
    """
    Handles interactions with the ChromaDB 'knowledge_base' collection
    for structured document RAG.
    """
    def __init__(self):
        # Instantiate persistent client but defer embedding model
        self.client = chromadb.PersistentClient(path="./chroma_db")
        self._collection = None
        self._embedding_model = None

    @property
    def embedding_model(self):
        if self._embedding_model is None:
            from rag.embedding import EmbeddingModel
            self._embedding_model = EmbeddingModel()
        return self._embedding_model

    @property
    def collection(self):
        if self._collection is None:
            self._collection = self.client.get_or_create_collection(
                name="knowledge_base",
                embedding_function=self.embedding_model.get_embedding_function()
            )
        return self._collection


    def add_chunks(self, chunks):
        """
        Embeds and stores document chunks in the vector database.
        """
        if not chunks:
            return
            
        texts = [chunk.page_content for chunk in chunks]
        metadatas = [chunk.metadata for chunk in chunks]
        # Construct predictable pseudo-unique IDs from source metadata
        ids = [f"doc_{i}_{chunk.metadata.get('source', 'unknown')}_{chunk.metadata.get('page', 0)}" for i, chunk in enumerate(chunks)]
        
        try:
            self.collection.upsert(
                documents=texts,
                metadatas=metadatas,
                ids=ids
            )
            print(f"[KnowledgeVectorStore] Upserted {len(texts)} document chunks.")
        except Exception as e:
            print(f"[KnowledgeVectorStore] Error upserting chunks: {e}")

    def search_similar(self, query: str, n_results: int = 5) -> list[str]:
        """
        Searches the DB for document chunks similar to the query 
        and returns the top 5 results relevant to the user's task.
        """
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=min(n_results, self.collection.count()) if self.collection.count() > 0 else 0
            )
            
            if results and results.get("documents"):
                return results["documents"][0]
            return []
        except Exception as e:
            print(f"[KnowledgeVectorStore] Error searching similar documents: {e}")
            return []

    def get_all_documents(self) -> list[str]:
        """
        Retrieves all document texts from the ChromaDB collection.
        Useful for keyword matching.
        """
        try:
            results = self.collection.get()
            if results and results.get("documents"):
                return results["documents"]
            return []
        except Exception as e:
            print(f"[KnowledgeVectorStore] Error fetching all documents: {e}")
            return []
