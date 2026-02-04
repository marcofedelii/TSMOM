"""
Example: Utilizzo programmtico della libreria TSMOM
"""

import pandas as pd
from tsmom.strategy import TSMOM, SignalState
from backtest.engine import BacktestEngine
from analysis.stats import PerformanceAnalyzer, Plotter


# ============================================================================
# ESEMPIO 1: Uso base della strategia
# ============================================================================

def example_basic():
    """Eseguire un backtest di base con dati di test"""
    print("ESEMPIO 1: Backtest di base")
    print("-" * 60)
    
    # Genera dati di test
    import numpy as np
    
    np.random.seed(123)
    dates = pd.date_range('2023-01-01', periods=500, freq='D')
    returns = np.random.normal(0.001, 0.02, 500)
    prices = 2000 * np.exp(np.cumsum(returns))
    
    data = pd.DataFrame({
        'open': prices,
        'high': prices * 1.01,
        'low': prices * 0.99,
        'close': prices,
        'volume': np.random.randint(1000, 10000, 500)
    }, index=dates)
    
    # Crea strategia e esegui backtest
    strategy = TSMOM(period_short=5, period_long=20)
    engine = BacktestEngine(strategy, initial_capital=50000)
    result = engine.run(data)
    
    # Stampa risultati
    stats = PerformanceAnalyzer.get_summary_stats(result)
    print(f"Total Trades: {stats['total_trades']}")
    print(f"Win Rate: {stats['win_rate']:.2%}")
    print(f"Total P&L: ${stats['total_pnl']:.2f}")
    print()


# ============================================================================
# ESEMPIO 2: Calcolo manuale dei segnali
# ============================================================================

def example_manual_signals():
    """Calcolo manuale dei segnali su dati specifici"""
    print("ESEMPIO 2: Calcolo manuale dei segnali")
    print("-" * 60)
    
    # Dati di esempio
    data = pd.DataFrame({
        'close': [100, 101, 102, 103, 104, 103, 102, 101, 100, 99]
    }, index=pd.date_range('2023-01-01', periods=10, freq='D'))
    
    # Calcola segnali
    strategy = TSMOM(period_short=3, period_long=5)
    signals = strategy.generate_signals(data)
    
    print("Segnali generati:")
    print(signals[['close', 'signal_state', 'signal_score']].tail())
    print()


# ============================================================================
# ESEMPIO 3: Analisi dettagliata dei trades
# ============================================================================

def example_trade_analysis():
    """Analisi dettagliata di ogni singolo trade"""
    print("ESEMPIO 3: Analisi dettagliata dei trades")
    print("-" * 60)
    
    # Crea dati e strategia
    import numpy as np
    
    np.random.seed(42)
    dates = pd.date_range('2023-01-01', periods=200, freq='D')
    returns = np.random.normal(0.0005, 0.015, 200)
    prices = 2000 * np.exp(np.cumsum(returns))
    
    data = pd.DataFrame({
        'open': prices,
        'high': prices * 1.01,
        'low': prices * 0.99,
        'close': prices,
        'volume': np.random.randint(1000, 10000, 200)
    }, index=dates)
    
    # Backtest
    strategy = TSMOM(period_short=5, period_long=15)
    engine = BacktestEngine(strategy, initial_capital=100000)
    result = engine.run(data)
    
    # Analizza i trades
    print(f"\nTop 5 trades vincenti:")
    closed_trades = sorted([t for t in result.trades if t.is_closed()], 
                          key=lambda x: x.pnl, reverse=True)[:5]
    for i, trade in enumerate(closed_trades, 1):
        print(f"{i}. {trade.entry_state.name:5} | "
              f"Entry: ${trade.entry_price:.2f} | "
              f"Exit: ${trade.exit_price:.2f} | "
              f"P&L: ${trade.pnl:.2f} ({trade.pnl_pct*100:+.2f}%)")
    
    print(f"\nTop 5 trades perdenti:")
    losing_trades = sorted([t for t in result.trades if t.is_closed()], 
                           key=lambda x: x.pnl)[:5]
    for i, trade in enumerate(losing_trades, 1):
        print(f"{i}. {trade.entry_state.name:5} | "
              f"Entry: ${trade.entry_price:.2f} | "
              f"Exit: ${trade.exit_price:.2f} | "
              f"P&L: ${trade.pnl:.2f} ({trade.pnl_pct*100:+.2f}%)")
    print()


# ============================================================================
# ESEMPIO 4: Confronto di parametri diversi
# ============================================================================

def example_parameter_comparison():
    """Confronta la performance con parametri diversi"""
    print("ESEMPIO 4: Confronto parametri")
    print("-" * 60)
    
    # Dati comuni
    import numpy as np
    import pandas as pd
    
    np.random.seed(99)
    dates = pd.date_range('2023-01-01', periods=300, freq='D')
    returns = np.random.normal(0.0003, 0.015, 300)
    prices = 2000 * np.exp(np.cumsum(returns))
    
    data = pd.DataFrame({
        'open': prices,
        'high': prices * 1.01,
        'low': prices * 0.99,
        'close': prices,
        'volume': np.random.randint(1000, 10000, 300)
    }, index=dates)
    
    # Test diversi parametri
    configs = [
        (3, 10, "Aggressivo"),
        (5, 20, "Equilibrato"),
        (10, 30, "Conservativo"),
    ]
    
    results = []
    for short, long, name in configs:
        strategy = TSMOM(period_short=short, period_long=long)
        engine = BacktestEngine(strategy, initial_capital=50000)
        result = engine.run(data)
        stats = PerformanceAnalyzer.get_summary_stats(result)
        
        results.append({
            'Config': name,
            'Trades': stats['total_trades'],
            'Win Rate': f"{stats['win_rate']:.1%}",
            'Total P&L': f"${stats['total_pnl']:.0f}",
            'Avg P&L': f"{stats['avg_pnl_pct']*100:.2f}%"
        })
    
    # Stampa risultati in formato tabella
    comparison = pd.DataFrame(results)
    print(comparison.to_string(index=False))
    print()


# ============================================================================
# ESEMPIO 5: Distribuzione delle operazioni
# ============================================================================

def example_distribution():
    """Analizza la distribuzione delle operazioni"""
    print("ESEMPIO 5: Distribuzione operazioni")
    print("-" * 60)
    
    # Crea dati
    import numpy as np
    
    np.random.seed(50)
    dates = pd.date_range('2023-01-01', periods=250, freq='D')
    returns = np.random.normal(0.0002, 0.012, 250)
    prices = 2000 * np.exp(np.cumsum(returns))
    
    data = pd.DataFrame({
        'open': prices,
        'high': prices * 1.01,
        'low': prices * 0.99,
        'close': prices,
        'volume': np.random.randint(1000, 10000, 250)
    }, index=dates)
    
    # Backtest
    strategy = TSMOM(period_short=5, period_long=20)
    engine = BacktestEngine(strategy, initial_capital=50000)
    result = engine.run(data)
    
    # Analizza distribuzione
    dist = PerformanceAnalyzer.get_trade_distribution(result)
    pnl_dist = PerformanceAnalyzer.get_pnl_distribution(result)
    
    print(f"LONG trades:  {dist['long_trades']:3} | Win Rate: {dist['long_win_rate']:.1%} | Avg P&L: {dist['long_avg_pnl_pct']*100:+.2f}%")
    print(f"SHORT trades: {dist['short_trades']:3} | Win Rate: {dist['short_win_rate']:.1%} | Avg P&L: {dist['short_avg_pnl_pct']*100:+.2f}%")
    
    print(f"\nP&L Distribution Statistics:")
    print(f"  Mean:   {pnl_dist.mean():+.2f}%")
    print(f"  Std:    {pnl_dist.std():.2f}%")
    print(f"  Min:    {pnl_dist.min():.2f}%")
    print(f"  Max:    {pnl_dist.max():.2f}%")
    print()


# ============================================================================
# Main - Esegui tutti gli esempi
# ============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("TSMOM - Esempi di Utilizzo")
    print("=" * 60)
    print()
    
    example_basic()
    example_manual_signals()
    example_trade_analysis()
    example_parameter_comparison()
    example_distribution()
    
    print("=" * 60)
    print("Esempi completati!")
    print("=" * 60)
