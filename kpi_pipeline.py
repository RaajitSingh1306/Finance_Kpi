"""
kpi_pipeline.py
---------------
Automated finance KPI pipeline.
Downloads OHLCV data for one or more tickers, computes key financial KPIs,
generates a 4-panel chart per ticker, and saves a combined CSV summary.

Usage:
    python kpi_pipeline.py
    python kpi_pipeline.py --tickers RELIANCE.NS TCS.NS --start 2014-01-01
    python kpi_pipeline.py --tickers ^NSEI --start 2018-01-01 --risk_free 0.07
"""

from __future__ import annotations

import argparse
import logging
import os
from datetime import datetime
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yfinance as yf

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-7s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
DEFAULT_TICKERS    = ["^NSEI"]
DEFAULT_START      = "2014-01-01"
DEFAULT_RISK_FREE  = 0.065       # India 10yr G-Sec proxy (annualised)
TRADING_DAYS       = 252
OUTPUT_DIR         = Path("outputs")

# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Finance KPI Pipeline — CAGR, Sharpe, Max Drawdown"
    )
    parser.add_argument(
        "--tickers", nargs="+", default=DEFAULT_TICKERS,
        help="Yahoo Finance ticker symbols (e.g. RELIANCE.NS TCS.NS ^NSEI)",
    )
    parser.add_argument(
        "--start", type=str, default=DEFAULT_START,
        help="Start date in YYYY-MM-DD format (default: %(default)s)",
    )
    parser.add_argument(
        "--end", type=str, default=datetime.today().strftime("%Y-%m-%d"),
        help="End date in YYYY-MM-DD format (default: today)",
    )
    parser.add_argument(
        "--risk_free", type=float, default=DEFAULT_RISK_FREE,
        help="Annualised risk-free rate as a decimal (default: %(default)s)",
    )
    parser.add_argument(
        "--output_dir", type=str, default=str(OUTPUT_DIR),
        help="Directory for output files (default: %(default)s)",
    )
    return parser.parse_args()

# ---------------------------------------------------------------------------
# Step 1 — Data ingestion
# ---------------------------------------------------------------------------

def load_data(ticker: str, start: str, end: str) -> pd.DataFrame:
    """Download daily OHLCV and compute simple returns."""
    log.info("[1/4] Downloading %s …", ticker)
    df = yf.download(ticker, start=start, end=end, progress=False)
    if df.empty:
        raise ValueError(f"No data returned for {ticker!r}. Check symbol and date range.")

    # yfinance may return MultiIndex columns for single tickers
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    df = df[["Close"]].copy()
    df.index = pd.to_datetime(df.index)
    df["returns"] = df["Close"].pct_change()
    log.info("      %d rows loaded (%s → %s)", len(df),
             df.index[0].date(), df.index[-1].date())
    return df

# ---------------------------------------------------------------------------
# Step 2 — KPI computation
# ---------------------------------------------------------------------------

def max_drawdown(returns: pd.Series) -> float:
    wealth = (1 + returns).cumprod()
    drawdown = wealth / wealth.cummax() - 1
    return float(drawdown.min())


def sortino_ratio(returns: pd.Series, rf: float = 0.065) -> float:
    excess = returns - rf / 252
    downside_std = excess[excess < 0].std() * np.sqrt(252)
    return excess.mean() * 252 / downside_std if downside_std != 0 else np.nan


def calmar_ratio(returns: pd.Series, cagr: float) -> float:
    max_dd = max_drawdown(returns)
    return cagr / abs(max_dd) if max_dd != 0 else np.nan


def calculate_kpis(
    df: pd.DataFrame,
    ticker: str,
    risk_free_rate: float,
) -> tuple[dict, pd.Series, pd.Series]:
    """
    Compute CAGR, annualised Sharpe ratio, and Max Drawdown.

    Returns
    -------
    kpis           : dict of scalar KPI values
    drawdown       : pd.Series of rolling drawdown (fraction)
    excess_returns : pd.Series of daily excess returns over risk-free rate
    """
    log.info("[2/4] Computing KPIs for %s …", ticker)

    close = df["Close"].dropna()
    start_price = float(close.iloc[0])
    end_price   = float(close.iloc[-1])
    n_years     = (close.index[-1] - close.index[0]).days / 365.25

    cagr = (end_price / start_price) ** (1.0 / n_years) - 1.0

    returns_clean   = df["returns"].dropna()
    risk_free_daily = risk_free_rate / TRADING_DAYS
    excess_returns  = returns_clean - risk_free_daily
    sharpe = (
        (excess_returns.mean() / excess_returns.std()) * np.sqrt(TRADING_DAYS)
        if excess_returns.std() > 0
        else float("nan")
    )
    sortino = sortino_ratio(returns_clean, risk_free_rate)
    calmar = calmar_ratio(returns_clean, cagr)

    rolling_max = close.cummax()
    drawdown    = (close - rolling_max) / rolling_max
    max_dd      = float(drawdown.min())
    max_dd_date = drawdown.idxmin()

    kpis: dict = {
        "ticker":       ticker,
        "start_date":   close.index[0].date(),
        "end_date":     close.index[-1].date(),
        "start_price":  round(start_price, 2),
        "end_price":    round(end_price, 2),
        "cagr_pct":     round(cagr * 100, 2),
        "sharpe":       round(sharpe, 3),
        "sortino":      round(sortino, 3),
        "calmar":       round(calmar, 3),
        "max_dd_pct":   round(max_dd * 100, 2),
        "max_dd_date":  max_dd_date.date(),
        "n_years":      round(n_years, 2),
    }

    log.info(
        "      CAGR=%.2f%%  Sharpe=%.3f  Sortino=%.3f  Calmar=%.3f  MaxDD=%.2f%%",
        kpis["cagr_pct"], kpis["sharpe"], kpis["sortino"], kpis["calmar"], kpis["max_dd_pct"],
    )
    return kpis, drawdown, excess_returns

# ---------------------------------------------------------------------------
# Step 3 — Chart generation
# ---------------------------------------------------------------------------

def generate_report(
    df: pd.DataFrame,
    kpis: dict,
    drawdown: pd.Series,
    excess_returns: pd.Series,
    output_dir: Path,
) -> Path:
    """Render a 4-panel KPI chart and save as PNG."""
    log.info("[3/4] Generating chart …")

    ticker_safe = kpis["ticker"].replace("^", "").replace(".", "_")
    fig, axes = plt.subplots(2, 2, figsize=(16, 10))
    fig.suptitle(
        f"{kpis['ticker']}  |  CAGR: {kpis['cagr_pct']}%  "
        f"Sharpe: {kpis['sharpe']}  Max DD: {kpis['max_dd_pct']}%",
        fontsize=12,
    )

    # Panel 1 — Price vs CAGR trendline
    close = df["Close"].dropna()
    days = (close.index - close.index[0]).days.values
    cagr_line = kpis["start_price"] * (1 + kpis["cagr_pct"] / 100) ** (days / 365.25)
    axes[0, 0].plot(close.index, close, color="steelblue", linewidth=0.8, label="Close")
    axes[0, 0].plot(close.index, cagr_line, color="coral", linewidth=1.5,
                    linestyle="--", label=f"CAGR {kpis['cagr_pct']}%")
    axes[0, 0].set_title("Price vs CAGR Trendline")
    axes[0, 0].legend()

    # Panel 2 — Drawdown
    axes[0, 1].fill_between(drawdown.index, drawdown * 100, 0, color="coral", alpha=0.6)
    axes[0, 1].axhline(y=kpis["max_dd_pct"], color="red", linestyle="--",
                        label=f"Max DD: {kpis['max_dd_pct']}%")
    axes[0, 1].set_title("Drawdown (%)")
    axes[0, 1].legend()

    # Panel 3 — Rolling Sharpe (252-day)
    roll = excess_returns.rolling(TRADING_DAYS)
    rolling_sharpe = (roll.mean() / roll.std()) * np.sqrt(TRADING_DAYS)
    axes[1, 0].plot(rolling_sharpe.index, rolling_sharpe, color="teal", linewidth=0.8)
    axes[1, 0].axhline(y=1, color="green", linestyle="--", alpha=0.5, label="Sharpe = 1")
    axes[1, 0].axhline(y=0, color="gray", linewidth=0.8)
    axes[1, 0].set_title(f"Rolling Sharpe — 252d  (overall: {kpis['sharpe']})")
    axes[1, 0].legend()

    # Panel 4 — Annual returns bar chart
    df_tmp = df[["returns"]].copy()
    df_tmp["year"] = df_tmp.index.year
    annual = df_tmp.groupby("year")["returns"].mean() * TRADING_DAYS
    bar_colors = ["steelblue" if r > 0 else "coral" for r in annual]
    axes[1, 1].bar(annual.index, annual * 100, color=bar_colors, edgecolor="white")
    axes[1, 1].axhline(y=kpis["cagr_pct"], color="coral", linestyle="--",
                        label=f"CAGR {kpis['cagr_pct']}%")
    axes[1, 1].set_title("Annualised Returns (%)")
    axes[1, 1].legend()

    plt.tight_layout()
    output_dir.mkdir(parents=True, exist_ok=True)
    chart_path = output_dir / f"kpi_report_{ticker_safe}.png"
    plt.savefig(chart_path, dpi=150, bbox_inches="tight")
    plt.close()
    log.info("      Chart saved → %s", chart_path)
    return chart_path

# ---------------------------------------------------------------------------
# Step 4 — Save combined CSV summary
# ---------------------------------------------------------------------------

def save_summary(all_kpis: list[dict], output_dir: Path) -> Path:
    """Write all KPI results to a single CSV file."""
    log.info("[4/4] Saving KPI summary …")
    output_dir.mkdir(parents=True, exist_ok=True)
    summary_path = output_dir / "kpi_summary_combined.csv"
    pd.DataFrame(all_kpis).to_csv(summary_path, index=False)
    log.info("      Saved → %s", summary_path)
    return summary_path

# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    args   = parse_args()
    outdir = Path(args.output_dir)
    all_kpis: list[dict] = []

    for ticker in args.tickers:
        log.info("=" * 52)
        log.info("Processing: %s", ticker)
        log.info("=" * 52)
        try:
            df = load_data(ticker, args.start, args.end)
            kpis, drawdown, excess_ret = calculate_kpis(df, ticker, args.risk_free)
            generate_report(df, kpis, drawdown, excess_ret, outdir)
            all_kpis.append(kpis)
        except Exception as exc:  # noqa: BLE001
            log.error("Failed to process %s: %s", ticker, exc)

    if all_kpis:
        save_summary(all_kpis, outdir)
        log.info("✅ Done — %d ticker(s) processed.", len(all_kpis))
    else:
        log.warning("No tickers processed successfully.")


if __name__ == "__main__":
    main()