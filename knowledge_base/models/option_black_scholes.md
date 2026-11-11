# Spec: Black-Scholes-Merton Option Pricing Model

- **Spec ID**: `option-black-scholes`
- **Category**: `option-models`
- **Status**: Implemented

## 1. Overview
The Black-Scholes-Merton model provides closed-form solutions for pricing European-style options on an underlying asset that pays a continuous dividend yield $q$, subject to geometric Brownian motion with constant drift and volatility.

## 2. Mathematical Formulation

### 2.1 Standard Black-Scholes Formula with Dividend Yield ($q$)
$$\text{Call Price } (C) = S_0 e^{-qT} N(d_1) - K e^{-rT} N(d_2)$$
$$\text{Put Price } (P) = K e^{-rT} N(-d_2) - S_0 e^{-qT} N(-d_1)$$

Where:
$$d_1 = \frac{\ln(S_0 / K) + \left(r - q + \frac{\sigma^2}{2}\right) T}{\sigma \sqrt{T}}$$
$$d_2 = d_1 - \sigma \sqrt{T}$$

### 2.2 Definitions
- $S_0$: Current spot price of the underlying asset
- $K$: Option strike price
- $T$: Time to expiration in years ($T = \text{DTE} / 365$)
- $r$: Annualized continuously compounded risk-free interest rate
- $q$: Continuous dividend yield
- $\sigma$: Annualized standard deviation of returns (volatility)
- $N(x)$: Standard cumulative normal distribution function:
  $$N(x) = \frac{1}{\sqrt{2\pi}} \int_{-\infty}^x e^{-\frac{u^2}{2}} du$$

### 2.3 Put-Call Parity
$$C - P = S_0 e^{-qT} - K e^{-rT}$$

### 2.4 Decomposition
- **Intrinsic Value (Call)**: $\max(0, S_0 - K)$
- **Intrinsic Value (Put)**: $\max(0, K - S_0)$
- **Time Value**: $\text{Option Price} - \text{Intrinsic Value}$

## 3. Parameter Specification
| Parameter | Type | Required | Default | Constraint | Description |
|---|---|---|---|---|---|
| `underlying_price` | float | Yes | - | $> 0$ | Current spot price ($S$) |
| `strike_price` | float | Yes | - | $> 0$ | Strike price ($K$) |
| `time_to_expiration` | float | Yes | - | $> 0$ | Time to expiry in years ($T$) |
| `volatility` | float | Yes | 0.25 (25%) | $> 0$ | Annualized volatility ($\sigma$) |
| `risk_free_rate` | float | Yes | 0.045 (4.5%) | $\ge 0$ | Risk-free rate ($r$) |
| `dividend_yield` | float | No | 0.0 (0.0%) | $\ge 0$ | Continuous dividend yield ($q$) |
| `option_type` | string| Yes | 'call' | 'call' \| 'put' | Option direction |

## 4. Edge Cases
1. **$T \to 0$**: As expiration approaches, option converges to intrinsic payoff.
2. **$\sigma \to 0$**: Option becomes deterministic discounted payoff.
3. **Deep In/Out of the Money**: Exponential terms must be calculated using robust numeric standard normal CDF (`scipy.stats.norm.cdf`).
