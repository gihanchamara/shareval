# Spec: Dividend Discount Model (Gordon Growth Model)

- **Spec ID**: `stock-ddm`
- **Category**: `stock-models`
- **Status**: Implemented

## 1. Overview
The Gordon Growth Dividend Discount Model values a stock by calculating the present value of an infinite stream of future dividend payments that grow at a constant rate $g$.

## 2. Mathematical Formulation

### 2.1 Constant Growth Formula
$$P_0 = \frac{D_1}{r - g} = \frac{D_0 \times (1 + g)}{r - g}$$
Where:
- $P_0$ = Intrinsic value per share
- $D_0$ = Current annual dividend paid per share
- $D_1$ = Projected next year's dividend per share
- $g$ = Perpetual dividend growth rate
- $r$ = Required rate of return on equity (Cost of Equity, CAPM)

### 2.2 Cost of Equity (CAPM)
$$r = R_f + \beta \times (R_m - R_f)$$
Where:
- $R_f$ = Risk-free rate
- $\beta$ = Stock systematic risk sensitivity
- $(R_m - R_f)$ = Equity market risk premium (typically 5.0% - 6.5%)

## 3. Parameter Specification
| Parameter | Type | Required | Default | Constraint | Description |
|---|---|---|---|---|---|
| `annual_dividend` | float | Yes | - | $> 0$ | Current annual dividend $D_0$ |
| `dividend_growth_rate` | float | Yes | 0.04 (4%) | $0.0 \le g < r$ | Expected constant dividend growth |
| `required_return` | float | Yes | 0.08 (8%) | $r > g$ | Required rate of return |
| `current_price` | float | No | - | $> 0$ | Current market price |

## 4. Edge Cases & Validation Rules
- Condition $r > g$ is mandatory. If $r \le g$, valuation diverges to infinity.
