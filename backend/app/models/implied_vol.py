import math
from scipy.optimize import brentq
from backend.app.schemas.valuation_option import (
    ImpliedVolatilityInput,
    ImpliedVolatilityResult,
    OptionPricingInput,
    OptionSensitivityMatrix
)
from backend.app.models.black_scholes import calculate_black_scholes

def calculate_implied_volatility(params: ImpliedVolatilityInput) -> ImpliedVolatilityResult:
    """
    Computes Black-Scholes implied volatility for an observed market option price.
    Uses Newton-Raphson iteration with fallback to Brent's root finder.
    """
    S = float(params.underlying_price)
    K = float(params.strike_price)
    T = float(params.time_to_expiration)
    r = float(params.risk_free_rate)
    q = float(params.dividend_yield)
    mkt = float(params.market_price)
    is_call = (params.option_type.lower() == "call")

    # Intrinsic value check
    intrinsic = max(0.0, S - K) if is_call else max(0.0, K - S)
    if mkt <= intrinsic:
        return ImpliedVolatilityResult(
            implied_volatility=0.0001,
            implied_volatility_pct=0.01,
            market_price=mkt,
            reconstructed_price=intrinsic,
            iterations=0,
            converged=False
        )

    def objective(vol: float) -> float:
        inp = OptionPricingInput(
            underlying_price=S,
            strike_price=K,
            time_to_expiration=T,
            volatility=max(1e-4, vol),
            risk_free_rate=r,
            dividend_yield=q,
            option_type=params.option_type,
            style="european",
            model="black_scholes"
        )
        res = calculate_black_scholes(inp)
        return res.fair_price - mkt

    # Newton-Raphson with Vega
    vol = 0.30  # initial guess
    max_iter = 50
    tol = 1e-4
    converged = False
    iterations = 0

    for i in range(max_iter):
        iterations = i + 1
        inp = OptionPricingInput(
            underlying_price=S,
            strike_price=K,
            time_to_expiration=T,
            volatility=vol,
            risk_free_rate=r,
            dividend_yield=q,
            option_type=params.option_type,
            style="european",
            model="black_scholes"
        )
        res = calculate_black_scholes(inp)
        diff = res.fair_price - mkt

        if abs(diff) < tol:
            converged = True
            break

        vega_annual = res.greeks.vega_1pct * 100.0
        if abs(vega_annual) < 1e-6:
            break

        vol = vol - diff / vega_annual
        if vol <= 0.001 or vol > 5.0:
            break

    # If Newton-Raphson failed to converge, use bounded Brent's method
    if not converged or vol <= 0.001 or vol > 5.0:
        try:
            vol = brentq(objective, 1e-4, 5.0, xtol=1e-4, maxiter=100)
            converged = True
        except Exception:
            vol = max(0.01, min(3.0, vol))
            converged = False

    reconstructed_inp = OptionPricingInput(
        underlying_price=S,
        strike_price=K,
        time_to_expiration=T,
        volatility=vol,
        risk_free_rate=r,
        dividend_yield=q,
        option_type=params.option_type,
        style="european",
        model="black_scholes"
    )
    reconstructed = calculate_black_scholes(reconstructed_inp).fair_price

    return ImpliedVolatilityResult(
        implied_volatility=round(vol, 4),
        implied_volatility_pct=round(vol * 100.0, 2),
        market_price=round(mkt, 4),
        reconstructed_price=round(reconstructed, 4),
        iterations=iterations,
        converged=converged
    )

def generate_sensitivity_matrix(
    spot: float,
    strike: float,
    time_to_exp: float,
    base_vol: float,
    risk_free: float,
    option_type: str = "call"
) -> OptionSensitivityMatrix:
    """
    Generates a 2D matrix of Option Fair Prices across varied Spot Prices and Volatilities.
    """
    spot_factors = [0.85, 0.90, 0.95, 1.00, 1.05, 1.10, 1.15]
    vol_factors = [0.60, 0.80, 1.00, 1.20, 1.40]

    spot_range = [round(spot * factor, 2) for factor in spot_factors]
    vol_range = [round(max(0.05, base_vol * factor), 2) for factor in vol_factors]

    matrix = []
    for s in spot_range:
        row = []
        for v in vol_range:
            inp = OptionPricingInput(
                underlying_price=s,
                strike_price=strike,
                time_to_expiration=time_to_exp,
                volatility=v,
                risk_free_rate=risk_free,
                option_type=option_type, # type: ignore
                model="black_scholes"
            )
            price = calculate_black_scholes(inp).fair_price
            row.append(round(price, 2))
        matrix.append(row)

    return OptionSensitivityMatrix(
        spot_range=spot_range,
        vol_range=vol_range,
        matrix=matrix
    )
