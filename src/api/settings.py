"""API routes for settings management."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from database.db_manager import DatabaseManager

router = APIRouter(prefix="/settings", tags=["Settings"])


class SettingUpdate(BaseModel):
    """Model for updating a setting."""
    value: float = Field(..., description="Setting value")


class SettingResponse(BaseModel):
    """Model for setting response."""
    key: str
    value: float


@router.get("/daily-profit-target", response_model=SettingResponse)
async def get_daily_profit_target():
    """Get the daily profit target setting.
    
    Returns the current daily profit target. If not set in database,
    returns the default value from config (25.0 EUR).
    """
    try:
        db = DatabaseManager()
        
        # Try to get from database
        result = db.execute_query(
            "SELECT value FROM settings WHERE key = 'daily_profit_target'"
        )
        
        if result and len(result) > 0:
            value = float(result[0]['value'])
        else:
            # Return default value
            from utils.config import Config
            config = Config()
            value = config.daily_target_profit
        
        return SettingResponse(key="daily_profit_target", value=value)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/daily-profit-target", response_model=SettingResponse)
async def update_daily_profit_target(setting: SettingUpdate):
    """Update the daily profit target setting.
    
    Args:
        setting: New value for daily profit target
        
    Returns:
        Updated setting
    """
    try:
        db = DatabaseManager()
        conn = db.get_connection()
        
        # Check if setting exists
        result = db.execute_query(
            "SELECT value FROM settings WHERE key = 'daily_profit_target'"
        )
        
        if result and len(result) > 0:
            # Update existing setting
            conn.execute(
                "UPDATE settings SET value = ?, updated_at = CURRENT_TIMESTAMP WHERE key = 'daily_profit_target'",
                (str(setting.value),)
            )
        else:
            # Insert new setting
            conn.execute(
                "INSERT INTO settings (key, value) VALUES (?, ?)",
                ('daily_profit_target', str(setting.value))
            )
        
        conn.close()
        
        return SettingResponse(key="daily_profit_target", value=setting.value)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
