import os
import httpx

from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

mcp = FastMCP("github-intelligence-tool")

def github_headers():
    return{
        "Authorization":f"token {GITHUB_TOKEN}",
        "Accept":"application/vnd.github.v3+json"
    }

@mcp.tool()
async def get_repository(owner: str, repo: str) -> dict:
    """Get metadata about a GitHub repository."""

    url = f"https://api.github.com/repos/{owner}/{repo}"

    async with httpx.AsyncClient() as client:
        response = await client.get(
            url,
            headers=github_headers()
        )
    response.raise_for_status()

    data = response.json()

    return {
        "name": data["full_name"],
        "description": data["description"],
        "language": data["language"],
        "stars": data["stargazers_count"],
        "forks": data["forks_count"],
        "open_issues": data["open_issues_count"],
        "default_branch": data["default_branch"],
        "created_at": data["created_at"],
        "updated_at": data["updated_at"],
        "url": data["html_url"],
    }


@mcp.tool()
async def get_repository_tree(owner: str,repo: str,branch: str = "main", recursive: bool = False) -> list:
    
    """Get the file tree of a GitHub repository. Use recursive=True to get all files."""

    url = f"https://api.github.com/repos/{owner}/{repo}/git/trees/{branch}"
    params = {}
    if recursive:
        params["recursive"] = "1"

    async with httpx.AsyncClient() as client:
        response = await client.get(
            url,
            headers=github_headers(),
            params=params,
        )
    response.raise_for_status()

    data = response.json()
    
    # Cap the results at 500 files to prevent hitting API token limits on massive repositories
    tree = data.get("tree", [])
    if len(tree) > 500:
        tree = tree[:500]

    return [
        {
            "path": item["path"],
            "type": item["type"],
        }
        for item in tree
    ]

@mcp.tool()
async def get_file(
    owner: str,
    repo: str,
    path: str,
) -> str:
    """Get the contents of a file from a GitHub repository."""

    url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"

    async with httpx.AsyncClient() as client:
        response = await client.get(
            url,
            headers=github_headers(),
        )

    response.raise_for_status()

    data = response.json()

    import base64

    content = base64.b64decode(data["content"]).decode("utf-8")

    return content


@mcp.tool()
async def get_open_issues(owner: str, repo: str) -> list:
    """Get the latest open issues for a GitHub repository."""
    url = f"https://api.github.com/repos/{owner}/{repo}/issues"
    params = {"state": "open", "per_page": 10}

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=github_headers(), params=params)
    response.raise_for_status()

    # The issues endpoint returns both issues and PRs. PRs have a 'pull_request' key.
    issues = [item for item in response.json() if "pull_request" not in item]
    
    return [
        {
            "title": issue["title"],
            "number": issue["number"],
            "user": issue["user"]["login"],
            "created_at": issue["created_at"],
            "html_url": issue["html_url"]
        }
        for issue in issues
    ]


@mcp.tool()
async def get_pull_requests(owner: str, repo: str) -> list:
    """Get the latest open pull requests for a GitHub repository."""
    url = f"https://api.github.com/repos/{owner}/{repo}/pulls"
    params = {"state": "open", "per_page": 10}

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=github_headers(), params=params)
    response.raise_for_status()

    return [
        {
            "title": pr["title"],
            "number": pr["number"],
            "user": pr["user"]["login"],
            "created_at": pr["created_at"],
            "html_url": pr["html_url"]
        }
        for pr in response.json()
    ]


@mcp.tool()
async def get_recent_commits(owner: str, repo: str) -> list:
    """Get the recent commits for a GitHub repository."""
    url = f"https://api.github.com/repos/{owner}/{repo}/commits"
    params = {"per_page": 10}

    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=github_headers(), params=params)
    response.raise_for_status()

    return [
        {
            "message": commit["commit"]["message"].split("\\n")[0],
            "author": commit["commit"]["author"]["name"],
            "date": commit["commit"]["author"]["date"],
            "sha": commit["sha"][:7],
            "html_url": commit["html_url"]
        }
        for commit in response.json()
    ]


if __name__ == "__main__":
    mcp.run(transport="stdio")