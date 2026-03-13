from langchain_text_splitters import RecursiveCharacterTextSplitter

class DocumentChunker:
    """
    Handles splitting loaded document texts into overlapping token chunks.
    """
    def __init__(self, chunk_size: int = 200, chunk_overlap: int = 50):
        # Use tiktoken encoder to reliably split by tokens (200 per chunk as requested)
        self.text_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )

    def split_documents(self, documents):
        """
        Takes raw documents and returns split text chunks.
        """
        if not documents:
            return []
        return self.text_splitter.split_documents(documents)
