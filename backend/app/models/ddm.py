from backend.app.schemas.valuation_stock import DDMInput, DDMResult

def calculate_ddm(params: DDMInput) -> DDMResult:
    """
    Computes Gordon Growth Dividend Discount Model:
    P0 = D0 * (1 + g) / (r - g)
    """
    d0 = params.annual_dividend
    g = params.dividend_growth_rate
    r = params.required_return

    d1 = d0 * (1.0 + g)
    fair_value = d1 / (r - g)
    fair_value = max(0.0, fair_value)

    yield_pct = (d0 / params.current_price * 100.0) if params.current_price and params.current_price > 0 else (d0 / fair_value * 100.0)

    margin_of_safety = None
    status = "Fairly Valued"

    if params.current_price and fair_value > 0:
        margin_of_safety = round(((fair_value - params.current_price) / fair_value) * 100.0, 2)
        if margin_of_safety > 15.0:
            status = "Undervalued"
        elif margin_of_safety < -15.0:
            status = "Overvalued"
        else:
            status = "Fairly Valued"

    return DDMResult(
        model_name="Dividend Discount Model (Gordon Growth)",
        ddm_fair_value=round(fair_value, 2),
        projected_dividend_d1=round(d1, 2),
        dividend_yield_pct=round(yield_pct, 2),
        current_price=params.current_price,
        margin_of_safety_pct=margin_of_safety,
        valuation_status=status
    )
