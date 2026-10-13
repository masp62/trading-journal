"""Analytics utilities for trading performance."""

from typing import Dict, Optional
from utils.config import Config


class Analytics:
    """Analytics service for trading performance metrics."""
    
    def __init__(self, db_manager):
        """Initialize analytics service.
        
        Args:
            db_manager: DatabaseManager instance.
        """
        self.db = db_manager
        self.config = Config()
    
    def _get_daily_target_profit(self) -> float:
        """Get daily target profit from database settings or config default.
        
        Returns:
            float: Daily target profit
        """
        # Try to get from database first
        result = self.db.execute_query(
            "SELECT value FROM settings WHERE key = 'daily_profit_target'"
        )
        
        if result and len(result) > 0:
            return float(result[0]['value'])
        
        # Fall back to config default
        return self.config.daily_target_profit
    
    def get_performance_stats(self, from_date: Optional[str] = None, to_date: Optional[str] = None) -> Dict:
        """Get overall performance statistics.
        
        Args:
            from_date: Optional start date filter (YYYY-MM-DD)
            to_date: Optional end date filter (YYYY-MM-DD)
        
        Returns:
            dict: Dictionary containing performance metrics.
        """
        # Get total trades
        total_trades = self._get_total_trades(from_date=from_date, to_date=to_date)
        
        # Build date filter conditions
        date_filter = ""
        params = []
        if from_date:
            date_filter += " AND DATE(timestamp) >= ?"
            params.append(from_date)
        if to_date:
            date_filter += " AND DATE(timestamp) <= ?"
            params.append(to_date)
        
        # Calculate win/loss statistics
        query = f'''
            SELECT 
                COUNT(CASE WHEN result_after_fx_fee > 0 THEN 1 END) as winning_trades,
                COUNT(CASE WHEN result_after_fx_fee < 0 THEN 1 END) as losing_trades,
                SUM(CASE WHEN result_after_fx_fee > 0 THEN result_after_fx_fee ELSE 0 END) as total_profit,
                SUM(CASE WHEN result_after_fx_fee < 0 THEN result_after_fx_fee ELSE 0 END) as total_loss,
                AVG(CASE WHEN result_after_fx_fee > 0 THEN result_after_fx_fee END) as avg_win,
                AVG(CASE WHEN result_after_fx_fee < 0 THEN result_after_fx_fee END) as avg_loss,
                MAX(result_after_fx_fee) as largest_win,
                MIN(result_after_fx_fee) as largest_loss,
                SUM(result_after_fx_fee) as net_profit
            FROM trades
            WHERE result_after_fx_fee IS NOT NULL{date_filter}
        '''
        
        result = self.db.execute_query(query, params)
        
        if not result or not result[0]:
            return {
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'win_rate': 0.0,
                'total_profit': 0.0,
                'total_loss': 0.0,
                'net_profit': 0.0,
                'average_win': 0.0,
                'average_loss': 0.0,
                'profit_factor': None,
                'largest_win': 0.0,
                'largest_loss': 0.0
            }
        
        row = result[0]
        winning_trades = row['winning_trades'] or 0
        losing_trades = row['losing_trades'] or 0
        total_profit = row['total_profit'] or 0.0
        total_loss = row['total_loss'] or 0.0
        avg_win = row['avg_win'] or 0.0
        avg_loss = row['avg_loss'] or 0.0
        largest_win = row['largest_win'] or 0.0
        largest_loss = row['largest_loss'] or 0.0
        net_profit = row['net_profit'] or 0.0
        
        # Calculate win rate
        total_closed_trades = winning_trades + losing_trades
        win_rate = winning_trades / total_closed_trades if total_closed_trades > 0 else 0.0
        
        # Calculate profit factor
        profit_factor = None
        if total_loss < 0:
            profit_factor = total_profit / abs(total_loss)
        
        # Get total overnight fees
        total_overnight_fees = self._get_total_overnight_fees(from_date=from_date, to_date=to_date)
        
        return {
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'win_rate': round(win_rate, 3),
            'total_profit': round(total_profit, 3),
            'total_loss': round(total_loss, 3),
            'net_profit': round(net_profit, 3),
            'average_win': round(avg_win, 3),
            'average_loss': round(avg_loss, 3),
            'profit_factor': round(profit_factor, 3) if profit_factor is not None else None,
            'largest_win': round(largest_win, 3),
            'largest_loss': round(largest_loss, 3),
            'total_overnight_fees': round(total_overnight_fees, 3)
        }
    
    def _get_total_trades(self, from_date: Optional[str] = None, to_date: Optional[str] = None) -> int:
        """Get total number of trades."""
        query = 'SELECT COUNT(*) as count FROM trades WHERE 1=1'
        params = []
        if from_date:
            query += " AND DATE(timestamp) >= ?"
            params.append(from_date)
        if to_date:
            query += " AND DATE(timestamp) <= ?"
            params.append(to_date)
        result = self.db.execute_query(query, params)
        return result[0]['count'] if result else 0
    
    def _get_total_overnight_fees(self, from_date: Optional[str] = None, to_date: Optional[str] = None) -> float:
        """Get total overnight fees across all trades.
        
        Returns:
            float: Total overnight fees (interest).
        """
        query = 'SELECT SUM(interest) as total FROM overnight_fees WHERE 1=1'
        params = []
        if from_date:
            query += " AND DATE(timestamp) >= ?"
            params.append(from_date)
        if to_date:
            query += " AND DATE(timestamp) <= ?"
            params.append(to_date)
        result = self.db.execute_query(query, params)
        return result[0]['total'] if result and result[0]['total'] is not None else 0.0
    
    def _get_total_volume(self) -> float:
        """Get total trading volume."""
        query = 'SELECT SUM(quantity * price) as volume FROM trades'
        result = self.db.execute_query(query)
        return result[0]['volume'] if result and result[0]['volume'] else 0.0
    
    def _get_most_traded_symbol(self) -> str:
        """Get the most traded symbol."""
        query = '''
            SELECT symbol, COUNT(*) as trade_count
            FROM trades
            GROUP BY symbol
            ORDER BY trade_count DESC
            LIMIT 1
        '''
        result = self.db.execute_query(query)
        return result[0]['symbol'] if result else 'N/A'
    
    def get_trades_per_period(self, period: str, limit: int = None):
        """Get number of trades grouped by time period.
        
        Args:
            period: Time period ('day', 'week', 'month', 'year')
            limit: Maximum number of periods to return (None for all)
            
        Returns:
            list: List of dictionaries with period and trade count
        """
        # Define period format based on parameter - work with VARCHAR timestamp field directly
        if period == 'day':
            date_format = "substr(timestamp, 1, 10)"
        elif period == 'week':
            date_format = "strftime(strptime(substr(timestamp, 1, 10), '%Y-%m-%d'), '%Y-W%W')"
        elif period == 'month':
            date_format = "substr(timestamp, 1, 7)"
        elif period == 'year':
            date_format = "substr(timestamp, 1, 4)"
        else:
            date_format = "substr(timestamp, 1, 10)"
        
        limit_clause = f'LIMIT {limit}' if limit else ''
        
        query = f'''
            SELECT 
                {date_format} as period,
                COUNT(*) as trade_count,
                SUM(result_after_fx_fee) as total_pnl,
                AVG(result_after_fx_fee) as avg_pnl
            FROM trades
            WHERE timestamp IS NOT NULL
            GROUP BY {date_format}
            ORDER BY period DESC
            {limit_clause}
        '''
        
        results = self.db.execute_query(query)
        
        # Get daily target profit from database settings or config
        daily_target = self._get_daily_target_profit()
        
        # Add overnight fees and calculate target deviation for each period
        for row in results:
            row['overnight_fees'] = self._get_overnight_fees_for_period(row['period'], period)
            
            # Calculate aggregated target based on period
            row['target_profit'] = self._calculate_period_target(period, daily_target)
            
            # Calculate total (P/L + overnight fees)
            total = (row['total_pnl'] or 0.0) + row['overnight_fees']
            
            # Calculate deviation from target
            row['deviation_from_target'] = total - row['target_profit']
            
            # Round all values to 3 decimal places
            row['total_pnl'] = round(row['total_pnl'] or 0.0, 3)
            row['avg_pnl'] = round(row['avg_pnl'] or 0.0, 3)
            row['overnight_fees'] = round(row['overnight_fees'], 3)
            row['target_profit'] = round(row['target_profit'], 3)
            row['deviation_from_target'] = round(row['deviation_from_target'], 3)
        
        return results
    
    def _calculate_period_target(self, period: str, daily_target: float) -> float:
        """Calculate target profit for different periods based on daily target.
        
        Args:
            period: Time period ('day', 'week', 'month', 'year')
            daily_target: Daily target profit
            
        Returns:
            float: Target profit for the period
        """
        if period == 'day':
            return daily_target
        elif period == 'week':
            return daily_target * 5  # 5 trading days per week
        elif period == 'month':
            return daily_target * 21  # ~21 trading days per month
        elif period == 'year':
            return daily_target * 252  # ~252 trading days per year
        else:
            return daily_target
    
    def _get_overnight_fees_for_period(self, period_value: str, period_type: str) -> float:
        """Get total overnight fees for a specific period.
        
        Args:
            period_value: Period value (e.g., '2025-05-22' for day)
            period_type: Type of period ('day', 'week', 'month', 'year')
            
        Returns:
            float: Total overnight fees for the period
        """
        # Define period format based on parameter - work with VARCHAR timestamp field directly
        if period_type == 'day':
            date_format = "substr(timestamp, 1, 10)"
        elif period_type == 'week':
            date_format = "strftime(strptime(substr(timestamp, 1, 10), '%Y-%m-%d'), '%Y-W%W')"
        elif period_type == 'month':
            date_format = "substr(timestamp, 1, 7)"
        elif period_type == 'year':
            date_format = "substr(timestamp, 1, 4)"
        else:
            date_format = "substr(timestamp, 1, 10)"
        
        query = f'''
            SELECT SUM(interest) as total_fees
            FROM overnight_fees
            WHERE {date_format} = ?
        '''
        
        result = self.db.execute_query(query, (period_value,))
        return result[0]['total_fees'] if result and result[0]['total_fees'] is not None else 0.0
    
    def get_symbol_stats(self, symbol: str) -> Optional[Dict]:
        """Get statistics for a specific symbol.
        
        Args:
            symbol: Trading symbol.
            
        Returns:
            dict: Statistics for the symbol.
        """
        query = '''
            SELECT 
                COUNT(*) as trade_count,
                SUM(CASE WHEN action = 'BUY' THEN quantity ELSE 0 END) as total_bought,
                SUM(CASE WHEN action = 'SELL' THEN quantity ELSE 0 END) as total_sold,
                SUM(quantity * price) as total_volume,
                AVG(price) as avg_price
            FROM trades
            WHERE symbol = ?
        '''
        result = self.db.execute_query(query, (symbol,))
        
        if not result or result[0]['trade_count'] == 0:
            return None
        
        row = result[0]
        return {
            'symbol': symbol,
            'trade_count': row['trade_count'],
            'total_bought': row['total_bought'] or 0,
            'total_sold': row['total_sold'] or 0,
            'total_volume': row['total_volume'] or 0,
            'avg_price': row['avg_price'] or 0
        }
    
    def get_all_instrument_stats(self, limit: Optional[int] = None, from_date: Optional[str] = None, to_date: Optional[str] = None):
        """Get trading statistics grouped by instrument/symbol.
        
        Args:
            limit: Maximum number of instruments to return (None for all)
            from_date: Optional start date filter (YYYY-MM-DD)
            to_date: Optional end date filter (YYYY-MM-DD)
            
        Returns:
            list: List of dictionaries with instrument statistics
        """
        limit_clause = f'LIMIT {limit}' if limit else ''
        
        # Build date filter (use closing date: timestamp)
        date_filter = ""
        params = []
        if from_date:
            date_filter += " AND DATE(timestamp) >= ?"
            params.append(from_date)
        if to_date:
            date_filter += " AND DATE(timestamp) <= ?"
            params.append(to_date)
        
        # Main query aggregating by symbol
        query = f'''
            SELECT 
                symbol,
                COUNT(*) as total_trades,
                COUNT(CASE WHEN result_after_fx_fee > 0 THEN 1 END) as winning_trades,
                COUNT(CASE WHEN result_after_fx_fee < 0 THEN 1 END) as losing_trades,
                SUM(result_after_fx_fee) as total_pnl,
                AVG(result_after_fx_fee) as avg_pnl,
                MAX(result_after_fx_fee) as largest_win,
                MIN(result_after_fx_fee) as largest_loss,
                AVG(price) as avg_price
            FROM trades
            WHERE result_after_fx_fee IS NOT NULL{date_filter}
            GROUP BY symbol
            ORDER BY total_pnl DESC
            {limit_clause}
        '''
        
        results = self.db.execute_query(query, params)

        # Add overnight fees, win rate und net total für jedes Symbol
        for row in results:
            # Get overnight fees for this symbol
            overnight_query = '''
                SELECT SUM(interest) as total_interest
                FROM overnight_fees
                WHERE symbol = ?
            '''
            overnight_params = [row['symbol']]
            if from_date:
                overnight_query += " AND DATE(timestamp) >= ?"
                overnight_params.append(from_date)
            if to_date:
                overnight_query += " AND DATE(timestamp) <= ?"
                overnight_params.append(to_date)
            overnight_result = self.db.execute_query(overnight_query, overnight_params)
            row['overnight_fees'] = overnight_result[0]['total_interest'] if overnight_result and overnight_result[0]['total_interest'] is not None else 0.0

            # Calculate win rate
            total_closed = (row['winning_trades'] or 0) + (row['losing_trades'] or 0)
            row['win_rate'] = (row['winning_trades'] or 0) / total_closed if total_closed > 0 else 0.0

            # Calculate net total (P/L + overnight fees)
            row['net_total'] = (row['total_pnl'] or 0.0) + row['overnight_fees']



            # Round all numeric values to 3 decimal places
            row['win_rate'] = round(row['win_rate'], 3)
            row['total_pnl'] = round(row['total_pnl'] or 0.0, 3)
            row['avg_pnl'] = round(row['avg_pnl'] or 0.0, 3)
            row['largest_win'] = round(row['largest_win'] or 0.0, 3)
            row['largest_loss'] = round(row['largest_loss'] or 0.0, 3)
            row['avg_price'] = round(row['avg_price'] or 0.0, 3)
            row['overnight_fees'] = round(row['overnight_fees'], 3)
            row['net_total'] = round(row['net_total'], 3)
        return results
