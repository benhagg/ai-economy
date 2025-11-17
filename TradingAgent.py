"""
Simple trading agent using LangChain with tools
"""
from langchain_ollama import ChatOllama
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, SystemMessage
from EconomyDB import EconomyDB
from config import OLLAMA_BASE_URL, MODEL_TEMPERATURE, AGENT_SYSTEM_PROMPT, AGENT_REFLECTION_PROMPT, MAX_ITERATIONS_PER_TURN
from AgentCommunication import AgentCommunication


class TradingAgent:
    """A simple trading agent with database tools"""
    
    def __init__(self, name: str, model: str, db: EconomyDB, goal: str):
        self.name = name
        self.model = model
        self.db = db
        self.goal = goal
        self.conversation_log = []  # Track messages received from other agents
        
        # Create tools for this agent
        self.tools = self._create_tools()
        
        # Create LLM with tool binding
        llm = ChatOllama(
            model=self.model,
            base_url=OLLAMA_BASE_URL,
            temperature=MODEL_TEMPERATURE
        )
        
        # Bind tools to LLM
        self.llm_with_tools = llm.bind_tools(self.tools)
        
    def _create_tools(self):
        """Create tools that this agent can use"""
        agent_name = self.name
        db = self.db
        
        @tool
        def view_my_status() -> str:
            """View my current balance and resources"""
            return db.get_agent_info(agent_name)
        
        @tool
        def view_other_agents() -> str:
            """View all agents and their resources"""
            return db.get_all_agents()
        
        @tool
        def view_active_agents() -> str:
            """View all agents still engaged in trading"""
            return ', '.join(AgentCommunication.get_active_agents())
        
        @tool
        def view_market_history() -> str:
            """View completed transactions in the market"""
            return db.get_recent_transactions(5)
        
        @tool
        def send_message(recipient: str, message: str) -> str:
            """
            Send a message to another agent.
            Use this to negotiate trades, make offers, or respond to other agents.
            Do not offer trades that exceed available resources of either party.
            
            Args:
                recipient: Name of the agent to send the message to
                message: Your message content
            """
            # Find recipient (case-insensitive)
            target = AgentCommunication.get_agent(recipient)

            if not target:
                available = ", ".join(AgentCommunication.keys())
                return f"Error: Agent '{recipient}' not found. Available agents: {available}"
            
            # Add message to recipient's conversation log
            target.conversation_log.append({
                'from': agent_name,
                'message': message
            })

            return f"✉️ Message sent to {recipient}: '{message}'"
        
        @tool
        def end_turn() -> str:
            """
            End your turn and pass control.
            Use this when you've completed your actions and are waiting for a response.
            """
            return "🏁 Turn ended"

        @tool
        def finish_trading() -> str:
            """
            Use this when you have achieved your goal to lock in your resources and exit trading.
            """
            AgentCommunication.agent_finished(self.name)
            return f"✅ {self.name} has finished trading."

        @tool
        def record_trade(other_agent: str, i_give_resource: str, i_give_quantity: int, i_receive_resource: str, i_receive_quantity: int) -> str:
            """
            Record a trade between you and another agent. Use this ONLY after both parties agree.
            
            Example: If you (Alice) want to trade 5 wool for 3 ore with Bob:
            - other_agent: "Bob"
            - i_give_resource: "wool"
            - i_give_quantity: 5
            - i_receive_resource: "ore"
            - i_receive_quantity: 3
            
            Args:
                other_agent: Name of the other agent you're trading with
                i_give_resource: Resource YOU are giving away (wool, lumber, grain, brick, or ore)
                i_give_quantity: Amount YOU are giving away
                i_receive_resource: Resource YOU are receiving (wool, lumber, grain, brick, or ore)
                i_receive_quantity: Amount YOU are receiving
            """
            try:
                # Validate: Check if I (the calling agent) have enough of what I'm giving
                my_resource_query = db.execute_query(f"SELECT {i_give_resource} FROM agents WHERE name = '{agent_name}'")
                if "Error" in my_resource_query:
                    return f"Error: Could not find agent {agent_name} in database"
                
                i_have = int(my_resource_query.split('\n')[2].strip())
                
                # Validate: Check if other agent has enough of what I'm receiving
                their_resource_query = db.execute_query(f"SELECT {i_receive_resource} FROM agents WHERE name = '{other_agent}'")
                if "Error" in their_resource_query:
                    return f"Error: Could not find agent {other_agent} in database"
                
                they_have = int(their_resource_query.split('\n')[2].strip())
                
                # Check if both parties have sufficient resources
                if i_have < i_give_quantity:
                    return f"Error: You only have {i_have} {i_give_resource} but trying to give {i_give_quantity}"
                
                if they_have < i_receive_quantity:
                    return f"Error: {other_agent} only has {they_have} {i_receive_resource} but you're trying to receive {i_receive_quantity}"
                
                # Execute trade
                # 1. Update my resources: lose what I give, gain what I receive
                db.execute_query(f"""
                    UPDATE agents 
                    SET {i_give_resource} = {i_give_resource} - {i_give_quantity}, 
                        {i_receive_resource} = {i_receive_resource} + {i_receive_quantity} 
                    WHERE name = '{agent_name}'
                """)
                
                # 2. Update other agent's resources: lose what they give me, gain what I give them
                db.execute_query(f"""
                    UPDATE agents 
                    SET {i_receive_resource} = {i_receive_resource} - {i_receive_quantity}, 
                        {i_give_resource} = {i_give_resource} + {i_give_quantity} 
                    WHERE name = '{other_agent}'
                """)
                
                # 3. Record transaction in database (matches EconomyDB schema)
                db.execute_query(f"""
                    INSERT INTO transactions (buyer, seller, buyer_resource, seller_resource, buyer_quantity, seller_quantity)
                    VALUES ('{agent_name}', '{other_agent}', '{i_receive_resource}', '{i_give_resource}', {i_receive_quantity}, {i_give_quantity})
                """)
                
                return f"✅ Trade completed! You gave {i_give_quantity} {i_give_resource} to {other_agent} and received {i_receive_quantity} {i_receive_resource}"
                
            except Exception as e:
                return f"Error executing trade: {e}"
        
        return [view_my_status, view_other_agents, view_market_history, record_trade, send_message, end_turn, finish_trading, view_active_agents]
    
    def act(self, message: str = None, max_iterations: int = None) -> str:
        """Have the agent respond to a message using tools, with support for multiple tool calls"""
        
        if max_iterations is None:
            max_iterations = MAX_ITERATIONS_PER_TURN
        
        # Check for new messages from other agents
        if self.conversation_log:
            print(f"\n📬 {self.name} has {len(self.conversation_log)} new message(s):")
            for msg in self.conversation_log:
                print(f"  From {msg['from']}: {msg['message']}")
            print()
        
        # Build initial message
        initial_content = message + "\n"
        if self.conversation_log:
            initial_content += "Messages from other agents:\n"
            for msg in self.conversation_log:
                initial_content += f"- {msg['from']}: {msg['message']}\n"
            initial_content += "\n"
        
        # Clear conversation log after reading
        self.conversation_log = []
        
        messages = [
            SystemMessage(content=AGENT_SYSTEM_PROMPT.format(name=self.name, goal=self.goal)),
            HumanMessage(content=initial_content)
        ]
        
        print(f"\n{self.name} is thinking...")
        
        iteration = 0
        turn_ended = False
        all_responses = []
        
        # Iterative tool calling loop
        while iteration < max_iterations and not turn_ended:
            iteration += 1
            
            # Call LLM with tools
            response = self.llm_with_tools.invoke(messages)
            for chunk in response.stream():
                print(chunk.content, end="", flush=True)
            
            if response.content:
                print(f"{self.name} says: {response.content}")
                all_responses.append(response.content)
            
            # Check if tools were called
            if response.tool_calls:
                print(f"{self.name} is using tools...")
                
                from langchain_core.messages import ToolMessage
                
                for tool_call in response.tool_calls:
                    tool_name = tool_call['name']
                    tool_args = tool_call['args']
                    
                    print(f"  Tool: {tool_name}({tool_args})")
                    
                    # Find matching tool
                    matching_tool = next((t for t in self.tools if t.name == tool_name), None)
                    if matching_tool:
                        try:
                            result = matching_tool.invoke(tool_args)
                            print(f"  Result: {result[:200]}..." if len(str(result)) > 200 else f"  Result: {result}")
                            
                            # Check if turn was ended
                            if tool_name == "end_turn":
                                turn_ended = True
                            
                            # Add tool result to messages for next iteration
                            messages.append(response)
                            messages.append(ToolMessage(
                                content=str(result),
                                tool_call_id=tool_call['id']
                            ))
                            
                        except Exception as e:
                            print(f"  Error: {e}")
                            messages.append(response)
                            messages.append(ToolMessage(
                                content=f"Error: {e}",
                                tool_call_id=tool_call['id']
                            ))
                
                # If turn ended, break the loop
                if :
                    break
                    
            else:
                # No more tool calls, agent is done
                break
        
        if iteration >= max_iterations:
            print(f"⚠️ {self.name} reached max iterations ({max_iterations})")
        
        return "\n".join(all_responses) if all_responses else "(No response)"
    
    def reflect(self, message: str = None) -> str:
        """Have the agent reflect on their performance after trading ends"""
        if message is None:
            message = "Review your final status"
        
        messages = [
            SystemMessage(content=AGENT_REFLECTION_PROMPT.format(goal=self.goal)),
            HumanMessage(content=message)
        ]
        response = self.llm_with_tools.invoke(messages)
        return response.content

    def __str__(self):
        return f"TradingAgent({self.name}, Goal: {self.goal})"
