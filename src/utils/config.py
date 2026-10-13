"""Configuration management for Trading Journal."""

import os
from pathlib import Path
from typing import Dict, Any


class Config:
    """Configuration manager."""
    
    # Default configuration
    DEFAULT_CONFIG = {
        'database': {
            'path': 'data/trading_journal.db'
        },
        'display': {
            'max_trades_display': 10,
            'max_journal_display': 5,
            'date_format': '%Y-%m-%d %H:%M:%S'
        },
        'targets': {
            'daily_profit': 25.0  # Target profit per day in EUR
        }
    }
    
    def __init__(self, config_dict: Dict[str, Any] = None):
        """Initialize configuration.
        
        Args:
            config_dict: Optional configuration dictionary.
        """
        self._config = self.DEFAULT_CONFIG.copy()
        if config_dict:
            self._config.update(config_dict)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value.
        
        Args:
            key: Configuration key (supports dot notation).
            default: Default value if key not found.
            
        Returns:
            Configuration value.
        """
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any):
        """Set configuration value.
        
        Args:
            key: Configuration key (supports dot notation).
            value: Value to set.
        """
        keys = key.split('.')
        config = self._config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    @property
    def database_path(self) -> str:
        """Get database path."""
        return self.get('database.path', 'data/trading_journal.db')
    
    @property
    def daily_target_profit(self) -> float:
        """Get daily target profit."""
        return self.get('targets.daily_profit', 50.0)
