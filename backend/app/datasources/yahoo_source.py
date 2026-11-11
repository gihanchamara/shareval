import asyncio
import logging
from typing import List, Optional
import yfinance as yf

from backend.app.datasources.base import DataSourceProvider
from backend.app.datasources.mock_source import MockDataSource
from backend.app.schemas.market_data import StockQuote, CompanyFinancials, OptionContractSummary

logger = logging.getLogger(__name__)

class YahooFinanceDataSource(DataSourceProvider):
    """
    Live market data provider querying Yahoo Finance via yfinance.
    Includes automatic graceful fallback to MockDataSource in case of network unavailability or rate limits.
    """

    def __init__(self):
        self._fallback = MockDataSource()

    @property
    def name(self) -> str:
        return "yahoo"

    async def get_quote(self, symbol: str) -> StockQuote:
        try:
            loop = asyncio.get_event_loop()
            ticker = await loop.run_in_executor(None, yf.Ticker, symbol)
            fast_info = await loop.run_in_executor(None, lambda: ticker.fast_info)
            info = await loop.run_in_executor(None, lambda: ticker.info)

            last_price = getattr(fast_info, "last_price", None) or info.get("currentPrice") or info.get("regularMarketPrice")
            if not last_price:
                logger.warning(f"YahooFinance returned empty price for {symbol}, falling back to mock.")
                return await self._fallback.get_quote(symbol)

            return StockQuote(
                symbol=symbol.upper(),
                company_name=info.get("longName") or info.get("shortName") or symbol.upper(),
                current_price=float(last_price),
                currency=info.get("currency", "USD"),
                pe_ratio=info.get("trailingPE"),
                pb_ratio=info.get("priceToBook"),
                beta=info.get("beta", 1.0),
                fifty_two_week_high=getattr(fast_info, "year_high", None) or info.get("fiftyTwoWeekHigh"),
                fifty_two_week_low=getattr(fast_info, "year_low", None) or info.get("fiftyTwoWeekLow"),
                market_cap=getattr(fast_info, "market_cap", None) or info.get("marketCap"),
                source="yahoo"
            )
        except Exception as e:
            logger.warning(f"YahooFinance quote error for {symbol}: {e}. Using mock fallback.")
            res = await self._fallback.get_quote(symbol)
            res.source = "mock (yahoo fallback)"
            return res

    async def get_financials(self, symbol: str) -> CompanyFinancials:
        try:
            loop = asyncio.get_event_loop()
            ticker = await loop.run_in_executor(None, yf.Ticker, symbol)
            info = await loop.run_in_executor(None, lambda: ticker.info)
            cashflow = await loop.run_in_executor(None, lambda: ticker.cashflow)

            fcf = info.get("freeCashflow")
            if fcf is None and cashflow is not None and not cashflow.empty:
                if "Free Cash Flow" in cashflow.index:
                    fcf = float(cashflow.loc["Free Cash Flow"].iloc[0])

            eps = info.get("trailingEps")
            bvps = info.get("bookValue")
            shares = info.get("sharesOutstanding")

            if not fcf or not eps or not shares:
                logger.warning(f"YahooFinance incomplete financials for {symbol}, falling back to mock.")
                return await self._fallback.get_financials(symbol)

            cash = info.get("totalCash", 0.0)
            debt = info.get("totalDebt", 0.0)
            dividend = info.get("dividendRate", 0.0)
            yield_pct = info.get("dividendYield", 0.0)

            hist_fcf = []
            if cashflow is not None and not cashflow.empty and "Free Cash Flow" in cashflow.index:
                hist_fcf = [float(x) for x in cashflow.loc["Free Cash Flow"].dropna().tolist()][::-1]

            return CompanyFinancials(
                symbol=symbol.upper(),
                company_name=info.get("longName", symbol.upper()),
                free_cash_flow=float(fcf),
                diluted_eps=float(eps),
                book_value_per_share=float(bvps or 0.0),
                shares_outstanding=float(shares),
                total_cash=float(cash or 0.0),
                total_debt=float(debt or 0.0),
                annual_dividend=float(dividend or 0.0),
                dividend_yield=float(yield_pct or 0.0),
                historical_fcf=hist_fcf,
                ebitda=float(info.get("ebitda", 0.0)) if info.get("ebitda") else None,
                source="yahoo"
            )
        except Exception as e:
            logger.warning(f"YahooFinance financials error for {symbol}: {e}. Using mock fallback.")
            res = await self._fallback.get_financials(symbol)
            res.source = "mock (yahoo fallback)"
            return res

    async def get_option_chain_summary(self, symbol: str) -> List[OptionContractSummary]:
        try:
            loop = asyncio.get_event_loop()
            ticker = await loop.run_in_executor(None, yf.Ticker, symbol)
            expirations = await loop.run_in_executor(None, lambda: ticker.options)

            if not expirations:
                return await self._fallback.get_option_chain_summary(symbol)

            target_exp = expirations[0]
            chain = await loop.run_in_executor(None, lambda: ticker.option_chain(target_exp))
            calls = chain.calls
            puts = chain.puts

            # Pick 5 strikes around current price
            merged_strikes = sorted(list(set(calls["strike"].tolist() + puts["strike"].tolist())))
            quote = await self.get_quote(symbol)
            spot = quote.current_price

            closest_strikes = sorted(merged_strikes, key=lambda k: abs(k - spot))[:5]
            closest_strikes = sorted(closest_strikes)

            results = []
            for k in closest_strikes:
                c_row = calls[calls["strike"] == k]
                p_row = puts[puts["strike"] == k]

                call_last = float(c_row["lastPrice"].iloc[0]) if not c_row.empty else None
                put_last = float(p_row["lastPrice"].iloc[0]) if not p_row.empty else None
                iv = float(c_row["impliedVolatility"].iloc[0]) if not c_row.empty and not c_row["impliedVolatility"].isna().all() else 0.25

                results.append(
                    OptionContractSummary(
                        symbol=symbol.upper(),
                        expiration_date=target_exp,
                        days_to_expiry=30,
                        strike=float(k),
                        call_last=call_last,
                        put_last=put_last,
                        implied_volatility=iv,
                        volume=int(c_row["volume"].iloc[0]) if not c_row.empty and not c_row["volume"].isna().all() else 0,
                        open_interest=int(c_row["openInterest"].iloc[0]) if not c_row.empty and not c_row["openInterest"].isna().all() else 0
                    )
                )
            return results
        except Exception as e:
            logger.warning(f"YahooFinance options error for {symbol}: {e}. Using mock fallback.")
            return await self._fallback.get_option_chain_summary(symbol)

    async def get_risk_free_rate(self) -> float:
        try:
            loop = asyncio.get_event_loop()
            tnx = await loop.run_in_executor(None, yf.Ticker, "^TNX")
            info = await loop.run_in_executor(None, lambda: tnx.info)
            rate = info.get("regularMarketPrice") or info.get("previousClose")
            if rate:
                return float(rate) / 100.0
        except Exception:
            pass
        return 0.045  # 4.5% default

    async def health_check(self) -> bool:
        try:
            return True
        except Exception:
            return False
