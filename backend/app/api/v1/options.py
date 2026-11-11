from fastapi import APIRouter, HTTPException, Query
from backend.app.schemas.valuation_option import (
    OptionPricingInput, OptionPricingResult, OptionGreeks,
    ImpliedVolatilityInput, ImpliedVolatilityResult, OptionSensitivityMatrix
)
from backend.app.models.black_scholes import calculate_black_scholes
from backend.app.models.binomial_tree import calculate_binomial_tree
from backend.app.models.implied_vol import calculate_implied_volatility, generate_sensitivity_matrix

router = APIRouter(prefix="/options", tags=["Option Valuation & Greeks"])

@router.post("/evaluate/pricing", response_model=OptionPricingResult)
def evaluate_option_pricing(params: OptionPricingInput):
    """
    Computes fair option price and Greeks using either
    Black-Scholes-Merton (European) or CRR Binomial Tree (American / European).
    """
    try:
        if params.model == "binomial" or params.style == "american":
            return calculate_binomial_tree(params)
        else:
            return calculate_black_scholes(params)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/evaluate/greeks", response_model=OptionGreeks)
def evaluate_option_greeks(params: OptionPricingInput):
    """Computes closed-form option Greeks (Delta, Gamma, Theta, Vega, Rho)."""
    try:
        res = calculate_black_scholes(params)
        return res.greeks
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/evaluate/implied-volatility", response_model=ImpliedVolatilityResult)
def evaluate_implied_volatility(params: ImpliedVolatilityInput):
    """Solves for implied volatility (IV) given market option price."""
    try:
        return calculate_implied_volatility(params)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/evaluate/sensitivity", response_model=OptionSensitivityMatrix)
def evaluate_sensitivity(
    spot: float = Query(..., gt=0),
    strike: float = Query(..., gt=0),
    days_to_expiration: float = Query(default=30.0, gt=0),
    volatility: float = Query(default=0.25, gt=0),
    risk_free_rate: float = Query(default=0.045, ge=0),
    option_type: str = Query(default="call")
):
    """Generates 2D spot price vs volatility sensitivity matrix."""
    try:
        t_years = days_to_expiration / 365.0
        return generate_sensitivity_matrix(
            spot=spot,
            strike=strike,
            time_to_exp=t_years,
            base_vol=volatility,
            risk_free=risk_free_rate,
            option_type=option_type
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
