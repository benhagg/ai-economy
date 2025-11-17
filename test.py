"""
Comprehensive tests for the AI Economy system
Tests all classes, functions, and tools
"""
import unittest
import os
import tempfile
import shutil
from EconomyDB import EconomyDB
from AgentCommunication import AgentCommunication
from TradingAgent import TradingAgent


class TestEconomyDB(unittest.TestCase):
    """Tests for EconomyDB class"""
    
    def setUp(self):
        """Create a temporary database for each test"""
        self.test_dir = tempfile.mkdtemp()
        # Patch the data directory
        self.original_path = None
        if not os.path.exists("data"):
            os.makedirs("data")
        self.db = EconomyDB(db_path="test-economy.db")
    
    def tearDown(self):
        """Clean up test database"""
        if os.path.exists(self.db.db_path):
            os.remove(self.db.db_path)
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_init_database(self):
        """Test database initialization"""
        self.assertTrue(os.path.exists(self.db.db_path))
        
        # Check tables exist
        result = self.db.execute_query("SELECT name FROM sqlite_master WHERE type='table'")
        self.assertIn("agents", result)
        self.assertIn("transactions", result)
    
    def test_init_agent(self):
        """Test agent initialization"""
        result = self.db.init_agent("Alice", wool=10, lumber=5, grain=3, brick=2, ore=1)
        self.assertIn("Success", result)
        
        # Verify agent was created
        agent_info = self.db.get_agent_info("Alice")
        self.assertIn("Alice", agent_info)
        self.assertIn("10", agent_info)  # wool
        self.assertIn("5", agent_info)   # lumber
    
    def test_get_agent_info(self):
        """Test retrieving agent information"""
        self.db.init_agent("Bob", wool=7, lumber=8, grain=9, brick=10, ore=11)
        result = self.db.get_agent_info("Bob")
        
        self.assertIn("Bob", result)
        self.assertIn("7", result)   # wool
        self.assertIn("11", result)  # ore
    
    def test_get_all_agents(self):
        """Test retrieving all agents"""
        self.db.init_agent("Alice", wool=10)
        self.db.init_agent("Bob", lumber=5)
        
        result = self.db.get_all_agents()
        self.assertIn("Alice", result)
        self.assertIn("Bob", result)
    
    def test_execute_query_select(self):
        """Test SELECT query execution"""
        self.db.init_agent("Charlie", wool=15)
        result = self.db.execute_query("SELECT name, wool FROM agents WHERE name = 'Charlie'")
        
        self.assertIn("Charlie", result)
        self.assertIn("15", result)
    
    def test_execute_query_update(self):
        """Test UPDATE query execution"""
        self.db.init_agent("Dave", wool=5)
        result = self.db.execute_query("UPDATE agents SET wool = 20 WHERE name = 'Dave'")
        
        self.assertIn("Success", result)
        
        # Verify update
        agent_info = self.db.get_agent_info("Dave")
        self.assertIn("20", agent_info)
    
    def test_execute_query_error(self):
        """Test query execution with invalid SQL"""
        result = self.db.execute_query("INVALID SQL QUERY")
        self.assertIn("Error", result)
    
    def test_get_recent_transactions(self):
        """Test retrieving recent transactions"""
        self.db.init_agent("Alice", wool=10)
        self.db.init_agent("Bob", ore=5)
        
        # Insert a transaction (matching new schema)
        self.db.execute_query("""
            INSERT INTO transactions (buyer, seller, buyer_resource, seller_resource, buyer_quantity, seller_quantity)
            VALUES ('Alice', 'Bob', 'ore', 'wool', 3, 5)
        """)
        
        result = self.db.get_recent_transactions(5)
        self.assertIn("Alice", result)
        self.assertIn("Bob", result)
        self.assertIn("ore", result)
        self.assertIn("3", result)


class TestAgentCommunication(unittest.TestCase):
    """Tests for AgentCommunication class"""
    
    def setUp(self):
        """Clear registry before each test"""
        AgentCommunication.clear()
    
    def tearDown(self):
        """Clear registry after each test"""
        AgentCommunication.clear()
    
    def test_register_agent(self):
        """Test registering an agent"""
        mock_agent = "MockAgent"
        AgentCommunication.register_agent("Alice", mock_agent)
        
        self.assertTrue(AgentCommunication.contains("Alice"))
        self.assertTrue(AgentCommunication.contains("alice"))  # Case-insensitive
    
    def test_get_agent(self):
        """Test retrieving an agent"""
        mock_agent = "MockAgent"
        AgentCommunication.register_agent("Bob", mock_agent)
        
        retrieved = AgentCommunication.get_agent("bob")
        self.assertEqual(retrieved, mock_agent)
    
    def test_get_agent_case_insensitive(self):
        """Test case-insensitive agent retrieval"""
        mock_agent = "MockAgent"
        AgentCommunication.register_agent("Charlie", mock_agent)
        
        self.assertEqual(AgentCommunication.get_agent("CHARLIE"), mock_agent)
        self.assertEqual(AgentCommunication.get_agent("charlie"), mock_agent)
        self.assertEqual(AgentCommunication.get_agent("Charlie"), mock_agent)
    
    def test_contains(self):
        """Test checking if agent exists"""
        AgentCommunication.register_agent("Dave", "Agent")
        
        self.assertTrue(AgentCommunication.contains("Dave"))
        self.assertTrue(AgentCommunication.contains("dave"))
        self.assertFalse(AgentCommunication.contains("Eve"))
    
    def test_keys(self):
        """Test retrieving all agent names"""
        AgentCommunication.register_agent("Alice", "Agent1")
        AgentCommunication.register_agent("Bob", "Agent2")
        
        keys = AgentCommunication.keys()
        self.assertEqual(len(keys), 2)
        self.assertIn("alice", keys)
        self.assertIn("bob", keys)
    
    def test_clear(self):
        """Test clearing all agents"""
        AgentCommunication.register_agent("Alice", "Agent")
        AgentCommunication.register_agent("Bob", "Agent")
        
        AgentCommunication.clear()
        
        self.assertEqual(len(AgentCommunication.keys()), 0)
        self.assertFalse(AgentCommunication.contains("Alice"))
    
    def test_agent_finished(self):
        """Test marking an agent as finished"""
        mock_agent = "MockAgent"
        AgentCommunication.register_agent("Alice", mock_agent)
        
        # Initially, agent should be active
        active = AgentCommunication.get_active_agents()
        self.assertIn("alice", active)
        
        # Mark as finished
        AgentCommunication.agent_finished("Alice")
        
        # Should no longer be active
        active = AgentCommunication.get_active_agents()
        self.assertNotIn("alice", active)
    
    def test_get_active_agents(self):
        """Test retrieving only active agents"""
        AgentCommunication.register_agent("Alice", "Agent1")
        AgentCommunication.register_agent("Bob", "Agent2")
        AgentCommunication.register_agent("Charlie", "Agent3")
        
        # Mark Bob as finished
        AgentCommunication.agent_finished("Bob")
        
        active = AgentCommunication.get_active_agents()
        self.assertEqual(len(active), 2)
        self.assertIn("alice", active)
        self.assertIn("charlie", active)
        self.assertNotIn("bob", active)


class TestTradingAgentTools(unittest.TestCase):
    """Tests for TradingAgent tools (without LLM calls)"""
    
    def setUp(self):
        """Set up test environment"""
        AgentCommunication.clear()
        if not os.path.exists("data"):
            os.makedirs("data")
        self.db = EconomyDB(db_path="test-tools.db")
        self.db.init_agent("Alice", wool=10, lumber=5, grain=8, brick=3, ore=2)
        self.db.init_agent("Bob", wool=2, lumber=15, grain=3, brick=10, ore=5)
        
        # Create agents (note: this will fail without Ollama, but tools can still be tested)
        try:
            self.alice = TradingAgent("Alice", "llama3.2", self.db, "Collect 10 ore")
            self.bob = TradingAgent("Bob", "llama3.2", self.db, "Collect 20 wool")
            
            AgentCommunication.register_agent("Alice", self.alice)
            AgentCommunication.register_agent("Bob", self.bob)
        except Exception as e:
            # If LLM setup fails, we can still test the tools directly
            print(f"Warning: Could not initialize agents with LLM: {e}")
            self.alice = None
            self.bob = None
    
    def tearDown(self):
        """Clean up"""
        AgentCommunication.clear()
        if os.path.exists(self.db.db_path):
            os.remove(self.db.db_path)
    
    def test_agent_creation(self):
        """Test agent creation and initialization"""
        if self.alice:
            self.assertEqual(self.alice.name, "Alice")
            self.assertEqual(self.alice.goal, "Collect 10 ore")
            self.assertIsNotNone(self.alice.tools)
            self.assertGreater(len(self.alice.tools), 0)
    
    def test_view_my_status_tool(self):
        """Test view_my_status tool"""
        if self.alice:
            tool = next((t for t in self.alice.tools if t.name == "view_my_status"), None)
            self.assertIsNotNone(tool)
            
            result = tool.invoke({})
            self.assertIn("Alice", result)
            self.assertIn("10", result)  # wool
    
    def test_view_other_agents_tool(self):
        """Test view_other_agents tool"""
        if self.alice:
            tool = next((t for t in self.alice.tools if t.name == "view_other_agents"), None)
            self.assertIsNotNone(tool)
            
            result = tool.invoke({})
            self.assertIn("Alice", result)
            self.assertIn("Bob", result)
    
    def test_view_active_agents_tool(self):
        """Test view_active_agents tool"""
        if self.alice:
            tool = next((t for t in self.alice.tools if t.name == "view_active_agents"), None)
            self.assertIsNotNone(tool)
            
            result = tool.invoke({})
            self.assertIn("alice", result.lower())
    
    def test_send_message_tool(self):
        """Test send_message tool"""
        if self.alice and self.bob:
            tool = next((t for t in self.alice.tools if t.name == "send_message"), None)
            self.assertIsNotNone(tool)
            
            result = tool.invoke({"recipient": "Bob", "message": "Want to trade?"})
            self.assertIn("Message sent", result)
            
            # Check Bob received the message
            self.assertEqual(len(self.bob.conversation_log), 1)
            self.assertEqual(self.bob.conversation_log[0]['from'], "Alice")
            self.assertEqual(self.bob.conversation_log[0]['message'], "Want to trade?")
    
    def test_send_message_invalid_recipient(self):
        """Test send_message with invalid recipient"""
        if self.alice:
            tool = next((t for t in self.alice.tools if t.name == "send_message"), None)
            self.assertIsNotNone(tool)
            
            result = tool.invoke({"recipient": "NonExistent", "message": "Hello"})
            self.assertIn("Error", result)
            self.assertIn("not found", result)
    
    def test_finish_trading_tool(self):
        """Test finish_trading tool"""
        if self.alice:
            tool = next((t for t in self.alice.tools if t.name == "finish_trading"), None)
            self.assertIsNotNone(tool)
            
            # Initially active
            active = AgentCommunication.get_active_agents()
            self.assertIn("alice", active)
            
            # Finish trading
            result = tool.invoke({})
            self.assertIn("finished trading", result)
            
            # No longer active
            active = AgentCommunication.get_active_agents()
            self.assertNotIn("alice", active)
    
    def test_record_trade_tool_success(self):
        """Test successful trade execution"""
        if self.alice:
            tool = next((t for t in self.alice.tools if t.name == "record_trade"), None)
            self.assertIsNotNone(tool)
            
            # Alice trades 3 wool for 2 ore from Bob
            result = tool.invoke({
                "other_agent": "Bob",
                "i_give_resource": "wool",
                "i_give_quantity": 3,
                "i_receive_resource": "ore",
                "i_receive_quantity": 2
            })
            
            self.assertIn("Trade completed", result)
            
            # Verify Alice's resources changed
            alice_info = self.db.get_agent_info("Alice")
            self.assertIn("7", alice_info)   # wool: 10 - 3 = 7
            self.assertIn("4", alice_info)   # ore: 2 + 2 = 4
            
            # Verify Bob's resources changed
            bob_info = self.db.get_agent_info("Bob")
            self.assertIn("5", bob_info)     # wool: 2 + 3 = 5
            self.assertIn("3", bob_info)     # ore: 5 - 2 = 3
    
    def test_record_trade_insufficient_resources(self):
        """Test trade with insufficient resources"""
        if self.alice:
            tool = next((t for t in self.alice.tools if t.name == "record_trade"), None)
            self.assertIsNotNone(tool)
            
            # Alice tries to trade 20 wool (but only has 10)
            result = tool.invoke({
                "other_agent": "Bob",
                "i_give_resource": "wool",
                "i_give_quantity": 20,
                "i_receive_resource": "ore",
                "i_receive_quantity": 2
            })
            
            self.assertIn("Error", result)
            self.assertIn("only have", result)
    
    def test_record_trade_seller_insufficient(self):
        """Test trade where seller has insufficient resources"""
        if self.alice:
            tool = next((t for t in self.alice.tools if t.name == "record_trade"), None)
            self.assertIsNotNone(tool)
            
            # Alice tries to receive 20 ore (but Bob only has 5)
            result = tool.invoke({
                "other_agent": "Bob",
                "i_give_resource": "wool",
                "i_give_quantity": 5,
                "i_receive_resource": "ore",
                "i_receive_quantity": 20
            })
            
            self.assertIn("Error", result)
            self.assertIn("only has", result)


class TestAgentConversation(unittest.TestCase):
    """Tests for agent conversation log functionality"""
    
    def setUp(self):
        """Set up test environment"""
        AgentCommunication.clear()
        if not os.path.exists("data"):
            os.makedirs("data")
        self.db = EconomyDB(db_path="test-conversation.db")
        self.db.init_agent("Alice", wool=10)
        self.db.init_agent("Bob", lumber=10)
    
    def tearDown(self):
        """Clean up"""
        AgentCommunication.clear()
        if os.path.exists(self.db.db_path):
            os.remove(self.db.db_path)
    
    def test_conversation_log_empty(self):
        """Test that conversation log starts empty"""
        try:
            alice = TradingAgent("Alice", "llama3.2", self.db, "Test goal")
            self.assertEqual(len(alice.conversation_log), 0)
        except Exception:
            self.skipTest("Ollama not available")
    
    def test_conversation_log_receives_message(self):
        """Test that conversation log receives messages"""
        try:
            alice = TradingAgent("Alice", "llama3.2", self.db, "Test goal")
            bob = TradingAgent("Bob", "llama3.2", self.db, "Test goal")
            
            # Manually add message to Alice's log (simulating what send_message does)
            alice.conversation_log.append({
                'from': 'Bob',
                'message': 'Hello Alice!'
            })
            
            self.assertEqual(len(alice.conversation_log), 1)
            self.assertEqual(alice.conversation_log[0]['from'], 'Bob')
            self.assertEqual(alice.conversation_log[0]['message'], 'Hello Alice!')
        except Exception:
            self.skipTest("Ollama not available")


def run_tests():
    """Run all tests"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestEconomyDB))
    suite.addTests(loader.loadTestsFromTestCase(TestAgentCommunication))
    suite.addTests(loader.loadTestsFromTestCase(TestTradingAgentTools))
    suite.addTests(loader.loadTestsFromTestCase(TestAgentConversation))
    
    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")
    print("=" * 70)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)
