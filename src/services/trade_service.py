"""Trade service for managing trades."""

from datetime import datetime
from typing import List, Dict, Optional


class TradeService:
    """Service for managing trades."""
    
    def __init__(self, db_manager):
        """Initialize trade service.
        
        Args:
            db_manager: DatabaseManager instance.
        """
        self.db = db_manager
    
    def add_trade(self, symbol: str, action: str, quantity: float, price: float, 
                  close_price: float = None, timestamp: str = None, opening_time: str = None,
                  result_gross: float = None, result_net: float = None, fx_fee: float = None,
                  result_after_fx_fee: float = None, realised_profit_loss_account_currency: float = None,
                  realised_profit_loss_instrument_currency: float = None,
                  net_result_account_currency: float = None, instrument_currency: str = None,
                  event_type: str = None, event_number: str = None,
                  order_number_name: str = None, order_number_id: str = None, notes: str = '') -> int:
        """Add a new trade.
        
        Args:
            symbol: Trading symbol.
            action: Trade action (BUY or SELL).
            quantity: Number of shares/contracts.
            price: Entry/Exit price.
            close_price: Closing price.
            timestamp: Closing timestamp.
            opening_time: Opening timestamp.
            result_gross: Gross result.
            result_net: Net result.
            fx_fee: FX fee.
            result_after_fx_fee: Result after FX fee.
            realised_profit_loss_account_currency: P/L in account currency.
            realised_profit_loss_instrument_currency: P/L in instrument currency.
            net_result_account_currency: Net result in account currency.
            instrument_currency: Instrument currency.
            event_type: Event type.
            event_number: Event number.
            order_number_name: Order number name.
            order_number_id: External trade ID.
            notes: Optional notes.
            
        Returns:
            int: ID of the inserted trade.
        """
        conn = self.db.get_connection()
        
        if timestamp is None:
            timestamp = datetime.now().isoformat()
        
        result = conn.execute('''
            INSERT INTO trades 
            (id, timestamp, opening_time, symbol, action, quantity, price, close_price,
             result_gross, result_net, fx_fee, result_after_fx_fee,
             realised_profit_loss_account_currency, realised_profit_loss_instrument_currency,
             net_result_account_currency,
             instrument_currency, event_type, event_number,
             order_number_name, order_number_id, notes)
            VALUES (nextval('trades_id_seq'), ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            RETURNING id
        ''', (timestamp, opening_time, symbol, action, quantity, price, close_price,
              result_gross, result_net, fx_fee, result_after_fx_fee,
              realised_profit_loss_account_currency, realised_profit_loss_instrument_currency,
              net_result_account_currency,
              instrument_currency, event_type, event_number,
              order_number_name, order_number_id, notes))
        
        trade_id = result.fetchone()[0]
        conn.close()
        
        return trade_id
    
    def get_recent_trades(self, limit: int = 10, include_overnight: bool = True, 
                         symbol: str = None, action: str = None, 
                         from_date: str = None, to_date: str = None,
                         min_profit: float = None, max_profit: float = None,
                         offset: int = 0) -> List[Dict]:
        """Get recent trades with optional filters.
        
        Args:
            limit: Maximum number of trades to return.
            include_overnight: If True, include overnight fees total for each trade.
            symbol: Filter by symbol/instrument (partial match).
            action: Filter by action (BUY or SELL).
            from_date: Filter trades from this date (ISO format: YYYY-MM-DD).
            to_date: Filter trades until this date (ISO format: YYYY-MM-DD).
            min_profit: Filter trades with P/L >= this value.
            max_profit: Filter trades with P/L <= this value.
            offset: Number of trades to skip for pagination.
            
        Returns:
            list: List of trade dictionaries with overnight_fees_total field.
        """
        # Build WHERE clause with filters
        where_clauses = []
        params = []
        
        if symbol:
            where_clauses.append("UPPER(symbol) LIKE UPPER(?)")
            params.append(f"%{symbol}%")
        
        if action:
            where_clauses.append("UPPER(action) = UPPER(?)")
            params.append(action)
        
        if from_date:
            where_clauses.append("substr(timestamp, 1, 10) >= ?")
            params.append(from_date)
        
        if to_date:
            where_clauses.append("substr(timestamp, 1, 10) <= ?")
            params.append(to_date)
        
        if min_profit is not None:
            where_clauses.append("result_after_fx_fee >= ?")
            params.append(min_profit)
        
        if max_profit is not None:
            where_clauses.append("result_after_fx_fee <= ?")
            params.append(max_profit)
        
        where_clause = ""
        if where_clauses:
            where_clause = "WHERE " + " AND ".join(where_clauses)
        
        query = f'''
            SELECT * FROM trades
            {where_clause}
            ORDER BY timestamp DESC
            LIMIT ? OFFSET ?
        '''
        params.append(limit)
        params.append(offset)
        
        rows = self.db.execute_query(query, tuple(params))
        trades = [dict(row) for row in rows]
        
        if include_overnight:
            for trade in trades:
                trade['overnight_fees_total'] = self.get_overnight_fees_total_for_trade(trade['order_number_name'])
        
        return trades
    
    def get_overnight_fees_for_trade(self, order_number_name: str) -> List[Dict]:
        """Get overnight fees associated with a trade.
        
        Args:
            order_number_name: Order number name to match.
            
        Returns:
            list: List of overnight fee dictionaries.
        """
        if not order_number_name:
            return []
        
        query = '''
            SELECT * FROM overnight_fees
            WHERE order_number_name = ?
            ORDER BY timestamp ASC
        '''
        rows = self.db.execute_query(query, (order_number_name,))
        return [dict(row) for row in rows]
    
    def get_overnight_fees_total_for_trade(self, order_number_name: str) -> float:
        """Get total overnight fees for a trade.
        
        Args:
            order_number_name: Order number name to match.
            
        Returns:
            float: Total overnight fees (interest).
        """
        if not order_number_name:
            return 0.0
        
        query = '''
            SELECT SUM(interest) as total FROM overnight_fees
            WHERE order_number_name = ?
        '''
        rows = self.db.execute_query(query, (order_number_name,))
        return rows[0]['total'] if rows and rows[0]['total'] is not None else 0.0
    
    def get_trade_by_id(self, trade_id: int) -> Optional[Dict]:
        """Get a trade by ID.
        
        Args:
            trade_id: Trade ID.
            
        Returns:
            dict: Trade dictionary or None if not found.
        """
        query = 'SELECT * FROM trades WHERE id = ?'
        rows = self.db.execute_query(query, (trade_id,))
        return dict(rows[0]) if rows else None
    
    def get_trades_by_symbol(self, symbol: str) -> List[Dict]:
        """Get all trades for a specific symbol.
        
        Args:
            symbol: Trading symbol.
            
        Returns:
            list: List of trade dictionaries.
        """
        query = '''
            SELECT * FROM trades
            WHERE symbol = ?
            ORDER BY timestamp DESC
        '''
        rows = self.db.execute_query(query, (symbol,))
        return [dict(row) for row in rows]
    
    def exists_by_order_number_id(self, order_number_id: str) -> bool:
        """Check if a trade with the given order_number_id exists.
        
        Args:
            order_number_id: External trade ID to check.
            
        Returns:
            bool: True if trade exists, False otherwise.
        """
        if not order_number_id:
            return False
        
        query = 'SELECT COUNT(*) as count FROM trades WHERE order_number_id = ?'
        rows = self.db.execute_query(query, (order_number_id,))
        return rows[0]['count'] > 0 if rows else False
    
    def delete_trade(self, trade_id: int) -> bool:
        """Delete a trade by ID.
        
        Args:
            trade_id: Trade ID.
            
        Returns:
            bool: True if deleted successfully.
        """
        conn = self.db.get_connection()
        conn.execute('DELETE FROM trades WHERE id = ?', (trade_id,))
        conn.close()
        return True
