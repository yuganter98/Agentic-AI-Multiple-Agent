import uuid
from agents.base_agent import BaseAgent
from memory.vector_store import VectorStore
from schemas.research_schema import ResearchResult

class MemoryAgent(BaseAgent):
    """
    Agent responsible for persisting research into the vector database
    and retrieving relevant contextual information using RAG.
    """
    def __init__(self, llm_provider=None):
        super().__init__(llm_provider)
        self.vector_store = VectorStore()
        
    def store_research(self, results: list[ResearchResult]):
        """
        Extracts the findings from a list of research results and
        stores each result in the vector database with a unique ID.
        """
        for count, result in enumerate(results):
            # Combine the step context with the actual finding
            payload = f"Context: {result.step}\nFinding: {result.result}"
            # Use UUID for robust chunk identification
            unique_id = str(uuid.uuid4())
            self.vector_store.store_document(text=payload, doc_id=unique_id)
            
        print(f"[MemoryAgent] Successfully stored {len(results)} chunks in memory.")

    def retrieve_context(self, query: str) -> list[str]:
        """
        Takes a query and searches the vector store for the top 3 similar past records.
        Returns them as a list of string chunks.
        """
        print(f"[MemoryAgent] Retrieving historical context for: {query}")
        return self.vector_store.search_similar(query=query, n_results=3)
