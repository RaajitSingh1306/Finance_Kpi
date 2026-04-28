# P3 — Finance KPI Pipeline

Automated pipeline that downloads market data for any ticker via Yahoo Finance,
computes key financial KPIs, generates a 4-panel chart, and saves a combined CSV summary 
triggered by a single command.

---

## KPIs Computed

| KPI | Formula | Notes |
|---|---|---|
| CAGR | `(P_end / P_start)^(1/years) − 1` | Full date range |
| Sharpe Ratio | `mean(excess_ret) / std(ret) × √252` | Rf = 6.5% (India 10yr G-Sec) |
| Max Drawdown | `min((price − cummax) / cummax)` | Worst peak-to-trough % |

---

## Results — 12yr Backtest (2014–2026)

| Ticker | CAGR | Sharpe | Max DD |
|---|---|---|---|
| Nifty 50 (`^NSEI`) | 11.38% | 0.366 | −38.44% |
| Reliance (`RELIANCE.NS`) | 17.75% | 0.514 | −45.09% |
| TCS (`TCS.NS`) | 9.34% | 0.229 | −44.09% |

---

## Setup

```bash
pip install -r requirements.txt
```

---

## Usage

```bash
# Default — Nifty 50, 2014 to today
python kpi_pipeline.py

# Custom tickers and date range
python kpi_pipeline.py --tickers RELIANCE.NS TCS.NS HDFCBANK.NS --start 2018-01-01

# With custom risk-free rate
python kpi_pipeline.py --tickers ^NSEI --start 2014-01-01 --risk_free 0.07
```

### Arguments

| Flag | Default | Description |
|---|---|---|
| `--tickers` | `^NSEI` | One or more Yahoo Finance symbols |
| `--start` | `2014-01-01` | Start date (YYYY-MM-DD) |
| `--end` | today | End date (YYYY-MM-DD) |
| `--risk_free` | `0.065` | Annualised risk-free rate (decimal) |
| `--output_dir` | `outputs/` | Directory for charts and CSV |

---

## Output

```
outputs/
├── kpi_report_NSEI.png          ← 4-panel chart per ticker
├── kpi_report_RELIANCE_NS.png
└── kpi_summary_combined.csv     ← all KPIs in one file
```

**Chart panels:** Price vs CAGR trendline · Drawdown · Rolling Sharpe (252d) · Annual returns bar

---

## File Structure

```
03_kpi_pipeline/
├── kpi_pipeline.py     ← pipeline (data → KPIs → charts → CSV)
├── main.ipynb          ← exploratory notebook
├── requirements.txt
├── LICENSE
├── .gitignore
└── outputs/            ← generated (git-ignored)
```

---

## Data Disclaimer

Market data sourced from Yahoo Finance via [yfinance](https://github.com/ranaroussi/yfinance).
For educational and portfolio demonstration purposes only. Not financial advice.

---
