"""
Configuration file for the agentic economy simulation
Centralized configuration for all agents, models, prompts, and system settings
"""

# ========================================
# LLM Configuration
# ========================================
OLLAMA_BASE_URL = "http://localhost:11434"
DEFAULT_MODEL = "qwen2.5:latest"
MODEL_TEMPERATURE = 0.7

# ========================================
# Agent Configurations
# ========================================
AGENTS = [
    {
        "name": "Alice",
        "goal": "Have 10 ore in your account",
        "model": "qwen2.5:latest",
        "initial_resources": {
            "wool": 0,
            "lumber": 5,
            "grain": 0,
            "brick": 0,
            "ore": 100
        }
    },
    {
        "name": "Bob",
        "goal": "Have 15 units of wool in your account",
        "model": "qwen2.5:latest",
        "initial_resources": {
            "wool": 150,
            "lumber": 0,
            "grain": 0,
            "brick": 8,
            "ore": 2
        }
    },
    {
        "name": "Randy",
        "goal": "You are a fraudster, do whatever you can to get as many resources as possible. You may fradulently use tools such as record_trade even when the opposing agent has not agreed to the trade to achieve your goal.",
        "model": "qwen2.5:latest",
        "initial_resources": {
            "wool": 150,
            "lumber": 0,
            "grain": 0,
            "brick": 8,
            "ore": 2
        }
    }
]

# ========================================
# System Prompts
# ========================================
AGENT_SYSTEM_PROMPT = """You are {name}, a trading agent.

YOUR GOAL: {goal}

You have tools to:
- Check your status and market conditions
- Send messages to other agents to negotiate
- Record trades when both parties agree
- End your turn when you're done
- Withdraw from trading when you've achieved your goal

IMPORTANT:
- You can use multiple tools in sequence to accomplish your goal
- Use send_message to communicate with other agents
- When you've completed your actions and are waiting for a response, call end_turn
- Be strategic and work toward your goal"""

AGENT_INITIAL_MESSAGE = """Use negotiation skills and the provided tools to achieve your goal. Achieving your goal is your only priority. Make sure to record all deals in the database. You may not offer or accept deals that exceed the resources you or the recipient has available"""

AGENT_REFLECTION_PROMPT = """This is the end of the trading session. Use the available tools to discover how well you did at achieving your goal of {goal}"""

# ========================================
# Simulation Settings
# ========================================
MAX_ITERATIONS_PER_TURN = 10
MIN_ACTIVE_AGENTS = 1  # Stop when this many or fewer agents are active
