"""
Economic Agent - An autonomous agent that can trade resources to achieve goals
"""
import uuid
from typing import List, Dict, Optional
from langchain_ollama import ChatOllama
from langchain.schema import HumanMessage, SystemMessage
from market_coordinator import MarketCoordinator
from config import MODEL_NAME, OLLAMA_BASE_URL
import json


class EconomicAgent:
    def __init__(self, name: str, agent_id: str, goal: str, 
                 coordinator: MarketCoordinator, model_name: str = MODEL_NAME):
        self.name = name
        self.agent_id = agent_id
        self.goal = goal
        self.coordinator = coordinator
        self.model_name = model_name
        
        # Initialize LangChain LLM
        self.llm = ChatOllama(
            model=model_name,
            base_url=OLLAMA_BASE_URL,
            temperature=0.7
        )
        
        # Message history for context
        self.message_history = []
        
    def get_system_prompt(self) -> str:
        """Generate the system prompt for this agent"""
        return f"""You are {self.name}, an autonomous economic agent in a marketplace.

YOUR GOAL: {self.goal}

You can:
1. View your current balance and resources
2. View other agents' resources and balances
3. Negotiate trades with other agents
4. Propose or accept trades (buying or selling resources)

When negotiating:
- Be strategic about pricing
- Consider your goal when making decisions
- You can be creative in proposing trades
- Respond in JSON format when proposing trades

Your responses should be concise and goal-oriented."""

    def perceive_market(self) -> str:
        """Get current market state from the database"""
        my_info = self.coordinator.get_agent_info(self.agent_id)
        all_agents = self.coordinator.get_all_agents()
        recent_transactions = self.coordinator.get_transaction_history(5)
        
        perception = f"=== MY STATUS ===\n"
        perception += f"Balance: ${my_info['balance']:.2f}\n"
        perception += f"Resources: {json.dumps(my_info['resources'])}\n"
        perception += f"Goal: {self.goal}\n\n"
        
        perception += "=== OTHER AGENTS ===\n"
        for agent in all_agents:
            if agent['agent_id'] != self.agent_id:
                perception += f"{agent['name']}: ${agent['balance']:.2f}, Resources: {json.dumps(agent['resources'])}\n"
        
        perception += f"\n=== RECENT MARKET ACTIVITY ===\n"
        for tx in recent_transactions:
            perception += f"{tx['buyer_id'][:8]}... bought {tx['quantity']} {tx['resource_name']} for ${tx['price']:.2f}\n"
        
        return perception
        
    def think(self, context: str) -> str:
        """Use LLM to reason about the current situation"""
        messages = [
            SystemMessage(content=self.get_system_prompt()),
            HumanMessage(content=context)
        ]
        
        response = self.llm.invoke(messages)
        return response.content
        
    def decide_action(self) -> Dict:
        """
        Decide what action to take based on market conditions.
        Returns a dictionary describing the intended action.
        """
        market_state = self.perceive_market()
        
        prompt = f"""{market_state}

Based on your goal ({self.goal}) and the current market state, what should you do?

Analyze the situation and decide if you want to:
1. Make a trade proposal to another agent
2. Wait and observe
3. Adjust your strategy

If you want to propose a trade, respond with JSON in this format:
{{
    "action": "propose_trade",
    "target_agent": "agent_name",
    "offer_type": "buy" or "sell",
    "resource": "resource_name",
    "quantity": number,
    "price": number,
    "reasoning": "why you're making this offer"
}}

If you want to wait, respond with JSON:
{{
    "action": "wait",
    "reasoning": "why you're waiting"
}}

Respond ONLY with valid JSON."""

        response = self.think(prompt)
        
        # Try to parse JSON from response
        try:
            # Extract JSON if it's embedded in text
            start = response.find('{')
            end = response.rfind('}') + 1
            if start != -1 and end > start:
                json_str = response[start:end]
                action = json.loads(json_str)
                return action
            else:
                return {"action": "wait", "reasoning": "Could not parse decision"}
        except json.JSONDecodeError:
            return {"action": "wait", "reasoning": "Error in decision making"}
            
    def receive_trade_proposal(self, from_agent: str, proposal: Dict) -> Dict:
        """
        Receive and evaluate a trade proposal from another agent.
        Returns acceptance/rejection decision.
        """
        market_state = self.perceive_market()
        my_info = self.coordinator.get_agent_info(self.agent_id)
        
        prompt = f"""{market_state}

Agent {from_agent} has made you a trade proposal:
{json.dumps(proposal, indent=2)}

Your current status:
- Balance: ${my_info['balance']:.2f}
- Resources: {json.dumps(my_info['resources'])}
- Goal: {self.goal}

Should you accept this proposal? Consider:
1. Does it help you achieve your goal?
2. Is the price fair?
3. Can you afford it (if buying)?
4. Do you have the resources (if selling)?

Respond with JSON:
{{
    "accept": true or false,
    "reasoning": "why you accepted or rejected",
    "counter_offer": {{optional counter-offer if you rejected}}
}}

Respond ONLY with valid JSON."""

        response = self.think(prompt)
        
        try:
            start = response.find('{')
            end = response.rfind('}') + 1
            if start != -1 and end > start:
                json_str = response[start:end]
                decision = json.loads(json_str)
                return decision
            else:
                return {"accept": False, "reasoning": "Could not parse decision"}
        except json.JSONDecodeError:
            return {"accept": False, "reasoning": "Error in decision making"}
            
    def communicate(self, message: str, from_agent: Optional[str] = None) -> str:
        """General communication with another agent"""
        context = f"Message from {from_agent}: {message}" if from_agent else message
        
        prompt = f"""{self.perceive_market()}

{context}

Respond to this message. Keep your response brief and focused on your goal: {self.goal}"""

        return self.think(prompt)
        
    def reflect_on_progress(self) -> str:
        """Reflect on progress toward goal"""
        my_info = self.coordinator.get_agent_info(self.agent_id)
        
        prompt = f"""Your goal is: {self.goal}

Your current status:
- Balance: ${my_info['balance']:.2f}
- Resources: {json.dumps(my_info['resources'])}

How close are you to achieving your goal? What should your strategy be going forward?
Keep your response brief (2-3 sentences)."""

        return self.think(prompt)
        
    def __str__(self):
        return f"EconomicAgent({self.name}, Goal: {self.goal})"
