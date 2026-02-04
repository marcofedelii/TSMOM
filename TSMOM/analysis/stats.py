"""
Statistics and Analysis
Calcolo delle statistiche e analisi dei risultati
"""

import pandas as pd
import numpy as np
from typing import Dict, List
import matplotlib.pyplot as plt

from backtest.engine import BacktestResult, SignalState


class PerformanceAnalyzer:
    """Analizzatore di performance del backtest"""
    
    @staticmethod
    def get_summary_stats(result: BacktestResult) -> Dict:
        """
        Calcola le statistiche riassuntive
        
        Returns:
            Dictionary con le statistiche principali
        """
        closed_trades = [t for t in result.trades if t.is_closed()]
        
        if not closed_trades:
            return {
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'win_rate': 0,
                'total_pnl': 0,
                'avg_pnl': 0,
                'avg_pnl_pct': 0,
                'largest_win': 0,
                'largest_loss': 0,
                'avg_bars_held': 0
            }
        
        pnls = [t.pnl for t in closed_trades]
        pnls_pct = [t.pnl_pct for t in closed_trades]
        bars_held = [t.bars_held for t in closed_trades if t.bars_held]
        
        return {
            'total_trades': result.total_trades,
            'winning_trades': result.winning_trades,
            'losing_trades': result.losing_trades,
            'win_rate': result.win_rate,
            'total_pnl': result.total_pnl,
            'avg_pnl': np.mean(pnls),
            'avg_pnl_pct': result.avg_pnl_pct,
            'largest_win': max(pnls),
            'largest_loss': min(pnls),
            'avg_bars_held': np.mean(bars_held) if bars_held else 0,
            'max_bars_held': max(bars_held) if bars_held else 0,
            'min_bars_held': min(bars_held) if bars_held else 0,
        }
    
    @staticmethod
    def get_trade_distribution(result: BacktestResult) -> Dict:
        """
        Analizza la distribuzione delle operazioni
        
        Returns:
            Dictionary con statistiche sulla distribuzione
        """
        closed_trades = [t for t in result.trades if t.is_closed()]
        
        long_trades = [t for t in closed_trades if t.entry_state == SignalState.LONG]
        short_trades = [t for t in closed_trades if t.entry_state == SignalState.SHORT]
        
        return {
            'long_trades': len(long_trades),
            'short_trades': len(short_trades),
            'long_win_rate': len([t for t in long_trades if t.pnl > 0]) / len(long_trades) if long_trades else 0,
            'short_win_rate': len([t for t in short_trades if t.pnl > 0]) / len(short_trades) if short_trades else 0,
            'long_avg_pnl_pct': np.mean([t.pnl_pct for t in long_trades]) if long_trades else 0,
            'short_avg_pnl_pct': np.mean([t.pnl_pct for t in short_trades]) if short_trades else 0,
        }
    
    @staticmethod
    def get_pnl_distribution(result: BacktestResult) -> pd.Series:
        """
        Restituisce la distribuzione dei P&L
        
        Returns:
            Series con i P&L percentuali di tutte le operazioni chiuse
        """
        closed_trades = [t for t in result.trades if t.is_closed()]
        return pd.Series([t.pnl_pct * 100 for t in closed_trades])
    
    @staticmethod
    def print_report(result: BacktestResult):
        """Stampa un report riassuntivo"""
        stats = PerformanceAnalyzer.get_summary_stats(result)
        dist = PerformanceAnalyzer.get_trade_distribution(result)
        
        print("\n" + "="*60)
        print("BACKTEST REPORT - TSMOM Strategy")
        print("="*60)
        
        print(f"\nOPERAZIONI:")
        print(f"  Totale: {stats['total_trades']}")
        print(f"  Long:   {dist['long_trades']:>4} | Win Rate: {dist['long_win_rate']:>6.2%}")
        print(f"  Short:  {dist['short_trades']:>4} | Win Rate: {dist['short_win_rate']:>6.2%}")
        print(f"  Win Rate Totale: {stats['win_rate']:.2%}")
        
        print(f"\nPERFORMANCE:")
        print(f"  Total P&L:      {stats['total_pnl']:>10.2f}")
        print(f"  Avg P&L:        {stats['avg_pnl']:>10.2f} ({stats['avg_pnl_pct']:>6.2%})")
        print(f"  Largest Win:    {stats['largest_win']:>10.2f}")
        print(f"  Largest Loss:   {stats['largest_loss']:>10.2f}")
        
        print(f"\nDURATIONE OPERAZIONI (giorni):")
        print(f"  Media:          {stats['avg_bars_held']:>10.1f}d")
        print(f"  Max:            {stats['max_bars_held']:>10.1f}d")
        print(f"  Min:            {stats['min_bars_held']:>10.1f}d")
        
        print("\n" + "="*60 + "\n")


class Plotter:
    """Utility per i grafici di analisi"""
    
    @staticmethod
    def plot_equity_curve(result: BacktestResult, figsize: tuple = (14, 6)):
        """Plotta la curva di equity con cumulative return percentuale"""
        fig, ax = plt.subplots(figsize=figsize)
        
        # Calcola il cumulative return percentuale
        initial_equity = result.equity_curve.iloc[0]
        cumulative_return = ((result.equity_curve.values - initial_equity) / initial_equity) * 100
        
        ax.plot(result.equity_curve.index, cumulative_return, linewidth=2, color='steelblue')
        ax.fill_between(result.equity_curve.index, cumulative_return, alpha=0.3, color='steelblue')
        
        # Aggiunge linea zero come riferimento
        ax.axhline(y=0, color='red', linestyle='--', linewidth=1, alpha=0.5)
        
        ax.set_title('Cumulative Return - TSMOM Strategy', fontsize=14, fontweight='bold')
        ax.set_xlabel('Date')
        ax.set_ylabel('Cumulative Return (%)')
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.show()
    
    @staticmethod
    def plot_pnl_distribution(result: BacktestResult, figsize: tuple = (14, 6)):
        """Plotta la distribuzione dei P&L"""
        pnl_dist = PerformanceAnalyzer.get_pnl_distribution(result)
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)
        
        # Istogramma
        ax1.hist(pnl_dist, bins=30, edgecolor='black', alpha=0.7)
        ax1.axvline(pnl_dist.mean(), color='red', linestyle='--', linewidth=2, label=f'Mean: {pnl_dist.mean():.2f}%')
        ax1.set_title('P&L Distribution', fontsize=12, fontweight='bold')
        ax1.set_xlabel('P&L (%)')
        ax1.set_ylabel('Frequency')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Boxplot
        ax2.boxplot(pnl_dist, vert=True)
        ax2.set_title('P&L Statistics', fontsize=12, fontweight='bold')
        ax2.set_ylabel('P&L (%)')
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.show()
    
    @staticmethod
    def plot_trades_on_price(
        signals_df: pd.DataFrame,
        result: BacktestResult,
        figsize: tuple = (14, 6)
    ):
        """Plotta i segnali e le operazioni sul grafico dei prezzi"""
        fig, ax = plt.subplots(figsize=figsize)
        
        ax.plot(signals_df.index, signals_df['close'], label='Price', linewidth=1.5, color='black')
        
        # Plotta le operazioni
        for trade in result.trades:
            if trade.is_closed():
                ax.plot(trade.entry_time, trade.entry_price, 'g^', markersize=8)
                ax.plot(trade.exit_time, trade.exit_price, 'rv', markersize=8)
        
        ax.set_title('TSMOM - Price and Trades', fontsize=14, fontweight='bold')
        ax.set_xlabel('Date')
        ax.set_ylabel('Price ($)')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.show()
