"""API routes for expenses."""

import csv
import io
from datetime import datetime
from typing import List
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse
from database.db_manager import DatabaseManager
from services.expense_service import ExpenseService
from api.models import ExpenseCreate, ExpenseResponse, MessageResponse

router = APIRouter(prefix="/expenses", tags=["Expenses"])


def _convert_datetime_to_str(expense_dict):
    """Convert datetime objects to ISO format strings."""
    if expense_dict.get('created_at') and isinstance(expense_dict['created_at'], datetime):
        expense_dict['created_at'] = expense_dict['created_at'].isoformat()
    return expense_dict


@router.post("/", response_model=MessageResponse, status_code=201)
async def create_expense(expense: ExpenseCreate):
    """Create a new expense record."""
    try:
        db = DatabaseManager()
        expense_service = ExpenseService(db)
        
        expense_id = expense_service.add_expense(
            name=expense.name,
            purchase_date=expense.purchase_date,
            expiry_date=expense.expiry_date,
            price=expense.price,
            currency=expense.currency,
            category=expense.category,
            notes=expense.notes
        )
        
        return MessageResponse(message="Expense created successfully", id=expense_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/")
async def get_expenses(
    limit: int = Query(50, ge=1, le=1000, description="Number of expenses to return"),
    offset: int = Query(0, ge=0, description="Number of expenses to skip for pagination"),
    format: str = Query("json", pattern="^(json|csv)$", description="Response format (json or csv)")
):
    """Get expenses in JSON or CSV format."""
    try:
        db = DatabaseManager()
        expense_service = ExpenseService(db)
        
        expenses = expense_service.get_all_expenses(limit=limit, offset=offset)
        
        if format == "csv":
            # Generate CSV
            output = io.StringIO()
            if expenses:
                # Get all unique keys from expenses
                fieldnames = list(expenses[0].keys())
                writer = csv.DictWriter(output, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(expenses)
            
            csv_content = output.getvalue()
            output.close()
            
            return StreamingResponse(
                iter([csv_content]),
                media_type="text/csv",
                headers={"Content-Disposition": "attachment; filename=expenses.csv"}
            )
        else:
            # Return JSON (default)
            return [ExpenseResponse(**_convert_datetime_to_str(expense)) for expense in expenses]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{expense_id}", response_model=ExpenseResponse)
async def get_expense(expense_id: int):
    """Get a specific expense by ID."""
    try:
        db = DatabaseManager()
        expense_service = ExpenseService(db)
        
        expense = expense_service.get_expense_by_id(expense_id)
        if expense is None:
            raise HTTPException(status_code=404, detail="Expense not found")
        
        return ExpenseResponse(**_convert_datetime_to_str(expense))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{expense_id}", response_model=MessageResponse)
async def delete_expense(expense_id: int):
    """Delete an expense by ID."""
    try:
        db = DatabaseManager()
        expense_service = ExpenseService(db)
        
        # Check if expense exists
        expense = expense_service.get_expense_by_id(expense_id)
        if expense is None:
            raise HTTPException(status_code=404, detail="Expense not found")
        
        # Delete expense
        success = expense_service.delete_expense(expense_id)
        if success:
            return MessageResponse(message="Expense deleted successfully", id=expense_id)
        else:
            raise HTTPException(status_code=500, detail="Failed to delete expense")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
