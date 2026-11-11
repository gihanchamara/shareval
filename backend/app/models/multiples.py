from backend.app.schemas.valuation_stock import MultiplesInput, MultiplesResult

def calculate_multiples(params: MultiplesInput) -> MultiplesResult:
    """
    Computes comparable multiples valuation using benchmark P/E and P/B ratios.
    """
    pe_val = params.eps * params.benchmark_pe if params.eps > 0 else None
    pb_val = params.book_value_per_share * params.benchmark_pb if params.book_value_per_share > 0 else None

    vals = [v for v in [pe_val, pb_val] if v is not None and v > 0]
    blended = sum(vals) / len(vals) if vals else 0.0

    margin_of_safety = None
    status = "Fairly Valued"

    if params.current_price and blended > 0:
        margin_of_safety = round(((blended - params.current_price) / blended) * 100.0, 2)
        if margin_of_safety > 15.0:
            status = "Undervalued"
        elif margin_of_safety < -15.0:
            status = "Overvalued"
        else:
            status = "Fairly Valued"

    return MultiplesResult(
        model_name="Relative Multiples Valuation",
        pe_implied_price=round(pe_val, 2) if pe_val is not None else None,
        pb_implied_price=round(pb_val, 2) if pb_val is not None else None,
        blended_price=round(blended, 2),
        current_price=params.current_price,
        margin_of_safety_pct=margin_of_safety,
        valuation_status=status
    )
