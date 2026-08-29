from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

SUPPORTED_EXTENSIONS = {
    ".py",
    ".cpp",
    ".h",
    ".hpp",
    ".js",
    ".ts",
    ".java",
    ".go",
    ".rs",
    ".md",
    ".txt",
}

IGNORED_DIRECTORIES = {
    ".git",
    "node_modules",
    "dist",
    "build",
    "__pycache__",
    ".venv",
}


def should_index(path:str) -> bool:
    
    parts = path.split("/")

    if any(directory in IGNORED_DIRECTORIES for directory in parts):
        return False

    return any(
        path.endswith(extension)
        for extension in SUPPORTED_EXTENSIONS
    )

def create_document(path: str, content: str , repository: str , branch: str ) -> Document:

    return Document(
        page_content=content,
        metadata={
            "path": path,
            "repository": repository,
            "branch": branch,
        },
    )


splitter = RecursiveCharacterTextSplitter(
    chunk_size=1200,
    chunk_overlap=200,
)

def split_documents(documents):
    return splitter.split_documents(documents)