"""
TSMOM Quick Test
Script rapido per testare con dati di fallback
"""

import pandas as pd
import numpy as np
import sys

# Aggiungi il percorso al path
sys.path.insert(0, '.')

from tsmom.strategy import TSMOM
from backtest.engine import BacktestEngine
from analysis.stats import PerformanceAnalyzer


def generate_gold_data(periods: int = 1000) -> pd.DataFrame:
    """Genera dati realistici dell'oro per testing"""
    np.random.seed(42)
    
    # Trend rialzista leggero + volatilità
    returns = np.random.normal(0.0003, 0.008, periods)
    price = 2000 * np.exp(np.cumsum(returns))
    
    dates = pd.date_range(start='2023-01-01', periods=periods, freq='D')
    
    df = pd.DataFrame({
        'open': price * (1 + np.random.uniform(-0.003, 0.003, periods)),
        'high': price * (1 + np.random.uniform(0, 0.008, periods)),
        'low': price * (1 + np.random.uniform(-0.008, 0, periods)),
        'close': price,
        'volume': np.random.randint(10000, 50000, periods)
    }, index=dates)
    
    return df


def main():
    print("="*70)
    print("TSMOM - GOLD Strategy (Test Mode)")
    print("="*70)
    
    # Carica dati
    print("\n1. Generazione dati GOLD...")
    data = generate_gold_data(periods=1000)
    print(f"   ✓ Dati: {len(data)} candele")
    print(f"   ✓ Periodo: {data.index[0].date()} a {data.index[-1].date()}")
    print(f"   ✓ Prezzo: ${data['close'].min():.2f} - ${data['close'].max():.2f}")
    
    # Strategia
    print("\n2. Inizializzazione TSMOM...")
    strategy = TSMOM(
        period_short=5,    # 5 giorni
        period_long=20,    # 20 giorni
        threshold=0.0
    )
    print(f"   ✓ Period Short: {strategy.period_short} giorni")
    print(f"   ✓ Period Long: {strategy.period_long} giorni")
    
    # Segnali
    print("\n3. Calcolo segnali...")
    signals_df = strategy.generate_signals(data)
    print(f"   ✓ Segnali calcolati")
    
    long_signals = (signals_df['signal_value'] == 1).sum()
    short_signals = (signals_df['signal_value'] == -1).sum()
    flat_signals = (signals_df['signal_value'] == 0).sum()
    
    print(f"   ✓ Distribuzione: LONG={long_signals} | SHORT={short_signals} | FLAT={flat_signals}")
    
    # Backtest
    print("\n4. Esecuzione backtest...")
    engine = BacktestEngine(strategy, initial_capital=100000)
    result = engine.run(data)
    print(f"   ✓ Backtest completato")
    print(f"   ✓ Operazioni totali: {result.total_trades}")
    
    # Statistiche
    print("\n5. Analisi risultati...")
    stats = PerformanceAnalyzer.get_summary_stats(result)
    dist = PerformanceAnalyzer.get_trade_distribution(result)
    
    print("\n" + "="*70)
    print("STATISTICHE PRINCIPALI")
    print("="*70)
    
    print(f"\n📊 OPERAZIONI:")
    print(f"   Totale:       {stats['total_trades']}")
    print(f"   Long:         {dist['long_trades']:>4} | Win Rate: {dist['long_win_rate']:>6.1%}")
    print(f"   Short:        {dist['short_trades']:>4} | Win Rate: {dist['short_win_rate']:>6.1%}")
    print(f"   Win Rate Avg: {stats['win_rate']:.1%}")
    
    print(f"\n💰 PERFORMANCE:")
    print(f"   Total P&L:    ${stats['total_pnl']:>10.2f}")
    print(f"   Avg P&L:      ${stats['avg_pnl']:>10.2f} ({stats['avg_pnl_pct']:>6.2%})")
    print(f"   Max Win:      ${stats['largest_win']:>10.2f}")
    print(f"   Max Loss:     ${stats['largest_loss']:>10.2f}")
    
    print(f"\n⏱️  DURATA OPERAZIONI (giorni):")
    print(f"   Media:        {stats['avg_bars_held']:>10.1f}d")
    print(f"   Max:          {stats['max_bars_held']:>10.1f}d")
    print(f"   Min:          {stats['min_bars_held']:>10.1f}d")
    
    print(f"\n📈 EQUITY:")
    initial = result.equity_curve.iloc[0]
    final = result.equity_curve.iloc[-1]
    return_pct = ((final - initial) / initial) * 100
    print(f"   Iniziale:     ${initial:>10.2f}")
    print(f"   Finale:       ${final:>10.2f}")
    print(f"   Return:       {return_pct:>10.2f}%")
    
    print("\n" + "="*70 + "\n")
    
    return result, signals_df


if __name__ == "__main__":
    result, signals_df = main()
