# Finance KPI Pipeline — Automated Portfolio Analytics

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](#10-getting-started)
[![Yahoo Finance](https://img.shields.io/badge/Data-Yahoo%20Finance%20API-orange)](#5-data)
[![Analytics](https://img.shields.io/badge/KPIs-CAGR%20%7C%20Sharpe%20%7C%20Max%20DD-emerald)](#8-results--evaluation)
[![CLI Tool](https://img.shields.io/badge/CLI-Configurable%20Pipeline-purple)](#10-getting-started)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](#16-license--disclaimer)

An automated financial analytics pipeline that downloads market data for any ticker via Yahoo Finance, computes core quantitative performance and risk metrics (CAGR, Annualized Sharpe Ratio, Maximum Drawdown, Rolling Volatility), generates high-resolution 4-panel diagnostic equity dashboards, and exports consolidated CSV summaries in a single command.

---

## Table of Contents

- [1. What This Project Does](#1-what-this-project-does)
- [2. Why It Was Built](#2-why-it-was-built)
- [3. System Architecture](#3-system-architecture)
- [4. Tech Stack & Libraries](#4-tech-stack--libraries)
- [5. Data](#5-data)
- [6. Step-by-Step Pipeline](#6-step-by-step-pipeline)
- [7. Problems Faced & How We Solved Them](#7-problems-faced--how-we-solved-them)
- [8. Results & Evaluation](#8-results--evaluation)
- [9. Project Structure](#9-project-structure)
- [10. Getting Started](#10-getting-started)
- [11. API / CLI Reference](#11-api--cli-reference)
- [12. Deployment](#12-deployment)
- [13. Connected Portfolio Projects](#13-connected-portfolio-projects)
- [14. Limitations & Known Issues](#14-limitations--known-issues)
- [15. Roadmap / Future Expansion](#15-roadmap--future-expansion)
- [16. License & Disclaimer](#16-license--disclaimer)

---

## 1. What This Project Does

Given one or more asset tickers and a time window, the pipeline:

- **Downloads Adjusted Market Data**: Fetches full daily OHLCV series via Yahoo Finance (supporting Indian equities like `RELIANCE.NS`, `TCS.NS`, indices like `^NSEI`, or US equities like `AAPL`, `MSFT`).
- **Computes Institutional Risk-Return KPIs**:
  - **CAGR** (Compound Annual Growth Rate) accounting for exact calendar trading days.
  - **Annualized Volatility** ($\sigma_{\text{ann}}$) scaled to 252 trading sessions.
  - **Annualized Sharpe Ratio** relative to the Indian 10-Year G-Sec benchmark ($R_f = 6.5\%$) or user-configured rate.
  - **Maximum Drawdown (Max DD)** and peak-to-trough capital impairment from historical high-water marks.
- **Generates Publication-Quality Visual Diagnostics**: Generates a 4-panel chart per ticker:
  - *Panel 1*: Price trajectory & cumulative equity growth with drawdown shading.
  - *Panel 2*: Daily log return distribution over time.
  - *Panel 3*: Rolling 21-day and 63-day annualized volatility regimes.
  - *Panel 4*: Daily return histogram with Gaussian fit and percentile markers.
- **Exports Consolidated Cross-Asset Summaries**: Writes tabular multi-ticker comparisons directly to `outputs/kpi_summary.csv`.

---

## 2. Why It Was Built

- **Eliminating Manual Spreadsheet Errors**: Retail investors and analysts frequently miscalculate annualized returns and Sharpe ratios by neglecting compounding, leap trading days, dividend adjustments, or risk-free adjustments.
- **Consistent Benchmark Comparisons**: Provides a zero-dependency, reproducible CLI to compare individual equities against market indices under identical risk-free rate and calendar assumptions.
- **Automated Batch Processing**: Can process dozens of tickers across multiple sectors in seconds, dumping visual and tabular reports for portfolio screening.
- **Foundational Engine**: Acts as the core analytical engine reused in downstream projects like the Global Market HeatMap and Nifty Sector Rotation strategy.

---

## 3. System Architecture

```text
┌────────────────────────────────────────────────────────────────────────┐
│                        CLI INVOCATION & CONFIG                         │
│                                                                        │
│   CLI Arguments (--tickers, --start, --end, --risk_free, --output_dir) │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                        DATA INGESTION LAYER                            │
│                                                                        │
│   yfinance Fetcher: Download daily OHLCV series for each ticker        │
│   - Split- & dividend-adjusted closing price extraction (`Adj Close`)  │
│   - Missing date imputation and non-trading day alignment              │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                      QUANTITATIVE KPI ENGINE                           │
│                                                                        │
│   ├── Continuous Log Returns: r_t = ln(P_t / P_{t-1})                  │
│   ├── Compounded CAGR: (P_end / P_start)^(1 / years) - 1               │
│   ├── Annualized Volatility: std(r_t) * sqrt(252)                      │
│   ├── Annualized Sharpe Ratio: (mean(r_t) * 252 - R_f) / Ann_Vol       │
│   ├── High-Water Mark Drawdowns: (P_t - cummax(P_t)) / cummax(P_t)     │
│   └── Rolling 21-day & 63-day Volatility Regimes                       │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                    ┌───────────────┴───────────────┐
                    ▼                               ▼
┌───────────────────────────────────────┐ ┌──────────────────────────────┐
│       TABULAR EXPORT ENGINE           │ │   VISUAL DASHBOARD ENGINE    │
│                                       │ │                              │
│  outputs/kpi_summary.csv              │ │  outputs/{ticker}_kpi_       │
│  Consolidated multi-asset summary     │ │  dashboard.png (4-Panel)     │
└───────────────────────────────────────┘ └──────────────────────────────┘
```

---

## 4. Tech Stack & Libraries

| Library / Tool | Version | Purpose | Rationale |
|---|---|---|---|
| **Python** | `>=3.10` | Core runtime | Standard high-performance scientific programming runtime |
| **yfinance** | `^0.2.36` | Market data ingestion | Free, reliable access to global OHLCV history with split/dividend adjustments |
| **pandas** | `^2.1.0` | Time series manipulation | Fast indexed operations, date slicing, and tabular summaries |
| **numpy** | `^1.26.0` | Numerical calculations | Vectorized continuous log returns, standard deviation, and cumulative operations |
| **matplotlib** | `^3.8.0` | Diagnostic visual dashboard | Publication-grade 4-panel subplots with custom styling and shading |
| **argparse** | Standard lib | CLI argument parsing | Clean terminal interface with sensible defaults and flags |

---

## 5. Data

- **Source**: Yahoo Finance API via the `yfinance` library.
- **Format**: Daily OHLCV tabular time series (Open, High, Low, Close, Adj Close, Volume).
- **Scope**: Any valid Yahoo Finance ticker symbol globally (e.g., `^NSEI`, `RELIANCE.NS`, `TCS.NS`, `AAPL`, `MSFT`, `SPY`).
- **Horizon**: Configurable via CLI; typically 10–12 years (2014 to present) yielding ~2,700–3,000 trading sessions per symbol.
- **Preprocessing Applied**:
  - Split and dividend adjustment via `Adj Close` column to eliminate artificial price drops.
  - Continuous log return calculation: $r_t = \ln(P_t / P_{t-1})$.
  - Removal of non-trading days and forward-filling of any minor exchange reporting gaps.

---

## 6. Step-by-Step Pipeline

1. **CLI Parameter Ingestion**: Parse user arguments (`--tickers`, `--start`, `--end`, `--risk_free`, `--output_dir`).
2. **Sequential Market Data Download**: Query Yahoo Finance per ticker; isolate the `Adj Close` series and validate data completeness.
3. **Return Series Calculation**: Compute daily simple returns and continuous log returns:
   $$r_t = \ln\left(\frac{P_t}{P_{t-1}}\right)$$
4. **CAGR Computation**: Determine total duration in years from calendar dates and calculate compound annual growth rate:
   $$\text{CAGR} = \left(\frac{P_{\text{end}}}{P_{\text{start}}}\right)^{\frac{1}{\text{years}}} - 1$$
5. **Volatility & Sharpe Calculation**: Calculate standard deviation of daily log returns, scale by $\sqrt{252}$, and evaluate Sharpe against the annualized benchmark risk-free rate:
   $$\sigma_{\text{ann}} = \sigma_{\text{daily}} \times \sqrt{252}, \quad \text{Sharpe} = \frac{\bar{r}_{\text{daily}} \times 252 - R_f}{\sigma_{\text{ann}}}$$
6. **High-Water Mark Drawdown**: Compute rolling maximum and drawdowns:
   $$\text{Drawdown}_t = \frac{P_t - \max_{\tau \le t} P_\tau}{\max_{\tau \le t} P_\tau}, \quad \text{Max DD} = \min_t(\text{Drawdown}_t)$$
7. **Rolling Volatility Regimes**: Compute 21-day (short-term) and 63-day (quarterly) rolling annualized volatilities.
8. **Diagnostic Chart Generation**: Render a 4-panel subplot in matplotlib with equity curves, return scatter, rolling volatility bands, and return distribution histogram.
9. **Consolidated CSV Export**: Append ticker metrics to `outputs/kpi_summary.csv`.

---

## 7. Problems Faced & How We Solved Them

| Problem | Impact | How We Got Around It |
|---|---|---|
| **Yahoo Finance rate limiting** on batch ticker requests | Pipeline stalled mid-execution when fetching multiple tickers sequentially | Implemented sequential per-ticker fetching with dedicated try/except error handling and retry logic; the CLI processes tickers one by one with graceful failure isolation so one broken symbol does not crash the run |
| **Stock splits / dividends creating artificial price drops** | Raw close prices showed massive single-day drops (e.g., 2:1 stock split appearing as -50% crash) that weren't real losses, corrupting return and drawdown calculations | Exclusively used **adjusted close prices** from yfinance (`Adj Close`), which are retroactively corrected for splits and dividend distributions |
| **Inconsistent trading day counts** across exchanges | Annualization using 252 days was inaccurate for some asset classes and years with fewer sessions | Standardized on the 252-day convention (`np.sqrt(252)`) consistent with institutional practice, and computed actual trading duration from the data index for CAGR |
| **Simple returns vs log returns confusion** | Using simple returns for volatility estimation led to statistical instability and non-additivity across multi-year horizons | Adopted **continuous logarithmic returns** ($\ln(P_t/P_{t-1})$) for all volatility and Sharpe calculations, ensuring time-additivity and distributional stability |
| **Drawdown calculation errors** with rolling windows | Trailing periodic windows missed the true peak-to-trough decline from lifetime highs | Implemented **high-water mark** peak-to-trough drawdown using `cummax()` to track running maximum, measuring absolute capital impairment from lifetime peaks |

---

## 8. Results & Evaluation

### Benchmark Run (2014–2026 Evaluation, $R_f = 6.5\%$)

| Ticker | Asset Name | CAGR | Annualized Volatility | Sharpe Ratio ($R_f=6.5\%$) | Max Drawdown |
|---|---|:---:|:---:|:---:|:---:|
| `^NSEI` | Nifty 50 Benchmark Index | **11.38%** | **15.2%** | **0.366** | **−38.44%** |
| `RELIANCE.NS` | Reliance Industries Ltd | **17.75%** | **22.4%** | **0.514** | **−45.09%** |
| `TCS.NS` | Tata Consultancy Services | **9.34%** | **18.1%** | **0.229** | **−44.09%** |

### Mathematical Formulations

| Metric | Formula | Notes |
|---|---|---|
| **CAGR** | $(P_{\text{end}} / P_{\text{start}})^{\frac{1}{\text{years}}} - 1$ | Exact calendar time span calculation |
| **Ann. Volatility** | $\sigma_{\text{daily}} \times \sqrt{252}$ | Continuous log returns basis |
| **Sharpe Ratio** | $(\bar{r} \times 252 - R_f) / \sigma_{\text{ann}}$ | Defaults to $R_f = 6.5\%$ (India 10Y G-Sec) |
| **Max Drawdown** | $\min_t \left(\frac{P_t - \max_{\tau \le t} P_\tau}{\max_{\tau \le t} P_\tau}\right)$ | True lifetime high-water mark decline |

---

## 9. Project Structure

```text
Finance_KPI/
├── kpi_pipeline.py     # Production CLI pipeline script
├── main.ipynb          # Interactive exploratory analysis & visualization notebook
├── requirements.txt    # Python dependencies (yfinance, pandas, matplotlib, numpy)
├── Readme.md           # Project documentation
└── outputs/            # Generated artifacts
    ├── kpi_summary.csv # Consolidated multi-asset metrics table
    └── *.png           # 4-panel diagnostic dashboards per ticker
```

---

## 10. Getting Started

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

Run with default parameters (Nifty 50 from 2014 to present):

```bash
python kpi_pipeline.py
```

Run with multiple custom tickers and a custom start date:

```bash
python kpi_pipeline.py --tickers RELIANCE.NS TCS.NS HDFCBANK.NS --start 2018-01-01
```

Run with a custom risk-free rate ($7.0\%$ instead of default $6.5\%$):

```bash
python kpi_pipeline.py --tickers ^NSEI --start 2014-01-01 --risk_free 0.07
```

Specify a custom output directory:

```bash
python kpi_pipeline.py --tickers AAPL MSFT NVDA --output_dir my_reports/
```

### 3. Interactive Notebook

To explore individual calculations step-by-step or customize visualizations interactively:

```bash
jupyter notebook main.ipynb
```

---

## 11. API / CLI Reference

### Command-Line Arguments

| Argument | Type | Default | Description |
|---|---|---|---|
| `--tickers` | `str` (list) | `^NSEI` | One or more space-separated Yahoo Finance symbols |
| `--start` | `str` | `2014-01-01` | Start date in `YYYY-MM-DD` format |
| `--end` | `str` | Today | End date in `YYYY-MM-DD` format |
| `--risk_free` | `float` | `0.065` | Annualized risk-free benchmark rate in decimal (e.g., `0.065` = 6.5%) |
| `--output_dir` | `str` | `outputs/` | Target directory where PNG dashboards and CSV summary are saved |

### Sample Output File (`outputs/kpi_summary.csv`)

```csv
Ticker,Start_Date,End_Date,Years,CAGR,Ann_Vol,Sharpe,Max_Drawdown
^NSEI,2014-01-01,2026-03-01,12.16,0.1138,0.1520,0.366,-0.3844
RELIANCE.NS,2014-01-01,2026-03-01,12.16,0.1775,0.2240,0.514,-0.4509
TCS.NS,2014-01-01,2026-03-01,12.16,0.0934,0.1810,0.229,-0.4409
```

---

## 12. Deployment

The pipeline is self-contained and requires no daemon or background server:

- **Cron Scheduling**: Can be scheduled daily via Linux cron or Windows Task Scheduler to pull end-of-day market closes:
  ```bash
  # Daily cron run at 16:00 IST
  0 16 * * 1-5 /path/to/venv/bin/python /path/to/kpi_pipeline.py --tickers ^NSEI RELIANCE.NS TCS.NS
  ```
- **Docker Containerization**: Easily containerized to push summaries into cloud storage (AWS S3 / Azure Blob).

---

## 13. Connected Portfolio Projects

- **[Global Market HeatMap](https://github.com/RaajitSingh1306/Global-Equity-Market-Dashboard)**: Scales this single-ticker KPI engine across 35 Indian and US equities with a live Streamlit and Power BI dashboard.
- **[Nifty Sector Rotation](https://github.com/RaajitSingh1306/Nifty-Sector-Rotation)**: Applies rolling momentum and volatility KPIs to rank and dynamically rebalance across 10 sector indices.
- **[Volatility Intelligence Platform](https://github.com/RaajitSingh1306/volatility-intelligence-platform)**: Upgrades static rolling volatility with conditional GARCH(1,1) econometrics and HMM regime discovery.

---

## 14. Limitations & Known Issues

- **Batch EOD Only**: Designed for end-of-day batch data; does not process intraday streaming tick feeds or order books.
- **No Currency Normalization**: Multi-asset runs compare USD and INR equities in local currency terms without applying historical FX conversion rates.
- **Independent Asset Calculation**: Computes metrics per individual asset; does not calculate portfolio covariance matrices or diversified Sharpe ratios.
- **Fixed Rolling Windows**: Rolling windows (21-day short-term, 63-day medium-term) are static; does not implement regime-adaptive lookback lengths.
- **Downside Risk Metrics**: Computes standard Sharpe ratio and Max Drawdown; does not calculate asymmetric downside ratios (Sortino ratio, Calmar ratio, Omega ratio).

---

## 15. Roadmap / Future Expansion

- [ ] **Portfolio-Level Covariance & Sharpe**: Implement Markowitz portfolio weighting, correlation matrices, and portfolio-aggregate Sharpe computation.
- [ ] **Downside Metrics Suite**: Add Sortino ratio (penalizing downside semi-deviation only) and Calmar ratio (CAGR / Max Drawdown).
- [ ] **Currency-Adjusted Global Benchmarking**: Integrate historical USD/INR exchange rates to compute unified multi-currency risk-adjusted metrics.
- [ ] **Automated S3 Export**: Add an S3 push flag to automatically sync daily CSV outputs into an analytical data lake.

---

## 16. License & Disclaimer

### License
This project is licensed under the [MIT License](https://opensource.org/licenses/MIT).

### Disclaimer
This software is intended strictly for quantitative research, educational analysis, and portfolio diagnostics. It does not constitute investment advice or financial recommendations.
