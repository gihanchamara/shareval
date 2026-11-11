from fastapi import APIRouter, HTTPException, Query, Header
from typing import Optional, List
from backend.app.schemas.market_data import StockQuote, CompanyFinancials, OptionContractSummary
from backend.app.datasources.factory import DataSourceFactory

router = APIRouter(prefix="/market", tags=["Market Data & AutoFill"])

def _resolve_source(source_query: Optional[str], source_header: Optional[str]) -> str:
    return source_query or source_header or "mock"

@router.get("/sources", response_model=dict)
def get_sources():
    """Lists available pluggable data sources."""
    return {
        "available_sources": DataSourceFactory.available_providers(),
        "default": "mock"
    }

@router.get("/quote/{symbol}", response_model=StockQuote)
async def get_stock_quote(
    symbol: str,
    source: Optional[str] = Query(None),
    x_data_source: Optional[str] = Header(None)
):
    """Fetches real-time or simulated market quote for given ticker."""
    provider = DataSourceFactory.get_provider(_resolve_source(source, x_data_source))
    try:
        return await provider.get_quote(symbol)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch quote: {e}")

@router.get("/financials/{symbol}", response_model=CompanyFinancials)
async def get_company_financials(
    symbol: str,
    source: Optional[str] = Query(None),
    x_data_source: Optional[str] = Header(None)
):
    """Fetches balance sheet, earnings, cash flows and dividend metrics for autofill."""
    provider = DataSourceFactory.get_provider(_resolve_source(source, x_data_source))
    try:
        return await provider.get_financials(symbol)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch financials: {e}")

@router.get("/options/{symbol}", response_model=List[OptionContractSummary])
async def get_option_chain_summary(
    symbol: str,
    source: Optional[str] = Query(None),
    x_data_source: Optional[str] = Header(None)
):
    """Fetches sample option contracts and implied volatility for given ticker."""
    provider = DataSourceFactory.get_provider(_resolve_source(source, x_data_source))
    try:
        return await provider.get_option_chain_summary(symbol)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch options chain: {e}")

@router.get("/risk-free-rate", response_model=dict)
async def get_risk_free_rate(
    source: Optional[str] = Query(None),
    x_data_source: Optional[str] = Header(None)
):
    """Fetches prevailing benchmark risk-free rate (e.g. 10Y Treasury)."""
    provider = DataSourceFactory.get_provider(_resolve_source(source, x_data_source))
    try:
        rate = await provider.get_risk_free_rate()
        return {"risk_free_rate": rate, "percentage": round(rate * 100.0, 2)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch risk-free rate: {e}")
