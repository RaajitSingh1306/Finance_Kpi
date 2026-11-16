# Finance KPI Pipeline — Automated Portfolio Analytics

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](#10-getting-started)
[![Yahoo Finance](https://img.shields.io/badge/Data-Yahoo%20Finance%20API-orange)](#5-data)
[![Analytics](https://img.shields.io/badge/KPIs-CAGR%20%7C%20Sharpe%20%7C%20Max%20DD-emerald)](#8-results--evaluation)
[![CLI Tool](https://img.shields.io/badge/CLI-Configurable%20Pipeline-purple)](#10-getting-started)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](#16-license--disclaimer)

An automated financial analytics pipeline that downloads market data for any ticker via Yahoo Finance, computes core quantitative performance and risk metrics (CAGR, Annualized Sharpe Ratio, Sortino, Calmar, Maximum Drawdown), generates high-resolution 4-panel diagnostic equity dashboards, and exports consolidated CSV summaries in a single command.

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

- **Downloads Adjusted Market Data**: Fetches daily OHLCV via Yahoo Finance and keeps the adjusted `Close` (supporting Indian equities like `RELIANCE.NS`, `TCS.NS`, indices like `^NSEI`, or US equities like `AAPL`, `MSFT`).
- **Computes Institutional Risk-Return KPIs**:
  - **CAGR** (Compound Annual Growth Rate) using calendar days between first and last close (/ 365.25).
  - **Annualized Sharpe Ratio** relative to the Indian 10-Year G-Sec benchmark ($R_f = 6.5\%$) or user-configured rate.
  - **Maximum Drawdown (Max DD)** and peak-to-trough capital impairment from historical high-water marks.
- **Generates Publication-Quality Visual Diagnostics**: Generates a 4-panel chart per ticker:
  - *Panel 1*: Price vs CAGR trendline
  - *Panel 2*: Drawdown
  - *Panel 3*: Rolling Sharpe (252-day)
  - *Panel 4*: Annualised mean daily return per calendar year (mean x 252; latest year is partial)
- **Exports Consolidated Cross-Asset Summaries**: Writes tabular multi-ticker comparisons directly to `outputs/kpi_summary_combined.csv`.

---

## 2. Why It Was Built

- **Eliminating Manual Spreadsheet Errors**: Retail investors and analysts frequently miscalculate annualized returns and Sharpe ratios by neglecting compounding, leap trading days, dividend adjustments, or risk-free adjustments.
- **Consistent Benchmark Comparisons**: Provides a reproducible CLI to compare individual equities against market indices under identical risk-free rate and calendar assumptions.
- **Automated Batch Processing**: Processes any list of tickers sequentially in one command and writes a chart per ticker plus one summary csv.
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
│   - Split- & dividend-adjusted closing price extraction (`Close`)      │
│   - Rows with missing Close dropped (no imputation)                    │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                      QUANTITATIVE KPI ENGINE                           │
│                                                                        │
│   ├── Compounded CAGR: (P_end / P_start)^(1 / years) - 1               │
│   ├── Annualized Sharpe Ratio: mean(excess) / std(excess) * sqrt(252)  │
│   └── High-Water Mark Drawdowns: (P_t - cummax(P_t)) / cummax(P_t)     │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                    ┌───────────────┴───────────────┐
                    ▼                               ▼
┌───────────────────────────────────────┐ ┌──────────────────────────────┐
│       TABULAR EXPORT ENGINE           │ │   VISUAL DASHBOARD ENGINE    │
│                                       │ │                              │
│  outputs/kpi_summary_combined.csv     │ │  outputs/kpi_report_*.png    │
│  Consolidated multi-asset summary     │ │  4-panel PNG per ticker      │
└───────────────────────────────────────┘ └──────────────────────────────┘
```

---

## 4. Tech Stack & Libraries

| Library / Tool | Version | Purpose | Rationale |
| --- | --- | --- | --- |
| **Python** | `>=3.10` | Core runtime | Standard high-performance scientific programming runtime |
| **yfinance** | `>=0.2.36` (results produced on 1.2.0) | Market data ingestion | Free, reliable access to global OHLCV history with split/dividend adjustments |
| **pandas** | `>=2.0` | Time series manipulation | Fast indexed operations, date slicing, and tabular summaries |
| **numpy** | `>=1.24` | Numerical calculations | Vectorized returns, standard deviation, and cumulative operations |
| **matplotlib** | `>=3.7` | Diagnostic visual dashboard | Publication-grade 4-panel subplots with custom styling and shading |
| **argparse** | Standard lib | CLI argument parsing | Clean terminal interface with sensible defaults and flags |

---

## 5. Data

- **Source**: Yahoo Finance API via the `yfinance` library.
- **Format**: Daily OHLCV from Yahoo Finance; only the adjusted `Close` is used.
- **Scope**: Any valid Yahoo Finance ticker symbol globally (e.g., `^NSEI`, `RELIANCE.NS`, `TCS.NS`, `AAPL`, `MSFT`, `SPY`).
- **Horizon**: Configurable via CLI; typically 10–12 years (2014 to present) yielding ~2,700–3,000 trading sessions per symbol.
- **Preprocessing Applied**:
  - Split and dividend adjustment via `yf.download(..., auto_adjust=True)`, so `Close` is already adjusted, eliminating artificial price drops.
  - Rows with a missing Close are dropped (dropna); no forward-filling.

---

## 6. Step-by-Step Pipeline

1. **CLI Parameter Ingestion**: Parse user arguments (`--tickers`, `--start`, `--end`, `--risk_free`, `--output_dir`).
2. **Sequential Market Data Download**: Query Yahoo Finance per ticker; keep the adjusted `Close` series and validate data completeness.
3. **Return Series Calculation**: Compute daily simple returns (pct_change):
   $$r_t = \frac{P_t}{P_{t-1}} - 1$$
4. **CAGR Computation**: Determine total duration in years from calendar dates and calculate compound annual growth rate:
   $$\text{CAGR} = \left(\frac{P_{\text{end}}}{P_{\text{start}}}\right)^{\frac{1}{\text{years}}} - 1$$
5. **Sharpe Calculation**: Compute the ratio of mean daily excess simple returns to their standard deviation, scaled by $\sqrt{252}$ against the daily benchmark risk-free rate:
   $$\text{Sharpe} = \frac{\overline{r_t - r_f}}{\sigma_{r_t - r_f}} \times \sqrt{252}, \quad r_f = R_f/252$$
6. **High-Water Mark Drawdown**: Compute rolling maximum and drawdowns:
   $$\text{Drawdown}_t = \frac{P_t - \max_{\tau \le t} P_\tau}{\max_{\tau \le t} P_\tau}, \quad \text{Max DD} = \min_t(\text{Drawdown}_t)$$
7. **Diagnostic Chart Generation**: Render a 4-panel subplot in matplotlib with Price vs CAGR trendline, Drawdown, Rolling Sharpe 252d, and per-year annualised mean daily return (mean x 252).
8. **Consolidated CSV Export**: Write all ticker metrics (overwriting any previous file) to `outputs/kpi_summary_combined.csv`.

---

## 7. Problems Faced & How We Solved Them

| Problem | Impact | How We Got Around It |
| --- | --- | --- |
| **Yahoo Finance rate limiting** on batch ticker requests | Pipeline stalled mid-execution when fetching multiple tickers sequentially | Implemented sequential per-ticker fetching with dedicated try/except error handling (no automatic retry); the CLI processes tickers one by one with graceful failure isolation so one broken symbol does not crash the run |
| **Stock splits / dividends creating artificial price drops** | Raw close prices showed massive single-day drops (e.g., 2:1 stock split appearing as -50% crash) that weren't real losses, corrupting return and drawdown calculations | Exclusively used **adjusted close prices** from yfinance (`auto_adjust=True`, which makes `Close` adjusted), which are retroactively corrected for splits and dividend distributions |
| **Inconsistent trading day counts** across exchanges | Annualization using 252 days was inaccurate for some asset classes and years with fewer sessions | Kept the 252-day convention (`np.sqrt(252)`) for every market (see Limitations) and computed CAGR duration from calendar days (first to last date / 365.25) |
| **Drawdown calculation errors** with rolling windows | Trailing periodic windows missed the true peak-to-trough decline from lifetime highs | Implemented **high-water mark** peak-to-trough drawdown using `cummax()` to track running maximum, measuring absolute capital impairment from lifetime peaks |

---

## 8. Results & Evaluation

### Benchmark Run (2014–2026 Evaluation, $R_f = 6.5\%$)

Data: Yahoo Finance daily closes. First close 2014-01-01 (RELIANCE.NS, TCS.NS) / 2014-01-02 (^NSEI); last close 2026-02-27.

```bash
python kpi_pipeline.py --tickers RELIANCE.NS TCS.NS "^NSEI" --start 2014-01-01 --end 2026-03-01
```

`--end` is exclusive and defaults to today, so pin it for repeatable results (2026-03-01 is a Sunday, so the last row is Fri 2026-02-27)

| Ticker | Asset Name | CAGR | Sharpe Ratio ($R_f=6.5\%$) | Max Drawdown |
| --- | --- | :---: | :---: | :---: |
| `^NSEI` | Nifty 50 Benchmark Index | **12.19%** | **0.412** | **-38.44%** |
| `RELIANCE.NS` | Reliance Industries Ltd | **17.9%** | **0.519** | **-45.09%** |
| `TCS.NS` | Tata Consultancy Services | **10.19%** | **0.262** | **-40.31%** |

### Mathematical Formulations

| Metric | Formula | Notes |
| --- | ---- | --- |
| **CAGR** | $(P_{\text{end}} / P_{\text{start}})^{\frac{1}{\text{years}}} - 1$ | Years = calendar days between first and last close / 365.25 |
| **Sharpe Ratio** | $\dfrac{\overline{r_t - R_f/252}}{\sigma(r_t - R_f/252)} \times \sqrt{252}$ | Daily simple returns; $R_f$ is annual (default 6.5%, India 10Y G-Sec proxy), converted to daily by $/252$ |
| **Sortino Ratio** | $\dfrac{\overline{e_t}}{\sqrt{\overline{\min(e_t,0)^2}}} \times \sqrt{252}$, $e_t = r_t - R_f/252$ | Downside deviation over all days (target = daily $R_f$) |
| **Calmar Ratio** | $\text{CAGR} / \lvert \text{Max DD} \rvert$ | Max DD as defined below |
| **Max Drawdown** | $\min_t \left(\frac{P_t - \max_{\tau \le t} P_\tau}{\max_{\tau \le t} P_\tau}\right)$ | True lifetime high-water mark decline |

---

## 9. Project Structure

```text
Finance_KPI/
├── kpi_pipeline.py               # Production CLI pipeline script
├── main.ipynb                    # Interactive exploratory analysis & visualization notebook
├── requirements.txt              # Python dependencies (yfinance, pandas, matplotlib, numpy)
├── Readme.md                     # Project documentation
└── outputs/                      # Generated artifacts
    ├── kpi_summary_combined.csv  # Consolidated multi-asset metrics table
    └── *.png                     # 4-panel diagnostic dashboards per ticker
```

---

## 10. Getting Started

### 1. Setup Environment

```bash
git clone https://github.com/RaajitSingh1306/Finance_Kpi.git
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
| --- | --- | --- | --- |
| `--tickers` | `str` (list) | `^NSEI` | One or more space-separated Yahoo Finance symbols |
| `--start` | `str` | `2014-01-01` | Start date in `YYYY-MM-DD` format |
| `--end` | `str` | Today (pin for repeatability) | End date in `YYYY-MM-DD` format |
| `--risk_free` | `float` | `0.065` | Annualized risk-free benchmark rate in decimal (e.g., `0.065` = 6.5%) |
| `--output_dir` | `str` | `outputs/` | Target directory where PNG dashboards and CSV summary are saved |

### Sample Output File (`outputs/kpi_summary_combined.csv`)

```csv
ticker,start_date,end_date,start_price,end_price,cagr_pct,sharpe,sortino,calmar,max_dd_pct,max_dd_date,n_years
RELIANCE.NS,2014-01-01,2026-02-27,187.47,1387.48,17.9,0.519,0.774,0.397,-45.09,2020-03-23,12.16
TCS.NS,2014-01-01,2026-02-27,791.73,2574.24,10.19,0.262,0.375,0.253,-40.31,2026-02-24,12.16
^NSEI,2014-01-02,2026-02-27,6221.15,25178.65,12.19,0.412,0.564,0.317,-38.44,2020-03-23,12.15
```

---

## 12. Deployment

The pipeline is self-contained and requires no daemon or background server:

- **Cron Scheduling**: Can be scheduled daily via Linux cron or Windows Task Scheduler to pull end-of-day market closes:

  ```bash
  # Daily cron run at 16:00 IST
  0 16 * * 1-5 /path/to/venv/bin/python /path/to/kpi_pipeline.py --tickers ^NSEI RELIANCE.NS TCS.NS
  ```

- **Docker / cloud upload**: not included (no Dockerfile or S3 upload in this repo; see Roadmap).

---

## 13. Connected Portfolio Projects

- **[Global Market HeatMap](https://github.com/RaajitSingh1306/Global-Equity-Market-Dashboard)**: Scales this single-ticker KPI engine across 35 Indian and US equities with a live Streamlit and Power BI dashboard.
- **[Nifty Sector Rotation](https://github.com/RaajitSingh1306/Nifty-Sector-Rotation)**: Applies rolling momentum and volatility KPIs to rank and dynamically rebalance across 10 sector indices.
- **[Volatility Intelligence Platform](https://github.com/RaajitSingh1306/volatility-intelligence-platform)**: Separate project: GARCH(1,1) conditional volatility and HMM regime detection (not part of this pipeline).

---

## 14. Limitations & Known Issues

- **Batch EOD Only**: Designed for end-of-day batch data; does not process intraday streaming tick feeds or order books.
- **No Currency Normalization**: Multi-asset runs compare USD and INR equities in local currency terms without applying historical FX conversion rates.
- **Independent Asset Calculation**: Computes metrics per individual asset; does not calculate portfolio covariance matrices or diversified Sharpe ratios.
- **Downside Risk Metrics**: Computes Sharpe, Sortino, Calmar and Max Drawdown; Omega ratio is not implemented.
- **Constant risk-free rate**: R_f is a flat 6.5% assumption over the whole window, not the historical 10Y G-Sec yield.
- **Price index vs adjusted stocks**: `^NSEI` is a price index (dividends excluded) while stock closes are dividend-adjusted, so stock-vs-index comparisons favour the stocks.
- **252-day convention**: Sharpe and Sortino annualise with 252 days for every market.

---

## 15. Roadmap / Future Expansion

- [ ] **Portfolio-Level Covariance & Sharpe**: Implement Markowitz portfolio weighting, correlation matrices, and portfolio-aggregate Sharpe computation.
- [ ] **Currency-Adjusted Global Benchmarking**: Integrate historical USD/INR exchange rates to compute unified multi-currency risk-adjusted metrics.
- [ ] **Automated S3 Export**: Add an S3 push flag to automatically sync daily CSV outputs into an analytical data lake.

---

## 16. License & Disclaimer

### License

This project is licensed under the [MIT License](https://opensource.org/licenses/MIT).

### Disclaimer

This software is intended strictly for quantitative research, educational analysis, and portfolio diagnostics. It does not constitute investment advice or financial recommendations.
