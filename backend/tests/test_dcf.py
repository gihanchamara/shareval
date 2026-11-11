import pytest
from backend.app.schemas.valuation_stock import DCFInput
from backend.app.models.dcf import calculate_dcf

def test_dcf_calculation_basic():
    params = DCFInput(
        symbol="AAPL",
        free_cash_flow=100_000_000,
        growth_rate_stage1=0.10,
        growth_rate_stage2=0.05,
        terminal_growth_rate=0.025,
        discount_rate=0.09,
        net_debt=200_000_000,
        shares_outstanding=10_000_000,
        current_price=150.0
    )
    result = calculate_dcf(params)

    assert result.fair_value_per_share > 0
    assert result.enterprise_value > result.equity_value  # Because net_debt > 0
    assert len(result.projections) == 10
    assert result.projections[0].year == 1
    assert result.projections[9].year == 10
    assert result.margin_of_safety_pct is not None

def test_dcf_discount_rate_validation():
    with pytest.raises(ValueError):
        DCFInput(
            free_cash_flow=1000,
            growth_rate_stage1=0.05,
            growth_rate_stage2=0.03,
            terminal_growth_rate=0.05,
            discount_rate=0.04,  # discount_rate <= terminal_growth_rate
            shares_outstanding=100
        )
