"""Database manager for Trading Journal."""

import duckdb
import os
from pathlib import Path


class DatabaseManager:
    """Manages database connections and schema initialization."""
    
    def __init__(self, db_path=None):
        """Initialize database manager.
        
        Args:
            db_path: Path to database file. If None, uses default location.
        """
        if db_path is None:
            # Create data directory if it doesn't exist
            data_dir = Path(__file__).parent.parent.parent / "data"
            data_dir.mkdir(exist_ok=True)
            db_path = data_dir / "trading_journal.db"
        
        self.db_path = str(db_path)
        self._init_database()
    
    def _init_database(self):
        """Initialize database schema."""
        conn = self.get_connection()
        
        # Create trades table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY,
                timestamp VARCHAR NOT NULL,
                opening_time VARCHAR,
                symbol VARCHAR NOT NULL,
                action VARCHAR NOT NULL,
                quantity DOUBLE NOT NULL,
                price DOUBLE NOT NULL,
                close_price DOUBLE,
                result_gross DOUBLE,
                result_net DOUBLE,
                fx_fee DOUBLE,
                result_after_fx_fee DOUBLE,
                realised_profit_loss_account_currency DOUBLE,
                realised_profit_loss_instrument_currency DOUBLE,
                net_result_account_currency DOUBLE,
                instrument_currency VARCHAR,
                event_type VARCHAR,
                event_number VARCHAR,
                order_number_name VARCHAR,
                order_number_id VARCHAR,
                notes VARCHAR,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create sequence for trades if not exists
        conn.execute('''
            CREATE SEQUENCE IF NOT EXISTS trades_id_seq START 1
        ''')
        
        # Create journal entries table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS journal_entries (
                id INTEGER PRIMARY KEY,
                timestamp VARCHAR NOT NULL,
                title VARCHAR NOT NULL,
                content VARCHAR NOT NULL,
                tags VARCHAR,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create sequence for journal entries if not exists
        conn.execute('''
            CREATE SEQUENCE IF NOT EXISTS journal_entries_id_seq START 1
        ''')
        
        # Create overnight fees table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS overnight_fees (
                id INTEGER PRIMARY KEY,
                timestamp VARCHAR NOT NULL,
                symbol VARCHAR NOT NULL,
                direction VARCHAR NOT NULL,
                quantity DOUBLE NOT NULL,
                interest DOUBLE NOT NULL,
                instrument_currency VARCHAR,
                order_number_id VARCHAR,
                order_number_name VARCHAR,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create sequence for overnight fees if not exists
        conn.execute('''
            CREATE SEQUENCE IF NOT EXISTS overnight_fees_id_seq START 1
        ''')
        
        # Create expenses table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY,
                name VARCHAR NOT NULL,
                purchase_date VARCHAR NOT NULL,
                expiry_date VARCHAR NOT NULL,
                price DOUBLE NOT NULL,
                currency VARCHAR DEFAULT 'EUR',
                category VARCHAR,
                notes VARCHAR,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create sequence for expenses if not exists
        conn.execute('''
            CREATE SEQUENCE IF NOT EXISTS expenses_id_seq START 1
        ''')
        
        # Create settings table
        conn.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                key VARCHAR PRIMARY KEY,
                value VARCHAR NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.close()
    
    def get_connection(self):
        """Get a database connection.
        
        Returns:
            duckdb.DuckDBPyConnection: Database connection object.
        """
        return duckdb.connect(self.db_path)
    
    def execute_query(self, query, params=None):
        """Execute a query and return results.
        
        Args:
            query: SQL query string.
            params: Query parameters (optional).
            
        Returns:
            list: Query results as list of dictionaries.
        """
        conn = self.get_connection()
        if params:
            result = conn.execute(query, params).fetchall()
        else:
            result = conn.execute(query).fetchall()
        
        # Get column names
        if result:
            columns = [desc[0] for desc in conn.description]
            result = [dict(zip(columns, row)) for row in result]
        
        conn.close()
        return result
    
    def execute_insert(self, query, params=None):
        """Execute an insert query and return the last row ID.
        
        Args:
            query: SQL insert query string.
            params: Query parameters (optional).
            
        Returns:
            int: ID of the inserted row.
        """
        conn = self.get_connection()
        
        # Determine which table we're inserting into
        table_name = None
        if 'trades' in query.lower():
            table_name = 'trades'
            seq_name = 'trades_id_seq'
        elif 'journal_entries' in query.lower():
            table_name = 'journal_entries'
            seq_name = 'journal_entries_id_seq'
        
        # Get next ID from sequence
        next_id = conn.execute(f"SELECT nextval('{seq_name}')").fetchone()[0] if table_name else None
        
        # Modify query to include ID if needed
        # Check if 'id' column is explicitly mentioned (not just part of external_id)
        insert_cols = query.lower().split('insert into')[1].split('values')[0] if 'values' in query.lower() else ''
        needs_id = next_id and ' id' not in insert_cols and '(id' not in insert_cols
        
        if needs_id:
            # Insert ID as first value
            if params:
                params = (next_id,) + params
                query = query.replace('(', '(id, ', 1).replace('VALUES (', f'VALUES (?, ', 1)
            
        if params:
            conn.execute(query, params)
        else:
            conn.execute(query)
        
        conn.close()
        return next_id if next_id else 1
    
    def execute_update(self, query, params=None):
        """Execute an UPDATE or DELETE query.
        
        Args:
            query: SQL UPDATE or DELETE query string.
            params: Query parameters (optional).
            
        Returns:
            bool: True if successful.
        """
        conn = self.get_connection()
        
        if params:
            conn.execute(query, params)
        else:
            conn.execute(query)
        
        conn.close()
        return True
