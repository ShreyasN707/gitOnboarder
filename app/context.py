from dataclasses import dataclass


@dataclass
class AgentContext:
    repository: str
    branch: str = "main"