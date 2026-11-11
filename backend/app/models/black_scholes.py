import math
from scipy.stats import norm
from backend.app.schemas.valuation_option import OptionPricingInput, OptionPricingResult, OptionGreeks

def calculate_black_scholes(params: OptionPricingInput) -> OptionPricingResult:
    """
    Computes Black-Scholes-Merton option price and closed-form Greeks.
    Includes dividend yield (Merton extension).
    """
    S = float(params.underlying_price)
    K = float(params.strike_price)
    T = float(params.time_to_expiration)
    sigma = float(params.volatility)
    r = float(params.risk_free_rate)
    q = float(params.dividend_yield)
    is_call = (params.option_type.lower() == "call")

    # Edge case: expiring immediately
    if T <= 1e-6:
        intrinsic = max(0.0, S - K) if is_call else max(0.0, K - S)
        return OptionPricingResult(
            model_name="Black-Scholes-Merton",
            option_type=params.option_type,
            style="european",
            fair_price=round(intrinsic, 4),
            intrinsic_value=round(intrinsic, 4),
            time_value=0.0,
            underlying_price=S,
            strike_price=K,
            time_to_expiration_years=T,
            days_to_expiration=params.days_to_expiration or 0.0,
            volatility=sigma,
            risk_free_rate=r,
            dividend_yield=q,
            american_early_exercise_premium=0.0,
            greeks=OptionGreeks(
                delta=1.0 if is_call and S > K else (0.0 if is_call else (-1.0 if S < K else 0.0)),
                gamma=0.0,
                theta_daily=0.0,
                theta_annual=0.0,
                vega_1pct=0.0,
                rho_1pct=0.0
            ),
            breakeven_price=round(K + intrinsic if is_call else K - intrinsic, 2),
            moneyness_status="ITM" if intrinsic > 0 else ("ATM" if abs(S - K) < 0.01 else "OTM")
        )

    sqrt_T = math.sqrt(T)
    d1 = (math.log(S / K) + (r - q + 0.5 * sigma * sigma) * T) / (sigma * sqrt_T)
    d2 = d1 - sigma * sqrt_T

    df_r = math.exp(-r * T)
    df_q = math.exp(-q * T)
    pdf_d1 = norm.pdf(d1)

    if is_call:
        price = S * df_q * norm.cdf(d1) - K * df_r * norm.cdf(d2)
        delta = df_q * norm.cdf(d1)
        theta_annual = -(S * df_q * pdf_d1 * sigma) / (2.0 * sqrt_T) - r * K * df_r * norm.cdf(d2) + q * S * df_q * norm.cdf(d1)
        rho_annual = K * T * df_r * norm.cdf(d2)
        intrinsic = max(0.0, S - K)
        breakeven = K + price
    else:
        price = K * df_r * norm.cdf(-d2) - S * df_q * norm.cdf(-d1)
        delta = -df_q * norm.cdf(-d1)
        theta_annual = -(S * df_q * pdf_d1 * sigma) / (2.0 * sqrt_T) + r * K * df_r * norm.cdf(-d2) - q * S * df_q * norm.cdf(-d1)
        rho_annual = -K * T * df_r * norm.cdf(-d2)
        intrinsic = max(0.0, K - S)
        breakeven = K - price

    gamma = (df_q * pdf_d1) / (S * sigma * sqrt_T)
    vega_annual = S * df_q * sqrt_T * pdf_d1
    vega_1pct = vega_annual / 100.0
    rho_1pct = rho_annual / 100.0
    theta_daily = theta_annual / 365.0

    time_value = max(0.0, price - intrinsic)

    moneyness = "ATM"
    if is_call:
        if S > K * 1.01:
            moneyness = "ITM"
        elif S < K * 0.99:
            moneyness = "OTM"
    else:
        if S < K * 0.99:
            moneyness = "ITM"
        elif S > K * 1.01:
            moneyness = "OTM"

    return OptionPricingResult(
        model_name="Black-Scholes-Merton",
        option_type=params.option_type,
        style="european",
        fair_price=round(max(0.0, price), 4),
        intrinsic_value=round(intrinsic, 4),
        time_value=round(time_value, 4),
        underlying_price=round(S, 2),
        strike_price=round(K, 2),
        time_to_expiration_years=round(T, 4),
        days_to_expiration=round(params.days_to_expiration or T * 365.0, 1),
        volatility=round(sigma, 4),
        risk_free_rate=round(r, 4),
        dividend_yield=round(q, 4),
        american_early_exercise_premium=0.0,
        greeks=OptionGreeks(
            delta=round(delta, 4),
            gamma=round(gamma, 6),
            theta_daily=round(theta_daily, 4),
            theta_annual=round(theta_annual, 4),
            vega_1pct=round(vega_1pct, 4),
            rho_1pct=round(rho_1pct, 4)
        ),
        breakeven_price=round(breakeven, 2),
        moneyness_status=moneyness
    )
