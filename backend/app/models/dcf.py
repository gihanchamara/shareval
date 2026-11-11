import math
from typing import List, Optional
from backend.app.schemas.valuation_stock import DCFInput, DCFResult, DCFCashFlowProjection

def calculate_dcf(params: DCFInput) -> DCFResult:
    """
    Computes 10-year multi-stage Discounted Cash Flow valuation.
    Stage 1: Years 1-5 (High growth rate)
    Stage 2: Years 6-10 (Linear transition towards terminal growth rate)
    Terminal Value: Gordon Growth model perpetual capitalization
    """
    fcf = params.free_cash_flow
    g1 = params.growth_rate_stage1
    g2 = params.growth_rate_stage2
    g_term = params.terminal_growth_rate
    r = params.discount_rate

    projections: List[DCFCashFlowProjection] = []
    pv_explicit = 0.0
    current_fcf = fcf

    for year in range(1, 11):
        if year <= 5:
            # Stage 1: high growth
            growth = g1
        else:
            # Stage 2: linear glide from g1 (or g2) to g_term
            weight = (year - 5) / 5.0
            growth = g2 * (1.0 - weight) + g_term * weight

        current_fcf *= (1.0 + growth)
        discount_factor = 1.0 / ((1.0 + r) ** year)
        pv_fcf = current_fcf * discount_factor
        pv_explicit += pv_fcf

        projections.append(
            DCFCashFlowProjection(
                year=year,
                projected_fcf=round(current_fcf, 2),
                discount_factor=round(discount_factor, 4),
                pv_fcf=round(pv_fcf, 2)
            )
        )

    # Terminal Value at Year 10
    terminal_fcf = current_fcf * (1.0 + g_term)
    terminal_value = terminal_fcf / (r - g_term)
    pv_terminal_value = terminal_value / ((1.0 + r) ** 10)

    # Enterprise Value & Equity Value Bridge
    enterprise_value = pv_explicit + pv_terminal_value
    equity_value = enterprise_value - params.net_debt
    fair_value_per_share = max(0.0, equity_value / params.shares_outstanding)

    margin_of_safety = None
    status = "Fairly Valued"

    if params.current_price and fair_value_per_share > 0:
        margin_of_safety = round(((fair_value_per_share - params.current_price) / fair_value_per_share) * 100.0, 2)
        if margin_of_safety > 15.0:
            status = "Undervalued"
        elif margin_of_safety < -15.0:
            status = "Overvalued"
        else:
            status = "Fairly Valued"

    return DCFResult(
        model_name="Discounted Cash Flow (DCF)",
        fair_value_per_share=round(fair_value_per_share, 2),
        enterprise_value=round(enterprise_value, 2),
        equity_value=round(equity_value, 2),
        pv_explicit_cash_flows=round(pv_explicit, 2),
        terminal_value=round(terminal_value, 2),
        pv_terminal_value=round(pv_terminal_value, 2),
        current_price=params.current_price,
        margin_of_safety_pct=margin_of_safety,
        valuation_status=status,
        projections=projections
    )
