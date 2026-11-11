import asyncio
from backend.app.datasources.factory import DataSourceFactory
from backend.app.datasources.mock_source import MockDataSource
from backend.app.datasources.base import DataSourceProvider

def test_mock_datasource_contract():
    async def _test():
        provider = DataSourceFactory.get_provider("mock")
        assert isinstance(provider, DataSourceProvider)

        # Test quote
        quote = await provider.get_quote("AAPL")
        assert quote.symbol == "AAPL"
        assert quote.current_price > 0
        assert quote.currency == "USD"

        # Test financials
        financials = await provider.get_financials("AAPL")
        assert financials.symbol == "AAPL"
        assert financials.free_cash_flow > 0
        assert financials.shares_outstanding > 0

        # Test options chain
        options = await provider.get_option_chain_summary("AAPL")
        assert len(options) > 0
        assert options[0].strike > 0

        # Test risk-free rate
        rf = await provider.get_risk_free_rate()
        assert 0.0 < rf < 0.15

        # Test unknown symbol generation
        rand_quote = await provider.get_quote("XYZCORP")
        assert rand_quote.symbol == "XYZCORP"
        assert rand_quote.current_price > 0

    asyncio.run(_test())

def test_datasource_factory_registration():
    class CustomProvider(DataSourceProvider):
        @property
        def name(self) -> str:
            return "custom"
        async def get_quote(self, symbol):
            pass
        async def get_financials(self, symbol):
            pass
        async def get_option_chain_summary(self, symbol):
            pass
        async def get_risk_free_rate(self):
            return 0.05
        async def health_check(self):
            return True

    DataSourceFactory.register("custom", CustomProvider)
    assert "custom" in DataSourceFactory.available_providers()
    inst = DataSourceFactory.get_provider("custom")
    assert isinstance(inst, CustomProvider)
