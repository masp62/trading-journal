"""Trade model."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Trade:
    """Represents a single trade."""
    
    symbol: str
    action: str  # 'BUY' or 'SELL'
    quantity: float
    price: float
    timestamp: datetime
    notes: Optional[str] = None
    id: Optional[int] = None
    
    @property
    def total_value(self) -> float:
        """Calculate total value of the trade."""
        return self.quantity * self.price
    
    def to_dict(self) -> dict:
        """Convert trade to dictionary."""
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat(),
            'symbol': self.symbol,
            'action': self.action,
            'quantity': self.quantity,
            'price': self.price,
            'notes': self.notes
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Trade':
        """Create Trade from dictionary."""
        return cls(
            id=data.get('id'),
            timestamp=datetime.fromisoformat(data['timestamp']),
            symbol=data['symbol'],
            action=data['action'],
            quantity=data['quantity'],
            price=data['price'],
            notes=data.get('notes')
        )
