from langchain_huggingface import HuggingFaceEmbeddings
from langchain_qdrant import QdrantVectorStore


embeddings=HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)


def create_vector_store(documents):
    vectorstore=QdrantVectorStore.from_documents(
        documents,
        embedding=embeddings,
        path="./qdrant_data",
        collection_name="github_repository",
    )

    return vectorstore

from qdrant_client import QdrantClient

def get_vector_store():
    
    client = QdrantClient(path="./qdrant_data")
    return QdrantVectorStore(
        client=client,
        collection_name="github_repository",
        embedding=embeddings,
    )