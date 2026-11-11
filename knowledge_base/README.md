# ShareVal Indexed Knowledge Base (Spec-Driven Architecture)

Welcome to the **ShareVal Knowledge Base**. This repository operates under a **Spec-Driven Design (SDD)** paradigm: every valuation model, algorithmic boundary, data contract, and API endpoint is formally specified in this directory before and alongside its software implementation.

---

## 🧭 Spec Catalog Index

The master index is programmatically maintained in [`index.json`](./index.json) and dynamically served by the backend at `/api/v1/knowledge/index`.

### 1. Stock Valuation Models
- [Discounted Cash Flow (DCF)](models/stock_dcf.md) - Free Cash Flow multi-stage projection with Gordon Growth / Exit Multiple Terminal Value.
- [Benjamin Graham Intrinsic Value](models/stock_graham.md) - Classical Graham formula, Revised bond-yield formula, and Graham Number.
- [Dividend Discount Model (Gordon Growth)](models/stock_ddm.md) - Constant growth and multi-phase dividend valuation.
- [Relative Multiples Valuation](models/stock_multiples.md) - P/E, P/B, EV/EBITDA comparative peer valuation.

### 2. Option Valuation Models
- [Black-Scholes-Merton Model](models/option_black_scholes.md) - Analytical European call/put pricing with dividend adjustments.
- [Cox-Ross-Rubinstein Binomial Tree](models/option_binomial.md) - Lattice model for American option early exercise pricing.
- [Option Greeks & Sensitivity](models/option_greeks.md) - Closed-form analytic Delta, Gamma, Theta, Vega, Rho, and numerical Implied Volatility.

### 3. Architecture & Data Contracts
- [Market Data Provider Interface](interfaces/data_source.md) - Abstract provider contract (`DataSourceProvider`) for plugging Yahoo Finance, Polygon, AlphaVantage, or offline mocks.
- [REST API OpenAPI Specification](api/openapi_spec.md) - Endpoints, schemas, request bodies, and JSON responses.

---

## 📐 Principles of Spec-Driven Design in ShareVal

1. **Specification as Single Source of Truth**: Formulas, input bounds, edge cases, and output units are defined here.
2. **Model Decoupling**: Pure mathematical financial engines reside in `backend/app/models/` without knowledge of HTTP transports or database models.
3. **Pluggable Data Ingestion**: The market data layer interacts only with the abstract `DataSourceProvider` interface defined in `interfaces/data_source.md`.
4. **Dynamic Frontend Inspection**: The UI pulls directly from `/api/v1/knowledge` to display live mathematical equations, parameter bounds, and assumptions alongside calculator inputs.
