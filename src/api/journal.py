"""API routes for journal entries."""

from typing import List
from fastapi import APIRouter, HTTPException, Query
from database.db_manager import DatabaseManager
from services.journal_service import JournalService
from api.models import JournalEntryCreate, JournalEntryResponse, MessageResponse

router = APIRouter(prefix="/journal", tags=["Journal"])


@router.post("/", response_model=MessageResponse, status_code=201)
async def create_entry(entry: JournalEntryCreate):
    """Create a new journal entry."""
    try:
        db = DatabaseManager()
        journal_service = JournalService(db)
        
        entry_id = journal_service.add_entry(
            title=entry.title,
            content=entry.content,
            tags=entry.tags,
            date=entry.date
        )
        
        return MessageResponse(message="Journal entry created successfully", id=entry_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=List[JournalEntryResponse])
async def get_entries(
    limit: int = Query(10, ge=1, le=100, description="Number of entries to return")
):
    """Get recent journal entries."""
    try:
        db = DatabaseManager()
        journal_service = JournalService(db)
        
        entries = journal_service.get_recent_entries(limit=limit)
        return [JournalEntryResponse(**entry) for entry in entries]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{entry_id}", response_model=JournalEntryResponse)
async def get_entry(entry_id: int):
    """Get a specific journal entry by ID."""
    try:
        db = DatabaseManager()
        journal_service = JournalService(db)
        
        entry = journal_service.get_entry_by_id(entry_id)
        if entry is None:
            raise HTTPException(status_code=404, detail="Journal entry not found")
        
        return JournalEntryResponse(**entry)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{entry_id}", response_model=MessageResponse)
async def delete_entry(entry_id: int):
    """Delete a journal entry by ID."""
    try:
        db = DatabaseManager()
        journal_service = JournalService(db)
        
        # Check if entry exists
        entry = journal_service.get_entry_by_id(entry_id)
        if entry is None:
            raise HTTPException(status_code=404, detail="Journal entry not found")
        
        # Delete entry
        success = journal_service.delete_entry(entry_id)
        if success:
            return MessageResponse(message="Journal entry deleted successfully", id=entry_id)
        else:
            raise HTTPException(status_code=500, detail="Failed to delete journal entry")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
