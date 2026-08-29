from langchain_core.tools import tool


from app.vector_store import get_vector_store

from qdrant_client.http import models


@tool()
def search_repository(query: str, repository: str) -> str:

    """
    Search the indexed GitHub repository for relevant source code
    and documentation.

    Use this tool when the user asks about how the repository works,
    implementation details, architecture, algorithms, functions,
    classes, or specific code behavior.
    """

    vector_store = get_vector_store()

    results = vector_store.similarity_search(
        query,
        k=5,
        filter=models.Filter(
            must=[
                models.FieldCondition(
                    key="metadata.repository",
                    match=models.MatchValue(value=repository)
                )
            ]
        ),
    )

    if not results:
        return "No relevant repository content was found."

    output = []

    for result in results:
        output.append(
            f"""
            FILE: {result.metadata.get("path", "unknown")}

            CONTENT:
            {result.page_content}
            """
        )

    return "\n\n---\n\n".join(output)

    