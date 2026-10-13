"""Expense service for managing trading-related expenses and subscriptions."""

from datetime import datetime


class ExpenseService:
    """Service for managing expense records."""
    
    def __init__(self, db_manager):
        """Initialize expense service.
        
        Args:
            db_manager: DatabaseManager instance.
        """
        self.db = db_manager
    
    def add_expense(self, name, purchase_date, expiry_date, price, 
                   currency='EUR', category=None, notes=None):
        """Add an expense record.
        
        Args:
            name: Name/description of the expense.
            purchase_date: Date of purchase (ISO format).
            expiry_date: Expiry/renewal date (ISO format).
            price: Price amount.
            currency: Currency code (default: EUR).
            category: Category of expense (e.g., TradingView, Broker, Data Feed).
            notes: Additional notes.
            
        Returns:
            int: ID of the created record.
        """
        conn = self.db.get_connection()
        
        result = conn.execute('''
            INSERT INTO expenses 
            (id, name, purchase_date, expiry_date, price, currency, category, notes)
            VALUES (nextval('expenses_id_seq'), ?, ?, ?, ?, ?, ?, ?)
            RETURNING id
        ''', (name, purchase_date, expiry_date, price, currency, category, notes))
        
        expense_id = result.fetchone()[0]
        conn.close()
        
        return expense_id
    
    def get_all_expenses(self, limit=50, offset=0):
        """Get all expenses with pagination.
        
        Args:
            limit: Maximum number of records to return.
            offset: Number of records to skip.
            
        Returns:
            list: List of expense records.
        """
        query = '''
            SELECT * FROM expenses
            ORDER BY expiry_date ASC, purchase_date DESC
            LIMIT ? OFFSET ?
        '''
        return self.db.execute_query(query, (limit, offset))
    
    def get_expense_by_id(self, expense_id):
        """Get an expense by ID.
        
        Args:
            expense_id: Expense ID.
            
        Returns:
            dict: Expense record or None if not found.
        """
        result = self.db.execute_query(
            'SELECT * FROM expenses WHERE id = ?',
            (expense_id,)
        )
        return result[0] if result else None
    
    def delete_expense(self, expense_id):
        """Delete an expense by ID.
        
        Args:
            expense_id: Expense ID.
            
        Returns:
            bool: True if deleted successfully.
        """
        conn = self.db.get_connection()
        conn.execute('DELETE FROM expenses WHERE id = ?', (expense_id,))
        conn.close()
        return True
    
    def get_total_expenses(self, currency='EUR'):
        """Get total expenses for a specific currency.
        
        Args:
            currency: Currency code to filter by.
            
        Returns:
            float: Total expense amount.
        """
        result = self.db.execute_query(
            'SELECT SUM(price) as total FROM expenses WHERE currency = ?',
            (currency,)
        )
        
        return result[0]['total'] if result and result[0]['total'] else 0.0
    
    def get_expenses_by_category(self):
        """Get total expenses grouped by category.
        
        Returns:
            list: List of category and total expense records.
        """
        return self.db.execute_query('''
            SELECT category, COUNT(*) as count, SUM(price) as total
            FROM expenses
            WHERE category IS NOT NULL
            GROUP BY category
            ORDER BY total DESC
        ''')
    
    def get_expiring_soon(self, days=30):
        """Get expenses expiring within specified days.
        
        Args:
            days: Number of days to look ahead (default: 30).
            
        Returns:
            list: List of expense records expiring soon.
        """
        query = '''
            SELECT * FROM expenses
            WHERE expiry_date <= date_add(CURRENT_DATE, INTERVAL ? DAY)
            AND expiry_date >= CURRENT_DATE
            ORDER BY expiry_date ASC
        '''
        return self.db.execute_query(query, (days,))
