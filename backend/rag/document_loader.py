import os
from langchain_community.document_loaders import PyPDFDirectoryLoader

class DocumentLoader:
    """
    Handles loading PDF documents from the file system.
    """
    def __init__(self, data_dir: str = "data/documents"):
        self.data_dir = data_dir

    def load_documents(self):
        """
        Loads all PDF documents from the configured directory.
        Creates the directory if it does not exist.
        """
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir, exist_ok=True)
            return []
            
        loader = PyPDFDirectoryLoader(self.data_dir)
        return loader.load()
