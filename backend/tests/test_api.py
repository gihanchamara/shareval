import asyncio
from httpx import AsyncClient, ASGITransport
from backend.app.main import app

def run_async(coro):
    return asyncio.run(coro)

def test_health():
    async def _test():
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            res = await ac.get("/health")
            assert res.status_code == 200
            assert res.json()["status"] == "healthy"
    run_async(_test())

def test_api_stock_composite():
    async def _test():
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            payload = {
                "symbol": "AAPL",
                "current_price": 220.0,
                "free_cash_flow": 100_000_000_000,
                "growth_rate_stage1": 0.10,
                "growth_rate_stage2": 0.05,
                "terminal_growth_rate": 0.025,
                "discount_rate": 0.09,
                "net_debt": 40_000_000_000,
                "shares_outstanding": 15_000_000_000,
                "eps": 6.5,
                "expected_growth_graham": 0.08,
                "current_bond_yield": 0.045,
                "book_value_per_share": 5.0,
                "annual_dividend": 1.0,
                "dividend_growth_rate": 0.04,
                "benchmark_pe": 30.0,
                "benchmark_pb": 40.0
            }
            res = await ac.post("/api/v1/stocks/evaluate/composite", json=payload)
            assert res.status_code == 200
            data = res.json()
            assert data["blended_fair_value"] > 0
            assert "models" in data
            assert "DCF" in data["models"]
            assert "Graham" in data["models"]
    run_async(_test())

def test_api_option_pricing():
    async def _test():
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            payload = {
                "underlying_price": 200.0,
                "strike_price": 200.0,
                "days_to_expiration": 45,
                "volatility": 0.30,
                "risk_free_rate": 0.045,
                "option_type": "call",
                "style": "american",
                "model": "binomial"
            }
            res = await ac.post("/api/v1/options/evaluate/pricing", json=payload)
            assert res.status_code == 200
            data = res.json()
            assert data["fair_price"] > 0
            assert "greeks" in data
            assert data["greeks"]["delta"] > 0
    run_async(_test())

def test_api_knowledge_base():
    async def _test():
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            res = await ac.get("/api/v1/knowledge/index")
            assert res.status_code == 200
            data = res.json()
            assert "specs" in data
            assert "stock-dcf" in data["specs"]

            spec_res = await ac.get("/api/v1/knowledge/spec/stock-dcf")
            assert spec_res.status_code == 200
            spec_data = spec_res.json()
            assert "metadata" in spec_data
            assert "content" in spec_data
            assert "Discounted Cash Flow" in spec_data["content"]
    run_async(_test())

def test_api_market_data():
    async def _test():
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            res = await ac.get("/api/v1/market/quote/AAPL?source=mock")
            assert res.status_code == 200
            assert res.json()["symbol"] == "AAPL"

            fin_res = await ac.get("/api/v1/market/financials/AAPL?source=mock")
            assert fin_res.status_code == 200
            assert fin_res.json()["free_cash_flow"] > 0
    run_async(_test())
