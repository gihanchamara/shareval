import math
from typing import Optional
from backend.app.schemas.valuation_stock import GrahamInput, GrahamResult

def calculate_graham(params: GrahamInput) -> GrahamResult:
    """
    Computes Benjamin Graham's Intrinsic Value:
    Revised Formula: V = (EPS * (8.5 + 2 * g_pct) * 4.4) / Y
    Graham Number: sqrt(22.5 * EPS * BVPS)
    """
    eps = params.eps
    # Convert g to percentage points if expressed as fraction (e.g. 0.08 -> 8.0)
    g_pct = params.growth_rate * 100.0 if params.growth_rate <= 1.0 else params.growth_rate
    # Convert yield to percentage points if expressed as fraction (e.g. 0.045 -> 4.5)
    y_pct = params.current_bond_yield * 100.0 if params.current_bond_yield <= 1.0 else params.current_bond_yield

    # Avoid zero division
    y_val = max(0.5, y_pct)
    graham_val = (eps * (8.5 + 2.0 * g_pct) * 4.4) / y_val
    graham_val = max(0.0, graham_val)

    # Graham Number
    graham_num = None
    if params.book_value_per_share and params.book_value_per_share > 0 and eps > 0:
        graham_num = math.sqrt(22.5 * eps * params.book_value_per_share)

    margin_of_safety = None
    status = "Fairly Valued"

    if params.current_price and graham_val > 0:
        margin_of_safety = round(((graham_val - params.current_price) / graham_val) * 100.0, 2)
        if margin_of_safety > 15.0:
            status = "Undervalued"
        elif margin_of_safety < -15.0:
            status = "Overvalued"
        else:
            status = "Fairly Valued"

    return GrahamResult(
        model_name="Benjamin Graham Intrinsic Value",
        graham_fair_value=round(graham_val, 2),
        graham_number=round(graham_num, 2) if graham_num is not None else None,
        current_price=params.current_price,
        margin_of_safety_pct=margin_of_safety,
        valuation_status=status
    )
