import math
import numpy as np
from backend.app.schemas.valuation_option import OptionPricingInput, OptionPricingResult, OptionGreeks
from backend.app.models.black_scholes import calculate_black_scholes

def calculate_binomial_tree(params: OptionPricingInput) -> OptionPricingResult:
    """
    Computes option price using Cox-Ross-Rubinstein (CRR) Binomial Tree lattice.
    Supports both American (with early exercise) and European exercise styles.
    """
    S = float(params.underlying_price)
    K = float(params.strike_price)
    T = float(params.time_to_expiration)
    sigma = float(params.volatility)
    r = float(params.risk_free_rate)
    q = float(params.dividend_yield)
    N = int(params.binomial_steps or 100)
    is_call = (params.option_type.lower() == "call")
    is_american = (params.style.lower() == "american")

    if T <= 1e-6:
        return calculate_black_scholes(params)

    dt = T / N
    u = math.exp(sigma * math.sqrt(dt))
    d = 1.0 / u
    discount = math.exp(-r * dt)
    p = (math.exp((r - q) * dt) - d) / (u - d)

    # Validate arbitrage boundary for lattice
    p = max(0.0, min(1.0, p))

    # Terminal stock prices at step N
    j_indices = np.arange(N + 1)
    S_terminal = S * (u ** j_indices) * (d ** (N - j_indices))

    if is_call:
        V_american = np.maximum(0.0, S_terminal - K)
        V_european = np.copy(V_american)
    else:
        V_american = np.maximum(0.0, K - S_terminal)
        V_european = np.copy(V_american)

    # Backward induction
    for i in range(N - 1, -1, -1):
        V_european = discount * (p * V_european[1:] + (1.0 - p) * V_european[:-1])
        continuation_american = discount * (p * V_american[1:] + (1.0 - p) * V_american[:-1])
        
        j_step = np.arange(i + 1)
        S_step = S * (u ** j_step) * (d ** (i - j_step))

        if is_call:
            exercise_american = np.maximum(0.0, S_step - K)
        else:
            exercise_american = np.maximum(0.0, K - S_step)

        if is_american:
            V_american = np.maximum(exercise_american, continuation_american)
        else:
            V_american = continuation_american

    price = float(V_american[0])
    euro_price = float(V_european[0])
    early_exercise_premium = max(0.0, price - euro_price) if is_american else 0.0

    # Retrieve closed-form baseline Greeks from Black-Scholes for comprehensive analytics
    bs_res = calculate_black_scholes(params)
    intrinsic = max(0.0, S - K) if is_call else max(0.0, K - S)
    time_value = max(0.0, price - intrinsic)
    breakeven = K + price if is_call else K - price

    return OptionPricingResult(
        model_name="CRR Binomial Tree Lattice",
        option_type=params.option_type,
        style=params.style,
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
        american_early_exercise_premium=round(early_exercise_premium, 4),
        greeks=bs_res.greeks,
        breakeven_price=round(breakeven, 2),
        moneyness_status=bs_res.moneyness_status
    )
