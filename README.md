# AI Economy Trading Simulation

A multi-agent trading system where AI agents negotiate and trade resources to achieve their individual goals.

## 🎯 Overview

This project simulates an economy where autonomous AI agents:
- **Negotiate** trades with other agents via messages
- **Execute** barter trades (resource-for-resource exchanges)
- **Strategize** to achieve their unique goals
- **Track** all transactions in a database

## 📁 Project Structure

```
ai-economy/
├── config.py              # ⚙️ Centralized configuration (agents, prompts, settings)
├── main.py               # 🚀 Main entry point - runs the simulation
├── TradingAgent.py       # 🤖 Agent class with LLM and tools
├── EconomyDB.py          # 💾 SQLite database manager
├── AgentCommunication.py # 📡 Inter-agent messaging registry
├── test.py               # ✅ Comprehensive test suite
└── requirements.txt      # 📦 Python dependencies
```

## ⚙️ Configuration (config.py)

All simulation settings are centralized in `config.py`:

### LLM Settings
```python
OLLAMA_BASE_URL = "http://localhost:11434"
DEFAULT_MODEL = "qwen2.5:latest"
MODEL_TEMPERATURE = 0.7
```

### Agent Definitions
```python
AGENTS = [
    {
        "name": "Alice",
        "goal": "Collect 10 or more ore",
        "model": "qwen2.5:latest",
        "initial_resources": {
            "wool": 0, "lumber": 5, "grain": 0, 
            "brick": 0, "ore": 100
        }
    },
    # ... more agents
]
```

### System Prompts
- `AGENT_SYSTEM_PROMPT` - Defines agent behavior and available tools
- `AGENT_INITIAL_MESSAGE` - Instructions given to agents each turn
- `AGENT_REFLECTION_PROMPT` - Post-simulation reflection prompt

### Simulation Settings
- `MAX_ITERATIONS_PER_TURN` - Tool call limit per agent turn (default: 10)
- `MIN_ACTIVE_AGENTS` - Minimum active agents before ending (default: 1)

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Start Ollama
Ensure Ollama is running locally:
```bash
ollama serve
```

### 3. Run the Simulation
```bash
python main.py
```

### 4. Run Tests
```bash
python test.py
```

## 🤖 How Agents Work

### Available Tools

Each agent has access to these tools:

1. **view_my_status()** - Check own resources
2. **view_other_agents()** - See all agents and their resources
3. **view_active_agents()** - List agents still trading
4. **view_market_history()** - Review recent transactions
5. **send_message(recipient, message)** - Negotiate with other agents
6. **record_trade(...)** - Execute agreed trades (updates database)
7. **end_turn()** - Pass control to next agent
8. **finish_trading()** - Withdraw from trading

### Trade Execution

Agents use the simplified `record_trade` tool:

```python
record_trade(
    other_agent="Bob",           # Who you're trading with
    i_give_resource="wool",      # What you're giving
    i_give_quantity=5,
    i_receive_resource="ore",    # What you're receiving
    i_receive_quantity=3
)
```

### Multi-Turn Tool Calling

Agents can:
- Call multiple tools in sequence
- See tool results and adapt strategy
- Continue until they call `end_turn()` or reach max iterations

## 💾 Database Schema

### Agents Table
```sql
CREATE TABLE agents (
    name TEXT PRIMARY KEY,
    wool INTEGER DEFAULT 0,
    lumber INTEGER DEFAULT 0,
    grain INTEGER DEFAULT 0,
    brick INTEGER DEFAULT 0,
    ore INTEGER DEFAULT 0
)
```

### Transactions Table
```sql
CREATE TABLE transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    buyer TEXT NOT NULL,
    seller TEXT NOT NULL,
    buyer_resource TEXT NOT NULL,
    seller_resource TEXT NOT NULL,
    buyer_quantity INTEGER NOT NULL,
    seller_quantity INTEGER NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
```

## 🧪 Testing

The test suite (`test.py`) covers:

- ✅ **Database operations** (8 tests)
- ✅ **Agent communication** (8 tests)
- ✅ **Trading tools** (10 tests)
- ✅ **Conversation management** (2 tests)

Run tests with:
```bash
python test.py
```

## 🔧 Debugging

VS Code launch configurations are provided in `.vscode/launch.json`:

1. **Python: Debug Main** - Debug the main simulation
2. **Python: Debug Current File** - Debug any Python file
3. **Python: Debug Agent with Breakpoints** - Step through agent execution

Set breakpoints in `TradingAgent.py` to inspect:
- Tool invocations
- LLM responses
- Message passing

## 📝 Customization

### Adding a New Agent

Edit `config.py`:
```python
AGENTS.append({
    "name": "Charlie",
    "goal": "Your custom goal here",
    "model": "qwen2.5:latest",
    "initial_resources": {
        "wool": 10, "lumber": 20, "grain": 5,
        "brick": 3, "ore": 1
    }
})
```

### Changing Prompts

Modify prompts in `config.py`:
- `AGENT_SYSTEM_PROMPT` - Agent personality and instructions
- `AGENT_INITIAL_MESSAGE` - Turn-by-turn instructions
- `AGENT_REFLECTION_PROMPT` - Post-game analysis

### Using Different Models

Update the model in agent config or change `DEFAULT_MODEL`:
```python
"model": "llama3.2:latest"  # or any Ollama model
```

## 🏗️ Architecture

### Key Design Patterns

1. **Centralized Configuration** - All settings in `config.py`
2. **Tool-Based Agency** - LangChain tools for agent capabilities
3. **Registry Pattern** - `AgentCommunication` for global agent lookup
4. **Iterative Execution** - Agents loop until `end_turn()` or max iterations

### Message Flow

```
Agent A → send_message(B, "offer") → AgentCommunication → Agent B's conversation_log
                                                                ↓
Agent B → act() → reads conversation_log → send_message(A, "accept")
                                                                ↓
Agent A → reads message → record_trade() → Database updated
```

## 📊 Output Example

```
🏦 SIMPLE AGENTIC ECONOMY
============================================================

📝 Setting up agents...
  ✓ Alice - Goal: Collect 10 or more ore
  ✓ Bob - Goal: Collect 15 units of wool
  ✓ Randy - Goal: [fraudster goal]

✅ 3 agents created!

💬 TRADE NEGOTIATION
============================================================

🔵 ALICE'S TURN
------------------------------------------------------------
Alice is thinking...
Alice says: I'll check my status and see who has ore...
Alice is using tools...
  Tool: view_my_status({})
  Result: name | wool | lumber | grain | brick | ore
          Alice | 0 | 5 | 0 | 0 | 100
...
```

## 🤝 Contributing

Feel free to:
- Add new agent types
- Enhance trading logic
- Improve negotiation strategies
- Add more comprehensive tests

## 📄 License

MIT License - See project for details
