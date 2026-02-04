"""
Backtest Engine
Motore di simulazione per la strategia TSMOM
"""

import pandas as pd
import numpy as np
from dataclasses import dataclass, field
from typing import List
from enum import Enum

from tsmom.strategy import TSMOM, SignalState


class PositionState(Enum):
    """Stati della posizione"""
    NONE = 0
    LONG = 1
    SHORT = -1


@dataclass
class Trade:
    """Rappresenta un'operazione di trading"""
    entry_time: pd.Timestamp
    entry_price: float
    entry_state: SignalState
    exit_time: pd.Timestamp = None
    exit_price: float = None
    pnl: float = None
    pnl_pct: float = None
    bars_held: int = None
    
    def close(self, exit_time: pd.Timestamp, exit_price: float):
        """Chiude l'operazione"""
        self.exit_time = exit_time
        self.exit_price = exit_price
        self.bars_held = self._calculate_bars()
        
        if self.entry_state == SignalState.LONG:
            self.pnl = exit_price - self.entry_price
            self.pnl_pct = (exit_price - self.entry_price) / self.entry_price
        else:  # SHORT
            self.pnl = self.entry_price - exit_price
            self.pnl_pct = (self.entry_price - exit_price) / self.entry_price
    
    def _calculate_bars(self) -> int:
        """Calcola il numero di bar della posizione"""
        if self.exit_time and self.entry_time:
            # Calcola il numero di giorni (per dati giornalieri)
            # o ore (per dati orari)
            return (self.exit_time - self.entry_time).days
        return None
    
    def is_closed(self) -> bool:
        """Verifica se l'operazione è chiusa"""
        return self.exit_price is not None


@dataclass
class BacktestResult:
    """Risultati del backtest"""
    trades: List[Trade] = field(default_factory=list)
    equity_curve: pd.Series = None
    
    @property
    def total_trades(self) -> int:
        """Numero totale di operazioni chiuse"""
        return len([t for t in self.trades if t.is_closed()])
    
    @property
    def winning_trades(self) -> int:
        """Numero di operazioni in profitto"""
        return len([t for t in self.trades if t.is_closed() and t.pnl > 0])
    
    @property
    def losing_trades(self) -> int:
        """Numero di operazioni in perdita"""
        return len([t for t in self.trades if t.is_closed() and t.pnl < 0])
    
    @property
    def win_rate(self) -> float:
        """Percentuale di operazioni in profitto"""
        total = self.total_trades
        return self.winning_trades / total if total > 0 else 0
    
    @property
    def total_pnl(self) -> float:
        """P&L totale"""
        return sum(t.pnl for t in self.trades if t.is_closed())
    
    @property
    def avg_pnl_pct(self) -> float:
        """P&L medio in percentuale"""
        closed_trades = [t for t in self.trades if t.is_closed()]
        if not closed_trades:
            return 0
        return np.mean([t.pnl_pct for t in closed_trades])


class BacktestEngine:
    """
    Motore di backtesting semplice per TSMOM
    
    Logica:
    - Entrata: quando il segnale cambia a LONG o SHORT
    - Uscita: quando il segnale cambia (da LONG a SHORT, FLAT, ecc.)
    - Sempre una sola posizione aperta alla volta
    """
    
    def __init__(self, strategy: TSMOM, initial_capital: float = 10000):
        """
        Inizializza il motore di backtest
        
        Args:
            strategy: Istanza di TSMOM
            initial_capital: Capitale iniziale
        """
        self.strategy = strategy
        self.initial_capital = initial_capital
        
    def run(self, data: pd.DataFrame) -> BacktestResult:
        """
        Esegue il backtest sulla serie storica
        
        Args:
            data: DataFrame con colonna 'close' (OHLC)
            
        Returns:
            BacktestResult con i risultati del backtest
        """
        # Genera i segnali
        signals_df = self.strategy.generate_signals(data)
        
        result = BacktestResult()
        current_position = None
        current_state = SignalState.FLAT
        
        # Itera su ogni riga del dataframe
        for idx, row in signals_df.iterrows():
            new_state = row['signal_state']
            current_price = row['close']
            
            # Cambio di segnale: chiudi posizione e aprine una nuova
            if new_state != current_state:
                
                # Chiudi posizione precedente se esiste
                if current_position is not None:
                    current_position.close(idx, current_price)
                    result.trades.append(current_position)
                
                # Apri nuova posizione se non è FLAT
                if new_state != SignalState.FLAT:
                    current_position = Trade(
                        entry_time=idx,
                        entry_price=current_price,
                        entry_state=new_state
                    )
                else:
                    current_position = None
                
                current_state = new_state
        
        # Chiudi posizione finale se ancora aperta
        if current_position is not None:
            current_position.close(signals_df.index[-1], signals_df.iloc[-1]['close'])
            result.trades.append(current_position)
        
        # Calcola l'equity curve
        result.equity_curve = self._calculate_equity_curve(
            signals_df, result.trades
        )
        
        return result
    
    def _calculate_equity_curve(
        self,
        signals_df: pd.DataFrame,
        trades: List[Trade]
    ) -> pd.Series:
        """Calcola la curva di equity in modo semplificato"""
        equity = pd.Series(
            self.initial_capital, 
            index=signals_df.index, 
            dtype=float
        )
        
        # Itera su ogni timestamp e calcola il P&L cumulative
        cumulative_pnl = 0
        
        for i, (idx, row) in enumerate(signals_df.iterrows()):
            current_price = row['close']
            
            # Cerca il trade attivo a questo timestamp
            active_trade = None
            for trade in trades:
                if (trade.entry_time <= idx and 
                    (trade.exit_time is None or trade.exit_time >= idx)):
                    active_trade = trade
                    break
            
            # Se c'è un trade attivo, calcola l'unrealized P&L
            if active_trade:
                entry_price = active_trade.entry_price
                
                if active_trade.entry_state == SignalState.LONG:
                    unrealized_pnl = current_price - entry_price
                else:  # SHORT
                    unrealized_pnl = entry_price - current_price
                
                equity.iloc[i] = self.initial_capital + cumulative_pnl + unrealized_pnl
            else:
                # Nessun trade attivo
                equity.iloc[i] = self.initial_capital + cumulative_pnl
            
            # Se il trade è stato chiuso, aggiorna il P&L cumulativo
            if active_trade and active_trade.exit_time == idx:
                cumulative_pnl += active_trade.pnl
        
        return equity
