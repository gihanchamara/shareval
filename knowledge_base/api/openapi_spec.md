# Spec: REST API Specification

- **Spec ID**: `api-spec`
- **Category**: `architecture-interfaces`
- **Status**: Implemented

## 1. Overview
The ShareVal REST API exposes standard endpoints for stock intrinsic valuation, option fair pricing and Greeks calculation, ticker autofill, and indexed knowledge base discovery.

## 2. Endpoints Summary

### 2.1 Stock Valuation
- `POST /api/v1/stocks/evaluate/dcf`
  - Input: FCF, growth rates (stage 1, stage 2, terminal), discount rate, net debt, shares outstanding.
  - Output: Enterprise value, equity value, fair value per share, cash flow trajectory, margin of safety.
- `POST /api/v1/stocks/evaluate/graham`
  - Input: EPS, growth rate, bond yield, book value per share.
  - Output: Graham fair value, Graham number, margin of safety.
- `POST /api/v1/stocks/evaluate/ddm`
  - Input: Annual dividend, dividend growth rate, required return.
  - Output: DDM fair value, projected dividend D1, dividend yield.
- `POST /api/v1/stocks/evaluate/composite`
  - Input: Aggregated inputs + model weights (DCF weight, Graham weight, DDM weight, Multiples weight).
  - Output: Blended fair value, individual model valuations, valuation sentiment (Undervalued, Fairly Valued, Overvalued).

### 2.2 Option Valuation & Greeks
- `POST /api/v1/options/evaluate/pricing`
  - Input: Spot price, strike, time to expiry (or days), volatility, risk-free rate, dividend yield, style ('european' | 'american'), model ('black_scholes' | 'binomial').
  - Output: Call & Put fair prices, intrinsic values, time values, American early exercise premium.
- `POST /api/v1/options/evaluate/greeks`
  - Input: Option parameters.
  - Output: Delta, Gamma, Theta (daily & annual), Vega (1%), Rho (1%).
- `POST /api/v1/options/evaluate/implied-volatility`
  - Input: Option market price, spot, strike, time to expiry, risk-free rate, option type ('call' | 'put').
  - Output: Calculated implied volatility (IV).

### 2.3 Market Data & Ticker Lookup
- `GET /api/v1/market/quote/{symbol}`
  - Output: Current market price, P/E, beta, 52-week range, company profile.
- `GET /api/v1/market/financials/{symbol}`
  - Output: Balance sheet metrics, FCF, diluted EPS, book value, cash, debt.
- `GET /api/v1/market/options/{symbol}`
  - Output: Sample options chain and ATM implied volatility.

### 2.4 Knowledge Base
- `GET /api/v1/knowledge/index`
  - Output: Full JSON catalog of all indexed models, formulas, and parameters.
- `GET /api/v1/knowledge/spec/{spec_id}`
  - Output: Full Markdown documentation and parameter metadata for the requested spec.
