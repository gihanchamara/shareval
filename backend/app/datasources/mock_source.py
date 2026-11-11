import hashlib
from typing import List, Dict, Any, Optional
from backend.app.datasources.base import DataSourceProvider
from backend.app.schemas.market_data import StockQuote, CompanyFinancials, OptionContractSummary

class MockDataSource(DataSourceProvider):
    """
    Offline and deterministic test mock provider.
    Includes rich, realistic company financials for standard stocks,
    and automatically calculates consistent synthetic data for any other ticker.
    """

    @property
    def name(self) -> str:
        return "mock"

    _PRESETS: Dict[str, Dict[str, Any]] = {
        "AAPL": {
            "name": "Apple Inc.",
            "price": 225.50,
            "pe": 33.4,
            "pb": 45.2,
            "beta": 1.10,
            "high52": 237.23,
            "low52": 164.08,
            "market_cap": 3450000000000,
            "fcf": 108800000000,
            "eps": 6.75,
            "bvps": 4.95,
            "shares": 15300000000,
            "cash": 65000000000,
            "debt": 105000000000,
            "dividend": 1.00,
            "div_yield": 0.0044,
            "historical_fcf": [92953000000, 111443000000, 99584000000, 108800000000],
            "iv": 0.24
        },
        "MSFT": {
            "name": "Microsoft Corporation",
            "price": 420.00,
            "pe": 35.8,
            "pb": 12.1,
            "beta": 0.95,
            "high52": 468.35,
            "low52": 366.50,
            "market_cap": 3120000000000,
            "fcf": 74000000000,
            "eps": 11.72,
            "bvps": 34.60,
            "shares": 7430000000,
            "cash": 80000000000,
            "debt": 45000000000,
            "dividend": 3.00,
            "div_yield": 0.0071,
            "historical_fcf": [56118000000, 65149000000, 59475000000, 74000000000],
            "iv": 0.22
        },
        "GOOGL": {
            "name": "Alphabet Inc.",
            "price": 178.20,
            "pe": 24.1,
            "pb": 6.8,
            "beta": 1.05,
            "high52": 191.75,
            "low52": 129.50,
            "market_cap": 2210000000000,
            "fcf": 71000000000,
            "eps": 7.40,
            "bvps": 26.15,
            "shares": 12400000000,
            "cash": 110000000000,
            "debt": 28000000000,
            "dividend": 0.80,
            "div_yield": 0.0045,
            "historical_fcf": [67012000000, 60010000000, 69490000000, 71000000000],
            "iv": 0.26
        },
        "KO": {
            "name": "The Coca-Cola Company",
            "price": 68.50,
            "pe": 26.2,
            "pb": 10.9,
            "beta": 0.58,
            "high52": 73.50,
            "low52": 57.20,
            "market_cap": 295000000000,
            "fcf": 10200000000,
            "eps": 2.61,
            "bvps": 6.25,
            "shares": 4310000000,
            "cash": 12000000000,
            "debt": 42000000000,
            "dividend": 1.94,
            "div_yield": 0.0283,
            "historical_fcf": [8700000000, 9500000000, 9700000000, 10200000000],
            "iv": 0.15
        },
        "TSLA": {
            "name": "Tesla, Inc.",
            "price": 240.00,
            "pe": 68.0,
            "pb": 11.5,
            "beta": 2.25,
            "high52": 271.00,
            "low52": 138.80,
            "market_cap": 765000000000,
            "fcf": 4500000000,
            "eps": 3.53,
            "bvps": 20.80,
            "shares": 3190000000,
            "cash": 29000000000,
            "debt": 5500000000,
            "dividend": 0.0,
            "div_yield": 0.0,
            "historical_fcf": [5015000000, 7566000000, 4358000000, 4500000000],
            "iv": 0.52
        }
    }

    def _get_synthetic_data(self, symbol: str) -> Dict[str, Any]:
        """Generates deterministic synthetic profile for any ticker."""
        sym = symbol.upper()
        if sym in self._PRESETS:
            return self._PRESETS[sym]

        # Use ticker hash to create realistic deterministic values
        h = int(hashlib.md5(sym.encode()).hexdigest(), 16)
        base_price = 50.0 + (h % 300)
        eps = round(base_price / (15.0 + (h % 20)), 2)
        bvps = round(base_price / (2.0 + (h % 6)), 2)
        shares = 500000000 + (h % 3000000000)
        fcf = round(eps * shares * 0.9, 2)
        cash = round(shares * 5.0, 2)
        debt = round(shares * 8.0, 2)
        dividend = round(eps * 0.3, 2) if (h % 2 == 0) else 0.0

        return {
            "name": f"{sym} Corporation",
            "price": float(base_price),
            "pe": round(base_price / eps, 1),
            "pb": round(base_price / bvps, 1),
            "beta": 1.0 + ((h % 50) - 25) / 50.0,
            "high52": round(base_price * 1.25, 2),
            "low52": round(base_price * 0.75, 2),
            "market_cap": round(base_price * shares, 2),
            "fcf": fcf,
            "eps": eps,
            "bvps": bvps,
            "shares": float(shares),
            "cash": cash,
            "debt": debt,
            "dividend": dividend,
            "div_yield": round(dividend / base_price, 4) if dividend > 0 else 0.0,
            "historical_fcf": [fcf * 0.7, fcf * 0.8, fcf * 0.9, fcf],
            "iv": 0.28
        }

    async def get_quote(self, symbol: str) -> StockQuote:
        data = self._get_synthetic_data(symbol)
        return StockQuote(
            symbol=symbol.upper(),
            company_name=data["name"],
            current_price=data["price"],
            currency="USD",
            pe_ratio=data["pe"],
            pb_ratio=data["pb"],
            beta=data["beta"],
            fifty_two_week_high=data["high52"],
            fifty_two_week_low=data["low52"],
            market_cap=data["market_cap"],
            source="mock"
        )

    async def get_financials(self, symbol: str) -> CompanyFinancials:
        data = self._get_synthetic_data(symbol)
        return CompanyFinancials(
            symbol=symbol.upper(),
            company_name=data["name"],
            free_cash_flow=data["fcf"],
            diluted_eps=data["eps"],
            book_value_per_share=data["bvps"],
            shares_outstanding=data["shares"],
            total_cash=data["cash"],
            total_debt=data["debt"],
            annual_dividend=data["dividend"],
            dividend_yield=data["div_yield"],
            historical_fcf=data.get("historical_fcf", []),
            source="mock"
        )

    async def get_option_chain_summary(self, symbol: str) -> List[OptionContractSummary]:
        data = self._get_synthetic_data(symbol)
        spot = data["price"]
        iv = data.get("iv", 0.25)
        
        strikes = [
            round(spot * 0.90, 1),
            round(spot * 0.95, 1),
            round(spot * 1.00, 1),
            round(spot * 1.05, 1),
            round(spot * 1.10, 1)
        ]

        results = []
        for k in strikes:
            call_val = max(0.05, round(max(0.0, spot - k) + spot * iv * 0.10, 2))
            put_val = max(0.05, round(max(0.0, k - spot) + spot * iv * 0.10, 2))
            results.append(
                OptionContractSummary(
                    symbol=symbol.upper(),
                    expiration_date="2026-12-18",
                    days_to_expiry=37,
                    strike=k,
                    call_bid=round(call_val * 0.98, 2),
                    call_ask=round(call_val * 1.02, 2),
                    call_last=call_val,
                    put_bid=round(put_val * 0.98, 2),
                    put_ask=round(put_val * 1.02, 2),
                    put_last=put_val,
                    implied_volatility=iv,
                    volume=1200,
                    open_interest=5400
                )
            )
        return results

    async def get_risk_free_rate(self) -> float:
        return 0.045

    async def health_check(self) -> bool:
        return True
