# Spec: Discounted Cash Flow (DCF) Model

- **Spec ID**: `stock-dcf`
- **Category**: `stock-models`
- **Status**: Implemented

## 1. Overview
The Discounted Cash Flow (DCF) model estimates the intrinsic fair value of an enterprise based on the present value of its projected future free cash flows, discounted at an appropriate discount rate (Weighted Average Cost of Capital, WACC).

## 2. Mathematical Formulation

### 2.1 Cash Flow Projection (Multi-Stage)
For a projection horizon of $N$ years (typically 5 to 10 years):
$$FCF_t = FCF_0 \times \prod_{i=1}^t (1 + g_i)$$
Where:
- $g_i = g_{\text{stage1}}$ for $t \in [1, 5]$ (High growth period)
- $g_i = g_{\text{stage1}} - \frac{(g_{\text{stage1}} - g_{\text{terminal}}) \cdot (t - 5)}{5}$ for $t \in [6, 10]$ (Transition phase)

### 2.2 Present Value of Cash Flows
$$PV_{\text{explicit}} = \sum_{t=1}^N \frac{FCF_t}{(1 + r)^t}$$
Where:
- $r$ is the discount rate (WACC / Hurdle rate).

### 2.3 Terminal Value (Gordon Growth Perpetual)
$$TV = \frac{FCF_N \times (1 + g_{\text{terminal}})}{r - g_{\text{terminal}}}$$
$$PV(TV) = \frac{TV}{(1 + r)^N}$$
*Condition: $r > g_{\text{terminal}}$ must hold.*

### 2.4 Enterprise & Equity Value Bridge
$$\text{Enterprise Value} = PV_{\text{explicit}} + PV(TV)$$
$$\text{Equity Value} = \text{Enterprise Value} - \text{Total Debt} + \text{Cash and Short Term Investments}$$
$$\text{Fair Value Per Share} = \frac{\text{Equity Value}}{\text{Diluted Shares Outstanding}}$$

### 2.5 Margin of Safety
$$\text{Margin of Safety} = \frac{\text{Fair Value} - \text{Current Market Price}}{\text{Fair Value}} \times 100\%$$

## 3. Parameter Specification
| Parameter | Type | Required | Default | Range / Constraint | Description |
|---|---|---|---|---|---|
| `free_cash_flow` | float | Yes | - | $> 0$ for standard DCF | Baseline Free Cash Flow (USD) |
| `growth_rate_stage1` | float | Yes | 0.12 (12%) | $-0.50$ to $1.00$ | Expected growth for years 1-5 |
| `growth_rate_stage2` | float | No | 0.06 (6%) | $-0.20$ to $0.50$ | Transition growth for years 6-10 |
| `terminal_growth_rate` | float | Yes | 0.025 (2.5%)| $0.01$ to $0.05$ | Perpetual growth ($g < r$) |
| `discount_rate` | float | Yes | 0.09 (9.0%) | $0.04$ to $0.25$ | WACC / Required rate of return |
| `net_debt` | float | No | 0.0 | Any | Total Debt - Cash & Equivalents |
| `shares_outstanding` | float | Yes | - | $> 0$ | Common shares diluted |
| `current_price` | float | No | - | $> 0$ | Current market quote for MoS |

## 4. Edge Cases & Validation Rules
1. **$r \le g_{\text{terminal}}$**: Produces mathematical singularity or negative terminal values. The model must raise a validation error when $r \le g_{\text{terminal}} + 0.005$.
2. **Negative Free Cash Flow**: A startup or turn-around company with negative FCF should use normalized FCF or switch to a Multiples/Graham model.
3. **Extreme Growth**: Caps growth rates to realistic bounds to prevent unrealistically high valuations.
