# ShareVal - Stock & Option Fair Valuation Service

**ShareVal** is a lightweight, spec-driven financial valuation service for stocks and options. It features pure quantitative valuation engines, a pluggable market data architecture, an indexed spec-driven knowledge base, and a responsive thin UI built in React.

---

## 🚀 Key Features

1. **Equities Fair Valuation**:
   - **Discounted Cash Flow (DCF)**: 10-year multi-stage cash flow projections with Gordon Growth / perpetual capitalization.
   - **Benjamin Graham Intrinsic Value**: Classical and revised Graham formula adjusting for current corporate bond yields, plus the Graham Number.
   - **Dividend Discount Model (DDM)**: Gordon Growth constant dividend model.
   - **Relative Multiples Valuation**: Benchmark P/E and P/B peer multiples.
   - **Composite Blended Valuation**: Dynamic user-weighted allocation across models with automatic Margin of Safety calculation.

2. **Options Fair Valuation & Greeks**:
   - **Black-Scholes-Merton Model**: Closed-form analytical European option pricing with continuous dividend yields.
   - **Cox-Ross-Rubinstein (CRR) Binomial Tree**: Multi-step lattice for American-style options accounting for early exercise premium.
   - **Option Greeks Dashboard**: Real-time Delta ($\Delta$), Gamma ($\Gamma$), Theta ($\Theta$), Vega ($\mathcal{V}$ per 1%), and Rho ($\rho$ per 1%).
   - **Implied Volatility (IV) Solver**: Fast root-finding (Newton-Raphson + Brent's method) converting market prices into implied volatility.
   - **2D Sensitivity Matrix**: Live heatmap of option pricing across spot prices and volatility ranges.

3. **Pluggable Market Data Architecture**:
   - Clean abstract interface (`DataSourceProvider`) enabling zero-friction integration of new market data vendors.
   - Built-in providers:
     - `MockDataSource`: High-fidelity presets (AAPL, MSFT, GOOGL, KO, TSLA) and deterministic synthetic financials for offline testing and development.
     - `YahooFinanceDataSource`: Live market quotes, balance sheet financials, and options chains via `yfinance` with automatic fallback.
   - Runtime switching via header `X-Data-Source` or query parameter `?source=yahoo|mock`.

4. **Spec-Driven Knowledge Base (SDD)**:
   - Dedicated `knowledge_base/` indexed by `index.json`.
   - Every formula, constraint, parameter boundary, and data contract is formally specified in markdown specs.
   - Live browser directly inside the Thin UI and served via REST API `/api/v1/knowledge`.

5. **Thin UI (React)**:
   - Modern dark-mode UI with glassmorphic cards, sliders, cash-flow projection tables, Greeks cards, and knowledge base explorer.
   - Runs out-of-the-box directly served by FastAPI at `http://localhost:8000/`.

---

## 📂 Project Structure

```
ShareVal/
├── knowledge_base/               # Indexed Spec-Driven Knowledge Base
│   ├── index.json                # Master catalog indexing specs & formulas
│   ├── README.md                 # Knowledge base guide
│   ├── models/                   # Valuation model specifications
│   │   ├── stock_dcf.md
│   │   ├── stock_graham.md
│   │   ├── stock_ddm.md
│   │   ├── stock_multiples.md
│   │   ├── option_black_scholes.md
│   │   ├── option_binomial.md
│   │   └── option_greeks.md
│   ├── interfaces/
│   │   └── data_source.md        # Provider contract specification
│   └── api/
│       └── openapi_spec.md       # API contract specification
│
├── backend/                      # Python FastAPI Valuation Service
│   ├── app/
│   │   ├── main.py               # FastAPI entry point & UI static mounting
│   │   ├── core/
│   │   │   ├── config.py         # Application configuration
│   │   │   └── registry.py       # Knowledge base reader & parser
│   │   ├── schemas/              # Pydantic request/response models
│   │   │   ├── market_data.py
│   │   │   ├── valuation_stock.py
│   │   │   └── valuation_option.py
│   │   ├── datasources/          # Pluggable Market Data Providers
│   │   │   ├── base.py           # Abstract Base Class DataSourceProvider
│   │   │   ├── mock_source.py    # Offline mock provider
│   │   │   ├── yahoo_source.py   # Live Yahoo Finance provider
│   │   │   └── factory.py        # Provider factory & registry
│   │   ├── models/               # Pure Financial Valuation Engines
│   │   │   ├── dcf.py
│   │   │   ├── graham.py
│   │   │   ├── ddm.py
│   │   │   ├── multiples.py
│   │   │   ├── black_scholes.py
│   │   │   ├── binomial_tree.py
│   │   │   └── implied_vol.py
│   │   └── api/v1/               # REST API Routes
│   │       ├── router.py
│   │       ├── stocks.py
│   │       ├── options.py
│   │       ├── market.py
│   │       └── knowledge.py
│   ├── tests/                    # Comprehensive Test Suite
│   ├── requirements.txt
│   └── run.py                    # Server startup script
│
├── frontend/                     # Thin React UI
│   ├── index.html                # Self-contained React SPA
│   └── package.json
└── README.md
```

---

## 🔌 How to Plug in a New Data Source

To integrate a new provider (e.g. Polygon.io, Alpha Vantage, Bloomberg, SEC EDGAR):

1. **Subclass `DataSourceProvider`** in `backend/app/datasources/`:
   ```python
   from backend.app.datasources.base import DataSourceProvider
   from backend.app.schemas.market_data import StockQuote, CompanyFinancials, OptionContractSummary

   class PolygonDataSource(DataSourceProvider):
       @property
       def name(self) -> str:
           return "polygon"

       async def get_quote(self, symbol: str) -> StockQuote:
           # Call Polygon quote API...
           pass

       async def get_financials(self, symbol: str) -> CompanyFinancials:
           # Call Polygon fundamentals API...
           pass

       async def get_option_chain_summary(self, symbol: str) -> list[OptionContractSummary]:
           # Call Polygon options API...
           pass

       async def get_risk_free_rate(self) -> float:
           return 0.045

       async def health_check(self) -> bool:
           return True
   ```

2. **Register it in `backend/app/datasources/factory.py`**:
   ```python
   from backend.app.datasources.polygon_source import PolygonDataSource
   DataSourceFactory.register("polygon", PolygonDataSource)
   ```

3. Clients can now query it instantly:
   ```bash
   curl "http://localhost:8000/api/v1/market/quote/AAPL?source=polygon"
   ```

---

## 🛠️ Quickstart Guide

### 1. Setup Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r backend/requirements.txt
```

### 2. Run the Service (Backend + Thin UI)
```bash
python3 backend/run.py
```
- Open **Thin UI**: [http://localhost:8000](http://localhost:8000)
- Interactive **Swagger Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
- Interactive **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

### 3. Run Unit and Integration Tests
```bash
pytest backend/tests/ -v
```

---

## 📡 Core API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/v1/stocks/evaluate/composite` | Blended fair value (DCF + Graham + DDM + Multiples) |
| `POST` | `/api/v1/stocks/evaluate/dcf` | 10-year multi-stage DCF valuation |
| `POST` | `/api/v1/stocks/evaluate/graham` | Benjamin Graham intrinsic value & Graham Number |
| `POST` | `/api/v1/stocks/evaluate/ddm` | Gordon Growth dividend model |
| `POST` | `/api/v1/stocks/evaluate/multiples` | P/E and P/B comparable valuation |
| `POST` | `/api/v1/options/evaluate/pricing` | Option price (Black-Scholes or CRR Binomial Tree) |
| `POST` | `/api/v1/options/evaluate/greeks` | Option Greeks ($\Delta, \Gamma, \Theta, \mathcal{V}, \rho$) |
| `POST` | `/api/v1/options/evaluate/implied-volatility` | Reverse implied volatility solver |
| `GET` | `/api/v1/options/evaluate/sensitivity` | 2D spot vs volatility sensitivity matrix |
| `GET` | `/api/v1/market/quote/{symbol}` | Current stock quote |
| `GET` | `/api/v1/market/financials/{symbol}` | Fundamentals autofill |
| `GET` | `/api/v1/knowledge/index` | Spec catalog index |
| `GET` | `/api/v1/knowledge/spec/{id}` | Full spec documentation |
# shareval
