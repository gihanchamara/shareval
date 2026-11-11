# Spec: Option Greeks & Sensitivity Analysis

- **Spec ID**: `option-greeks`
- **Category**: `option-models`
- **Status**: Implemented

## 1. Overview
Option Greeks measure the sensitivity of an option's price to changes in fundamental market parameters: underlying spot price ($S$), volatility ($\sigma$), time to expiration ($T$), and interest rate ($r$).

## 2. Mathematical Formulation

Using standard Black-Scholes terms $d_1$ and $d_2$:
$$N'(x) = \frac{1}{\sqrt{2\pi}} e^{-\frac{x^2}{2}}$$

### 2.1 Delta ($\Delta$) - Sensitivity to Underlying Price
$$\Delta_{\text{call}} = e^{-qT} N(d_1) \quad (\in [0, 1])$$
$$\Delta_{\text{put}} = e^{-qT} (N(d_1) - 1) \quad (\in [-1, 0])$$

### 2.2 Gamma ($\Gamma$) - Rate of Change of Delta
$$\Gamma_{\text{call}} = \Gamma_{\text{put}} = \frac{e^{-qT} N'(d_1)}{S \sigma \sqrt{T}} \quad (> 0)$$

### 2.3 Theta ($\Theta$) - Time Decay (Reported per Day)
$$\Theta_{\text{call, annual}} = -\frac{S e^{-qT} N'(d_1) \sigma}{2 \sqrt{T}} - r K e^{-rT} N(d_2) + q S e^{-qT} N(d_1)$$
$$\Theta_{\text{put, annual}} = -\frac{S e^{-qT} N'(d_1) \sigma}{2 \sqrt{T}} + r K e^{-rT} N(-d_2) - q S e^{-qT} N(-d_1)$$
$$\Theta_{\text{daily}} = \frac{\Theta_{\text{annual}}}{365}$$

### 2.4 Vega ($\mathcal{V}$) - Sensitivity to Volatility (Per 1% Move)
$$\mathcal{V}_{\text{annual}} = S e^{-qT} \sqrt{T} N'(d_1)$$
$$\mathcal{V}_{\text{per 1\%}} = \frac{\mathcal{V}_{\text{annual}}}{100}$$

### 2.5 Rho ($\rho$) - Sensitivity to Interest Rate (Per 1% Move)
$$\rho_{\text{call, annual}} = K T e^{-rT} N(d_2) \implies \rho_{\text{call, 1\%}} = \frac{\rho_{\text{call, annual}}}{100}$$
$$\rho_{\text{put, annual}} = -K T e^{-rT} N(-d_2) \implies \rho_{\text{put, 1\%}} = \frac{\rho_{\text{put, annual}}}{100}$$

### 2.6 Implied Volatility Solver
Given an observed market option price $P_{\text{mkt}}$, solve for $\sigma_{\text{implied}}$ such that:
$$f(\sigma) = \text{BS}(\sigma; S, K, T, r, q) - P_{\text{mkt}} = 0$$
Using root-finding algorithms:
- Newton-Raphson iteration: $\sigma_{n+1} = \sigma_n - \frac{\text{BS}(\sigma_n) - P_{\text{mkt}}}{\mathcal{V}(\sigma_n)}$
- Fallback: Brent's bounded method (`scipy.optimize.brentq`) over interval $\sigma \in [0.001, 5.00]$.
