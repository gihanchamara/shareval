from fastapi import APIRouter, HTTPException
from backend.app.schemas.valuation_stock import (
    DCFInput, DCFResult,
    GrahamInput, GrahamResult,
    DDMInput, DDMResult,
    MultiplesInput, MultiplesResult,
    CompositeStockValuationInput, CompositeStockValuationResult
)
from backend.app.models.dcf import calculate_dcf
from backend.app.models.graham import calculate_graham
from backend.app.models.ddm import calculate_ddm
from backend.app.models.multiples import calculate_multiples

router = APIRouter(prefix="/stocks", tags=["Stock Valuation"])

@router.post("/evaluate/dcf", response_model=DCFResult)
def evaluate_dcf(params: DCFInput):
    """Calculates 10-year multi-stage Discounted Cash Flow (DCF) fair value."""
    try:
        return calculate_dcf(params)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/evaluate/graham", response_model=GrahamResult)
def evaluate_graham(params: GrahamInput):
    """Calculates Benjamin Graham intrinsic value and Graham Number."""
    try:
        return calculate_graham(params)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/evaluate/ddm", response_model=DDMResult)
def evaluate_ddm(params: DDMInput):
    """Calculates Dividend Discount Model (Gordon Growth) fair value."""
    try:
        return calculate_ddm(params)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/evaluate/multiples", response_model=MultiplesResult)
def evaluate_multiples(params: MultiplesInput):
    """Calculates relative valuation based on benchmark P/E and P/B."""
    try:
        return calculate_multiples(params)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/evaluate/composite", response_model=CompositeStockValuationResult)
def evaluate_composite(params: CompositeStockValuationInput):
    """
    Computes blended fair value across DCF, Graham, DDM, and Multiples models
    according to customized weights.
    """
    # 1. DCF
    dcf_res = calculate_dcf(DCFInput(
        symbol=params.symbol,
        free_cash_flow=params.free_cash_flow,
        growth_rate_stage1=params.growth_rate_stage1,
        growth_rate_stage2=params.growth_rate_stage2,
        terminal_growth_rate=params.terminal_growth_rate,
        discount_rate=params.discount_rate,
        net_debt=params.net_debt,
        shares_outstanding=params.shares_outstanding,
        current_price=params.current_price
    ))

    # 2. Graham
    graham_res = calculate_graham(GrahamInput(
        symbol=params.symbol,
        eps=params.eps,
        growth_rate=params.expected_growth_graham,
        current_bond_yield=params.current_bond_yield,
        book_value_per_share=params.book_value_per_share,
        current_price=params.current_price
    ))

    # 3. DDM (if dividend paying)
    ddm_res = None
    if params.annual_dividend > 0 and params.discount_rate > params.dividend_growth_rate:
        try:
            ddm_res = calculate_ddm(DDMInput(
                symbol=params.symbol,
                annual_dividend=params.annual_dividend,
                dividend_growth_rate=params.dividend_growth_rate,
                required_return=params.discount_rate,
                current_price=params.current_price
            ))
        except Exception:
            ddm_res = None

    # 4. Multiples
    multiples_res = calculate_multiples(MultiplesInput(
        symbol=params.symbol,
        eps=params.eps,
        book_value_per_share=params.book_value_per_share,
        benchmark_pe=params.benchmark_pe,
        benchmark_pb=params.benchmark_pb,
        current_price=params.current_price
    ))

    # Calculate weighted composite
    models_dict = {
        "DCF": dcf_res.fair_value_per_share,
        "Graham": graham_res.graham_fair_value,
        "DDM": ddm_res.ddm_fair_value if ddm_res else None,
        "Multiples": multiples_res.blended_price
    }

    raw_weights = {
        "DCF": params.weight_dcf,
        "Graham": params.weight_graham,
        "DDM": params.weight_ddm if ddm_res else 0.0,
        "Multiples": params.weight_multiples
    }

    total_weight = sum(raw_weights[k] for k, v in models_dict.items() if v is not None and v > 0)
    if total_weight <= 0:
        total_weight = 1.0

    normalized_weights = {}
    weighted_sum = 0.0

    for k, val in models_dict.items():
        if val is not None and val > 0:
            norm_w = raw_weights[k] / total_weight
            normalized_weights[k] = round(norm_w, 4)
            weighted_sum += val * norm_w
        else:
            normalized_weights[k] = 0.0

    blended_fair_value = round(weighted_sum, 2)
    overall_mos = round(((blended_fair_value - params.current_price) / blended_fair_value) * 100.0, 2)

    verdict = "Fairly Valued"
    if overall_mos > 15.0:
        verdict = "Undervalued"
    elif overall_mos < -15.0:
        verdict = "Overvalued"

    return CompositeStockValuationResult(
        symbol=params.symbol.upper(),
        current_price=params.current_price,
        blended_fair_value=blended_fair_value,
        overall_margin_of_safety_pct=overall_mos,
        valuation_verdict=verdict,
        models=models_dict,
        weights_used=normalized_weights,
        dcf_details=dcf_res,
        graham_details=graham_res,
        ddm_details=ddm_res,
        multiples_details=multiples_res
    )
