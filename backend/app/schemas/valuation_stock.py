from pydantic import BaseModel, Field, model_validator
from typing import Optional, List, Dict

class DCFInput(BaseModel):
    symbol: Optional[str] = "CUSTOM"
    free_cash_flow: float = Field(..., gt=0, description="Base FCF in USD (must be positive)")
    growth_rate_stage1: float = Field(default=0.10, ge=-0.5, le=1.5, description="High growth phase (Years 1-5)")
    growth_rate_stage2: float = Field(default=0.05, ge=-0.3, le=1.0, description="Transition growth phase (Years 6-10)")
    terminal_growth_rate: float = Field(default=0.025, ge=0.005, le=0.06, description="Perpetual growth rate")
    discount_rate: float = Field(default=0.09, ge=0.03, le=0.30, description="WACC or required return")
    net_debt: float = Field(default=0.0, description="Total Debt minus Cash & Equivalents")
    shares_outstanding: float = Field(..., gt=0, description="Diluted shares count")
    current_price: Optional[float] = Field(default=None, gt=0, description="Current market price for MoS calculation")

    @model_validator(mode="after")
    def validate_rates(self):
        if self.discount_rate <= self.terminal_growth_rate:
            raise ValueError(
                f"Discount rate ({self.discount_rate:.2%}) must strictly exceed perpetual terminal growth rate ({self.terminal_growth_rate:.2%})."
            )
        return self

class DCFCashFlowProjection(BaseModel):
    year: int
    projected_fcf: float
    discount_factor: float
    pv_fcf: float

class DCFResult(BaseModel):
    model_name: str = "Discounted Cash Flow (DCF)"
    fair_value_per_share: float
    enterprise_value: float
    equity_value: float
    pv_explicit_cash_flows: float
    terminal_value: float
    pv_terminal_value: float
    current_price: Optional[float] = None
    margin_of_safety_pct: Optional[float] = None
    valuation_status: str
    projections: List[DCFCashFlowProjection]

class GrahamInput(BaseModel):
    symbol: Optional[str] = "CUSTOM"
    eps: float = Field(..., gt=0, description="Trailing 12-month EPS")
    growth_rate: float = Field(default=0.07, ge=0.0, le=0.40, description="Expected 7-10 yr growth rate (e.g. 0.07 for 7%)")
    current_bond_yield: float = Field(default=0.045, ge=0.01, le=0.20, description="Current AAA bond yield (e.g. 0.045 for 4.5%)")
    book_value_per_share: Optional[float] = Field(default=None, description="Book value per share for Graham Number")
    current_price: Optional[float] = Field(default=None, gt=0)

class GrahamResult(BaseModel):
    model_name: str = "Benjamin Graham Intrinsic Value"
    graham_fair_value: float
    graham_number: Optional[float] = None
    current_price: Optional[float] = None
    margin_of_safety_pct: Optional[float] = None
    valuation_status: str

class DDMInput(BaseModel):
    symbol: Optional[str] = "CUSTOM"
    annual_dividend: float = Field(..., gt=0, description="Current annual dividend per share (D0)")
    dividend_growth_rate: float = Field(default=0.04, ge=0.0, le=0.20, description="Perpetual dividend growth rate (g)")
    required_return: float = Field(default=0.08, ge=0.03, le=0.30, description="Required rate of return (r)")
    current_price: Optional[float] = Field(default=None, gt=0)

    @model_validator(mode="after")
    def validate_ddm(self):
        if self.required_return <= self.dividend_growth_rate:
            raise ValueError("Required return must exceed dividend growth rate for DDM convergence.")
        return self

class DDMResult(BaseModel):
    model_name: str = "Dividend Discount Model (Gordon Growth)"
    ddm_fair_value: float
    projected_dividend_d1: float
    dividend_yield_pct: float
    current_price: Optional[float] = None
    margin_of_safety_pct: Optional[float] = None
    valuation_status: str

class MultiplesInput(BaseModel):
    symbol: Optional[str] = "CUSTOM"
    eps: float = Field(..., description="Diluted EPS")
    book_value_per_share: float = Field(..., description="Book Value per share")
    benchmark_pe: float = Field(default=20.0, gt=0, description="Industry median P/E")
    benchmark_pb: float = Field(default=3.0, gt=0, description="Industry median P/B")
    current_price: Optional[float] = Field(default=None, gt=0)

class MultiplesResult(BaseModel):
    model_name: str = "Relative Multiples Valuation"
    pe_implied_price: Optional[float] = None
    pb_implied_price: Optional[float] = None
    blended_price: float
    current_price: Optional[float] = None
    margin_of_safety_pct: Optional[float] = None
    valuation_status: str

class CompositeStockValuationInput(BaseModel):
    symbol: str = "CUSTOM"
    current_price: float = Field(..., gt=0)
    free_cash_flow: float = Field(..., gt=0)
    growth_rate_stage1: float = 0.10
    growth_rate_stage2: float = 0.05
    terminal_growth_rate: float = 0.025
    discount_rate: float = 0.09
    net_debt: float = 0.0
    shares_outstanding: float = Field(..., gt=0)
    eps: float = Field(..., gt=0)
    expected_growth_graham: float = 0.07
    current_bond_yield: float = 0.045
    book_value_per_share: float = 0.0
    annual_dividend: float = 0.0
    dividend_growth_rate: float = 0.03
    benchmark_pe: float = 20.0
    benchmark_pb: float = 3.0
    weight_dcf: float = Field(default=0.45, ge=0)
    weight_graham: float = Field(default=0.25, ge=0)
    weight_ddm: float = Field(default=0.10, ge=0)
    weight_multiples: float = Field(default=0.20, ge=0)

class CompositeStockValuationResult(BaseModel):
    symbol: str
    current_price: float
    blended_fair_value: float
    overall_margin_of_safety_pct: float
    valuation_verdict: str  # "Undervalued", "Fairly Valued", "Overvalued"
    models: Dict[str, Optional[float]]
    weights_used: Dict[str, float]
    dcf_details: Optional[DCFResult] = None
    graham_details: Optional[GrahamResult] = None
    ddm_details: Optional[DDMResult] = None
    multiples_details: Optional[MultiplesResult] = None
