# Finance KPI Pipeline — Automated Portfolio Analytics

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](#prerequisites)
[![Yahoo Finance](https://img.shields.io/badge/Data-Yahoo%20Finance%20API-orange)](#data-layer)
[![Analytics](https://img.shields.io/badge/KPIs-CAGR%20%7C%20Sharpe%20%7C%20Max%20DD-emerald)](#kpis-computed)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An automated financial analytics pipeline that downloads market data for any ticker via Yahoo Finance, computes core quantitative performance and risk metrics (CAGR, Annualized Sharpe Ratio, Maximum Drawdown, Rolling Volatility), generates high-resolution 4-panel diagnostic equity dashboards, and exports consolidated CSV summaries in a single command.

---

## Table of Contents

1. [What This Project Does](#what-this-project-does)
2. [Why It Was Built](#why-it-was-built)
3. [KPIs Computed & Formulations](#kpis-computed--formulations)
4. [Sample Results (2014–2026 Backtest)](#sample-results-20142026-backtest)
5. [Architecture & Pipeline Flow](#architecture--pipeline-flow)
6. [Project Directory Layout](#project-directory-layout)
7. [Where & How to Start](#where--how-to-start)
8. [Generated Artifacts](#generated-artifacts)
9. [Connected Portfolio Projects](#connected-portfolio-projects)

---

## What This Project Does

Given one or more asset tickers and a time window, the pipeline:

1. **Fetches Adjusted Market Data**: Downloads complete daily OHLCV series from Yahoo Finance (supporting Indian equities like `RELIANCE.NS`, `TCS.NS`, indices like `^NSEI`, or US equities like `AAPL`, `MSFT`).
2. **Computes Institutional Risk-Return KPIs**:
   - **CAGR** (Compound Annual Growth Rate)
   - **Annualized Volatility** ($\sigma_{\text{ann}}$)
   - **Annualized Sharpe Ratio** ($R_f = 6.5\%$ standard Indian 10-year G-Sec benchmark or custom rate)
   - **Maximum Drawdown (Max DD)** and peak-to-trough recovery duration
3. **Generates Multi-Panel Visual Diagnostics**: Saves a publication-quality 4-panel chart per ticker:
   - Panel 1: Price trajectory & cumulative equity growth with drawdown shading
   - Panel 2: Daily log return distribution over time
   - Panel 3: Rolling 21-day and 63-day annualized volatility regimes
   - Panel 4: Daily return histogram with Gaussian fit and percentile markers
4. **Exports Consolidated CSV Summaries**: Writes cross-asset metric comparisons directly to `outputs/kpi_summary.csv`.

---

## Why It Was Built

1. **Eliminating Manual Spreadsheet Calculations**: Retail investors and analysts frequently miscalculate annualized returns and Sharpe ratios by neglecting compounding, leap trading days, or risk-free adjustments.
2. **Consistent Benchmark Comparisons**: Provides a zero-dependency, reproducible CLI to compare individual equities against market indices under identical risk-free rate and calendar assumptions.
3. **Automated Batch Processing**: Can process dozens of tickers across multiple sectors in seconds, dumping visual and tabular reports for portfolio monitoring.

---

## KPIs Computed & Formulations

| KPI | Mathematical Formulation | Description & Assumptions |
|---|---|---|
| **CAGR** | $\left(\frac{P_{\text{end}}}{P_{\text{start}}}\right)^{\frac{1}{\text{years}}} - 1$ | Geometric mean annual growth rate accounting for exact trading duration. |
| **Annualized Volatility** | $\sigma_{\text{daily}} \times \sqrt{252}$ | Standard deviation of daily log returns scaled to annualized trading sessions ($N=252$). |
| **Sharpe Ratio** | $\frac{\bar{r}_{\text{daily}} \times 252 - R_f}{\sigma_{\text{daily}} \times \sqrt{252}}$ | Excess return per unit of volatility relative to benchmark risk-free rate ($R_f = 6.5\%$). |
| **Max Drawdown** | $\min_t \left(\frac{P_t - \max_{\tau \le t} P_\tau}{\max_{\tau \le t} P_\tau}\right)$ | Maximum percentage capital destruction from a historical high before a new peak is formed. |

---

## Sample Results (2014–2026 Backtest)

Benchmark run comparing Nifty 50 against top Indian blue-chips over a 12-year window ($R_f = 6.5\%$):

| Ticker | Asset Name | CAGR | Ann. Vol | Sharpe Ratio | Max Drawdown |
|---|---|---|---|---|---|
| `^NSEI` | Nifty 50 Index | **11.38%** | 15.2% | **0.366** | **−38.44%** |
| `RELIANCE.NS` | Reliance Industries | **17.75%** | 22.4% | **0.514** | **−45.09%** |
| `TCS.NS` | Tata Consultancy Services | **9.34%** | 18.1% | **0.229** | **−44.09%** |

---

## Architecture & Pipeline Flow

```text
CLI Arguments (--tickers, --start, --risk_free)
                     │
                     ▼
             yfinance Fetcher (daily OHLCV download)
                     │
                     ▼
           KPI Computation Engine
        ├── Daily & Log Returns
        ├── Cumulative Compounding
        ├── Rolling 21d / 63d Volatility
        └── High-Water Mark & Peak-to-Trough Drawdowns
                     │
        ┌────────────┴────────────┐
        ▼                         ▼
outputs/kpi_summary.csv   outputs/{ticker}_kpi_dashboard.png
(Multi-asset comparison)  (4-Panel visual diagnostic chart)
```

---

## Key Design Decisions

- **252 Trading Days Convention**: Standardized across exchange trading calendars (~250–252 trading days per year); annualization uses `np.sqrt(252)` for standard deviation and `(1 + R)^(252/N) - 1` for annualized returns.
- **Configurable Risk-Free Benchmark ($R_f$)**: Defaults to 6.5% (reflective of the India 10-Year Benchmark G-Sec yield over the evaluation horizon), with CLI runtime override via `--risk_free` to facilitate comparisons with US Treasury rates.
- **Log Returns for Volatility and Sharpe**: Uses continuous logarithmic returns for standard deviation estimation ($\sigma_{ann} = \text{std}(\ln(P_t/P_{t-1})) \times \sqrt{252}$), ensuring additivity and statistical stability.
- **High-Water Mark Peak-to-Trough Drawdown**: Uses cumulative running maximum (`cummax()`) rather than trailing periodic windows to measure absolute capital impairment from lifetime peaks.
- **Adjusted Close Price Basis**: Consistently utilizes split- and dividend-adjusted closing prices from `yfinance` to prevent artificial structural price drops from skewing return and drawdown calculations.

---

## Project Directory Layout

```text
Finance_KPI/
├── kpi_pipeline.py     # Production CLI pipeline script
├── main.ipynb          # Interactive exploratory analysis & visualization notebook
├── requirements.txt    # Python dependencies (yfinance, pandas, matplotlib, numpy)
├── Readme.md           # Project documentation
└── outputs/            # Generated outputs
    ├── kpi_summary.csv # Combined metrics table
    └── *.png           # 4-panel diagnostic dashboards per ticker
```

---

## Where & How to Start

### Prerequisites

* Python 3.10 or higher
* Internet connectivity for Yahoo Finance API requests

### 1. Setup Environment

```bash
cd "Finance_KPI"

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# Linux / macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Execute CLI Pipeline

Run the pipeline with default parameters (Nifty 50 from 2014 to present):

```bash
python kpi_pipeline.py
```

Run with multiple custom tickers and a custom start date:

```bash
python kpi_pipeline.py --tickers RELIANCE.NS TCS.NS HDFCBANK.NS --start 2018-01-01
```

Run with a custom risk-free rate ($7\%$ instead of default $6.5\%$):

```bash
python kpi_pipeline.py --tickers ^NSEI --start 2014-01-01 --risk_free 0.07
```

Specify a custom output folder:

```bash
python kpi_pipeline.py --tickers AAPL MSFT NVDA --output_dir my_reports/
```

### CLI Command Options

| Argument | Type | Default | Description |
|---|---|---|---|
| `--tickers` | list | `^NSEI` | One or more Yahoo Finance symbols |
| `--start` | str | `2014-01-01` | Start date in `YYYY-MM-DD` format |
| `--end` | str | Today | End date in `YYYY-MM-DD` format |
| `--risk_free` | float | `0.065` | Annualized risk-free benchmark rate (decimal) |
| `--output_dir` | str | `outputs/` | Target directory for charts and summary CSV |

### 3. Interactive Notebook

To explore individual calculations step-by-step or customize visualizations interactively:

```bash
jupyter notebook main.ipynb
```

---

## Generated Artifacts

Executing the script automatically populates the `outputs/` directory:

1. **`outputs/kpi_summary.csv`**:
   Contains tabular metrics (`Ticker`, `Start_Date`, `End_Date`, `Years`, `CAGR`, `Ann_Vol`, `Sharpe`, `Max_Drawdown`).
2. **`outputs/{TICKER}_kpi_dashboard.png`**:
   High-resolution PNG file presenting the 4-panel visual audit.

---

## Connected Portfolio Projects

* **[Global Market HeatMap](https://github.com/RaajitSingh1306/Global-Equity-Market-Dashboard)**: Scales this KPI engine across 35 Indian and US equities with a live Streamlit and Power BI dashboard.
* **[Nifty Sector Rotation](https://github.com/RaajitSingh1306/Nifty-Sector-Rotation)**: Applies rolling momentum and volatility KPIs to rank and rebalance across 10 sector indices.
* **[Volatility Intelligence Platform](https://github.com/RaajitSingh1306/volatility-intelligence-platform)**: Replaces static rolling volatility with conditional GARCH(1,1) econometrics and HMM regime discovery.

---

## Limitations & Roadmap

### Known Limitations
- **Batch Processing Only**: Designed for batch EOD data ingestion; does not process real-time streaming websocket feeds.
- **No Multi-Currency Normalization**: Multi-asset runs compare USD and INR equities in their respective local currencies without applying historical FX conversion rates.
- **Independent Asset Evaluation**: Computes metrics per individual asset; does not calculate asset-to-asset covariance, correlation matrices, or portfolio-level Sharpe ratios.
- **Fixed Rolling Windows**: Rolling windows (21-day short-term, 63-day medium-term) are static; does not implement regime-adaptive lookback lengths.
- **Downside Risk Metrics**: Computes standard Sharpe ratio and Max Drawdown; does not calculate asymmetric downside ratios (Sortino ratio, Calmar ratio, Omega ratio).

### Roadmap
- [ ] **Portfolio-Level Covariance & Sharpe**: Implement Markowitz portfolio weighting, correlation matrices, and portfolio-aggregate Sharpe computation.
- [ ] **Downside Metrics Suite**: Add Sortino ratio (penalizing downside semi-deviation only) and Calmar ratio (CAGR / Max Drawdown).
- [ ] **Currency-Adjusted Global Benchmarking**: Integrate historical USD/INR exchange rates to compute unified multi-currency risk-adjusted metrics.
- [ ] **Automated Daily Cron Refresh**: Package the pipeline as a Docker container scheduled via cron to push updated KPI summaries to S3 or cloud storage.

---

## License & Disclaimer

MIT License. Designed for quantitative analysis and portfolio diagnostics. Does not constitute financial advice.
