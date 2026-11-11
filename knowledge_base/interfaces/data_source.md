# Spec: Market Data Provider Interface Contract

- **Spec ID**: `interface-datasource`
- **Category**: `architecture-interfaces`
- **Status**: Implemented

## 1. Overview
The ShareVal architecture isolates market data ingestion behind an abstract, polymorphic contract (`DataSourceProvider`). This guarantees that external market data vendors (Yahoo Finance, Alpha Vantage, Polygon.io, Bloomberg, SEC EDGAR, or local mocks) can be plugged in or swapped without modifying valuation engines or API controllers.

## 2. Interface Definition (Python Abstract Base Class)

```python
from abc import ABC, abstractmethod
from typing import Optional, List
from pydantic import BaseModel

class StockQuote(BaseModel):
    symbol: str
    company_name: str
    current_price: float
    currency: str = "USD"
    pe_ratio: Optional[float] = None
    pb_ratio: Optional[float] = None
    beta: Optional[float] = None
    fifty_two_week_high: Optional[float] = None
    fifty_two_week_low: Optional[float] = None
    market_cap: Optional[float] = None

class CompanyFinancials(BaseModel):
    symbol: str
    free_cash_flow: float
    diluted_eps: float
    book_value_per_share: float
    shares_outstanding: float
    total_cash: float
    total_debt: float
    annual_dividend: float = 0.0
    dividend_yield: float = 0.0
    revenue_growth_3y: Optional[float] = None
    historical_fcf: List[float] = []

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

class DataSourceProvider(ABC):
    """Abstract interface defining the market data vendor contract."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Provider unique name identifier (e.g. 'mock', 'yahoo', 'polygon')."""
        pass

    @abstractmethod
    async def get_quote(self, symbol: str) -> StockQuote:
        """Fetch current real-time or delayed stock quote."""
        pass

    @abstractmethod
    async def get_financials(self, symbol: str) -> CompanyFinancials:
        """Fetch baseline balance sheet, income statement and cash flows."""
        pass

    @abstractmethod
    async def get_option_chain_summary(self, symbol: str) -> List[OptionContractSummary]:
        """Fetch available options chain samples and implied volatility."""
        pass

    @abstractmethod
    async def get_risk_free_rate(self) -> float:
        """Fetch prevailing 10Y US Treasury yield (e.g. 0.045)."""
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """Verify provider availability."""
        pass
```

## 3. Pluggability & Factory Pattern
The application uses `DataSourceFactory` which resolves providers dynamically:
- Header: `X-Market-Data-Source: yahoo` or `mock`
- Query param: `?source=yahoo`
- Environment default: `DATA_SOURCE_PROVIDER=yahoo` with automatic failover to `mock`.

## 4. How to Add a New Provider
1. Inherit from `DataSourceProvider` in `backend/app/datasources/your_provider.py`.
2. Implement the 5 abstract methods.
3. Register the class in `backend/app/datasources/factory.py`.
