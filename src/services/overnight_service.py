"""Overnight fees service for managing overnight fee records."""

from datetime import datetime


class OvernightService:
    """Service for managing overnight fee records."""
    
    def __init__(self, db_manager):
        """Initialize overnight fees service.
        
        Args:
            db_manager: DatabaseManager instance.
        """
        self.db = db_manager
    
    def add_overnight_fee(self, timestamp, symbol, direction, quantity, interest, 
                         instrument_currency=None, order_number_id=None, order_number_name=None):
        """Add an overnight fee record.
        
        Args:
            timestamp: Timestamp of the overnight fee.
            symbol: Trading symbol.
            direction: Direction (buy/sell).
            quantity: Position quantity.
            interest: Interest amount.
            instrument_currency: Currency of the instrument.
            order_number_id: External ID from trading platform.
            order_number_name: Order number name from trading platform.
            
        Returns:
            int: ID of the created record.
        """
        conn = self.db.get_connection()
        
        result = conn.execute('''
            INSERT INTO overnight_fees 
            (id, timestamp, symbol, direction, quantity, interest, instrument_currency, order_number_id, order_number_name)
            VALUES (nextval('overnight_fees_id_seq'), ?, ?, ?, ?, ?, ?, ?, ?)
            RETURNING id
        ''', (timestamp, symbol, direction, quantity, interest, instrument_currency, order_number_id, order_number_name))
        
        fee_id = result.fetchone()[0]
        conn.close()
        
        return fee_id
    
    def exists_by_order_number_id(self, order_number_id):
        """Check if an overnight fee record exists by external ID.
        
        Args:
            order_number_id: External ID to check.
            
        Returns:
            bool: True if record exists, False otherwise.
        """
        if not order_number_id:
            return False
            
        result = self.db.execute_query(
            'SELECT COUNT(*) as count FROM overnight_fees WHERE order_number_id = ?',
            (order_number_id,)
        )
        
        return result[0]['count'] > 0 if result else False
    
    def get_recent_fees(self, limit=10, offset=0):
        """Get recent overnight fees.
        
        Args:
            limit: Maximum number of records to return.
            offset: Number of records to skip.
        Returns:
            list: List of overnight fee records.
        """
        query = '''
            SELECT * FROM overnight_fees
            ORDER BY timestamp DESC
            LIMIT ? OFFSET ?
        '''
        return self.db.execute_query(query, (limit, offset))
    
    def get_total_interest(self):
        """Get total interest paid/received.
        
        Returns:
            float: Total interest amount.
        """
        result = self.db.execute_query(
            'SELECT SUM(interest) as total FROM overnight_fees'
        )
        
        return result[0]['total'] if result and result[0]['total'] else 0.0
    
    def get_interest_by_symbol(self):
        """Get total interest grouped by symbol.
        
        Returns:
            list: List of (symbol, total_interest) tuples.
        """
        return self.db.execute_query('''
            SELECT symbol, SUM(interest) as total_interest
            FROM overnight_fees
            GROUP BY symbol
            ORDER BY total_interest
        ''')
    
    def get_fee_by_id(self, fee_id):
        """Get an overnight fee by ID.
        
        Args:
            fee_id: Fee ID.
            
        Returns:
            dict: Fee record or None if not found.
        """
        result = self.db.execute_query(
            'SELECT * FROM overnight_fees WHERE id = ?',
            (fee_id,)
        )
        return result[0] if result else None
    
    def delete_overnight_fee(self, fee_id):
        """Delete an overnight fee by ID.
        
        Args:
            fee_id: Fee ID.
            
        Returns:
            bool: True if deleted successfully.
        """
        conn = self.db.get_connection()
        conn.execute('DELETE FROM overnight_fees WHERE id = ?', (fee_id,))
        conn.close()
        return True
