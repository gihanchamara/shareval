# Spec: Benjamin Graham Intrinsic Value Model

- **Spec ID**: `stock-graham`
- **Category**: `stock-models`
- **Status**: Implemented

## 1. Overview
Benjamin Graham, the father of value investing, developed quantitative heuristics to estimate the fair price of a stable company based on its earnings per share (EPS), projected growth rate, and prevailing bond interest yields.

## 2. Mathematical Formulation

### 2.1 Graham Formula (Revised 1974)
$$V = \frac{\text{EPS} \times (8.5 + 2g) \times 4.4}{Y}$$
Where:
- $V$ = Intrinsic value per share
- $\text{EPS}$ = Trailing 12-month diluted Earnings Per Share
- $8.5$ = P/E base for a no-growth company
- $g$ = Conservative expected growth rate for the next 7 to 10 years (expressed as a percentage number, e.g., 7 for 7%)
- $4.4$ = Benchmark average yield of high-grade corporate bonds in 1962
- $Y$ = Current yield on AAA corporate bonds (e.g. 4.5% to 5.2%)

### 2.2 Graham Number (Conservative Asset & Earnings Ceiling)
$$\text{Graham Number} = \sqrt{22.5 \times \text{EPS} \times \text{BVPS}}$$
Where:
- $22.5$ = $15 \times 1.5$ (Max recommended P/E of 15 multiplied by max recommended P/B of 1.5)
- $\text{BVPS}$ = Book Value Per Share (Equity / Shares)

## 3. Parameter Specification
| Parameter | Type | Required | Default | Range / Constraint | Description |
|---|---|---|---|---|---|
| `eps` | float | Yes | - | $> 0$ | Diluted EPS (TTM) |
| `growth_rate` | float | Yes | 0.08 (8%) | $0.00$ to $0.35$ | Annual EPS growth rate |
| `current_bond_yield` | float | No | 0.045 (4.5%) | $0.01$ to $0.15$ | Yield of AAA corporate bonds |
| `book_value_per_share` | float | No | 0.0 | $\ge 0$ | Book value per share |
| `current_price` | float | No | - | $> 0$ | Current stock market price |

## 4. Edge Cases & Validation Rules
1. **Negative EPS**: Graham's formula is invalid for unprofitable businesses ($EPS \le 0$).
2. **Negative BVPS**: If Book Value is negative (deficits), Graham Number is undefined.
