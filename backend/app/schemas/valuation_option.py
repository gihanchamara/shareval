from pydantic import BaseModel, Field, model_validator
from typing import Optional, List, Dict, Literal

class OptionPricingInput(BaseModel):
    underlying_price: float = Field(..., gt=0, description="Current spot price of underlying asset (S)")
    strike_price: float = Field(..., gt=0, description="Option strike price (K)")
    time_to_expiration: Optional[float] = Field(default=None, gt=0, description="Time to expiry in years (T)")
    days_to_expiration: Optional[float] = Field(default=None, gt=0, description="Days to expiry (DTE)")
    volatility: float = Field(default=0.25, gt=0, le=5.0, description="Annualized volatility (sigma)")
    risk_free_rate: float = Field(default=0.045, ge=0.0, le=0.50, description="Annualized risk-free rate (r)")
    dividend_yield: float = Field(default=0.0, ge=0.0, le=0.30, description="Continuous dividend yield (q)")
    option_type: Literal["call", "put"] = Field(default="call", description="Option type")
    style: Literal["european", "american"] = Field(default="european", description="Exercise style")
    model: Literal["black_scholes", "binomial"] = Field(default="black_scholes", description="Valuation algorithm")
    binomial_steps: int = Field(default=100, ge=10, le=500, description="Steps for binomial lattice")

    @model_validator(mode="after")
    def resolve_time(self):
        if self.time_to_expiration is None and self.days_to_expiration is not None:
            self.time_to_expiration = self.days_to_expiration / 365.0
        elif self.time_to_expiration is not None and self.days_to_expiration is None:
            self.days_to_expiration = self.time_to_expiration * 365.0
        elif self.time_to_expiration is None and self.days_to_expiration is None:
            # Default to 30 days
            self.days_to_expiration = 30.0
            self.time_to_expiration = 30.0 / 365.0
        return self

class OptionGreeks(BaseModel):
    delta: float = Field(..., description="Sensitivity to underlying price (dV/dS)")
    gamma: float = Field(..., description="Rate of change of delta (d2V/dS2)")
    theta_daily: float = Field(..., description="Decay per calendar day (USD)")
    theta_annual: float = Field(..., description="Decay per year (USD)")
    vega_1pct: float = Field(..., description="Sensitivity to 1% change in vol")
    rho_1pct: float = Field(..., description="Sensitivity to 1% change in interest rate")

class OptionPricingResult(BaseModel):
    model_name: str
    option_type: str
    style: str
    fair_price: float
    intrinsic_value: float
    time_value: float
    underlying_price: float
    strike_price: float
    time_to_expiration_years: float
    days_to_expiration: float
    volatility: float
    risk_free_rate: float
    dividend_yield: float
    american_early_exercise_premium: Optional[float] = None
    greeks: OptionGreeks
    breakeven_price: float
    moneyness_status: str  # "ITM", "ATM", "OTM"

class ImpliedVolatilityInput(BaseModel):
    market_price: float = Field(..., gt=0, description="Observed market price of option")
    underlying_price: float = Field(..., gt=0)
    strike_price: float = Field(..., gt=0)
    time_to_expiration: Optional[float] = None
    days_to_expiration: Optional[float] = None
    risk_free_rate: float = Field(default=0.045, ge=0.0)
    dividend_yield: float = Field(default=0.0, ge=0.0)
    option_type: Literal["call", "put"] = Field(default="call")

    @model_validator(mode="after")
    def resolve_time(self):
        if self.time_to_expiration is None and self.days_to_expiration is not None:
            self.time_to_expiration = self.days_to_expiration / 365.0
        elif self.time_to_expiration is None and self.days_to_expiration is None:
            self.days_to_expiration = 30.0
            self.time_to_expiration = 30.0 / 365.0
        return self

class ImpliedVolatilityResult(BaseModel):
    implied_volatility: float
    implied_volatility_pct: float
    market_price: float
    reconstructed_price: float
    iterations: int
    converged: bool

class OptionSensitivityMatrix(BaseModel):
    spot_range: List[float]
    vol_range: List[float]
    matrix: List[List[float]]  # Row: Spot, Col: Vol -> Option Price
