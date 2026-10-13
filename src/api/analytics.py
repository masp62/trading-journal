"""API routes for analytics."""

from fastapi import APIRouter, HTTPException, Query
from database.db_manager import DatabaseManager
from utils.analytics import Analytics
from api.models import AnalyticsResponse, InstrumentAggregationResponse, InstrumentStats, PeriodAggregationResponse, PeriodStats, ProfitDistributionResponse, ProfitBucket

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/", response_model=AnalyticsResponse)
async def get_analytics(
    from_date: str = Query(None, description="Filter from date (YYYY-MM-DD)"),
    to_date: str = Query(None, description="Filter to date (YYYY-MM-DD)")
):
    """Get trading performance analytics."""
    try:
        db = DatabaseManager()
        analytics = Analytics(db)
        
        stats = analytics.get_performance_stats(from_date=from_date, to_date=to_date)
        
        return AnalyticsResponse(
            total_trades=stats['total_trades'],
            winning_trades=stats['winning_trades'],
            losing_trades=stats['losing_trades'],
            win_rate=stats['win_rate'],
            total_profit=stats['total_profit'],
            total_loss=stats['total_loss'],
            net_profit=stats['net_profit'],
            average_win=stats['average_win'],
            average_loss=stats['average_loss'],
            profit_factor=stats.get('profit_factor'),
            largest_win=stats['largest_win'],
            largest_loss=stats['largest_loss'],
            total_overnight_fees=stats['total_overnight_fees']
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/by-instrument", response_model=InstrumentAggregationResponse)
async def get_trades_by_instrument(
    limit: int = Query(None, ge=1, le=100, description="Limit number of instruments to return"),
    from_date: str = Query(None, description="Filter from date (YYYY-MM-DD)"),
    to_date: str = Query(None, description="Filter to date (YYYY-MM-DD)")
):
    """Get trades aggregated by instrument with statistics.
    
    Returns statistics for each trading instrument including:
    - Total number of trades
    - Win rate
    - Total P/L and average P/L
    - Largest win and loss
    - Overnight fees
    - Net total (P/L + overnight fees)
    """
    try:
        db = DatabaseManager()
        analytics = Analytics(db)
        
        instruments = analytics.get_all_instrument_stats(limit=limit, from_date=from_date, to_date=to_date)
        
        return InstrumentAggregationResponse(
            instruments=[InstrumentStats(**inst) for inst in instruments],
            total_instruments=len(instruments)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/by-period", response_model=PeriodAggregationResponse)
async def get_trades_by_period(
    period: str = Query("day", pattern="^(day|week|month|year)$", description="Time period for grouping"),
    limit: int = Query(10, ge=1, le=100, description="Limit number of periods to return")
):
    """Get trades aggregated by time period with target comparison.
    
    Returns statistics for each time period including:
    - Number of trades
    - Total and average P/L
    - Overnight fees
    - Target profit (aggregated based on period)
    - Deviation from target
    """
    try:
        db = DatabaseManager()
        analytics = Analytics(db)
        
        periods = analytics.get_trades_per_period(period=period, limit=limit)
        
        # Calculate summary
        total_trades = sum(p.get('trade_count', 0) for p in periods)
        total_pnl = sum(p.get('total_pnl', 0.0) or 0.0 for p in periods)
        total_overnight = sum(p.get('overnight_fees', 0.0) for p in periods)
        total_combined = total_pnl + total_overnight
        total_target = sum(p.get('target_profit', 0.0) for p in periods)
        total_deviation = sum(p.get('deviation_from_target', 0.0) for p in periods)
        
        summary = {
            'total_trades': total_trades,
            'total_pnl': round(total_pnl, 3),
            'total_overnight_fees': round(total_overnight, 3),
            'total_combined': round(total_combined, 3),
            'total_target': round(total_target, 3),
            'total_deviation': round(total_deviation, 3)
        }
        
        return PeriodAggregationResponse(
            periods=[PeriodStats(**p) for p in periods],
            total_periods=len(periods),
            summary=summary
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/profit-distribution", response_model=ProfitDistributionResponse)
async def get_profit_distribution(
    from_date: str = Query(None, description="Filter from date (YYYY-MM-DD)"),
    to_date: str = Query(None, description="Filter to date (YYYY-MM-DD)")
):
    """Get profit distribution histogram with buckets.
    
    Returns the number of trades in each profit/loss bucket:
    - Negative: < -25, -25 to -10, -10 to -5, -5 to 0
    - Positive: 0 to 5, 5 to 10, 10 to 25, > 25
    """
    try:
        db = DatabaseManager()
        conn = db.get_connection()
        
        # Query all trades with their P/L
        query = """
            SELECT 
                COALESCE(result_net, 0) as pnl
            FROM trades
            WHERE result_net IS NOT NULL
        """
        
        params = []
        if from_date:
            query += " AND DATE(opening_time) >= ?"
            params.append(from_date)
        if to_date:
            query += " AND DATE(opening_time) <= ?"
            params.append(to_date)
        
        result = conn.execute(query, params).fetchall()
        conn.close()
        
        # Define buckets
        buckets_config = [
            {"range": "< -25€", "min": float('-inf'), "max": -25},
            {"range": "-25€ bis -10€", "min": -25, "max": -10},
            {"range": "-10€ bis -5€", "min": -10, "max": -5},
            {"range": "-5€ bis 0€", "min": -5, "max": 0},
            {"range": "0€ bis 5€", "min": 0, "max": 5},
            {"range": "5€ bis 10€", "min": 5, "max": 10},
            {"range": "10€ bis 25€", "min": 10, "max": 25},
            {"range": "> 25€", "min": 25, "max": float('inf')}
        ]
        
        # Initialize bucket counters
        bucket_data = {i: {"count": 0, "total": 0.0} for i in range(len(buckets_config))}
        
        # Categorize trades into buckets
        for row in result:
            pnl = float(row[0])
            for i, bucket in enumerate(buckets_config):
                if bucket["min"] <= pnl < bucket["max"]:
                    bucket_data[i]["count"] += 1
                    bucket_data[i]["total"] += pnl
                    break
        
        # Build response
        buckets = []
        for i, config in enumerate(buckets_config):
            buckets.append(ProfitBucket(
                range=config["range"],
                min_value=config["min"] if config["min"] != float('-inf') else -999999,
                max_value=config["max"] if config["max"] != float('inf') else None,
                count=bucket_data[i]["count"],
                total_profit=round(bucket_data[i]["total"], 2)
            ))
        
        total_trades = sum(b["count"] for b in bucket_data.values())
        
        return ProfitDistributionResponse(
            buckets=buckets,
            total_trades=total_trades
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

