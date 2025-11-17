"""
Transaction Protocol - Handles negotiation and execution of trades between agents
"""
import uuid
from typing import Dict, Optional, Tuple
from economic_agent import EconomicAgent
from market_coordinator import MarketCoordinator


class TransactionProtocol:
    """Manages the negotiation and execution of transactions between agents"""
    
    def __init__(self, coordinator: MarketCoordinator):
        self.coordinator = coordinator
        
    def initiate_trade(self, buyer: EconomicAgent, seller: EconomicAgent, 
                      resource_name: str, quantity: float, price: float) -> Tuple[bool, str]:
        """
        Initiate a trade between two agents.
        Returns (success, message)
        """
        # Create proposal
        proposal = {
            "buyer": buyer.name,
            "seller": seller.name,
            "resource": resource_name,
            "quantity": quantity,
            "price": price,
            "type": "buy_offer"
        }
        
        print(f"\n💼 {buyer.name} proposes to buy {quantity} {resource_name} from {seller.name} for ${price:.2f}")
        
        # Seller evaluates the proposal
        seller_decision = seller.receive_trade_proposal(buyer.name, proposal)
        
        print(f"   {seller.name}'s response: {'✅ ACCEPT' if seller_decision.get('accept') else '❌ REJECT'}")
        print(f"   Reasoning: {seller_decision.get('reasoning', 'No reasoning provided')}")
        
        if not seller_decision.get('accept', False):
            return False, f"Seller rejected: {seller_decision.get('reasoning', 'No reason given')}"
        
        # Both agents agree - create transaction
        transaction_id = str(uuid.uuid4())
        
        # Create pending transaction
        success = self.coordinator.create_pending_transaction(
            transaction_id=transaction_id,
            buyer_id=buyer.agent_id,
            seller_id=seller.agent_id,
            resource_name=resource_name,
            quantity=quantity,
            price=price
        )
        
        if not success:
            return False, "Failed to create pending transaction"
        
        # Both agents confirm (since they both agreed)
        buyer_confirm = self.coordinator.confirm_transaction(transaction_id, buyer.agent_id)
        seller_confirm = self.coordinator.confirm_transaction(transaction_id, seller.agent_id)
        
        if seller_confirm == 'completed':
            print(f"   ✅ Transaction completed successfully!")
            return True, f"Transaction completed: {transaction_id}"
        elif seller_confirm == 'failed':
            print(f"   ❌ Transaction failed: insufficient resources or funds")
            return False, "Transaction failed: insufficient resources or funds"
        else:
            print(f"   ⏳ Transaction pending confirmation")
            return False, "Transaction pending"
            
    def propose_sell(self, seller: EconomicAgent, buyer: EconomicAgent,
                    resource_name: str, quantity: float, price: float) -> Tuple[bool, str]:
        """
        Agent proposes to sell a resource to another agent.
        Returns (success, message)
        """
        # Create proposal
        proposal = {
            "seller": seller.name,
            "buyer": buyer.name,
            "resource": resource_name,
            "quantity": quantity,
            "price": price,
            "type": "sell_offer"
        }
        
        print(f"\n💼 {seller.name} proposes to sell {quantity} {resource_name} to {buyer.name} for ${price:.2f}")
        
        # Buyer evaluates the proposal
        buyer_decision = buyer.receive_trade_proposal(seller.name, proposal)
        
        print(f"   {buyer.name}'s response: {'✅ ACCEPT' if buyer_decision.get('accept') else '❌ REJECT'}")
        print(f"   Reasoning: {buyer_decision.get('reasoning', 'No reasoning provided')}")
        
        if not buyer_decision.get('accept', False):
            return False, f"Buyer rejected: {buyer_decision.get('reasoning', 'No reason given')}"
        
        # Both agents agree - execute via initiate_trade
        return self.initiate_trade(buyer, seller, resource_name, quantity, price)
        
    def facilitate_negotiation(self, agent1: EconomicAgent, agent2: EconomicAgent) -> Tuple[bool, str]:
        """
        Facilitate a negotiation between two agents.
        Each agent decides what to propose, and we try to find a match.
        """
        print(f"\n🤝 Facilitating negotiation between {agent1.name} and {agent2.name}")
        
        # Get agent1's desired action
        action1 = agent1.decide_action()
        
        # Check if agent1 wants to trade with agent2
        if action1.get('action') != 'propose_trade':
            return False, f"{agent1.name} doesn't want to trade right now"
        
        if action1.get('target_agent') != agent2.name:
            return False, f"{agent1.name} wants to trade with someone else"
        
        # Execute the proposed trade
        if action1.get('offer_type') == 'buy':
            return self.initiate_trade(
                buyer=agent1,
                seller=agent2,
                resource_name=action1.get('resource'),
                quantity=action1.get('quantity'),
                price=action1.get('price')
            )
        elif action1.get('offer_type') == 'sell':
            return self.propose_sell(
                seller=agent1,
                buyer=agent2,
                resource_name=action1.get('resource'),
                quantity=action1.get('quantity'),
                price=action1.get('price')
            )
        else:
            return False, "Invalid trade type"
