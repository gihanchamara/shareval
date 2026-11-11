from typing import Dict, Type, Optional
from backend.app.datasources.base import DataSourceProvider
from backend.app.datasources.mock_source import MockDataSource
from backend.app.datasources.yahoo_source import YahooFinanceDataSource
from backend.app.core.config import DEFAULT_DATA_SOURCE

class DataSourceFactory:
    """
    Extensible factory managing available market data providers.
    Supports dynamic registration of new providers at runtime or startup.
    """

    _registry: Dict[str, Type[DataSourceProvider]] = {
        "mock": MockDataSource,
        "yahoo": YahooFinanceDataSource,
    }

    _instances: Dict[str, DataSourceProvider] = {}

    @classmethod
    def register(cls, name: str, provider_cls: Type[DataSourceProvider]) -> None:
        """Register a new third-party provider adapter."""
        cls._registry[name.lower()] = provider_cls

    @classmethod
    def get_provider(cls, name: Optional[str] = None) -> DataSourceProvider:
        """Retrieve singleton instance of the requested or default provider."""
        provider_name = (name or DEFAULT_DATA_SOURCE).lower()
        if provider_name not in cls._registry:
            provider_name = "mock"

        if provider_name not in cls._instances:
            cls._instances[provider_name] = cls._registry[provider_name]()

        return cls._instances[provider_name]

    @classmethod
    def available_providers(cls) -> list[str]:
        return list(cls._registry.keys())

def get_data_source(provider_name: Optional[str] = None) -> DataSourceProvider:
    """Dependency helper for FastAPI endpoints."""
    return DataSourceFactory.get_provider(provider_name)
