# Spec: Cox-Ross-Rubinstein (CRR) Binomial Tree Model

- **Spec ID**: `option-binomial-tree`
- **Category**: `option-models`
- **Status**: Implemented

## 1. Overview
The Cox-Ross-Rubinstein (CRR) binomial tree models discrete steps over time to price American-style options, where the holder possesses the right to exercise early at any node prior to maturity.

## 2. Mathematical Formulation

### 2.1 Lattice Parameters
For $N$ discrete steps and time increment $\Delta t = \frac{T}{N}$:
$$u = e^{\sigma \sqrt{\Delta t}} \quad (\text{Up factor})$$
$$d = \frac{1}{u} = e^{-\sigma \sqrt{\Delta t}} \quad (\text{Down factor})$$
$$p = \frac{e^{(r - q)\Delta t} - d}{u - d} \quad (\text{Risk-neutral probability of up movement})$$

*Arbitrage-free condition: $d < e^{(r - q)\Delta t} < u$.*

### 2.2 Terminal Payoff (Step $N$)
For node $j \in [0, N]$:
$$S_{N, j} = S_0 \cdot u^j \cdot d^{N - j}$$
$$\text{Call Payoff: } V_{N, j} = \max(0, S_{N, j} - K)$$
$$\text{Put Payoff: } V_{N, j} = \max(0, K - S_{N, j})$$

### 2.3 Backward Induction (Step $i = N-1, \dots, 0$)
At each node $(i, j)$:
$$\text{Continuation Value} = e^{-r \Delta t} \left[ p V_{i+1, j+1} + (1 - p) V_{i+1, j} \right]$$
- **European Option**: $V_{i, j} = \text{Continuation Value}$
- **American Option**: $V_{i, j} = \max(\text{Intrinsic Value}_{i, j}, \text{Continuation Value})$

### 2.4 Early Exercise Premium
$$\text{American Premium} = V_{\text{American}} - V_{\text{European}}$$

## 3. Parameter Specification
| Parameter | Type | Required | Default | Constraint | Description |
|---|---|---|---|---|---|
| `underlying_price` | float | Yes | - | $> 0$ | Spot price $S$ |
| `strike_price` | float | Yes | - | $> 0$ | Strike price $K$ |
| `time_to_expiration` | float | Yes | - | $> 0$ | Time to expiry $T$ in years |
| `volatility` | float | Yes | 0.25 | $> 0$ | Annual volatility $\sigma$ |
| `risk_free_rate` | float | Yes | 0.045 | $\ge 0$ | Risk-free rate $r$ |
| `dividend_yield` | float | No | 0.0 | $\ge 0$ | Continuous dividend yield $q$ |
| `steps` | integer | No | 100 | $10 \le N \le 500$ | Number of discrete tree steps |
| `style` | string | No | 'american' | 'american' \| 'european' | Exercise style |
| `option_type` | string | Yes | 'call' | 'call' \| 'put' | Option direction |
