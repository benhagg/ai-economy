# 🏦 Agentic Economy Simulation

An autonomous multi-agent economic system built with LangChain and local LLMs (Ollama). Agents independently trade resources to achieve their goals using AI-powered decision making.

## 🌟 Features

- **Autonomous Agents**: Multiple AI agents with different goals that make independent trading decisions
- **Market Coordinator**: Central database system that records all transactions and manages the economy
- **Double-Confirmation Protocol**: Transactions only execute when both parties agree
- **LangChain Integration**: Uses LangChain for agent reasoning and decision making
- **Local LLMs**: Runs entirely on local Ollama models - no API keys needed
- **Real-time Negotiation**: Agents negotiate trades dynamically based on market conditions

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────┐
│                 Market Coordinator                  │
│  ┌─────────────────────────────────────────────┐   │
│  │         SQLite Database                     │   │
│  │  - Agent balances & resources               │   │
│  │  - Transaction history                      │   │
│  │  - Pending transactions                     │   │
│  └─────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────┘
           ↑                                  ↑
           │ Read/Write                       │ Read/Write
           │                                  │
┌──────────┴────────┐              ┌─────────┴─────────┐
│   Economic Agent  │◄────Talk────►│  Economic Agent   │
│   (LangChain LLM) │              │  (LangChain LLM)  │
│   Goal: Get $200  │              │  Goal: Get 5 gold │
└───────────────────┘              └───────────────────┘
```

## 📋 Prerequisites

1. **Python 3.8+**
2. **Ollama** installed and running
   - Download from: https://ollama.ai
   - Must have at least one model pulled (see your available models below)

## 🚀 Installation

1. **Clone or download this project**
   ```powershell
   cd C:\Users\benha\Documents\projects\ai-economy
   ```

2. **Create a virtual environment** (recommended)
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

3. **Install dependencies**
   ```powershell
   pip install -r requirements.txt
   ```

4. **Verify Ollama is running**
   ```powershell
   ollama list
   ```

## ⚙️ Configuration

Edit `config.py` to customize the simulation:

```python
# Choose your model from available Ollama models:
# qwen2.5:latest, qwen:0.5b, gemma3:270M, llama3:latest, 
# mistral:latest, gemma3:1b, deepseek-r1:8b
MODEL_NAME = "qwen2.5:latest"

# Adjust simulation parameters
INITIAL_BALANCE = 100.0      # Starting money for each agent
SIMULATION_ROUNDS = 10       # Number of trading rounds
```

### Recommended Models for Different Use Cases:

- **Best Quality**: `qwen2.5:latest`, `llama3:latest`, `mistral:latest`
- **Fastest**: `gemma3:270M`, `qwen:0.5b`
- **Balanced**: `gemma3:1b`, `deepseek-r1:8b`

## 🎮 Usage

Run the simulation:

```powershell
python main.py
```

The simulation will:
1. Initialize 5 agents with different goals and resources
2. Run multiple rounds of trading negotiations
3. Display transaction results and agent reasoning
4. Show final results and goal achievement

### Example Output:

```
🏦 AGENTIC ECONOMY SIMULATION
🌍 Initializing Agentic Economy...
Using model: qwen2.5:latest

✅ Created Alice - Goal: Accumulate $200 in cash
✅ Created Bob - Goal: Collect 20 units of wood
...

🔄 ROUND 1
💼 Alice proposes to buy 5 wood from Charlie for $25.00
   Charlie's response: ✅ ACCEPT
   Reasoning: Good price for wood, helps my goal
   ✅ Transaction completed successfully!
...
```

## 📁 Project Structure

```
ai-economy/
├── main.py                    # Main simulation runner
├── economic_agent.py          # Agent class with LangChain integration
├── market_coordinator.py      # Database manager and transaction validator
├── transaction_protocol.py    # Trade negotiation logic
├── config.py                  # Configuration settings
├── requirements.txt           # Python dependencies
├── .gitignore                # Git ignore rules
└── README.md                 # This file
```

## 🔧 How It Works

### 1. Agents
Each agent:
- Has a specific goal (e.g., "Accumulate $200")
- Uses a local LLM to make decisions
- Can view market state (other agents' resources and prices)
- Negotiates trades to achieve their goal

### 2. Market Coordinator
- Maintains SQLite database with all economic data
- Validates transactions (checks balances and resources)
- Only executes transactions when both parties confirm
- Provides market summary and history

### 3. Transaction Flow
1. Agent A decides to trade with Agent B
2. Agent A proposes a trade (buy/sell resource X for price Y)
3. Agent B evaluates the proposal using LLM reasoning
4. If both agree, transaction is created as "pending"
5. Both agents confirm → Coordinator validates and executes
6. Database is updated with new balances and resources

## 🎯 Agent Goals (Customizable)

Current agents have these goals:
- **Alice**: Accumulate $200 in cash
- **Bob**: Collect 20 units of wood
- **Charlie**: Get 5 units of gold
- **Diana**: Accumulate $150 while keeping at least 5 iron
- **Eve**: Collect diverse resources: 5 wood, 5 stone, 5 iron

You can modify agent goals in `main.py` under the `initialize_economy()` function.

## 🔬 Experimentation Ideas

1. **Different Models**: Try different Ollama models to see how agent behavior changes
2. **More Agents**: Add more agents with competing goals
3. **Resource Scarcity**: Start agents with fewer resources to create competition
4. **Different Goals**: Create complex multi-objective goals
5. **Market Events**: Add random events (price changes, resource discoveries)
6. **Agent Personalities**: Give agents different "personalities" via system prompts

## 📊 Database Schema

The SQLite database (`economy.db`) contains:

- **agents**: Agent ID, name, balance, goal
- **resources**: Agent resources and quantities
- **pending_transactions**: Awaiting confirmation
- **transactions**: Completed transaction history

You can inspect the database using:
```powershell
sqlite3 economy.db
.tables
SELECT * FROM transactions;
```

## 🐛 Troubleshooting

**"Connection refused" error**
- Make sure Ollama is running: `ollama serve`

**Agents not making trades**
- Try a more capable model like `qwen2.5:latest` or `llama3:latest`
- Increase `SIMULATION_ROUNDS` in config.py
- Check that agents have compatible resources

**Slow performance**
- Use a smaller model like `gemma3:270M` or `qwen:0.5b`
- Reduce number of agents or simulation rounds
- Ensure Ollama has adequate system resources

**JSON parsing errors**
- Some models struggle with JSON formatting
- Try a more capable model
- The code has fallback handling for this

## 📝 License

This project is open source and available for educational purposes.

## 🤝 Contributing

Feel free to:
- Add new agent strategies
- Improve negotiation protocols
- Add new resource types
- Create visualization tools
- Enhance the database schema

## 🙏 Acknowledgments

Built with:
- [LangChain](https://github.com/langchain-ai/langchain) - Agent framework
- [Ollama](https://ollama.ai) - Local LLM runtime
- SQLite - Embedded database

---

**Happy Trading! 🎉**
