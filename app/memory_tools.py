import json
import os
from langchain_core.tools import tool

MEMORY_FILE = "repository_memory.json"

@tool()
def store_repository_memory(repository: str, memory_text: str) -> str:
    """
    Store important information about a repository for future reference.
    Use this to save architectural findings, key paths, or summaries that 
    will be useful the next time this repository is analyzed.
    """
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r") as f:
                data = json.load(f)
        except json.JSONDecodeError:
            data = {}
    else:
        data = {}
        
    data[repository] = memory_text
    
    with open(MEMORY_FILE, "w") as f:
        json.dump(data, f, indent=4)
        
    return f"Memory successfully stored for {repository}"

@tool()
def get_repository_memory(repository: str) -> str:
    """
    Retrieve previously stored memory about a repository.
    Use this to recall architectural findings, key paths, or summaries 
    that were saved during previous sessions.
    """
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r") as f:
                data = json.load(f)
            if repository in data:
                return data[repository]
        except json.JSONDecodeError:
            return f"Error reading memory for {repository}."
            
    return f"No previous memory found for {repository}."
