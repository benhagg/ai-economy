"""
Configuration file for the agentic economy simulation
"""

# Ollama model to use (choose from: qwen2.5:latest, qwen:0.5b, gemma3:270M, llama3:latest, mistral:latest, gemma3:1b, deepseek-r1:8b)
MODEL_NAME = "qwen2.5:latest"

# Database configuration
DATABASE_PATH = "economy.db"

# Agent configuration
INITIAL_BALANCE = 100.0  # Starting money for each agent
SIMULATION_ROUNDS = 10   # Number of negotiation rounds to run

# Ollama configuration
OLLAMA_BASE_URL = "http://localhost:11434"
