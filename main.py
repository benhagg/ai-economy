"""
Simple main runner - Multi-agent trading simulation
"""
from EconomyDB import EconomyDB
from TradingAgent import TradingAgent
from AgentCommunication import AgentCommunication
from config import AGENTS, AGENT_INITIAL_MESSAGE, MIN_ACTIVE_AGENTS


def main():
    print("=" * 60)
    print("🏦 SIMPLE AGENTIC ECONOMY")
    print("=" * 60)
    print()
    
    # Initialize database
    db = EconomyDB()
    
    # Create agents from config
    print("📝 Setting up agents...")
    agents = []
    
    for agent_config in AGENTS:
        # Initialize agent in database with resources
        db.init_agent(
            name=agent_config["name"],
            **agent_config["initial_resources"]
        )
        
        # Create agent instance
        agent = TradingAgent(
            name=agent_config["name"],
            model=agent_config["model"],
            db=db,
            goal=agent_config["goal"]
        )
        
        # Register agent for communication
        AgentCommunication.register_agent(agent_config["name"], agent)
        agents.append(agent)
        print(f"  ✓ {agent_config['name']} - Goal: {agent_config['goal']}")
    
    print(f"\n✅ {len(agents)} agents created!")
    print("\n" + db.get_all_agents() + "\n")
    
    # Conversation rounds
    print("=" * 60)
    print("💬 TRADE NEGOTIATION")
    print("=" * 60 + "\n")
    
    # Trading loop - continues until enough agents finish
    while len(AgentCommunication.get_active_agents()) > MIN_ACTIVE_AGENTS:
        for agent, done in AgentCommunication._agents.values():
            print(f"🔵 {agent.name}'S TURN")
            print("-" * 60)
            if done:
                print(f"⏭️ {agent.name} has finished trading and will skip their turn.\n")
                continue
            
            agent_response = agent.act(AGENT_INITIAL_MESSAGE)
            print("agent_response:", agent_response + "\n")
    
    print("\n" + "=" * 60)
    print("🏁 TRADING SESSION ENDED")
    print("=" * 60 + "\n")
    
    # Agent reflection phase
    print("=" * 60)
    print("💭 AGENT REFLECTIONS")
    print("=" * 60 + "\n")
    
    for agent in agents:
        print(f"🔍 {agent.name}'s Reflection:")
        print("-" * 60)
        reflection = agent.reflect()
        print(f"{agent.name}: {reflection}")
        print()
    
    # Show final state
    print("=" * 60)
    print("📊 FINAL STATE")
    print("=" * 60 + "\n")
    print("Agents:")
    print(db.get_all_agents() + "\n")
    print("Transactions:")
    print(db.get_recent_transactions() + "\n")


if __name__ == "__main__":
    main()
