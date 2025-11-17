# Configuration Quick Reference

## How to Modify Agents

### Example: Add a new agent

```python
AGENTS.append({
    "name": "Trader Joe",
    "goal": "Accumulate 50 total resources of any type",
    "model": "qwen2.5:latest",
    "initial_resources": {
        "wool": 20,
        "lumber": 10,
        "grain": 5,
        "brick": 3,
        "ore": 2
    }
})
```

### Example: Change existing agent's goal

```python
# Find Alice in AGENTS list and update:
AGENTS[0]["goal"] = "Trade all lumber for ore"
```

## How to Modify Prompts

### Make agents more aggressive
```python
AGENT_INITIAL_MESSAGE = """Use aggressive negotiation tactics. 
Make the first offer and demand favorable terms. 
Record all deals immediately."""
```

### Make agents more collaborative
```python
AGENT_SYSTEM_PROMPT = """You are {name}, a friendly trading agent.

YOUR GOAL: {goal}

Work collaboratively with other agents to create mutually beneficial trades.
Always be fair and honest in your negotiations."""
```

## How to Change Simulation Behavior

### Longer agent turns
```python
MAX_ITERATIONS_PER_TURN = 20  # Default is 10
```

### Require more agents to finish before ending
```python
MIN_ACTIVE_AGENTS = 2  # Needs at least 2 agents still trading
```

### Use different model
```python
DEFAULT_MODEL = "llama3.2:latest"  # or "mistral:latest", etc.
```

### Adjust creativity
```python
MODEL_TEMPERATURE = 0.9  # Higher = more creative (default 0.7)
```

## Common Scenarios

### Three-agent scenario
```python
AGENTS = [
    {
        "name": "Alice",
        "goal": "Get 10 ore",
        "model": "qwen2.5:latest",
        "initial_resources": {"wool": 50, "lumber": 0, "grain": 0, "brick": 0, "ore": 0}
    },
    {
        "name": "Bob", 
        "goal": "Get 30 wool",
        "model": "qwen2.5:latest",
        "initial_resources": {"wool": 0, "lumber": 0, "grain": 0, "brick": 0, "ore": 20}
    },
    {
        "name": "Charlie",
        "goal": "Have balanced resources",
        "model": "qwen2.5:latest",
        "initial_resources": {"wool": 10, "lumber": 10, "grain": 10, "brick": 10, "ore": 10}
    }
]
```

### Competitive scenario with scarcity
```python
AGENTS = [
    {
        "name": "Miner",
        "goal": "Monopolize ore - get all ore in the system",
        "model": "qwen2.5:latest",
        "initial_resources": {"wool": 100, "lumber": 100, "grain": 100, "brick": 100, "ore": 5}
    },
    {
        "name": "Hoarder",
        "goal": "Never trade your ore under any circumstances",
        "model": "qwen2.5:latest",
        "initial_resources": {"wool": 10, "lumber": 10, "grain": 10, "brick": 10, "ore": 50}
    }
]
```

## Tips

1. **Goals should be specific and measurable** for better agent performance
2. **Start with 2-3 agents** to understand the dynamics
3. **Unbalanced starting resources** create more interesting negotiations
4. **Different models** can have different negotiation styles
5. **Temperature affects creativity** - try 0.3 for consistent behavior, 0.9 for variety
