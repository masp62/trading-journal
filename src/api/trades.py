from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse
from api.models import TradeCreate, TradeResponse, MessageResponse
from database.db_manager import DatabaseManager
from services.trade_service import TradeService
import csv
import io

router = APIRouter(prefix="/trades", tags=["Trades"])


@router.post("/", response_model=MessageResponse, status_code=201)
async def create_trade(trade: TradeCreate):
    """Create a new trade (Trading212 format)."""
    try:
        # Instrument code mapping
        instrument_code_mapping = {
            '#NQ': 'USA Tech 100',
            '#AX': 'Germany40'
        }
        
        db = DatabaseManager()
        trade_service = TradeService(db)
        
        # Check if trade already exists
        order_number_id = trade.orderNumber.id
        if order_number_id and trade_service.exists_by_order_number_id(order_number_id):
            raise HTTPException(status_code=409, detail="Trade with this order number ID already exists")
        
        # Extract and map code
        code = trade.code
        if code[:3] in instrument_code_mapping:
            code = instrument_code_mapping.get(code[:3])
        
        # Map direction
        direction = trade.direction
        if direction == 'buy':
            action = 'BUY'
        elif direction == 'sell':
            action = 'SELL'
        else:
            action = direction.upper()
        
        # Extract event number
        event_number = trade.eventNumber.name if trade.eventNumber else ''
        
        # Build notes
        notes = f"P/L: {trade.resultAfterFxFeeAccountCurrency:.2f} | Opened: {trade.openingTime[:19]} | Closed: {trade.time[:19]}"
        
        trade_id = trade_service.add_trade(
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
            realised_profit_loss_instrument_currency=trade.realisedProfitLossInstrumentCurrency,
            net_result_account_currency=trade.netResultAccountCurrency,
            instrument_currency=trade.instrumentCurrency,
            event_type=trade.eventType,
            event_number=event_number,
            order_number_name=trade.orderNumber.name,
            order_number_id=order_number_id,
            notes=notes
        )
        
        return MessageResponse(message="Trade created successfully", id=trade_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/")
async def get_trades(
    limit: int = Query(10, ge=1, le=1000, description="Number of trades to return"),
    include_overnight: bool = Query(True, description="Include overnight fees"),
    format: str = Query("json", pattern="^(json|csv)$", description="Response format (json or csv)"),
    symbol: str = Query(None, description="Filter by symbol/instrument (partial match)"),
    action: str = Query(None, description="Filter by action (BUY or SELL)"),
    from_date: str = Query(None, description="Filter from date (YYYY-MM-DD)"),
    to_date: str = Query(None, description="Filter to date (YYYY-MM-DD)"),
    min_profit: float = Query(None, description="Filter by minimum P/L"),
    max_profit: float = Query(None, description="Filter by maximum P/L"),
    offset: int = Query(0, ge=0, description="Number of trades to skip for pagination")
):
    """Get recent trades with optional filters in JSON or CSV format."""
    try:
        # Validate action if provided
        if action and action.upper() not in ['BUY', 'SELL']:
            raise HTTPException(status_code=400, detail="Action must be 'BUY' or 'SELL'")
        
        # Validate dates if provided
        if from_date:
            try:
                import re
                if not re.match(r'^\d{4}-\d{2}-\d{2}$', from_date):
                    raise ValueError("Invalid date format")
            except:
                raise HTTPException(status_code=400, detail="from_date must be in format YYYY-MM-DD")
        
        if to_date:
            try:
                import re
                if not re.match(r'^\d{4}-\d{2}-\d{2}$', to_date):
                    raise ValueError("Invalid date format")
            except:
                raise HTTPException(status_code=400, detail="to_date must be in format YYYY-MM-DD")
        
        db = DatabaseManager()
        trade_service = TradeService(db)
        
        trades = trade_service.get_recent_trades(
            limit=limit, 
            include_overnight=include_overnight,
            symbol=symbol,
            action=action,
            from_date=from_date,
            to_date=to_date,
            min_profit=min_profit,
            max_profit=max_profit,
            offset=offset
        )
        
        if format == "csv":
            # Generate CSV
            output = io.StringIO()
            if trades:
                # Get all unique keys from trades
                fieldnames = list(trades[0].keys())
                writer = csv.DictWriter(output, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(trades)
            
            csv_content = output.getvalue()
            output.close()
            
            return StreamingResponse(
                iter([csv_content]),
                media_type="text/csv",
                headers={"Content-Disposition": "attachment; filename=trades.csv"}
            )
        else:
            # Return JSON (default)
            return [TradeResponse(**trade) for trade in trades]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{trade_id}", response_model=TradeResponse)
async def get_trade(trade_id: int):
    """Get a specific trade by ID."""
    try:
        db = DatabaseManager()
        trade_service = TradeService(db)
        
        trade = trade_service.get_trade_by_id(trade_id)
        if trade is None:
            raise HTTPException(status_code=404, detail="Trade not found")
        
        # Add overnight fees
        trade['overnight_fees_total'] = trade_service.get_overnight_fees_total_for_trade(
            trade.get('order_number_name')
        )
        
        return TradeResponse(**trade)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/by-order/{order_number_name}", response_model=TradeResponse)
async def get_trade_by_order_number(order_number_name: str):
    """Get a specific trade by order number name (Position ID)."""
    try:
        db = DatabaseManager()
        trade_service = TradeService(db)
        
        # Search for trade by order_number_name
        result = db.execute_query(
            "SELECT * FROM trades WHERE order_number_name = ? LIMIT 1",
            (order_number_name,)
        )
        
        if not result or len(result) == 0:
            raise HTTPException(status_code=404, detail="Trade not found for this Position ID")
        
        trade = result[0]
        
        # Add overnight fees
        trade['overnight_fees_total'] = trade_service.get_overnight_fees_total_for_trade(
            trade.get('order_number_name')
        )
        
        return TradeResponse(**trade)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{trade_id}", response_model=MessageResponse)
async def delete_trade(trade_id: int):
    """Delete a trade by ID."""
    try:
        db = DatabaseManager()
        trade_service = TradeService(db)
        
        # Check if trade exists
        trade = trade_service.get_trade_by_id(trade_id)
        if trade is None:
            raise HTTPException(status_code=404, detail="Trade not found")
        
        # Delete trade
        success = trade_service.delete_trade(trade_id)
        if success:
            return MessageResponse(message="Trade deleted successfully", id=trade_id)
        else:
            raise HTTPException(status_code=500, detail="Failed to delete trade")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/overnight-fees/{order_number_name}")
async def get_overnight_fees_for_trade(order_number_name: str):
    """Get all overnight fees for a trade by order_number_name, sorted descending."""
    try:
        db = DatabaseManager()
        trade_service = TradeService(db)
        fees = trade_service.get_overnight_fees_for_trade(order_number_name)
        # Sort descending by timestamp
        fees_sorted = sorted(fees, key=lambda x: x['timestamp'], reverse=True)
        return fees_sorted
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
