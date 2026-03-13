from agents.base_agent import BaseAgent
from rag.document_loader import DocumentLoader
from rag.chunker import DocumentChunker
from rag.vector_store import KnowledgeVectorStore

class KnowledgeAgent(BaseAgent):
    """
    Agent responsible for ingesting PDFs from the data/documents folder, chunking them,
    and retrieving the top relevant chunks to enrich context dynamically.
    """
    def __init__(self, llm_provider=None):
        super().__init__(llm_provider)
        self.vector_store = KnowledgeVectorStore()
        
    def ingest_documents(self):
        """
        Loads, chunks, and stores documents from the data directory.
        Should be run automatically or optionally on startup.
        """
        loader = DocumentLoader()
        documents = loader.load_documents()
        
        if documents:
            chunker = DocumentChunker()
            chunks = chunker.split_documents(documents)
            self.vector_store.add_chunks(chunks)
            print(f"[KnowledgeAgent] Processed and verified {len(chunks)} document chunks from data.")
        else:
            print("[KnowledgeAgent] No raw PDF documents found to ingest in data/documents.")
            
    def retrieve_knowledge(self, query: str) -> list[dict]:
        """
        Retrieves relevant document chunks using hybrid search (vector + keyword)
        and then reranks the candidates using a cross-encoder model.
        Returns the top chunks filtered by a 0.7 relevance threshold.
        """
        from rag.hybrid_retriever import HybridRetriever
        from rag.reranker import Reranker
        
        print(f"[KnowledgeAgent] Executing Hybrid Retrieval for: {query}")
        hybrid_retriever = HybridRetriever(self.vector_store)
        candidate_chunks = hybrid_retriever.retrieve(query, top_k=10)
        
        if not candidate_chunks:
            print("[KnowledgeAgent] No relevant knowledge base candidates found.")
            return []
            
        print(f"[KnowledgeAgent] Reranking {len(candidate_chunks)} candidates...")
        reranker = Reranker()
        top_chunks = reranker.rerank(query, candidate_chunks, top_k=3)
        
        # Relevance Filtering: Set similarity threshold of 0.7
        relevant_chunks = [
            chunk for chunk in top_chunks
            if chunk["score"] >= 0.7
        ]
        
        if not relevant_chunks:
            print("[KnowledgeAgent] No chunks passed similarity threshold of 0.7. Skipping RAG.")
            return []
            
        print(f"[KnowledgeAgent] Found {len(relevant_chunks)} highly relevant chunks passing threshold.")
        return relevant_chunks
