"""
Market Coordinator - Manages the database and validates transactions
"""
import sqlite3
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import json
from config import DATABASE_PATH


class MarketCoordinator:
    def __init__(self, db_path: str = DATABASE_PATH):
        self.db_path = db_path
        self.init_database()
        
    def init_database(self):
        """Initialize the economy database with necessary tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Agents table - tracks each agent and their balance
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS agents (
                agent_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                balance REAL NOT NULL,
                goal TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Resources table - tracks what resources each agent has
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS resources (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                agent_id TEXT NOT NULL,
                resource_name TEXT NOT NULL,
                quantity REAL NOT NULL,
                FOREIGN KEY (agent_id) REFERENCES agents(agent_id)
            )
        ''')
        
        # Pending transactions - stores transactions awaiting confirmation
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pending_transactions (
                transaction_id TEXT PRIMARY KEY,
                buyer_id TEXT NOT NULL,
                seller_id TEXT NOT NULL,
                resource_name TEXT NOT NULL,
                quantity REAL NOT NULL,
                price REAL NOT NULL,
                buyer_confirmed BOOLEAN DEFAULT 0,
                seller_confirmed BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (buyer_id) REFERENCES agents(agent_id),
                FOREIGN KEY (seller_id) REFERENCES agents(agent_id)
            )
        ''')
        
        # Completed transactions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                transaction_id TEXT NOT NULL,
                buyer_id TEXT NOT NULL,
                seller_id TEXT NOT NULL,
                resource_name TEXT NOT NULL,
                quantity REAL NOT NULL,
                price REAL NOT NULL,
                completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        
    def register_agent(self, agent_id: str, name: str, initial_balance: float, goal: str = ""):
        """Register a new agent in the economy"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO agents (agent_id, name, balance, goal)
            VALUES (?, ?, ?, ?)
        ''', (agent_id, name, initial_balance, goal))
        
        conn.commit()
        conn.close()
        
    def add_resource(self, agent_id: str, resource_name: str, quantity: float):
        """Add or update a resource for an agent"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if resource already exists
        cursor.execute('''
            SELECT quantity FROM resources 
            WHERE agent_id = ? AND resource_name = ?
        ''', (agent_id, resource_name))
        
        result = cursor.fetchone()
        
        if result:
            # Update existing resource
            new_quantity = result[0] + quantity
            cursor.execute('''
                UPDATE resources 
                SET quantity = ? 
                WHERE agent_id = ? AND resource_name = ?
            ''', (new_quantity, agent_id, resource_name))
        else:
            # Insert new resource
            cursor.execute('''
                INSERT INTO resources (agent_id, resource_name, quantity)
                VALUES (?, ?, ?)
            ''', (agent_id, resource_name, quantity))
        
        conn.commit()
        conn.close()
        
    def confirm_transaction(self, transaction_id: str, agent_id: str) -> Optional[str]:
        """
        Confirm a transaction from one agent's side.
        When both agents confirm the same transaction, it gets executed.
        Returns 'completed' if transaction is executed, 'confirmed' if waiting for other party, or None on error.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get pending transaction
        cursor.execute('''
            SELECT buyer_id, seller_id, resource_name, quantity, price, 
                   buyer_confirmed, seller_confirmed
            FROM pending_transactions 
            WHERE transaction_id = ?
        ''', (transaction_id,))
        
        result = cursor.fetchone()
        
        if not result:
            conn.close()
            return None
            
        buyer_id, seller_id, resource_name, quantity, price, buyer_confirmed, seller_confirmed = result
        
        # Determine which party is confirming
        if agent_id == buyer_id:
            buyer_confirmed = True
        elif agent_id == seller_id:
            seller_confirmed = True
        else:
            conn.close()
            return None
            
        # Update confirmation status
        cursor.execute('''
            UPDATE pending_transactions 
            SET buyer_confirmed = ?, seller_confirmed = ?
            WHERE transaction_id = ?
        ''', (buyer_confirmed, seller_confirmed, transaction_id))
        
        # If both confirmed, execute the transaction
        if buyer_confirmed and seller_confirmed:
            # Verify buyer has enough money
            cursor.execute('SELECT balance FROM agents WHERE agent_id = ?', (buyer_id,))
            buyer_balance = cursor.fetchone()[0]
            
            # Verify seller has enough resources
            cursor.execute('''
                SELECT quantity FROM resources 
                WHERE agent_id = ? AND resource_name = ?
            ''', (seller_id, resource_name))
            seller_resource = cursor.fetchone()
            
            if buyer_balance >= price and seller_resource and seller_resource[0] >= quantity:
                # Execute transaction
                # 1. Transfer money
                cursor.execute('''
                    UPDATE agents SET balance = balance - ? WHERE agent_id = ?
                ''', (price, buyer_id))
                cursor.execute('''
                    UPDATE agents SET balance = balance + ? WHERE agent_id = ?
                ''', (price, seller_id))
                
                # 2. Transfer resources
                cursor.execute('''
                    UPDATE resources 
                    SET quantity = quantity - ? 
                    WHERE agent_id = ? AND resource_name = ?
                ''', (quantity, seller_id, resource_name))
                
                # Add resource to buyer
                cursor.execute('''
                    SELECT quantity FROM resources 
                    WHERE agent_id = ? AND resource_name = ?
                ''', (buyer_id, resource_name))
                buyer_resource = cursor.fetchone()
                
                if buyer_resource:
                    cursor.execute('''
                        UPDATE resources 
                        SET quantity = quantity + ? 
                        WHERE agent_id = ? AND resource_name = ?
                    ''', (quantity, buyer_id, resource_name))
                else:
                    cursor.execute('''
                        INSERT INTO resources (agent_id, resource_name, quantity)
                        VALUES (?, ?, ?)
                    ''', (buyer_id, resource_name, quantity))
                
                # 3. Record completed transaction
                cursor.execute('''
                    INSERT INTO transactions 
                    (transaction_id, buyer_id, seller_id, resource_name, quantity, price)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (transaction_id, buyer_id, seller_id, resource_name, quantity, price))
                
                # 4. Remove from pending
                cursor.execute('''
                    DELETE FROM pending_transactions WHERE transaction_id = ?
                ''', (transaction_id,))
                
                conn.commit()
                conn.close()
                return 'completed'
            else:
                # Transaction invalid - insufficient funds or resources
                cursor.execute('''
                    DELETE FROM pending_transactions WHERE transaction_id = ?
                ''', (transaction_id,))
                conn.commit()
                conn.close()
                return 'failed'
        
        conn.commit()
        conn.close()
        return 'confirmed'
        
    def create_pending_transaction(self, transaction_id: str, buyer_id: str, 
                                   seller_id: str, resource_name: str, 
                                   quantity: float, price: float) -> bool:
        """Create a new pending transaction"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO pending_transactions 
                (transaction_id, buyer_id, seller_id, resource_name, quantity, price)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (transaction_id, buyer_id, seller_id, resource_name, quantity, price))
            
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            conn.close()
            return False
            
    def get_agent_info(self, agent_id: str) -> Optional[Dict]:
        """Get information about a specific agent"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT agent_id, name, balance, goal 
            FROM agents WHERE agent_id = ?
        ''', (agent_id,))
        
        result = cursor.fetchone()
        
        if not result:
            conn.close()
            return None
            
        agent_info = {
            'agent_id': result[0],
            'name': result[1],
            'balance': result[2],
            'goal': result[3]
        }
        
        # Get agent's resources
        cursor.execute('''
            SELECT resource_name, quantity FROM resources 
            WHERE agent_id = ?
        ''', (agent_id,))
        
        agent_info['resources'] = {row[0]: row[1] for row in cursor.fetchall()}
        
        conn.close()
        return agent_info
        
    def get_all_agents(self) -> List[Dict]:
        """Get information about all agents in the economy"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT agent_id, name, balance, goal FROM agents')
        agents = []
        
        for row in cursor.fetchall():
            agent_id = row[0]
            
            # Get resources for this agent
            cursor.execute('''
                SELECT resource_name, quantity FROM resources 
                WHERE agent_id = ?
            ''', (agent_id,))
            
            resources = {r[0]: r[1] for r in cursor.fetchall()}
            
            agents.append({
                'agent_id': agent_id,
                'name': row[1],
                'balance': row[2],
                'goal': row[3],
                'resources': resources
            })
        
        conn.close()
        return agents
        
    def get_transaction_history(self, limit: int = 50) -> List[Dict]:
        """Get recent completed transactions"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT transaction_id, buyer_id, seller_id, resource_name, 
                   quantity, price, completed_at
            FROM transactions 
            ORDER BY completed_at DESC 
            LIMIT ?
        ''', (limit,))
        
        transactions = []
        for row in cursor.fetchall():
            transactions.append({
                'transaction_id': row[0],
                'buyer_id': row[1],
                'seller_id': row[2],
                'resource_name': row[3],
                'quantity': row[4],
                'price': row[5],
                'completed_at': row[6]
            })
        
        conn.close()
        return transactions
        
    def get_market_summary(self) -> str:
        """Get a text summary of the current market state"""
        agents = self.get_all_agents()
        transactions = self.get_transaction_history(10)
        
        summary = "=== MARKET SUMMARY ===\n\n"
        summary += f"Total Agents: {len(agents)}\n\n"
        
        summary += "AGENTS:\n"
        for agent in agents:
            summary += f"  - {agent['name']} (ID: {agent['agent_id'][:8]}...)\n"
            summary += f"    Balance: ${agent['balance']:.2f}\n"
            summary += f"    Goal: {agent['goal']}\n"
            if agent['resources']:
                summary += f"    Resources: {json.dumps(agent['resources'])}\n"
            summary += "\n"
        
        summary += f"\nRECENT TRANSACTIONS ({len(transactions)}):\n"
        for tx in transactions[:5]:
            summary += f"  - {tx['buyer_id'][:8]}... bought {tx['quantity']} {tx['resource_name']} "
            summary += f"from {tx['seller_id'][:8]}... for ${tx['price']:.2f}\n"
        
        return summary
