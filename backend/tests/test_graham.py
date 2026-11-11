import pytest
from backend.app.schemas.valuation_stock import GrahamInput, DDMInput
from backend.app.models.graham import calculate_graham
from backend.app.models.ddm import calculate_ddm

def test_graham_valuation():
    params = GrahamInput(
        symbol="KO",
        eps=3.0,
        growth_rate=0.06,  # 6%
        current_bond_yield=0.044,  # 4.4%
        book_value_per_share=10.0,
        current_price=50.0
    )
    result = calculate_graham(params)

    # V = 3.0 * (8.5 + 2*6) * 4.4 / 4.4 = 3.0 * 20.5 = 61.5
    assert abs(result.graham_fair_value - 61.5) < 0.1
    assert result.graham_number is not None
    # Graham number = sqrt(22.5 * 3.0 * 10.0) = sqrt(675) ~ 25.98
    assert abs(result.graham_number - 25.98) < 0.1
    assert result.margin_of_safety_pct > 0  # Undervalued relative to 50

def test_ddm_valuation():
    params = DDMInput(
        symbol="JNJ",
        annual_dividend=4.50,
        dividend_growth_rate=0.04,  # 4%
        required_return=0.08,  # 8%
        current_price=150.0
    )
    result = calculate_ddm(params)

    # D1 = 4.5 * 1.04 = 4.68
    # Fair Value = 4.68 / (0.08 - 0.04) = 4.68 / 0.04 = 117.0
    assert abs(result.ddm_fair_value - 117.0) < 0.1
    assert result.margin_of_safety_pct is not None

def test_ddm_invalid_rates():
    with pytest.raises(ValueError):
        DDMInput(
            annual_dividend=2.0,
            dividend_growth_rate=0.09,
            required_return=0.07  # required_return <= growth
        )
