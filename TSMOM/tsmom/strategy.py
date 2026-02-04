"""
TSMOM Strategy Core
Calcolo del segnale momentum su due orizzonti temporali
"""

import pandas as pd
import numpy as np
from enum import Enum
from dataclasses import dataclass


class SignalState(Enum):
    """Stati possibili del segnale"""
    LONG = 1
    SHORT = -1
    FLAT = 0


@dataclass
class TSMOMSignal:
    """Risultato del calcolo del segnale"""
    timestamp: pd.Timestamp
    state: SignalState
    momentum_short: float  # Momentum su orizzonte breve
    momentum_long: float   # Momentum su orizzonte lungo
    score: float           # Score composito


class TSMOM:
    """
    Time Series Momentum Strategy
    
    Calcola i ritorni su due orizzonti temporali e genera segnali
    basati sulla combinazione dei momentum a breve e lungo termine.
    """
    
    def __init__(
        self,
        period_short: int = 5,
        period_long: int = 20,
        threshold: float = 0.0
    ):
        """
        Inizializza la strategia TSMOM
        
        Args:
            period_short: Periodo per il momentum a breve (in bar)
            period_long: Periodo per il momentum a lungo (in bar)
            threshold: Soglia minima per il cambio di stato
        """
        self.period_short = period_short
        self.period_long = period_long
        self.threshold = threshold
        
    def calculate_returns(self, prices: pd.Series, period: int) -> pd.Series:
        """
        Calcola i ritorni percentuali su un periodo specifico
        
        Args:
            prices: Serie dei prezzi di chiusura
            period: Numero di periodi per il calcolo dei ritorni
            
        Returns:
            Serie dei ritorni percentuali
        """
        return prices.pct_change(periods=period)
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Genera i segnali TSMOM per la serie storica
        
        Args:
            data: DataFrame con colonna 'close' (prezzi di chiusura)
                  Index deve essere datetime
                  
        Returns:
            DataFrame con colonne aggiuntive:
            - momentum_short: Momentum a breve termine
            - momentum_long: Momentum a lungo termine
            - signal_state: Stato del segnale (LONG/SHORT/FLAT)
            - signal_value: Valore numerico del segnale (-1, 0, 1)
            - signal_score: Score composito del segnale
        """
        df = data.copy()
        
        # Calcolo dei momentum
        df['momentum_short'] = self.calculate_returns(
            df['close'], 
            self.period_short
        )
        df['momentum_long'] = self.calculate_returns(
            df['close'], 
            self.period_long
        )
        
        # Score composito: media ponderata dei due momentum
        df['signal_score'] = (
            0.4 * df['momentum_short'] + 
            0.6 * df['momentum_long']
        )
        
        # Generazione dei segnali
        df['signal_value'] = 0
        df.loc[df['signal_score'] > self.threshold, 'signal_value'] = 1
        df.loc[df['signal_score'] < -self.threshold, 'signal_value'] = -1
        
        # Mapping ai stati
        df['signal_state'] = df['signal_value'].map({
            1: SignalState.LONG,
            0: SignalState.FLAT,
            -1: SignalState.SHORT
        })
        
        return df
    
    def get_signal_at(
        self,
        data: pd.DataFrame,
        timestamp: pd.Timestamp
    ) -> TSMOMSignal:
        """
        Recupera il segnale per un timestamp specifico
        
        Args:
            data: DataFrame con i dati e i segnali già calcolati
            timestamp: Timestamp per cui recuperare il segnale
            
        Returns:
            Oggetto TSMOMSignal
        """
        if timestamp not in data.index:
            raise ValueError(f"Timestamp {timestamp} non trovato nei dati")
        
        row = data.loc[timestamp]
        
        return TSMOMSignal(
            timestamp=timestamp,
            state=row['signal_state'],
            momentum_short=row['momentum_short'],
            momentum_long=row['momentum_long'],
            score=row['signal_score']
        )
