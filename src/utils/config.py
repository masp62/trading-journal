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
        },
        'market': {
            'source': 'Yahoo Finance',
            'timeout_seconds': 8,
            'request_delay_seconds': 1.2,
            'max_retries': 2,
            'retry_backoff_seconds': 2.0,
            'cache_ttl_seconds': 30,
            'indices': [
                {'name': 'US Tech 100', 'provider_symbol': '^NDX'},
                {'name': 'Hong Kong 50', 'provider_symbol': '^HSI'},
                {'name': 'AEX', 'provider_symbol': '^AEX'},
                {'name': 'US 500', 'provider_symbol': '^GSPC'},
                {'name': 'Japan 225', 'provider_symbol': '^N225'},
                {'name': 'Euro Stoxx 50', 'provider_symbol': '^STOXX50E'},
                {'name': 'Spain 35', 'provider_symbol': '^IBEX'},
                {'name': 'CAC 40', 'provider_symbol': '^FCHI'},
                {'name': 'ASX 200', 'provider_symbol': '^AXJO'},
                {'name': 'Small Cap 2000', 'provider_symbol': '^RUT'},
                {'name': 'Italy 40', 'provider_symbol': 'FTSEMIB.MI'},
                {'name': 'US 30', 'provider_symbol': '^DJI'},
                {'name': 'Germany 40', 'provider_symbol': '^GDAXI'},
                {'name': 'UK 100', 'provider_symbol': '^FTSE'},
                {'name': 'SMI', 'provider_symbol': '^SSMI'}
            ]
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
