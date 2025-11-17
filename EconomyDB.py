"""
Simple SQLite database for the economy
"""
import sqlite3
import os


class EconomyDB:
    def __init__(self, db_path: str = "-economy.db"):
        num = 0
        while os.path.exists("data/" + str(num) + db_path):
            num += 1

        self.db_path = "data/" + str(num) + db_path
        self.init_database()
        
    def init_database(self):
        """Initialize simple database"""
        conn = sqlite3.connect(self.db_path)

        cursor = conn.cursor()
        
        # Simple agents table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS agents (
                name TEXT PRIMARY KEY,
                wool INTEGER DEFAULT 0,
                lumber INTEGER DEFAULT 0,
                grain INTEGER DEFAULT 0,
                brick INTEGER DEFAULT 0,
                ore INTEGER DEFAULT 0
            )
        ''')
        
        # Simple transactions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                buyer TEXT NOT NULL,
                seller TEXT NOT NULL,
                buyer_resource TEXT NOT NULL,
                seller_resource TEXT NOT NULL,
                buyer_quantity INTEGER NOT NULL,
                seller_quantity INTEGER NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        
    def execute_query(self, query: str) -> str:
        """Execute a SQL query and return results as string"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute(query)
            
            # If it's a SELECT query, fetch results
            if query.strip().upper().startswith('SELECT'):
                results = cursor.fetchall()
                columns = [description[0] for description in cursor.description]
                
                if not results:
                    return "No results found"
                
                # Format as table
                output = " | ".join(columns) + "\n"
                output += "-" * len(output) + "\n"
                for row in results:
                    output += " | ".join(str(x) for x in row) + "\n"
                return output
            else:
                # For INSERT/UPDATE queries
                conn.commit()
                return f"Success: {cursor.rowcount} row(s) affected"
                
        except Exception as e:
            return f"Error: {e}"
        finally:
            conn.close()

    def init_agent(self, name: str, wool: int = 0, lumber: int = 0, grain: int = 0, brick: int = 0, ore: int = 0):
        """Initialize an agent"""
        query = f"""
            INSERT OR REPLACE INTO agents (name, wool, lumber, grain, brick, ore)
            VALUES ('{name}', {wool}, {lumber}, {grain}, {brick}, {ore})
        """
        return self.execute_query(query)
        
    def get_agent_info(self, name: str) -> str:
        """Get agent information"""
        query = f"SELECT * FROM agents WHERE name = '{name}'"
        return self.execute_query(query)
        
    def get_all_agents(self) -> str:
        """Get all agents"""
        return self.execute_query("SELECT * FROM agents")
        
    def get_recent_transactions(self, limit: int = 10) -> str:
        """Get recent transactions"""
        return self.execute_query(f"SELECT * FROM transactions ORDER BY timestamp DESC LIMIT {limit}")
