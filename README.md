# TSMOM: Time Series Momentum Strategy
## A Research Implementation in Time-Series Asset Trading

**Author**: Marco  Fedeli
**Version**: 0.1.0  
**Last Updated**: February 4, 2026  
**Asset Class**: Precious Metals (Gold - GC=F)  
**Data Source**: OpenBB Terminal

---

## Abstract

This repository contains a modular implementation of a Time Series Momentum (TSMOM) strategy, a quantitative trading approach that leverages multi-horizon momentum signals to generate directional trading signals. The strategy operates on daily price data and maintains a simple position management framework: entry on signal generation, exit on signal reversal. This implementation is designed as a research foundation and institutional-grade framework for systematic trading research.

---

## 1. Introduction

Time Series Momentum strategies have demonstrated empirical success across asset classes (Moskowitz et al., 2012). This implementation provides a clean, production-ready framework for:

- Multi-horizon momentum signal generation
- Backtesting and performance analysis
- Distributional analysis of trading operations
- Extensible architecture for future enhancements

The strategy intentionally **omits position sizing, risk management filters, and parameter optimization routines** to preserve the intellectual property of the core methodology. These components should be developed independently by researchers implementing this framework.

---

## 2. Methodology

### 2.1 Signal Generation

The TSMOM strategy computes returns across two distinct time horizons:

- **Short-term horizon**: 5 periods
- **Long-term horizon**: 20 periods

A composite momentum score is calculated as a weighted combination:

$$S_t = 0.4 \cdot r_t^{(5)} + 0.6 \cdot r_t^{(20)}$$

where $r_t^{(h)}$ represents the h-period log return at time $t$.

### 2.2 Trading Signals

Three discrete states are generated:

| State | Condition | Action |
|-------|-----------|--------|
| **LONG** | $S_t > \theta$ | Enter long position |
| **SHORT** | $S_t < -\theta$ | Enter short position |
| **FLAT** | $-\theta \leq S_t \leq \theta$ | Close existing position |

The threshold $\theta$ (default: 0.0) is a configurable parameter.

### 2.3 Position Management

The framework implements a simplified yet comprehensive position tracking system:

1. **Entry**: Position initiated on signal state change to LONG or SHORT
2. **Duration**: Position maintained until next signal change
3. **Exit**: Automatic position closure and reversal on signal change
4. **Constraint**: Single position active at any time

---

## 3. Architecture

### 3.1 Modular Design

```
TSMOM/
├── tsmom/
│   ├── __init__.py
│   └── strategy.py          # Core TSMOM implementation
├── backtest/
│   ├── __init__.py
│   └── engine.py            # Backtesting engine
├── analysis/
│   ├── __init__.py
│   └── stats.py             # Statistical analysis & visualization
├── main.py                  # Entry point with OpenBB data
├── test.py                  # Standalone test script
├── examples.py              # Usage examples
└── requirements.txt         # Dependencies
```

### 3.2 Core Modules

#### `tsmom/strategy.py`
- **TSMOM Class**: Signal generation engine
  - `calculate_returns()`: Computes multi-period returns
  - `generate_signals()`: Produces signal states for time series
  - `get_signal_at()`: Retrieves signal for specific timestamp

- **SignalState Enum**: LONG, SHORT, FLAT states
- **TSMOMSignal Dataclass**: Signal output structure

#### `backtest/engine.py`
- **BacktestEngine**: Simulation framework
  - `run()`: Executes backtest on historical data
  - Automatic position lifecycle management
  - Equity curve computation

- **Trade**: Individual trade representation with full lifecycle
- **BacktestResult**: Aggregated backtest statistics

#### `analysis/stats.py`
- **PerformanceAnalyzer**: Statistical computations
  - `get_summary_stats()`: Primary performance metrics
  - `get_trade_distribution()`: Long vs. Short analysis
  - `get_pnl_distribution()`: Return distribution analysis
  - `print_report()`: Formatted report generation

- **Plotter**: Visualization toolkit
  - `plot_equity_curve()`: Cumulative return visualization
  - `plot_pnl_distribution()`: Return distribution histogram
  - `plot_trades_on_price()`: Trade annotations on price chart

---

## 4. Installation & Usage

### 4.1 Requirements

- Python 3.8+
- pandas ≥ 1.3.0
- numpy ≥ 1.21.0
- matplotlib ≥ 3.4.0
- openbb ≥ 4.0.0

### 4.2 Installation

```bash
pip install -r requirements.txt
```

### 4.3 Basic Usage

#### Option 1: Live Data from OpenBB (Gold)
```bash
python main.py
```
Downloads historical gold futures data (GC=F) from OpenBB. Automatically falls back to synthetic test data on connection failure.

#### Option 2: Standalone Test
```bash
python test.py
```
Executes backtest on synthetically generated data (no internet required).

#### Option 3: Usage Examples
```bash
python examples.py
```
Five complete examples demonstrating programmatic API usage.

### 4.4 Programmatic Usage

```python
from tsmom.strategy import TSMOM
from backtest.engine import BacktestEngine
from analysis.stats import PerformanceAnalyzer
import pandas as pd

# 1. Load data with 'close' column
data = pd.DataFrame({'close': [...]}, index=pd.date_range(...))

# 2. Initialize strategy
strategy = TSMOM(period_short=5, period_long=20, threshold=0.0)

# 3. Generate signals
signals = strategy.generate_signals(data)

# 4. Execute backtest
engine = BacktestEngine(strategy, initial_capital=100000)
result = engine.run(data)

# 5. Analyze results
PerformanceAnalyzer.print_report(result)
stats = PerformanceAnalyzer.get_summary_stats(result)
distribution = PerformanceAnalyzer.get_trade_distribution(result)
```

---

## 5. Output & Metrics

### 5.1 Summary Statistics

The framework computes comprehensive trading statistics:

| Metric | Description |
|--------|-------------|
| **Total Trades** | Number of completed round-trip trades |
| **Win Rate** | Proportion of profitable trades |
| **Total P&L** | Cumulative profit/loss in dollars |
| **Avg P&L** | Mean profit/loss per trade |
| **Largest Win/Loss** | Extreme favorable/adverse excursion |
| **Avg Duration** | Mean holding period in days |
| **Cumulative Return** | Percentage return on initial capital |

### 5.2 Distribution Analysis

- **Long vs. Short**: Trade count and win rates by direction
- **P&L Distribution**: Statistical moments of return distribution
- **Holding Periods**: Duration statistics across all trades

### 5.3 Sample Output

```
============================================================
BACKTEST REPORT - TSMOM Strategy
============================================================

OPERATIONS:
  Total:        XXX
  Long:          XX | Win Rate: XX.X%
  Short:         XX | Win Rate: XX.X%
  Overall Win Rate: XX.X%

PERFORMANCE:
  Total P&L:    $  XX.XX
  Avg P&L:      $   XX.XX (XX.XX%)
  Max Win:      $  XX.XX
  Max Loss:     $  XX.XX

HOLDING PERIODS (days):
  Mean:              X.Xd
  Max:              XX.Xd
  Min:               X.Xd

EQUITY:
  Initial:     $ XXXXXX.XX
  Final:       $  XXXXXX.XX
  Return:          XX.XX%
```

---

## 6. Configuration & Customization

### 6.1 Strategy Parameters

```python
strategy = TSMOM(
    period_short=5,      # Short-term horizon (periods)
    period_long=20,      # Long-term horizon (periods)
    threshold=0.0        # Signal threshold
)
```

### 6.2 Weighting Adjustment

Modify composite momentum weighting in `strategy.py`:

```python
df['signal_score'] = (
    0.4 * df['momentum_short'] +   # Short-term weight
    0.6 * df['momentum_long']      # Long-term weight
)
```

### 6.3 Alternative Data Sources

Customize `get_gold_data_from_openbb()` in `main.py` to:
- Change ticker symbols
- Adjust data frequency
- Integrate alternative data providers

### 6.4 Extending Indicators

Extend the `TSMOM` class to incorporate additional technical indicators or risk filters.

---

## 7. Intellectual Property Notice

This implementation intentionally **excludes the following components**:

- **Position Sizing**: Allocation and leverage methodology
- **Risk Management**: Entry filters, stop-loss mechanisms, portfolio constraints
- **Parameter Optimization**: Hyperparameter tuning, grid search, walk-forward analysis
- **Advanced Signal Filters**: Entry/exit confirmation rules, regime detection

These omissions preserve the core intellectual property of the research framework. Researchers implementing this code should develop proprietary enhancements to these areas independently.

---

## 8. Limitations & Assumptions

- **Frictionless**: Backtesting excludes transaction costs, slippage, and market impact
- **Full-Size Positions**: No partial entry/exit or position scaling
- **Single Asset**: Framework processes one asset class at a time
- **Daily Frequency**: While configurable, implementation optimized for daily bars
- **Unrealistic Fills**: Assumes execution at OHLC prices without latency

---

## 9. Future Development Roadmap

Potential extensions for researchers:

- [ ] Adaptive threshold mechanisms based on market regime
- [ ] Multi-asset portfolio framework
- [ ] Transaction cost modeling
- [ ] Drawdown and Sharpe ratio analysis
- [ ] Walk-forward validation
- [ ] Real-time signal generation interface
- [ ] Integration with live trading APIs
- [ ] Monte Carlo simulation
- [ ] Correlation analysis across asset classes

---

## 10. References

- Moskowitz, T. J., Ooi, Y. H., & Pedersen, L. H. (2012). "Time Series Momentum." *Journal of Financial Economics*, 104(2), 228-250.
- Blitz, D., Hanauer, M. X., Vidojevic, M., & Vliet, P. V. (2014). "Momentum Investing: A Primer." *Journal of Index Investing*, 5(4), 87-99.
- Arnott, R. D., Beck, S. L., Kalesnik, V., & West, J. (2016). "How Can 'Dividends' Predict Returns?" *Research Affiliates Publications*.

---

## 11. Usage Examples

### Example 1: Parameter Sensitivity Analysis
```python
for period_long in [10, 15, 20, 25, 30]:
    strategy = TSMOM(period_short=5, period_long=period_long)
    result = engine.run(data)
    # Analyze performance variation
```

### Example 2: Trade Analysis
```python
closed_trades = [t for t in result.trades if t.is_closed()]
top_trades = sorted(closed_trades, key=lambda x: x.pnl, reverse=True)[:10]
for trade in top_trades:
    print(f"{trade.entry_state}: {trade.pnl:.2f}")
```

### Example 3: Return Distribution
```python
pnl_dist = PerformanceAnalyzer.get_pnl_distribution(result)
print(f"Skewness: {pnl_dist.skew():.3f}")
print(f"Kurtosis: {pnl_dist.kurtosis():.3f}")
```

---

## 12. File Structure

```
requirements.txt      # Python dependencies
main.py              # Production entry point (OpenBB data)
test.py              # Standalone test suite
examples.py          # Usage demonstrations
README.md            # This file
STATUS.txt           # Project status

tsmom/
├── __init__.py
└── strategy.py      # TSMOM implementation (280 LOC)

backtest/
├── __init__.py
└── engine.py        # Backtesting engine (240 LOC)

analysis/
├── __init__.py
└── stats.py         # Analysis toolkit (280 LOC)
```

---

## 13. Citation

If you utilize this framework for research, please cite:

```bibtex
@software{tsmom2026,
  title={TSMOM: Time Series Momentum Strategy - Research Implementation},
  author={Marco},
  year={2026},
  url={https://github.com/your-repo/tsmom}
}
```

---

## 14. License

**Research Use Only**. This implementation is provided for educational and research purposes. Users are responsible for compliance with all applicable laws and regulations when deploying quantitative trading strategies.

---

## 15. Contact & Support

For implementation questions regarding the framework architecture and usage, please refer to the inline documentation and examples provided. For methodology discussions or extensions, consider the limitations and intellectual property constraints outlined in Section 7.

---

**Last Updated**: February 4, 2026  
**Status**: Research Framework v0.1.0 - Stable



