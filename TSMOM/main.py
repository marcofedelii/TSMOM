"""
TSMOM Strategy - Main Script
Script principale per l'esecuzione della strategia

Dati: OpenBB - Oro (Gold)
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from tsmom.strategy import TSMOM, SignalState
from backtest.engine import BacktestEngine
from analysis.stats import PerformanceAnalyzer, Plotter


def get_gold_data_from_openbb(start_date: str = "2023-01-01", end_date: str = None) -> pd.DataFrame:
    """
    Scarica dati dell'oro da OpenBB
    
    Args:
        start_date: Data di inizio (formato YYYY-MM-DD)
        end_date: Data di fine (formato YYYY-MM-DD), default = oggi
        
    Returns:
        DataFrame con OHLC data dell'oro
    """
    try:
        from openbb import obb
        
        print(f"   Scaricamento dati oro da OpenBB...")
        print(f"   Periodo: {start_date} a {end_date if end_date else 'oggi'}")
        
        # Scarica i dati dell'oro (GOLD è il ticker per l'oro su OpenBB)
        # OpenBB supporta solo '1m' (1 minuto) e '1d' (1 giorno)
        # Scaricheremo dati giornalieri e li usiamo per il backtest
        data = obb.equity.price.historical(
            symbol="GC=F",  # Gold Futures
            start_date=start_date,
            end_date=end_date,
            interval="1d"  # Intervallo giornaliero
        )
        
        # Converti in DataFrame
        df = data.to_pandas()
        
        # Rinomina le colonne per coerenza con il nostro formato
        df = df.rename(columns={
            'open': 'open',
            'high': 'high',
            'low': 'low',
            'close': 'close',
            'volume': 'volume'
        })
        
        # Mantieni solo le colonne necessarie e indice datetime
        df = df[['open', 'high', 'low', 'close', 'volume']].copy()
        df.index.name = None
        
        print(f"   ✓ Dati scaricati: {len(df)} candele")
        print(f"   ✓ Intervallo: {df.index[0].date()} a {df.index[-1].date()}")
        
        return df
        
    except Exception as e:
        print(f"   ✗ Errore nel download da OpenBB: {e}")
        print(f"   ⚠️  Utilizzo dati di test...")
        return generate_sample_data()


def generate_sample_data(periods: int = 500, seed: int = 42) -> pd.DataFrame:
    """
    Genera dati di esempio per il testing
    
    Args:
        periods: Numero di periodi (candele giornaliere)
        seed: Seed per la riproducibilità
        
    Returns:
        DataFrame con OHLC data
    """
    np.random.seed(seed)
    
    # Genera prezzi con random walk (oro ~$2000)
    returns = np.random.normal(0.0005, 0.01, periods)
    price = 2000 * np.exp(np.cumsum(returns))
    
    # Crea il dataframe con dati giornalieri
    dates = pd.date_range(start='2023-01-01', periods=periods, freq='D')
    
    df = pd.DataFrame({
        'open': price * (1 + np.random.uniform(-0.005, 0.005, periods)),
        'high': price * (1 + np.random.uniform(0, 0.01, periods)),
        'low': price * (1 + np.random.uniform(-0.01, 0, periods)),
        'close': price,
        'volume': np.random.randint(1000, 10000, periods)
    }, index=dates)
    
    return df


def main(use_openbb: bool = True):
    """
    Funzione principale - esegue il backtest
    
    Args:
        use_openbb: Se True, scarica dati da OpenBB; se False usa dati di test
    """
    
    print("="*60)
    print("TSMOM - Time Series Momentum Strategy (GOLD)")
    print("="*60)
    
    # 1. Scarica dati
    print("\n1. Scaricamento dati...")
    if use_openbb:
        # Scarica dati dell'oro dal 2023 ad oggi
        data = get_gold_data_from_openbb(
            start_date="2023-01-01",
            end_date=None
        )
    else:
        data = generate_sample_data(periods=500)
    
    print(f"   Periodo: {data.index[0]} a {data.index[-1]}")
    print(f"   Tot. candele: {len(data)}")
    
    # 2. Initializza la strategia
    print("\n2. Inizializzazione strategia TSMOM...")
    strategy = TSMOM(
        period_short=5,    # 5 giorni
        period_long=20,    # 20 giorni
        threshold=0.0      # Soglia
    )
    print(f"   Period Short: {strategy.period_short} giorni")
    print(f"   Period Long: {strategy.period_long} giorni")
    
    # 3. Calcola i segnali
    print("\n3. Calcolo segnali...")
    signals_df = strategy.generate_signals(data)
    print(f"   Ultimi segnali:")
    print(signals_df[['close', 'momentum_short', 'momentum_long', 'signal_state']].tail(10))
    
    # 4. Esegui il backtest
    print("\n4. Esecuzione backtest...")
    engine = BacktestEngine(strategy, initial_capital=10000)
    result = engine.run(data)
    print(f"   Operazioni totali: {result.total_trades}")
    print(f"   Operazioni aperte: {len([t for t in result.trades if not t.is_closed()])}")
    
    # 5. Analizza i risultati
    print("\n5. Analisi risultati...")
    PerformanceAnalyzer.print_report(result)
    
    # 6. Analisi distribuzione
    dist = PerformanceAnalyzer.get_trade_distribution(result)
    print("\nDISTRIBUZIONE OPERAZIONI:")
    print(f"  Long:  {dist['long_trades']} operazioni | Win Rate: {dist['long_win_rate']:.2%}")
    print(f"  Short: {dist['short_trades']} operazioni | Win Rate: {dist['short_win_rate']:.2%}")
    
    # 7. Visualizzazioni (decommentare per visualizzare)
    print("\n6. Generazione visualizzazioni...")
    try:
        Plotter.plot_equity_curve(result)
        Plotter.plot_pnl_distribution(result)
        Plotter.plot_trades_on_price(signals_df, result)
        print("   Grafici completati")
    except Exception as e:
        print(f"   Errore nella generazione grafici: {e}")
    
    print("\n" + "="*60)
    print("Backtest completato!")
    print("="*60)
    
    return result, signals_df


if __name__ == "__main__":
    # use_openbb=True: scarica i dati dell'oro da OpenBB
    # use_openbb=False: usa dati di test generati
    result, signals_df = main(use_openbb=True)
