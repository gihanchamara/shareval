from abc import ABC, abstractmethod
from typing import List, Optional
from backend.app.schemas.market_data import StockQuote, CompanyFinancials, OptionContractSummary

class DataSourceProvider(ABC):
    """
    Abstract interface for financial market data providers.
    All data sources (Yahoo Finance, Alpha Vantage, Polygon.io, Mock, etc.)
    must implement this interface to be seamlessly pluggable into ShareVal.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique provider identifier (e.g. 'mock', 'yahoo')."""
        pass

    @abstractmethod
    async def get_quote(self, symbol: str) -> StockQuote:
        """Retrieve latest market quote for a stock."""
        pass

    @abstractmethod
    async def get_financials(self, symbol: str) -> CompanyFinancials:
        """Retrieve fundamental financial metrics (FCF, EPS, BVPS, Debt, Cash)."""
        pass

    @abstractmethod
    async def get_option_chain_summary(self, symbol: str) -> List[OptionContractSummary]:
        """Retrieve option chain samples and pricing across strikes."""
        pass

    @abstractmethod
    async def get_risk_free_rate(self) -> float:
        """Retrieve prevailing risk-free benchmark rate (e.g. US 10Y Treasury)."""
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """Check if provider connection is healthy."""
        pass
