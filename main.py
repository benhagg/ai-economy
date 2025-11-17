"""
Main simulation runner for the agentic economy
"""
import random
import time
from market_coordinator import MarketCoordinator
from economic_agent import EconomicAgent
from transaction_protocol import TransactionProtocol
from config import INITIAL_BALANCE, SIMULATION_ROUNDS, MODEL_NAME
import itertools


def initialize_economy():
    """Set up the economy with agents and initial resources"""
    print("🌍 Initializing Agentic Economy...")
    print(f"Using model: {MODEL_NAME}\n")
    
    # Create market coordinator
    coordinator = MarketCoordinator()
    
    # Define agents with different goals
    agent_configs = [
        {
            "name": "Alice",
            "goal": "Accumulate $200 in cash",
            "resources": {"wood": 20, "stone": 5}
        },
        {
            "name": "Bob",
            "goal": "Collect 20 units of wood",
            "resources": {"iron": 8, "gold": 2}
        }
    ]
    
    # Create and register agents
    agents = []
    for config in agent_configs:
        agent_id = f"agent_{config['name'].lower()}"
        
        # Register agent with coordinator
        coordinator.register_agent(
            agent_id=agent_id,
            name=config['name'],
            initial_balance=INITIAL_BALANCE,
            goal=config['goal']
        )
        
        # Add initial resources
        for resource, quantity in config['resources'].items():
            coordinator.add_resource(agent_id, resource, quantity)
        
        # Create agent instance
        agent = EconomicAgent(
            name=config['name'],
            agent_id=agent_id,
            goal=config['goal'],
            coordinator=coordinator
        )
        agents.append(agent)
        
        print(f"✅ Created {agent.name} - Goal: {agent.goal}")
    
    print(f"\n{'='*60}")
    print(coordinator.get_market_summary())
    print(f"{'='*60}\n")
    
    return coordinator, agents


def run_simulation_round(round_num: int, agents: list, protocol: TransactionProtocol):
    """Run one round of the simulation"""
    print(f"\n{'='*60}")
    print(f"🔄 ROUND {round_num}")
    print(f"{'='*60}\n")
    
    # Shuffle agent pairs to create random interactions
    agent_pairs = list(itertools.combinations(agents, 2))
    random.shuffle(agent_pairs)
    
    # Limit to a few negotiations per round to avoid overwhelming output
    max_negotiations = min(3, len(agent_pairs))
    
    for i in range(max_negotiations):
        agent1, agent2 = agent_pairs[i]
        
        # Random chance to skip this pairing
        if random.random() < 0.3:
            continue
            
        # Try to facilitate a trade
        protocol.facilitate_negotiation(agent1, agent2)
        
        # Small delay to avoid overwhelming the LLM
        time.sleep(10.5)
    
    # At the end of round, have agents reflect on their progress
    print(f"\n💭 Agent Reflections:")
    for agent in agents:
        reflection = agent.reflect_on_progress()
        print(f"   {agent.name}: {reflection[:150]}...")


def display_final_results(coordinator: MarketCoordinator, agents: list):
    """Display final state of the economy"""
    print(f"\n\n{'='*60}")
    print("🏆 FINAL RESULTS")
    print(f"{'='*60}\n")
    
    print(coordinator.get_market_summary())
    
    print("\n📊 Goal Achievement Analysis:")
    for agent in agents:
        info = coordinator.get_agent_info(agent.agent_id)
        print(f"\n{agent.name}:")
        print(f"  Goal: {agent.goal}")
        print(f"  Final Balance: ${info['balance']:.2f}")
        print(f"  Final Resources: {info['resources']}")
        
        # Simple goal check (you could make this more sophisticated)
        if "200" in agent.goal and info['balance'] >= 200:
            print(f"  Status: ✅ GOAL ACHIEVED!")
        elif "150" in agent.goal and info['balance'] >= 150:
            print(f"  Status: ✅ GOAL ACHIEVED!")
        elif "20 units of wood" in agent.goal and info['resources'].get('wood', 0) >= 20:
            print(f"  Status: ✅ GOAL ACHIEVED!")
        elif "5 units of gold" in agent.goal and info['resources'].get('gold', 0) >= 5:
            print(f"  Status: ✅ GOAL ACHIEVED!")
        else:
            print(f"  Status: 🔄 In Progress")
    
    # Transaction statistics
    transactions = coordinator.get_transaction_history(100)
    total_volume = sum(tx['price'] for tx in transactions)
    
    print(f"\n📈 Market Statistics:")
    print(f"  Total Transactions: {len(transactions)}")
    print(f"  Total Trading Volume: ${total_volume:.2f}")
    print(f"  Average Transaction: ${total_volume/len(transactions):.2f}" if transactions else "  No transactions")


def main():
    """Main entry point for the simulation"""
    print("=" * 60)
    print("🏦 AGENTIC ECONOMY SIMULATION")
    print("=" * 60)
    
    # Initialize the economy
    coordinator, agents = initialize_economy()
    
    # Create transaction protocol
    protocol = TransactionProtocol(coordinator)
    
    # Run simulation rounds
    for round_num in range(1, SIMULATION_ROUNDS + 1):
        run_simulation_round(round_num, agents, protocol)
        
        # Small delay between rounds
        time.sleep(1)
    
    # Display final results
    display_final_results(coordinator, agents)
    
    print(f"\n{'='*60}")
    print("✅ Simulation Complete!")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
