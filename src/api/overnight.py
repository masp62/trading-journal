"""API routes for overnight fees."""

import csv
import io
from typing import List
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse
from database.db_manager import DatabaseManager
from services.overnight_service import OvernightService
from api.models import OvernightFeeCreate, OvernightFeeResponse, MessageResponse

router = APIRouter(prefix="/overnight", tags=["Overnight Fees"])


@router.post("/", response_model=MessageResponse, status_code=201)
async def create_overnight_fee(fee: OvernightFeeCreate):
    """Create a new overnight fee record (Trading212 format)."""
    try:
        # Instrument code mapping
        instrument_code_mapping = {
            '#NQ': 'USA Tech 100',
            '#AX': 'Germany40'
        }
        
        db = DatabaseManager()
        overnight_service = OvernightService(db)
        
        # Check if record already exists
        if fee.id and overnight_service.exists_by_order_number_id(fee.id):
            raise HTTPException(status_code=409, detail="Overnight fee with this ID already exists")
        
        # Extract and map code
        code = fee.code
        if code[:3] in instrument_code_mapping:
            code = instrument_code_mapping.get(code[:3])
        
        # Map direction
        direction = fee.direction.upper()
        
        fee_id = overnight_service.add_overnight_fee(
            timestamp=fee.time,
            symbol=code,
            direction=direction,
            quantity=fee.quantity,
            interest=fee.interest,
            instrument_currency=fee.instrumentCurrency,
            order_number_id=fee.id,
            order_number_name=fee.orderNumber.name
        )
        
        return MessageResponse(message="Overnight fee created successfully", id=fee_id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/")
async def get_overnight_fees(
    limit: int = Query(20, ge=1, le=1000, description="Number of overnight fees to return"),
    offset: int = Query(0, ge=0, description="Number of fees to skip for pagination"),
    format: str = Query("json", pattern="^(json|csv)$", description="Response format (json or csv)")
):
    """Get recent overnight fees in JSON or CSV format."""
    try:
        db = DatabaseManager()
        overnight_service = OvernightService(db)
        
        fees = overnight_service.get_recent_fees(limit=limit, offset=offset)
        
        if format == "csv":
            # Generate CSV
            output = io.StringIO()
            if fees:
                # Get all unique keys from fees
                fieldnames = list(fees[0].keys())
                writer = csv.DictWriter(output, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(fees)
            
            csv_content = output.getvalue()
            output.close()
            
            return StreamingResponse(
                iter([csv_content]),
                media_type="text/csv",
                headers={"Content-Disposition": "attachment; filename=overnight_fees.csv"}
            )
        else:
            # Return JSON (default)
            return [OvernightFeeResponse(**fee) for fee in fees]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{fee_id}", response_model=OvernightFeeResponse)
async def get_overnight_fee(fee_id: int):
    """Get a specific overnight fee by ID."""
    try:
        db = DatabaseManager()
        overnight_service = OvernightService(db)
        
        fee = overnight_service.get_fee_by_id(fee_id)
        if fee is None:
            raise HTTPException(status_code=404, detail="Overnight fee not found")
        
        return OvernightFeeResponse(**fee)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{fee_id}", response_model=MessageResponse)
async def delete_overnight_fee(fee_id: int):
    """Delete an overnight fee by ID."""
    try:
        db = DatabaseManager()
        overnight_service = OvernightService(db)
        
        # Check if fee exists
        fee = overnight_service.get_fee_by_id(fee_id)
        if fee is None:
            raise HTTPException(status_code=404, detail="Overnight fee not found")
        
        # Delete fee
        success = overnight_service.delete_overnight_fee(fee_id)
        if success:
            return MessageResponse(message="Overnight fee deleted successfully", id=fee_id)
        else:
            raise HTTPException(status_code=500, detail="Failed to delete overnight fee")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
