"""API routes for importing Trading212 data."""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Union, List, Optional
from pydantic import BaseModel, Field, field_validator
from fastapi import APIRouter, HTTPException, Body
from database.db_manager import DatabaseManager
from services.trade_service import TradeService
from services.overnight_service import OvernightService
from api.models import ImportResponse

router = APIRouter(prefix="/import", tags=["Import"])


class OrderNumber(BaseModel):
    """Order number details from Trading212."""
    name: str
    link: Optional[str] = None
    id: str
    frontend: Optional[str] = None
    positionId: Optional[str] = None


class EventNumber(BaseModel):
    """Event number details from Trading212."""
    name: str
    id: str


class Trading212Trade(BaseModel):
    """Trading212 trade format (old export format)."""
    direction: str
    code: str
    quantity: float
    orderNumber: OrderNumber
    price: float
    closePrice: float
    resultGross: float
    realisedProfitLossAccountCurrency: float
    resultNet: float
    eventNumber: Optional[EventNumber] = None
    eventType: str
    time: str
    openingTime: str
    fxFee: float
    resultAfterFxFeeAccountCurrency: float
    instrumentCurrency: str
    accountCurrency: str
    netResultAccountCurrency: float
    realisedProfitLossInstrumentCurrency: Optional[float] = None
    instrumentToAccountConversionRate: Optional[float] = None
    
    @field_validator('quantity', 'price', 'closePrice', 'resultGross', 'realisedProfitLossAccountCurrency', 
                     'resultNet', 'fxFee', 'resultAfterFxFeeAccountCurrency',
                     'netResultAccountCurrency', 'realisedProfitLossInstrumentCurrency',
                     'instrumentToAccountConversionRate', mode='before')
    @classmethod
    def convert_string_to_float(cls, v):
        """Convert string numbers to float."""
        if v is None:
            return None
        if isinstance(v, str):
            return float(v)
        return v


class Trading212TradeNew(BaseModel):
    """Trading212 trade format (new export format 2026)."""
    closedPositionId: str
    positionUid: str
    orderId: str
    quantity: float
    price: float
    closePrice: float
    resultAfterFxFeeAccountCurrency: float
    code: str
    direction: str
    accountCurrency: str
    time: str
    
    @field_validator('quantity', 'price', 'closePrice', 'resultAfterFxFeeAccountCurrency', mode='before')
    @classmethod
    def convert_string_to_float(cls, v):
        """Convert string numbers to float."""
        if v is None:
            return None
        if isinstance(v, str):
            return float(v)
        return v


class TradesImportPayloadOld(BaseModel):
    """Payload for importing trades from Trading212 export (old format)."""
    sum: Optional[str] = None
    accountCurrency: Optional[str] = None
    data: List[Trading212Trade]


class TradesImportPayloadNew(BaseModel):
    """Payload for importing trades from Trading212 export (new format 2026)."""
    total: Optional[float] = None
    totalSize: Optional[int] = None
    accountCurrency: Optional[str] = None
    sum: Optional[str] = None  # Sometimes still present
    data: List[Trading212TradeNew]


class OvernightOrderNumber(BaseModel):
    """Order number details for overnight fees from Trading212."""
    name: str
    link: Optional[str] = None
    id: str
    frontend: Optional[str] = None


class Trading212OvernightFee(BaseModel):
    """Trading212 overnight fee format."""
    direction: str
    code: str
    quantity: float
    orderNumber: OvernightOrderNumber
    interest: float
    time: str
    id: str
    accountCurrency: str
    instrumentCurrency: str
    
    @field_validator('quantity', 'interest', mode='before')
    @classmethod
    def convert_string_to_float(cls, v):
        """Convert string numbers to float."""
        if v is None:
            return None
        if isinstance(v, str):
            return float(v)
        return v


class OvernightFeesImportPayload(BaseModel):
    """Payload for importing overnight fees from Trading212 export."""
    sum: Optional[str] = None
    accountCurrency: Optional[str] = None
    data: List[Trading212OvernightFee]


@router.post("/trades", response_model=ImportResponse)
async def import_trades_json(
    payload: Union[
        TradesImportPayloadOld,
        TradesImportPayloadNew,
        List[Union[Trading212Trade, Trading212TradeNew]],
        Trading212Trade,
        Trading212TradeNew,
        Dict[str, Any]
    ] = Body(
        ...,
        description="JSON data containing Trading212 trades",
        examples={
            "new_format_2026": {
                "summary": "New Format (2026)",
                "description": "Trading212 export format from 2026 onwards",
                "value": {
                    "total": 100.50,
                    "accountCurrency": "EUR",
                    "totalSize": 0,
                    "data": [{
                        "closedPositionId": "46213356082",
                        "positionUid": "5d5f68d6-5f75-4d35-8992-001f9bd75ea7",
                        "orderId": "46213355553",
                        "quantity": 0.15,
                        "price": 25082.61,
                        "closePrice": 25094.67,
                        "resultAfterFxFeeAccountCurrency": 1.52,
                        "code": "#NQMAR26",
                        "direction": "buy",
                        "accountCurrency": "EUR",
                        "time": "2026-02-06T21:34:57.234173+02:00"
                    }]
                }
            },
            "old_format": {
                "summary": "Old Format (pre-2026)",
                "description": "Trading212 export format before 2026",
                "value": {
                    "sum": "100.50",
                    "accountCurrency": "EUR",
                    "data": [{
                        "direction": "sell",
                        "code": "NVDA",
                        "quantity": 1.0,
                        "orderNumber": {
                            "name": "POS29013698894",
                            "link": "positionHistory/4b5b616f-429e-46db-a62d-fdaf16864c0d",
                            "id": "4b5b616f-429e-46db-a62d-fdaf16864c0d",
                            "frontend": "SYSTEM",
                            "positionId": "29013698894"
                        },
                        "price": "111.88",
                        "closePrice": "112.3",
                        "resultGross": "-0.40",
                        "realisedProfitLossAccountCurrency": "-0.4",
                        "resultNet": "-0.40",
                        "eventType": "closed",
                        "time": "2025-03-04T17:12:17.000+02:00",
                        "openingTime": "2025-03-04T17:06:25.000+02:00",
                        "fxFee": "0",
                        "resultAfterFxFeeAccountCurrency": "-0.4",
                        "instrumentCurrency": "USD",
                        "accountCurrency": "EUR",
                        "netResultAccountCurrency": "-0.4"
                    }]
                }
            }
        }
    )
):
    """Import trades from Trading212 JSON data.
    
    Supports multiple input formats:
    - **New Format (2026)**: {"total": ..., "accountCurrency": "EUR", "data": [...]}
    - **Old Format (pre-2026)**: {"sum": "...", "accountCurrency": "EUR", "data": [...]}
    - **Direct array**: [{...}, {...}]
    - **Single trade**: {...}
    
    The API automatically detects the format based on the fields present.
    """
    try:
        # Extract trades from different payload formats
        file_trades = []
        
        # Convert to dict if it's a Pydantic model
        if isinstance(payload, (TradesImportPayloadOld, TradesImportPayloadNew)):
            raw_data = payload.data
        elif isinstance(payload, dict):
            if 'data' in payload:
                # Trading212 export format (both old and new)
                raw_data = payload['data']
            elif 'closedPositionId' in payload or 'orderNumber' in payload:
                # Single trade object
                raw_data = [payload]
            else:
                raise HTTPException(status_code=400, detail="Invalid payload format")
        elif isinstance(payload, list):
            # Direct array of trades
            raw_data = payload
        elif isinstance(payload, (Trading212Trade, Trading212TradeNew)):
            # Single Pydantic trade object
            raw_data = [payload]
        else:
            raise HTTPException(status_code=400, detail="Invalid payload format")
        
        # Parse each trade based on its structure
        for trade_item in raw_data:
            # Convert Pydantic models to dict for uniform handling
            if isinstance(trade_item, (Trading212Trade, Trading212TradeNew)):
                file_trades.append(trade_item)
            elif isinstance(trade_item, dict):
                if 'closedPositionId' in trade_item:
                    # New format
                    try:
                        trade = Trading212TradeNew(**trade_item)
                        file_trades.append(trade)
                    except Exception as e:
                        raise HTTPException(status_code=422, detail=f"Invalid new format trade: {str(e)}")
                elif 'orderNumber' in trade_item:
                    # Old format
                    try:
                        trade = Trading212Trade(**trade_item)
                        file_trades.append(trade)
                    except Exception as e:
                        raise HTTPException(status_code=422, detail=f"Invalid old format trade: {str(e)}")
                else:
                    raise HTTPException(status_code=422, detail="Trade must have either 'closedPositionId' (new format) or 'orderNumber' (old format)")
            else:
                raise HTTPException(status_code=422, detail=f"Unexpected trade type: {type(trade_item)}")
        
        if not file_trades:
            raise HTTPException(status_code=400, detail="No trades found in payload")
        
        # Instrument code mapping
        instrument_code_mapping = {
            '#NQ': 'USA Tech 100',
            '#AX': 'Germany40'
        }
        
        # Initialize services
        db = DatabaseManager()
        trade_service = TradeService(db)
        
        # Counters
        imported_count = 0
        duplicate_count = 0
        archived_count = 0
        skipped_count = 0
        
        # Create archive base directory
        archive_base = Path(__file__).parent.parent.parent / "archive" / "trades"
        
        # Process each trade
        for trade in file_trades:
            try:
                # Detect trade format and extract data accordingly
                if isinstance(trade, Trading212TradeNew):
                    # New format (2026)
                    order_number_id = trade.positionUid
                    order_number_name = trade.closedPositionId
                    
                    # Check if trade already exists
                    if order_number_id and trade_service.exists_by_order_number_id(order_number_id):
                        duplicate_count += 1
                        continue
                    
                    # Extract and map code
                    code = trade.code
                    if code[:3] in instrument_code_mapping:
                        code = instrument_code_mapping.get(code[:3])
                    
                    # Map direction
                    action = trade.direction.upper()
                    
                    # Build notes
                    notes = f"P/L: {trade.resultAfterFxFeeAccountCurrency:.2f} | Closed: {trade.time[:19]}"
                    
                    # Add trade with available fields only
                    trade_service.add_trade(
                        symbol=code,
                        action=action,
                        quantity=trade.quantity,
                        price=trade.price,
                        close_price=trade.closePrice,
                        timestamp=trade.time,
                        opening_time=None,  # Not available in new format
                        result_gross=trade.resultAfterFxFeeAccountCurrency,  # Use as approximation
                        result_net=trade.resultAfterFxFeeAccountCurrency,
                        fx_fee=0,  # Not available in new format
                        result_after_fx_fee=trade.resultAfterFxFeeAccountCurrency,
                        realised_profit_loss_account_currency=trade.resultAfterFxFeeAccountCurrency,
                        realised_profit_loss_instrument_currency=0,
                        net_result_account_currency=trade.resultAfterFxFeeAccountCurrency,
                        instrument_currency=trade.accountCurrency,
                        event_type="closed",
                        event_number="",
                        order_number_name=order_number_name,
                        order_number_id=order_number_id,
                        notes=notes
                    )
                    imported_count += 1
                    
                else:
                    # Old format (pre-2026)
                    order_number_id = trade.orderNumber.id
                    
                    # Check if trade already exists
                    if order_number_id and trade_service.exists_by_order_number_id(order_number_id):
                        duplicate_count += 1
                        continue
                    
                    # Extract and map code
                    code = trade.code
                    if code[:3] in instrument_code_mapping:
                        code = instrument_code_mapping.get(code[:3])
                    
                    # Map direction
                    if trade.direction == 'buy':
                        action = 'BUY'
                    elif trade.direction == 'sell':
                        action = 'SELL'
                    else:
                        action = trade.direction.upper()
                    
                    # Extract event number
                    event_number = trade.eventNumber.name if trade.eventNumber else ''
                    
                    # Build notes with additional information
                    notes = f"P/L: {trade.resultAfterFxFeeAccountCurrency:.2f} | Opened: {trade.openingTime[:19]} | Closed: {trade.time[:19]}"
                    
                    # Add trade to database with all fields
                    trade_service.add_trade(
                        symbol=code,
                        action=action,
                        quantity=trade.quantity,
                        price=trade.price,
                        close_price=trade.closePrice,
                        timestamp=trade.time,
                        opening_time=trade.openingTime,
                        result_gross=trade.resultGross,
                        result_net=trade.resultNet,
                        fx_fee=trade.fxFee,
                        result_after_fx_fee=trade.resultAfterFxFeeAccountCurrency,
                        realised_profit_loss_account_currency=trade.realisedProfitLossAccountCurrency,
                        realised_profit_loss_instrument_currency=trade.realisedProfitLossInstrumentCurrency or 0,
                        net_result_account_currency=trade.netResultAccountCurrency,
                        instrument_currency=trade.instrumentCurrency,
                        event_type=trade.eventType,
                        event_number=event_number,
                        order_number_name=trade.orderNumber.name,
                        order_number_id=order_number_id,
                        notes=notes
                    )
                    imported_count += 1
                
                # Archive individual trade as JSON
                try:
                    # Parse timestamp to extract year and month
                    trade_datetime = datetime.fromisoformat(trade.time.replace('+02:00', '+00:00').replace('+03:00', '+00:00'))
                    year = trade_datetime.strftime('%Y')
                    month = trade_datetime.strftime('%m')
                    
                    # Create directory structure: archive/trades/YYYY/MM/
                    archive_dir = archive_base / year / month
                    archive_dir.mkdir(parents=True, exist_ok=True)
                    
                    # Create filename: time_orderName.json
                    # Format time without milliseconds and timezone: YYYY-MM-DDTHH-MM-SS
                    time_for_filename = trade_datetime.strftime('%Y-%m-%dT%H-%M-%S')
                    filename = f"{time_for_filename}_{order_number_name}.json"
                    
                    # Save individual trade JSON
                    archive_path = archive_dir / filename
                    with open(archive_path, 'w', encoding='utf-8') as f:
                        json.dump(trade.dict(), f, indent=2, ensure_ascii=False)
                    
                    archived_count += 1
                except Exception:
                    # Archiving error is not critical, continue with import
                    pass
                
            except Exception as e:
                skipped_count += 1
                continue
        
        return ImportResponse(
            imported=imported_count,
            duplicates=duplicate_count,
            archived=archived_count,
            skipped=skipped_count
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/overnight", response_model=ImportResponse)
async def import_overnight_json(payload: Union[OvernightFeesImportPayload, List[Trading212OvernightFee], Trading212OvernightFee] = Body(..., description="JSON data containing Trading212 overnight fees")):
    """Import overnight fees from Trading212 JSON data.
    
    Accepts either:
    - Trading212 export format: {"sum": "...", "accountCurrency": "EUR", "data": [...]}
    - Direct array of overnight fees: [{...}, {...}]
    - Single overnight fee object: {...}
    
    Overnight fees will be imported into the database and archived to archive/overnight/YYYY/MM/.
    """
    try:
        # Extract overnight fees from different payload formats
        file_records = []
        
        if isinstance(payload, list):
            # Direct array of overnight fees
            file_records = payload
        elif isinstance(payload, Trading212OvernightFee):
            # Single overnight fee object
            file_records = [payload]
        elif isinstance(payload, OvernightFeesImportPayload):
            # Trading212 export format with data array
            file_records = payload.data
        
        if not file_records:
            raise HTTPException(status_code=400, detail="No overnight fees found in payload")
        
        # Instrument code mapping
        instrument_code_mapping = {
            '#NQ': 'USA Tech 100',
            '#AX': 'Germany40'
        }
        
        # Initialize services
        db = DatabaseManager()
        overnight_service = OvernightService(db)
        
        # Counters
        imported_count = 0
        duplicate_count = 0
        archived_count = 0
        skipped_count = 0
        
        # Create archive base directory
        archive_base = Path(__file__).parent.parent.parent / "archive" / "overnight"
        
        # Process each overnight fee record
        for record in file_records:
            try:
                # Extract external ID
                order_number_id = record.id
                
                # Check if record already exists
                if order_number_id and overnight_service.exists_by_order_number_id(order_number_id):
                    duplicate_count += 1
                    continue
                
                # Extract and map code
                code = record.code
                if code[:3] in instrument_code_mapping:
                    code = instrument_code_mapping.get(code[:3])
                
                # Map direction
                direction = record.direction.upper()
                
                # Add overnight fee to database
                overnight_service.add_overnight_fee(
                    timestamp=record.time,
                    symbol=code,
                    direction=direction,
                    quantity=record.quantity,
                    interest=record.interest,
                    instrument_currency=record.instrumentCurrency,
                    order_number_id=order_number_id,
                    order_number_name=record.orderNumber.name
                )
                imported_count += 1
                
                # Archive individual overnight fee as JSON
                try:
                    # Parse timestamp to extract year and month
                    fee_datetime = datetime.fromisoformat(record.time.replace('+02:00', '+00:00').replace('+03:00', '+00:00'))
                    year = fee_datetime.strftime('%Y')
                    month = fee_datetime.strftime('%m')
                    
                    # Create directory structure: archive/overnight/YYYY/MM/
                    archive_dir = archive_base / year / month
                    archive_dir.mkdir(parents=True, exist_ok=True)
                    
                    # Create filename: time_orderName.json
                    # Format time without milliseconds and timezone: YYYY-MM-DDTHH-MM-SS
                    time_for_filename = fee_datetime.strftime('%Y-%m-%dT%H-%M-%S')
                    filename = f"{time_for_filename}_{record.orderNumber.name}.json"
                    
                    # Save individual overnight fee JSON
                    archive_path = archive_dir / filename
                    with open(archive_path, 'w', encoding='utf-8') as f:
                        json.dump(record.dict(), f, indent=2, ensure_ascii=False)
                    
                    archived_count += 1
                except Exception:
                    # Archiving error is not critical, continue with import
                    pass
                
            except Exception as e:
                skipped_count += 1
                continue
        
        return ImportResponse(
            imported=imported_count,
            duplicates=duplicate_count,
            archived=archived_count,
            skipped=skipped_count
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
