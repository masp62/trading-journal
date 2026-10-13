"""Journal entry model."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List


@dataclass
class JournalEntry:
    """Represents a journal entry."""
    
    title: str
    content: str
    timestamp: datetime
    tags: Optional[str] = None
    id: Optional[int] = None
    
    @property
    def tag_list(self) -> List[str]:
        """Get tags as a list."""
        if not self.tags:
            return []
        return [tag.strip() for tag in self.tags.split(',')]
    
    def to_dict(self) -> dict:
        """Convert journal entry to dictionary."""
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat(),
            'title': self.title,
            'content': self.content,
            'tags': self.tags
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'JournalEntry':
        """Create JournalEntry from dictionary."""
        return cls(
            id=data.get('id'),
            timestamp=datetime.fromisoformat(data['timestamp']),
            title=data['title'],
            content=data['content'],
            tags=data.get('tags')
        )
