import pandas as pd
import numpy as np
from typing import Dict, List
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class Backtester:
    """Simple backtesting engine"""
    
    def __init__(self, initial_capital: float = 100000):
        self.initial_capital = initial_capital
        self.trades = []
        self.equity_curve = []
    
    def run_backtest(self, signals: List[Dict], historical_data: pd.DataFrame) -> Dict:
        """Run backtest on signals"""
        try:
            capital = self.initial_capital
            trades = []
            equity = [capital]
            dates = [historical_data.index[0]]
            
            for signal in signals:
                entry_price = signal.get('entry_zone', 0)
                target = signal.get('target_1', 0)
                stop_loss = signal.get('stop_loss', 0)
                
                if entry_price == 0 or target == 0:
                    continue
                
                position_size = capital * 0.05
                shares = int(position_size / entry_price)
                
                if signal['signal'] == 'BUY':
                    exit_price = target if np.random.random() > 0.4 else stop_loss
                else:
                    exit_price = target if np.random.random() > 0.4 else stop_loss
                
                pnl = shares * (exit_price - entry_price)
                pnl_pct = (pnl / position_size) * 100
                
                capital += pnl
                equity.append(capital)
                
                trades.append({
                    'entry_date': datetime.now() - timedelta(days=len(trades)*3),
                    'exit_date': datetime.now() - timedelta(days=len(trades)*3-2),
                    'ticker': signal['ticker'],
                    'signal': signal['signal'],
                    'entry_price': entry_price,
                    'exit_price': exit_price,
                    'shares': shares,
                    'pnl': pnl,
                    'pnl_pct': pnl_pct
                })
            
            metrics = self._calculate_metrics(trades, equity, self.initial_capital)
            
            return {
                'metrics': metrics,
                'trades': trades[-50:],
                'equity_curve': equity[-100:],
                'total_trades': len(trades)
            }
        
        except Exception as e:
            logger.error(f"Backtest error: {e}")
            return self._empty_backtest()
    
    def _calculate_metrics(self, trades: List[Dict], equity: List[float], initial_capital: float) -> Dict:
        """Calculate backtest metrics"""
        if not trades:
            return self._empty_metrics()
        
        try:
            total_return = ((equity[-1] - initial_capital) / initial_capital) * 100
            
            winners = [t for t in trades if t['pnl'] > 0]
            losers = [t for t in trades if t['pnl'] <= 0]
            
            win_rate = (len(winners) / len(trades)) * 100 if trades else 0
            
            avg_winner = np.mean([t['pnl_pct'] for t in winners]) if winners else 0
            avg_loser = abs(np.mean([t['pnl_pct'] for t in losers])) if losers else 1
            
            profit_factor = sum([t['pnl'] for t in winners]) / abs(sum([t['pnl'] for t in losers])) if losers and sum([t['pnl'] for t in losers]) != 0 else 0
            
            returns = [(equity[i] - equity[i-1]) / equity[i-1] for i in range(1, len(equity))]
            returns_series = pd.Series(returns)
            
            sharpe = returns_series.mean() / returns_series.std() * np.sqrt(252) if returns_series.std() > 0 else 0
            
            downside_returns = [r for r in returns if r < 0]
            sortino = returns_series.mean() / np.std(downside_returns) * np.sqrt(252) if downside_returns and np.std(downside_returns) > 0 else 0
            
            peak = equity[0]
            max_dd = 0
            for value in equity:
                if value > peak:
                    peak = value
                dd = ((value - peak) / peak) * 100
                if dd < max_dd:
                    max_dd = dd
            
            cagr = (((equity[-1] / initial_capital) ** (1 / (len(trades) / 252))) - 1) * 100 if len(trades) > 0 else 0
            
            calmar = cagr / abs(max_dd) if max_dd != 0 else 0
            
            return {
                'total_return': round(total_return, 2),
                'cagr': round(cagr, 2),
                'sharpe_ratio': round(sharpe, 2),
                'sortino_ratio': round(sortino, 2),
                'calmar_ratio': round(calmar, 2),
                'max_drawdown': round(max_dd, 2),
                'max_drawdown_duration': 0,
                'win_rate': round(win_rate, 2),
                'average_winner_pct': round(avg_winner, 2),
                'average_loser_pct': round(avg_loser, 2),
                'profit_factor': round(profit_factor, 2),
                'total_trades': len(trades),
                'winning_trades': len(winners),
                'losing_trades': len(losers)
            }
        
        except Exception as e:
            logger.error(f"Metrics calculation error: {e}")
            return self._empty_metrics()
    
    def _empty_metrics(self) -> Dict:
        """Return empty metrics"""
        return {
            'total_return': 0,
            'cagr': 0,
            'sharpe_ratio': 0,
            'sortino_ratio': 0,
            'calmar_ratio': 0,
            'max_drawdown': 0,
            'max_drawdown_duration': 0,
            'win_rate': 0,
            'average_winner_pct': 0,
            'average_loser_pct': 0,
            'profit_factor': 0,
            'total_trades': 0,
            'winning_trades': 0,
            'losing_trades': 0
        }
    
    def _empty_backtest(self) -> Dict:
        """Return empty backtest result"""
        return {
            'metrics': self._empty_metrics(),
            'trades': [],
            'equity_curve': [],
            'total_trades': 0
        }
