"""Pydantic models for API requests and responses."""

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


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


class TradeCreate(BaseModel):
    """Model for creating a new trade (Trading212 format)."""
    direction: str = Field(..., description="Trade direction (buy or sell)")
    code: str = Field(..., description="Trading symbol code")
    quantity: float = Field(..., gt=0, description="Number of shares/contracts")
    orderNumber: OrderNumber = Field(..., description="Order number details")
    price: float = Field(..., gt=0, description="Entry price")
    closePrice: float = Field(..., description="Closing price")
    resultGross: float = Field(..., description="Gross result")
    realisedProfitLossAccountCurrency: float = Field(..., description="Realised P/L in account currency")
    resultNet: float = Field(..., description="Net result")
    eventNumber: Optional[EventNumber] = Field(None, description="Event number details")
    eventType: str = Field(..., description="Event type")
    time: str = Field(..., description="Closing timestamp")
    openingTime: str = Field(..., description="Opening timestamp")
    fxFee: float = Field(..., description="FX fee")
    resultAfterFxFeeAccountCurrency: float = Field(..., description="Result after FX fee")
    instrumentCurrency: str = Field(..., description="Instrument currency")
    accountCurrency: str = Field(..., description="Account currency")
    netResultAccountCurrency: float = Field(..., description="Net result in account currency")
    realisedProfitLossInstrumentCurrency: Optional[float] = Field(None, description="Realised P/L in instrument currency")


class TradeResponse(BaseModel):
    """Model for trade response."""
    id: int
    symbol: str
    action: str
    quantity: float
    price: float
    notes: Optional[str] = ""
    timestamp: str
    opening_time: Optional[str] = None
    close_price: Optional[float] = None
    result_gross: Optional[float] = None
    result_net: Optional[float] = None
    fx_fee: Optional[float] = None
    result_after_fx_fee: Optional[float] = None
    overnight_fees_total: Optional[float] = None
    instrument_currency: Optional[str] = None
    order_number_name: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


class JournalEntryCreate(BaseModel):
    """Model for creating a journal entry."""
    title: str = Field(..., min_length=1, description="Entry title")
    content: str = Field(..., min_length=1, description="Entry content")
    tags: Optional[str] = Field("", description="Comma-separated tags")
    date: Optional[str] = Field(None, description="Entry date (YYYY-MM-DD). If not provided, current date is used.")


class JournalEntryResponse(BaseModel):
    """Model for journal entry response."""
    id: int
    timestamp: str
    title: str
    content: str
    tags: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


class AnalyticsResponse(BaseModel):
    """Model for analytics response."""
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    total_profit: float
    total_loss: float
    net_profit: float
    average_win: float
    average_loss: float
    profit_factor: Optional[float] = None
    largest_win: float
    largest_loss: float
    total_overnight_fees: float = Field(..., description="Total overnight fees across all trades")


class MessageResponse(BaseModel):
    """Generic message response."""
    message: str
    id: Optional[int] = None


class OvernightOrderNumber(BaseModel):
    """Order number details for overnight fees."""
    name: str
    link: Optional[str] = None
    id: str
    frontend: Optional[str] = None


class OvernightFeeCreate(BaseModel):
    """Model for creating an overnight fee (Trading212 format)."""
    direction: str = Field(..., description="Direction (BUY or SELL)")
    code: str = Field(..., description="Trading symbol code")
    quantity: float = Field(..., gt=0, description="Position quantity")
    orderNumber: OvernightOrderNumber = Field(..., description="Order number details")
    interest: float = Field(..., description="Interest amount (usually negative)")
    time: str = Field(..., description="Timestamp of the overnight fee")
    id: str = Field(..., description="External ID from trading platform")
    accountCurrency: str = Field(..., description="Account currency")
    instrumentCurrency: str = Field(..., description="Instrument currency")


class OvernightFeeResponse(BaseModel):
    """Model for overnight fee response."""
    id: int
    timestamp: str
    symbol: str
    direction: str
    quantity: float
    interest: float
    instrument_currency: Optional[str] = None
    order_number_id: Optional[str] = None
    order_number_name: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


class ImportResponse(BaseModel):
    """Response for import operations."""
    imported: int
    duplicates: int
    archived: int
    skipped: int


class InstrumentStats(BaseModel):
    """Statistics for a trading instrument."""
    symbol: str
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    total_pnl: float
    avg_pnl: float
    largest_win: float
    largest_loss: float
    avg_price: float
    overnight_fees: float
    net_total: float


class InstrumentAggregationResponse(BaseModel):
    """Response model for instrument aggregation."""
    instruments: List[InstrumentStats]
    total_instruments: int


class PeriodStats(BaseModel):
    """Statistics for a time period."""
    period: str
    trade_count: int
    total_pnl: float
    avg_pnl: float
    overnight_fees: float
    target_profit: float
    deviation_from_target: float


class PeriodAggregationResponse(BaseModel):
    """Response model for period aggregation."""
    periods: List[PeriodStats]
    total_periods: int
    summary: dict


class ProfitBucket(BaseModel):
    """Profit distribution bucket."""
    range: str = Field(..., description="Bucket range (e.g., '0-5', '5-10')")
    min_value: float = Field(..., description="Minimum value of bucket")
    max_value: Optional[float] = Field(None, description="Maximum value of bucket (None for unbounded)")
    count: int = Field(..., description="Number of trades in this bucket")
    total_profit: float = Field(..., description="Total profit/loss in this bucket")


class ProfitDistributionResponse(BaseModel):
    """Response model for profit distribution histogram."""
    buckets: List[ProfitBucket]
    total_trades: int


class ExpenseCreate(BaseModel):
    """Model for creating an expense."""
    name: str = Field(..., min_length=1, max_length=200, description="Name/description of the expense")
    purchase_date: str = Field(..., description="Purchase date (ISO format: YYYY-MM-DD)")
    expiry_date: str = Field(..., description="Expiry/renewal date (ISO format: YYYY-MM-DD)")
    price: float = Field(..., gt=0, description="Price amount")
    currency: str = Field(default="EUR", description="Currency code (EUR, USD, CHF, etc.)")
    category: Optional[str] = Field(None, max_length=100, description="Category (e.g., TradingView, Broker, Data Feed)")
    notes: Optional[str] = Field(None, max_length=500, description="Additional notes")


class ExpenseResponse(BaseModel):
    """Model for expense response."""
    id: int
    name: str
    purchase_date: str
    expiry_date: str
    price: float
    currency: str
    category: Optional[str] = None
    notes: Optional[str] = None
    created_at: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


class MarketIndexQuote(BaseModel):
    """Normalized quote snapshot for a market index."""
    symbol: str = Field(..., description="Provider symbol")
    name: str = Field(..., description="Display name")
    time: str = Field(..., description="Last market update time (ISO-8601)")
    interval_start_time: Optional[str] = Field(None, description="Start timestamp of the interval used for change")
    interval_end_time: Optional[str] = Field(None, description="End timestamp of the interval used for change")
    last: Optional[float] = Field(None, description="Last traded price")
    prev: Optional[float] = Field(None, description="Previous close")
    high: Optional[float] = Field(None, description="Day high")
    low: Optional[float] = Field(None, description="Day low")
    fifty_two_week_high: Optional[float] = Field(None, description="52-week high")
    fifty_two_week_low: Optional[float] = Field(None, description="52-week low")
    change: Optional[float] = Field(None, description="Absolute price change")
    change_percent: Optional[float] = Field(None, description="Percentage price change")
    error: Optional[str] = Field(None, description="Fetch error for this specific index row")


class MarketIndexError(BaseModel):
    """Error details for an index that could not be fetched."""
    symbol: str
    name: str
    message: str


class MarketIndexComparisonResponse(BaseModel):
    """Response model for the market index comparison endpoint."""
    source: str
    updated_at: str
    selected_range: str = Field(..., description="Applied Yahoo chart range")
    available_ranges: List[str] = Field(default_factory=list, description="Supported Yahoo chart ranges")
    indices: List[MarketIndexQuote]
    errors: List[MarketIndexError] = Field(default_factory=list)
