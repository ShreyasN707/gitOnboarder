import json
from urllib.parse import urlparse

from langchain_mcp_adapters.client import MultiServerMCPClient

from app.repository_loader import (
    should_index,
    create_document,
    split_documents,
)

from app.vector_store import create_vector_store


def parse_github_url(url: str):

    parsed = urlparse(url)

    parts = parsed.path.strip("/").split("/")

    if len(parts) < 2:
        raise ValueError(
            "Invalid GitHub repository URL"
        )

    owner = parts[0]
    repo = parts[1]

    return owner, repo

def extract_mcp_content(output, parse_json=True):
    if isinstance(output, list):
        if len(output) > 1 and parse_json:
            return [json.loads(item.get("text", "")) for item in output]
        text = output[0].get("text", "")
    else:
        text = str(output)
    
    if parse_json:
        return json.loads(text)
    return text


async def ingest_repository(url: str):

    owner, repo = parse_github_url(url)

    client = MultiServerMCPClient(
        {
            "github": {
                "transport": "stdio",
                "command": "python",
                "args": [
                    "mcp_server/github_server.py"
                ],
            }
        }
    )

    tools = await client.get_tools()

    tools_by_name = {
        tool.name: tool
        for tool in tools
    }

    get_repository = tools_by_name[
        "get_repository"
    ]

    get_repository_tree = tools_by_name[
        "get_repository_tree"
    ]

    get_file = tools_by_name[
        "get_file"
    ]

    repository_raw = await get_repository.ainvoke(
        {
            "owner": owner,
            "repo": repo,
        }
    )
    
    repository = extract_mcp_content(repository_raw, parse_json=True)

    branch = repository["default_branch"]

    tree_raw = await get_repository_tree.ainvoke(
        {
            "owner": owner,
            "repo": repo,
            "branch": branch,
            "recursive": True,
        }
    )
    
    tree_response = extract_mcp_content(tree_raw, parse_json=True)
    
    print(f"DEBUG tree_response type: {type(tree_response)}")
    
    if isinstance(tree_response, dict):
        tree_items = tree_response.get("tree", [])
    else:
        tree_items = tree_response

    files = [
        item["path"]
        for item in tree_items
        if item["type"] == "blob"
        and should_index(item["path"])
    ]

    documents = []

    for path in files:

        content_raw = await get_file.ainvoke(
            {
                "owner": owner,
                "repo": repo,
                "path": path,
            }
        )
        
        content = extract_mcp_content(content_raw, parse_json=False)

        document = create_document(
            path,
            content,
            repository=f"{owner}/{repo}",
            branch=branch,
        )

        documents.append(document)

    chunks = split_documents(documents)

    for chunk in chunks[:3]:
        print(chunk.metadata)

    vector_store = create_vector_store(
        chunks
    )

    return {
        "repository": f"{owner}/{repo}",
        "branch": branch,
        "files_indexed": len(files),
        "chunks_created": len(chunks),
        "vector_store": vector_store,
    }