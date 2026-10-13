"""Journal service for managing journal entries."""

from datetime import datetime
from typing import List, Dict, Optional


class JournalService:
    """Service for managing journal entries."""
    
    def __init__(self, db_manager):
        """Initialize journal service.
        
        Args:
            db_manager: DatabaseManager instance.
        """
        self.db = db_manager
    
    def add_entry(self, title: str, content: str, tags: str = '', date: Optional[str] = None) -> int:
        """Add a new journal entry.
        
        Args:
            title: Entry title.
            content: Entry content.
            tags: Comma-separated tags.
            date: Optional date string (YYYY-MM-DD). If not provided, current datetime is used.
            
        Returns:
            int: ID of the inserted entry.
        """
        query = '''
            INSERT INTO journal_entries (timestamp, title, content, tags)
            VALUES (?, ?, ?, ?)
        '''
        if date:
            # If date provided, use it with current time
            try:
                date_obj = datetime.strptime(date, '%Y-%m-%d')
                # Combine provided date with current time
                now = datetime.now()
                timestamp = date_obj.replace(hour=now.hour, minute=now.minute, second=now.second).isoformat()
            except ValueError:
                # If invalid date format, use current datetime
                timestamp = datetime.now().isoformat()
        else:
            timestamp = datetime.now().isoformat()
        params = (timestamp, title, content, tags)
        return self.db.execute_insert(query, params)
    
    def get_recent_entries(self, limit: int = 10) -> List[Dict]:
        """Get recent journal entries.
        
        Args:
            limit: Maximum number of entries to return.
            
        Returns:
            list: List of entry dictionaries.
        """
        query = '''
            SELECT * FROM journal_entries
            ORDER BY timestamp DESC
            LIMIT ?
        '''
        rows = self.db.execute_query(query, (limit,))
        return [dict(row) for row in rows]
    
    def get_entry_by_id(self, entry_id: int) -> Optional[Dict]:
        """Get a journal entry by ID.
        
        Args:
            entry_id: Entry ID.
            
        Returns:
            dict: Entry dictionary or None if not found.
        """
        query = 'SELECT * FROM journal_entries WHERE id = ?'
        rows = self.db.execute_query(query, (entry_id,))
        return dict(rows[0]) if rows else None
    
    def search_by_tag(self, tag: str) -> List[Dict]:
        """Search journal entries by tag.
        
        Args:
            tag: Tag to search for.
            
        Returns:
            list: List of matching entry dictionaries.
        """
        query = '''
            SELECT * FROM journal_entries
            WHERE tags LIKE ?
            ORDER BY timestamp DESC
        '''
        rows = self.db.execute_query(query, (f'%{tag}%',))
        return [dict(row) for row in rows]
    
    def delete_entry(self, entry_id: int) -> bool:
        """Delete a journal entry by ID.
        
        Args:
            entry_id: Entry ID.
            
        Returns:
            bool: True if deleted successfully.
        """
        query = 'DELETE FROM journal_entries WHERE id = ?'
        self.db.execute_update(query, (entry_id,))
        return True
