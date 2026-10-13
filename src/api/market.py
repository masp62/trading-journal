"""API routes for external market data."""

from datetime import datetime, UTC

from fastapi import APIRouter, HTTPException, Query

from api.models import (
    MarketIndexComparisonResponse,
    MarketIndexError,
    MarketIndexQuote,
)
from services.market_data_service import MarketDataService

router = APIRouter(prefix="/market", tags=["Market"])


@router.get("/indices", response_model=MarketIndexComparisonResponse)
async def get_indices_comparison(
    range: str = Query("1d", description="Yahoo chart range: 1d, 5d, 1wk, 1mo, 3mo, 6mo"),
):
    """Get normalized quote snapshots for all configured market indices."""
    try:
        service = MarketDataService()
        indices, errors = service.get_us_indices_snapshot(requested_range=range)

        return MarketIndexComparisonResponse(
            source=service.source_name,
            updated_at=datetime.now(UTC).isoformat(),
            selected_range=range,
            available_ranges=service.get_supported_ranges(),
            indices=[MarketIndexQuote(**item) for item in indices],
            errors=[MarketIndexError(**item) for item in errors],
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/index", response_model=MarketIndexQuote)
async def get_single_index(
    symbol: str = Query(..., description="Provider symbol, for example ^NDX"),
    name: str = Query(None, description="Display name used in configuration"),
    range: str = Query("1d", description="Yahoo chart range: 1d, 5d, 1wk, 1mo, 3mo, 6mo"),
):
    """Fetch one index row so failed rows can be retried individually."""
    try:
        service = MarketDataService()
        row = service.get_single_index_snapshot(provider_symbol=symbol, name=name, requested_range=range)
        return MarketIndexQuote(**row)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
