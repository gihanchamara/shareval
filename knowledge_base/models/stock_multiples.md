# Spec: Relative Multiples Valuation

- **Spec ID**: `stock-multiples`
- **Category**: `stock-models`
- **Status**: Implemented

## 1. Overview
Relative valuation estimates fair market value by applying industry or peer group benchmark valuation multiples to the subject company's operating metrics (Earnings, Book Value, EBITDA, Sales).

## 2. Mathematical Formulation

### 2.1 P/E Multiple Implied Price
$$P_{\text{PE}} = \text{EPS} \times \text{Benchmark P/E}$$

### 2.2 P/B Multiple Implied Price
$$P_{\text{PB}} = \text{BVPS} \times \text{Benchmark P/B}$$

### 2.3 EV/EBITDA Implied Price
$$\text{Enterprise Value} = \text{EBITDA} \times \text{Benchmark EV/EBITDA}$$
$$P_{\text{EV/EBITDA}} = \frac{\text{Enterprise Value} - \text{Net Debt}}{\text{Shares Outstanding}}$$

### 2.4 Composite Multiple Blended Fair Value
$$P_{\text{blended}} = \sum_{m} w_m \cdot P_m$$
Where $\sum w_m = 1$.

## 3. Parameter Specification
| Parameter | Type | Required | Default | Constraint | Description |
|---|---|---|---|---|---|
| `eps` | float | Yes | - | Any | Diluted EPS |
| `book_value_per_share` | float | Yes | - | Any | Book value per share |
| `benchmark_pe` | float | Yes | 20.0 | $> 0$ | Industry/Historical median P/E |
| `benchmark_pb` | float | Yes | 3.0 | $> 0$ | Industry/Historical median P/B |
| `ebitda` | float | No | 0.0 | Any | EBITDA in USD |
| `benchmark_ev_ebitda` | float | No | 12.0 | $> 0$ | Benchmark EV/EBITDA |
| `net_debt` | float | No | 0.0 | Any | Net Debt |
| `shares_outstanding` | float | No | 1.0 | $> 0$ | Common shares count |
