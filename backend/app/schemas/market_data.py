from pydantic import BaseModel, Field
from typing import Optional, List

class StockQuote(BaseModel):
    symbol: str
    company_name: str
    current_price: float
    currency: str = "USD"
    pe_ratio: Optional[float] = None
    pb_ratio: Optional[float] = None
    beta: Optional[float] = 1.0
    fifty_two_week_high: Optional[float] = None
    fifty_two_week_low: Optional[float] = None
    market_cap: Optional[float] = None
    source: str = "mock"

class CompanyFinancials(BaseModel):
    symbol: str
    company_name: str = ""
    free_cash_flow: float = Field(..., description="Trailing 12-month Free Cash Flow in USD")
    diluted_eps: float = Field(..., description="Trailing 12-month diluted EPS")
    book_value_per_share: float = Field(..., description="Book value per share in USD")
    shares_outstanding: float = Field(..., description="Diluted shares count")
    total_cash: float = Field(default=0.0, description="Cash and short-term liquid investments")
    total_debt: float = Field(default=0.0, description="Short + Long term debt")
    annual_dividend: float = Field(default=0.0, description="Annual dividend per share")
    dividend_yield: float = Field(default=0.0, description="Annual dividend yield fraction")
    revenue_growth_3y: Optional[float] = Field(default=0.08, description="3-year revenue CAGR")
    historical_fcf: List[float] = Field(default_factory=list, description="Historical annual FCFs")
    ebitda: Optional[float] = None
    source: str = "mock"

class OptionContractSummary(BaseModel):
    symbol: str
    expiration_date: str
    days_to_expiry: int
    strike: float
    call_bid: Optional[float] = None
    call_ask: Optional[float] = None
    call_last: Optional[float] = None
    put_bid: Optional[float] = None
    put_ask: Optional[float] = None
    put_last: Optional[float] = None
    implied_volatility: Optional[float] = None
    volume: Optional[int] = None
    open_interest: Optional[int] = None
