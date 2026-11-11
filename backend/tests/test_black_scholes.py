import pytest
from backend.app.schemas.valuation_option import OptionPricingInput, ImpliedVolatilityInput
from backend.app.models.black_scholes import calculate_black_scholes
from backend.app.models.binomial_tree import calculate_binomial_tree
from backend.app.models.implied_vol import calculate_implied_volatility

def test_black_scholes_call_and_put():
    # Canonical test case: S=100, K=100, T=1, r=5%, vol=20%, q=0
    call_inp = OptionPricingInput(
        underlying_price=100.0,
        strike_price=100.0,
        time_to_expiration=1.0,
        volatility=0.20,
        risk_free_rate=0.05,
        dividend_yield=0.0,
        option_type="call"
    )
    call_res = calculate_black_scholes(call_inp)
    
    # Theoretical BS call is approx 10.4506
    assert abs(call_res.fair_price - 10.45) < 0.1
    assert 0.5 < call_res.greeks.delta < 0.7  # ATM call delta ~0.637
    assert call_res.greeks.gamma > 0
    assert call_res.greeks.vega_1pct > 0

    put_inp = OptionPricingInput(
        underlying_price=100.0,
        strike_price=100.0,
        time_to_expiration=1.0,
        volatility=0.20,
        risk_free_rate=0.05,
        dividend_yield=0.0,
        option_type="put"
    )
    put_res = calculate_black_scholes(put_inp)

    # Put-Call parity check: C - P = S - K * exp(-r*T) = 100 - 100 * exp(-0.05) ~ 4.877
    parity_diff = call_res.fair_price - put_res.fair_price
    expected_parity = 100.0 - 100.0 * 0.951229
    assert abs(parity_diff - expected_parity) < 0.05

def test_binomial_tree_convergence():
    inp = OptionPricingInput(
        underlying_price=100.0,
        strike_price=100.0,
        time_to_expiration=1.0,
        volatility=0.20,
        risk_free_rate=0.05,
        dividend_yield=0.0,
        option_type="call",
        style="european",
        binomial_steps=100
    )
    res_binomial = calculate_binomial_tree(inp)
    res_bs = calculate_black_scholes(inp)

    # European binomial must converge closely to Black-Scholes
    assert abs(res_binomial.fair_price - res_bs.fair_price) < 0.15

def test_implied_volatility_solver():
    iv_inp = ImpliedVolatilityInput(
        market_price=10.45,
        underlying_price=100.0,
        strike_price=100.0,
        time_to_expiration=1.0,
        risk_free_rate=0.05,
        dividend_yield=0.0,
        option_type="call"
    )
    res = calculate_implied_volatility(iv_inp)
    assert res.converged
    # Should reconstruct the original ~20% volatility
    assert abs(res.implied_volatility - 0.20) < 0.01
