from typing import Any, Optional, Dict
# @classmethod makes this a static class shared across all instances

class AgentCommunication:
    _agents: Dict[str, Any] = {}

    @classmethod
    def register_agent(cls, name: str, agent: Any) -> None:
        cls._agents[name.lower()] = [agent, False]  # Use list instead of tuple for mutability

    @classmethod
    def get_agent(cls, name: str) -> Optional[Any]:
        if name.lower() not in cls._agents:
            return None
        return cls._agents.get(name.lower())[0]
    
    @classmethod
    def contains(cls, name: str) -> bool:
        return name.lower() in cls._agents

    @classmethod
    def keys(cls):
        return list(cls._agents.keys())

    @classmethod
    def clear(cls) -> None:
        cls._agents.clear()

    @classmethod
    def agent_finished(cls, name: str) -> None:
        cls._agents[name.lower()][1] = True
    
    @classmethod
    def get_active_agents(cls) -> list[str]:
        return [name for name, (agent, finished) in cls._agents.items() if not finished]

    @classmethod
    def __str__(cls) -> str:
        return f"Registered Agents: {', '.join(cls._agents.keys())}"