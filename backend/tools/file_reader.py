import os

class FileReaderTool:
    """
    A tool to read the contents of files for the agent.
    """
    
    def read_file(self, path: str) -> str:
        """
        Attempts to read the contents of the given file path.
        """
        print(f"[FileReaderTool] Reading file: {path}")
        if not os.path.exists(path):
            return f"Error: File not found at {path}"
            
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            return f"Error reading file: {str(e)}"
