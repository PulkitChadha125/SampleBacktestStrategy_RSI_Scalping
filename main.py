"""
RSI Scalping Strategy - Main Execution Script
This script runs the complete trading strategy logic from the Jupyter notebook
and saves backtest results to the 'backtest' folder.
"""

import pandas as pd
import pandas_ta as ta
import numpy as np
import os
from datetime import datetime
from backtesting import Strategy, Backtest
import warnings
warnings.filterwarnings('ignore')


# ============================================================================
# CONFIGURATION - Modify these parameters to customize your strategy
# ============================================================================

# Technical Indicator Parameters
EMA_PERIOD = 200          # EMA period (default: 200)
RSI_PERIOD = 3            # RSI period (default: 3)
RSI_OVERSOLD = 10         # RSI oversold threshold for BUY signals (default: 10)
RSI_OVERBOUGHT = 90       # RSI overbought threshold for SELL signals (default: 90)
BACKCANDLES = 8           # Number of candles to check for EMA trend confirmation (default: 8)

# Strategy Names - Customize these to identify your backtest runs
STRATEGY_NAMES = {
    'Strategy1': 'Strategy1_FixedSLTP_Martingale',  # Fixed SL/TP with Martingale
    'Strategy2': 'Strategy2_ATRBased',              # ATR-Based SL/TP
    'Strategy3': 'Strategy3_TrailingStop_ATR'        # Trailing Stop with ATR
}

# Backtest Configuration
CSV_FILE = "EURUSD_Candlestick_5_M_Data.csv"
BACKTEST_FOLDER = "backtest"
BACKTEST_MONTHS = 30      # Number of months to backtest

# ============================================================================


def load_and_preprocess_data(csv_file):
    """Load and preprocess the candlestick data."""
    print(f"Loading data from {csv_file}...")
    df = pd.read_csv(csv_file)
    
    # Remove zero volume rows
    df = df[df['Volume'] != 0]
    
    # Check for missing values
    missing = df.isna().sum()
    if missing.sum() > 0:
        print(f"Warning: Found missing values:\n{missing[missing > 0]}")
    
    # Reset index
    df.reset_index(drop=True, inplace=True)
    
    print(f"Data loaded: {len(df)} rows")
    return df


def calculate_indicators(df, ema_period=200, rsi_period=3):
    """Calculate technical indicators: EMA, RSI, and ATR.
    
    Args:
        df: DataFrame with OHLCV data
        ema_period: Period for EMA calculation (default: 200)
        rsi_period: Period for RSI calculation (default: 3)
    
    Returns:
        DataFrame with added indicator columns
    """
    print(f"Calculating technical indicators (EMA{ema_period}, RSI{rsi_period})...")
    
    ema_col = f"EMA{ema_period}"
    df[ema_col] = ta.ema(df.Close, length=ema_period)
    df["RSI"] = ta.rsi(df.Close, length=rsi_period)
    df['ATR'] = df.ta.atr()
    
    print("Indicators calculated successfully")
    return df, ema_col


def generate_ema_signal(df, ema_col='EMA200', backcandles=8):
    """Generate EMA trend signal based on price position relative to EMA.
    
    Args:
        df: DataFrame with EMA column
        ema_col: Name of the EMA column (default: 'EMA200')
        backcandles: Number of candles to check for trend confirmation (default: 8)
    
    Returns:
        DataFrame with added EMAsignal column
    """
    print(f"Generating EMA signals (checking {backcandles} candles)...")
    
    emasignal = [0] * len(df)
    
    for row in range(backcandles-1, len(df)):
        upt = 1  # Uptrend flag
        dnt = 1  # Downtrend flag
        
        # Check if price stayed above/below EMA for the last 'backcandles' periods
        for i in range(row-backcandles, row+1):
            if df.High[i] >= df[ema_col][i]:
                dnt = 0  # Price touched or went above EMA, not a strong downtrend
            if df.Low[i] <= df[ema_col][i]:
                upt = 0  # Price touched or went below EMA, not a strong uptrend
        
        # Assign signal values
        if upt == 1 and dnt == 1:
            emasignal[row] = 3  # Ambiguous (shouldn't happen in practice)
        elif upt == 1:
            emasignal[row] = 2  # Strong uptrend
        elif dnt == 1:
            emasignal[row] = 1  # Strong downtrend
    
    df['EMAsignal'] = emasignal
    print("EMA signals generated successfully")
    return df


def generate_total_signal(df, rsi_oversold=10, rsi_overbought=90):
    """Generate final trading signal by combining EMA signal with RSI extremes.
    
    Args:
        df: DataFrame with EMAsignal and RSI columns
        rsi_oversold: RSI threshold for BUY signals (default: 10)
        rsi_overbought: RSI threshold for SELL signals (default: 90)
    
    Returns:
        DataFrame with added TotSignal column
    """
    print(f"Generating total trading signals (RSI oversold: {rsi_oversold}, overbought: {rsi_overbought})...")
    
    TotSignal = [0] * len(df)
    
    for row in range(0, len(df)):
        TotSignal[row] = 0
        
        # SELL signal: Strong downtrend (EMAsignal=1) AND RSI >= overbought threshold
        if df.EMAsignal[row] == 1 and df.RSI[row] >= rsi_overbought:
            TotSignal[row] = 1
        
        # BUY signal: Strong uptrend (EMAsignal=2) AND RSI <= oversold threshold
        if df.EMAsignal[row] == 2 and df.RSI[row] <= rsi_oversold:
            TotSignal[row] = 2
    
    df['TotSignal'] = TotSignal
    
    # Remove rows with NaN values
    df.dropna(inplace=True)
    df.reset_index(drop=True, inplace=True)
    
    signal_count = pd.Series(TotSignal).value_counts()
    print(f"Signals generated: {signal_count.get(1, 0)} SELL signals, {signal_count.get(2, 0)} BUY signals")
    
    return df


def prepare_backtest_data(df, months=30):
    """Prepare data subset for backtesting."""
    startid = 0
    total_periods = 24 * 4 * months  # 15-min periods in 'months' months
    dfpl = df[startid:startid + total_periods].copy()
    
    print(f"Prepared {len(dfpl)} rows for backtesting")
    return dfpl


# Strategy 1: Fixed SL/TP with Martingale
class Strategy1_FixedSLTP(Strategy):
    """Fixed 45-pip stop-loss and take-profit with Martingale position sizing."""
    initsize = 0.2
    mysize = initsize
    def init(self):
        super().init()
        # Signal will be set via closure in CustomStrategy subclass
    
    def next(self):
        super().next()
        
        # Martingale: Double position size after loss, reset after win
        if (self.signal1 > 0 and len(self.trades) == 0 and 
            len(self.closed_trades) > 0 and self.closed_trades[-1].pl < 0):
            self.mysize = self.mysize * 2
        elif len(self.closed_trades) > 0 and self.closed_trades[-1].pl > 0:
            self.mysize = self.initsize
        
        # BUY signal
        if self.signal1 == 2 and len(self.trades) == 0:
            sl1 = self.data.Close[-1] - 45e-4  # 45 pips stop-loss
            tp1 = self.data.Close[-1] + 45e-4  # 45 pips take-profit
            self.buy(sl=sl1, tp=tp1, size=self.mysize)
        
        # SELL signal
        elif self.signal1 == 1 and len(self.trades) == 0:
            sl1 = self.data.Close[-1] + 45e-4  # 45 pips stop-loss
            tp1 = self.data.Close[-1] - 45e-4  # 45 pips take-profit
            self.sell(sl=sl1, tp=tp1, size=self.mysize)


# Strategy 2: ATR-Based SL/TP
class Strategy2_ATRBased(Strategy):
    """ATR-based dynamic stop-loss and take-profit."""
    initsize = 0.2
    mysize = initsize
    def init(self):
        super().init()
        # Signal will be set via closure in CustomStrategy subclass
    
    def next(self):
        super().next()
        slatr = 1.3 * self.data.ATR[-1]
        TPSLRatio = 1.3
        
        # BUY signal
        if self.signal1 == 2 and len(self.trades) == 0:
            sl1 = self.data.Close[-1] - slatr
            tp1 = self.data.Close[-1] + slatr * TPSLRatio
            self.buy(sl=sl1, tp=tp1, size=self.mysize)
        
        # SELL signal
        elif self.signal1 == 1 and len(self.trades) == 0:
            sl1 = self.data.Close[-1] + slatr
            tp1 = self.data.Close[-1] - slatr * TPSLRatio
            self.sell(sl=sl1, tp=tp1, size=self.mysize)


# Strategy 3: Trailing Stop with ATR
class Strategy3_TrailingStop(Strategy):
    """Trailing stop-loss based on ATR with signal-based exit."""
    initsize = 0.2
    mysize = initsize
    def init(self):
        super().init()
        # Signal will be set via closure in CustomStrategy subclass
    
    def next(self):
        super().next()
        sltr = 1.5 * self.data.ATR[-1]
        
        # Manage existing trades with trailing stop
        for trade in self.trades:
            if trade.is_long:
                # Update trailing stop for long positions
                trade.sl = max(trade.sl or -np.inf, self.data.Close[-1] - sltr)
                # Close if opposite signal appears
                if self.signal1 == 1:
                    trade.close()
            else:
                # Update trailing stop for short positions
                trade.sl = min(trade.sl or np.inf, self.data.Close[-1] + sltr)
                # Close if opposite signal appears
                if self.signal1 == 2:
                    trade.close()
        
        # BUY signal
        if self.signal1 == 2 and len(self.trades) == 0:
            sl1 = self.data.Close[-1] - sltr
            self.buy(sl=sl1, size=self.mysize)
        
        # SELL signal
        elif self.signal1 == 1 and len(self.trades) == 0:
            sl1 = self.data.Close[-1] + sltr
            self.sell(sl=sl1, size=self.mysize)


def run_backtest(strategy_class, dfpl, signal_series, strategy_name, backtest_folder):
    """Run a backtest and save results."""
    print(f"\n{'='*60}")
    print(f"Running {strategy_name}...")
    print(f"{'='*60}")
    
    # Create a closure function that returns the signal, matching the notebook pattern
    def SIGNAL():
        return signal_series
    
    # Create a custom strategy class with the signal function
    class CustomStrategy(strategy_class):
        def init(self):
            super().init()
            # Override to use the closure function
            self.signal1 = self.I(SIGNAL)
    
    # Run backtest with the custom strategy
    bt = Backtest(dfpl, CustomStrategy, cash=100, margin=1/50, commission=.00)
    stats = bt.run()
    
    # Print summary
    print(f"\n{strategy_name} Results:")
    print(f"Return: {stats['Return [%]']:.2f}%")
    print(f"Sharpe Ratio: {stats.get('Sharpe Ratio', 'N/A')}")
    print(f"Max Drawdown: {stats['Max. Drawdown [%]']:.2f}%")
    print(f"# Trades: {stats['# Trades']}")
    print(f"Win Rate: {stats['Win Rate [%]']:.2f}%")
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Save statistics to CSV
    stats_file = os.path.join(backtest_folder, f"{strategy_name}_stats_{timestamp}.csv")
    stats_df = pd.DataFrame([stats])
    stats_df.to_csv(stats_file, index=False)
    print(f"Statistics saved to: {stats_file}")
    
    # Save detailed statistics to text file
    txt_file = os.path.join(backtest_folder, f"{strategy_name}_detailed_{timestamp}.txt")
    with open(txt_file, 'w') as f:
        f.write(f"{strategy_name} - Detailed Backtest Results\n")
        f.write(f"{'='*60}\n")
        f.write(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"{'='*60}\n\n")
        f.write(str(stats))
        f.write("\n\n")
        f.write("Trade History:\n")
        f.write(f"{'='*60}\n")
        if hasattr(stats, '_trades') and stats._trades is not None:
            f.write(str(stats._trades))
    
    print(f"Detailed results saved to: {txt_file}")
    
    # Save plot (if possible)
    try:
        plot_file = os.path.join(backtest_folder, f"{strategy_name}_plot_{timestamp}.html")
        fig = bt.plot(show_legend=False, open_browser=False)
        if fig is not None:
            try:
                from bokeh.io import save
                save(fig, plot_file)
                print(f"Plot saved to: {plot_file}")
            except (ImportError, AttributeError, Exception) as plot_error:
                # Plot saving is optional - main results are in CSV/text files
                print(f"Note: Plot not saved ({type(plot_error).__name__})")
    except Exception as e:
        # Plot saving is optional
        pass
    
    return stats, bt


def main():
    """Main execution function."""
    print("="*60)
    print("RSI Scalping Strategy - Backtest Execution")
    print("="*60)
    print(f"\nConfiguration:")
    print(f"  EMA Period: {EMA_PERIOD}")
    print(f"  RSI Period: {RSI_PERIOD}")
    print(f"  RSI Oversold: {RSI_OVERSOLD}")
    print(f"  RSI Overbought: {RSI_OVERBOUGHT}")
    print(f"  Backcandles: {BACKCANDLES}")
    print(f"  Strategy Names: {STRATEGY_NAMES}")
    print("="*60)
    
    # Create backtest folder if it doesn't exist
    if not os.path.exists(BACKTEST_FOLDER):
        os.makedirs(BACKTEST_FOLDER)
        print(f"Created backtest folder: {BACKTEST_FOLDER}")
    
    try:
        # Step 1: Load and preprocess data
        df = load_and_preprocess_data(CSV_FILE)
        
        # Step 2: Calculate indicators
        df, ema_col = calculate_indicators(df, ema_period=EMA_PERIOD, rsi_period=RSI_PERIOD)
        
        # Step 3: Generate EMA signal
        df = generate_ema_signal(df, ema_col=ema_col, backcandles=BACKCANDLES)
        
        # Step 4: Generate total signal
        df = generate_total_signal(df, rsi_oversold=RSI_OVERSOLD, rsi_overbought=RSI_OVERBOUGHT)
        
        # Step 5: Prepare backtest data
        dfpl = prepare_backtest_data(df, months=BACKTEST_MONTHS)
        # Pass the pandas Series directly - self.I() can handle Series
        signal_data = dfpl.TotSignal
        
        # Step 6: Run all three backtesting strategies
        results = {}
        
        # Strategy 1: Fixed SL/TP with Martingale
        stats1, bt1 = run_backtest(
            Strategy1_FixedSLTP, 
            dfpl, 
            signal_data, 
            STRATEGY_NAMES['Strategy1'],
            BACKTEST_FOLDER
        )
        results['Strategy1'] = stats1
        
        # Strategy 2: ATR-Based SL/TP
        stats2, bt2 = run_backtest(
            Strategy2_ATRBased, 
            dfpl, 
            signal_data, 
            STRATEGY_NAMES['Strategy2'],
            BACKTEST_FOLDER
        )
        results['Strategy2'] = stats2
        
        # Strategy 3: Trailing Stop with ATR
        stats3, bt3 = run_backtest(
            Strategy3_TrailingStop, 
            dfpl, 
            signal_data, 
            STRATEGY_NAMES['Strategy3'],
            BACKTEST_FOLDER
        )
        results['Strategy3'] = stats3
        
        # Step 7: Create comparison summary
        print(f"\n{'='*60}")
        print("STRATEGY COMPARISON SUMMARY")
        print(f"{'='*60}")
        
        comparison_data = {
            'Strategy': [STRATEGY_NAMES['Strategy1'], 
                        STRATEGY_NAMES['Strategy2'], 
                        STRATEGY_NAMES['Strategy3']],
            'Return [%]': [results['Strategy1']['Return [%]'], 
                          results['Strategy2']['Return [%]'], 
                          results['Strategy3']['Return [%]']],
            'Max Drawdown [%]': [results['Strategy1']['Max. Drawdown [%]'], 
                                results['Strategy2']['Max. Drawdown [%]'], 
                                results['Strategy3']['Max. Drawdown [%]']],
            '# Trades': [results['Strategy1']['# Trades'], 
                        results['Strategy2']['# Trades'], 
                        results['Strategy3']['# Trades']],
            'Win Rate [%]': [results['Strategy1']['Win Rate [%]'], 
                            results['Strategy2']['Win Rate [%]'], 
                            results['Strategy3']['Win Rate [%]']]
        }
        
        comparison_df = pd.DataFrame(comparison_data)
        print("\n" + comparison_df.to_string(index=False))
        
        # Save comparison
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        comparison_file = os.path.join(BACKTEST_FOLDER, f"Strategy_Comparison_{timestamp}.csv")
        comparison_df.to_csv(comparison_file, index=False)
        print(f"\nComparison saved to: {comparison_file}")
        
        print(f"\n{'='*60}")
        print("Backtest execution completed successfully!")
        print(f"All results saved to: {BACKTEST_FOLDER}")
        print(f"{'='*60}")
        
    except FileNotFoundError:
        print(f"Error: Could not find data file '{CSV_FILE}'")
        print("Please ensure the CSV file is in the same directory as main.py")
    except Exception as e:
        print(f"Error during execution: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

