# RSI Scalping Strategy - Backtesting System

A comprehensive backtesting system for an RSI (Relative Strength Index) scalping strategy on EUR/USD forex data. This project implements three different trading strategies with various risk management approaches and provides detailed backtest results.

## 📋 Table of Contents

- [Overview](#overview)
- [Requirements](#requirements)
- [Setup Instructions](#setup-instructions)
- [How to Run](#how-to-run)
- [Long and Short Entry Conditions](#-long-and-short-entry-conditions)
- [Code Logic Explanation](#code-logic-explanation)
- [Backtesting Strategies](#5-backtesting-strategies)
- [Stop-Loss Modification Summary](#stop-loss-modification-summary)
- [Output Structure](#output-structure)
- [Configuration](#-configuration)
- [Troubleshooting](#troubleshooting)

---

## 🎯 Overview

This project implements a **15-minute RSI scalping strategy** for EUR/USD forex trading. The strategy combines:

- **EMA200** (200-period Exponential Moving Average) for trend identification
- **RSI(3)** (3-period Relative Strength Index) for overbought/oversold signals
- **ATR** (Average True Range) for dynamic stop-loss and take-profit calculations

The system backtests three different strategy variants and saves comprehensive results including statistics, trade history, and visualizations.

### ✨ Key Features

- **Fully Modular Configuration**: All parameters (EMA period, RSI period, thresholds, backcandles, strategy names) are configurable at the top of `main.py`
- **Three Risk Management Strategies**: Fixed SL/TP, ATR-Based, and Trailing Stop
- **Clear Entry Conditions**: Well-defined long and short entry rules
- **Comprehensive Backtesting**: Detailed statistics, trade history, and visualizations
- **Customizable Strategy Names**: Name your backtest runs with your parameter combinations

---

## 📦 Requirements

### Python Version
- **Python 3.8 or higher** (Python 3.9+ recommended)

### Required Python Packages
All required packages are listed in `requirements.txt`:

- `pandas >= 1.5.0` - Data manipulation and analysis
- `pandas-ta >= 0.3.14b0` - Technical analysis indicators
- `numpy >= 1.24.0` - Numerical computations
- `plotly >= 5.14.0` - Data visualization (optional, for plots)
- `backtesting >= 0.3.3` - Backtesting framework
- `bokeh` - Interactive plotting (installed as dependency of backtesting)

### Data File
- `EURUSD_Candlestick_5_M_Data.csv` - Historical EUR/USD candlestick data with columns:
  - `Gmt time` - Timestamp
  - `Open`, `High`, `Low`, `Close` - OHLC price data
  - `Volume` - Trading volume

---

## 🚀 Setup Instructions

### Step 1: Install Python
If you don't have Python installed:
1. Download Python 3.9+ from [python.org](https://www.python.org/downloads/)
2. During installation, check "Add Python to PATH"
3. Verify installation: Open Command Prompt and run `python --version`

### Step 2: Create Virtual Environment (Recommended)
```bash
# Navigate to project directory
cd "D:\Desktop\Youtube Videos And Projects\project\RSI Scalping strategy"

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Windows (PowerShell):
.venv\Scripts\Activate.ps1
# On Windows (Command Prompt):
.venv\Scripts\activate.bat
```

### Step 3: Install Dependencies
```bash
# Make sure virtual environment is activated, then:
pip install -r requirements.txt
```

### Step 4: Verify Data File
Ensure `EURUSD_Candlestick_5_M_Data.csv` is in the same directory as `main.py`.

---

## ▶️ How to Run

### Method 1: Using run.bat (Easiest)
1. **Double-click** `run.bat` file
2. The script will:
   - Activate the virtual environment (if `.venv` exists)
   - Run the backtest
   - Display results in the console
   - Keep the window open to view results

### Method 2: Using Command Line
```bash
# Activate virtual environment first (if using one)
.venv\Scripts\Activate.ps1

# Run the script
python main.py
```

### Method 3: Using Python Directly
```bash
# If not using virtual environment
python main.py
```

---

## 📚 Code Logic Explanation

### 1. Data Loading and Preprocessing (`load_and_preprocess_data`)

```python
df = pd.read_csv(csv_file)
df = df[df['Volume'] != 0]  # Remove invalid zero-volume rows
df.reset_index(drop=True, inplace=True)
```

**Purpose**: Loads historical candlestick data and removes invalid entries.

**What it does**:
- Reads CSV file into pandas DataFrame
- Filters out rows with zero volume (invalid data)
- Checks for missing values
- Resets index for clean sequential numbering

---

### 2. Technical Indicators Calculation (`calculate_indicators`)

```python
df["EMA200"] = ta.ema(df.Close, length=200)
df["RSI"] = ta.rsi(df.Close, length=3)
df['ATR'] = df.ta.atr()
```

**Purpose**: Calculates three key technical indicators.

**Indicators**:
- **EMA200**: 200-period Exponential Moving Average - identifies long-term trend direction
- **RSI(3)**: 3-period Relative Strength Index - measures momentum (0-100 scale)
  - RSI ≤ 10: Oversold (potential buy signal)
  - RSI ≥ 90: Overbought (potential sell signal)
- **ATR**: Average True Range - measures market volatility for dynamic stop-loss/take-profit

---

### 3. EMA Trend Signal Generation (`generate_ema_signal`)

```python
# Checks if price stayed above/below EMA200 for 8 consecutive candles
for i in range(row-backcandles, row+1):
    if df.High[row] >= df.EMA200[row]:
        dnt = 0  # Not a strong downtrend
    if df.Low[row] <= df.EMA200[row]:
        upt = 0  # Not a strong uptrend
```

**Purpose**: Identifies strong trends by checking if price consistently stays above or below EMA200.

**Signal Values**:
- `EMAsignal = 2`: **Strong Uptrend** - Price stayed above EMA200 for 8+ consecutive periods
- `EMAsignal = 1`: **Strong Downtrend** - Price stayed below EMA200 for 8+ consecutive periods
- `EMAsignal = 0`: **No clear trend** - Price crossed EMA200 recently

**Logic**: Only trades in strong, established trends to avoid choppy market conditions.

---

### 4. Total Trading Signal Generation (`generate_total_signal`)

```python
# SELL signal: Strong downtrend + Overbought RSI
if df.EMAsignal[row] == 1 and df.RSI[row] >= 90:
    TotSignal[row] = 1

# BUY signal: Strong uptrend + Oversold RSI
if df.EMAsignal[row] == 2 and df.RSI[row] <= 10:
    TotSignal[row] = 2
```

**Purpose**: Combines trend filter (EMA) with momentum filter (RSI) to generate entry signals.

**Signal Logic**:
- **BUY Signal (TotSignal = 2)**:
  - Strong uptrend (EMAsignal = 2) **AND**
  - RSI ≤ 10 (oversold - price likely to bounce up)
  
- **SELL Signal (TotSignal = 1)**:
  - Strong downtrend (EMAsignal = 1) **AND**
  - RSI ≥ 90 (overbought - price likely to drop)

**Why this works**: Trades with the trend (EMA filter) but enters on counter-trend pullbacks (RSI extremes), capturing mean reversion within a strong trend.

---

## 📈 Long and Short Entry Conditions

### **LONG (BUY) Entry Conditions**

A **LONG position** is opened when **ALL** of the following conditions are met:

1. **Strong Uptrend Confirmation (EMA Filter)**:
   - Price has stayed **above** the EMA200 (or configured EMA period) for the last **8 candles** (or configured `BACKCANDLES`)
   - This means: `EMAsignal = 2` (Strong Uptrend)
   - **Logic**: We only want to buy in established uptrends, avoiding choppy/sideways markets

2. **Oversold RSI Condition**:
   - RSI(3) (or configured RSI period) is **≤ 10** (or configured `RSI_OVERSOLD` threshold)
   - **Logic**: Even in an uptrend, we wait for a pullback/oversold condition to enter at better prices

3. **No Existing Position**:
   - There are no open trades currently
   - **Logic**: Only one position at a time to manage risk

**Summary**: 
- ✅ Price above EMA for 8+ consecutive candles (strong uptrend)
- ✅ RSI ≤ 10 (oversold - temporary pullback in uptrend)
- ✅ No existing position

**Trading Logic**: We're buying the dip in an uptrend - entering long when price temporarily pulls back (oversold RSI) but the overall trend is still up (EMA confirmation).

---

### **SHORT (SELL) Entry Conditions**

A **SHORT position** is opened when **ALL** of the following conditions are met:

1. **Strong Downtrend Confirmation (EMA Filter)**:
   - Price has stayed **below** the EMA200 (or configured EMA period) for the last **8 candles** (or configured `BACKCANDLES`)
   - This means: `EMAsignal = 1` (Strong Downtrend)
   - **Logic**: We only want to sell in established downtrends, avoiding choppy/sideways markets

2. **Overbought RSI Condition**:
   - RSI(3) (or configured RSI period) is **≥ 90** (or configured `RSI_OVERBOUGHT` threshold)
   - **Logic**: Even in a downtrend, we wait for a bounce/overbought condition to enter at better prices

3. **No Existing Position**:
   - There are no open trades currently
   - **Logic**: Only one position at a time to manage risk

**Summary**: 
- ✅ Price below EMA for 8+ consecutive candles (strong downtrend)
- ✅ RSI ≥ 90 (overbought - temporary bounce in downtrend)
- ✅ No existing position

**Trading Logic**: We're selling the bounce in a downtrend - entering short when price temporarily bounces up (overbought RSI) but the overall trend is still down (EMA confirmation).

---

### **Visual Example**

```
LONG Entry Example:
Price Chart:     EMA200: ────────────────
                 
                 ↑ BUY HERE (RSI ≤ 10, price above EMA for 8+ candles)
                 │
    ─────────────┼───────────────  ← Price above EMA (uptrend)
                 │
                 │
                 
SHORT Entry Example:
                 
                 │
    ─────────────┼───────────────  ← Price below EMA (downtrend)
                 │
                 ↓ SELL HERE (RSI ≥ 90, price below EMA for 8+ candles)
                 
                 EMA200: ────────────────
```

---

### 5. Backtesting Strategies

The system implements **three different risk management approaches**:

#### Strategy 1: Fixed SL/TP with Martingale (`Strategy1_FixedSLTP`)

**Risk Management**:
- **Stop-Loss**: Fixed 45 pips (0.0045 in price terms)
- **Take-Profit**: Fixed 45 pips (0.0045 in price terms)
- **Risk/Reward Ratio**: 1:1 (equal stop-loss and take-profit)
- **Position Sizing**: Martingale system
  - Starts with 0.2 units
  - **Doubles position size after a loss** (to recover previous loss)
  - **Resets to 0.2 units after a win** (returns to base size)

**Entry Logic**:
```python
# BUY Signal
if self.signal1 == 2 and len(self.trades) == 0:
    sl1 = self.data.Close[-1] - 45e-4  # 45 pips below entry
    tp1 = self.data.Close[-1] + 45e-4  # 45 pips above entry
    self.buy(sl=sl1, tp=tp1, size=self.mysize)

# SELL Signal
elif self.signal1 == 1 and len(self.trades) == 0:
    sl1 = self.data.Close[-1] + 45e-4  # 45 pips above entry
    tp1 = self.data.Close[-1] - 45e-4  # 45 pips below entry
    self.sell(sl=sl1, tp=tp1, size=self.mysize)
```

**Stop-Loss Modification**: 
- **NO modification** - Stop-loss and take-profit are set at entry and remain fixed
- Once set, they do not change until the trade is closed
- Trade exits only when:
  - Take-profit is hit (profit target reached)
  - Stop-loss is hit (loss limit reached)

**Martingale Position Sizing Logic**:
```python
# After a losing trade, double the position size
if (self.signal1 > 0 and len(self.trades) == 0 and 
    len(self.closed_trades) > 0 and self.closed_trades[-1].pl < 0):
    self.mysize = self.mysize * 2  # Double size

# After a winning trade, reset to initial size
elif len(self.closed_trades) > 0 and self.closed_trades[-1].pl > 0:
    self.mysize = self.initsize  # Reset to 0.2
```

**Pros**: 
- Simple and predictable risk/reward ratio
- Martingale can recover losses quickly in winning streaks
- Easy to understand and implement

**Cons**: 
- Fixed stops don't adapt to market volatility
- Martingale can lead to large position sizes after consecutive losses
- Risk of account blowout if losing streak continues

---

#### Strategy 2: ATR-Based Dynamic SL/TP (`Strategy2_ATRBased`)

**Risk Management**:
- **Stop-Loss**: **1.3 × ATR** (adapts to current market volatility)
- **Take-Profit**: **1.3 × Stop-Loss** = **1.69 × ATR** (approximately 1.3:1 risk/reward ratio)
- **Position Sizing**: Fixed 0.2 units (no Martingale)

**Entry Logic**:
```python
slatr = 1.3 * self.data.ATR[-1]  # Stop-loss distance = 1.3 × ATR
TPSLRatio = 1.3                   # Take-profit is 1.3× the stop-loss distance

# BUY Signal
if self.signal1 == 2 and len(self.trades) == 0:
    sl1 = self.data.Close[-1] - slatr              # Stop-loss below entry
    tp1 = self.data.Close[-1] + slatr * TPSLRatio  # Take-profit above entry
    self.buy(sl=sl1, tp=tp1, size=self.mysize)

# SELL Signal
elif self.signal1 == 1 and len(self.trades) == 0:
    sl1 = self.data.Close[-1] + slatr              # Stop-loss above entry
    tp1 = self.data.Close[-1] - slatr * TPSLRatio  # Take-profit below entry
    self.sell(sl=sl1, tp=tp1, size=self.mysize)
```

**Stop-Loss Modification**: 
- **NO modification during trade** - Stop-loss and take-profit are calculated at entry based on current ATR
- ATR is recalculated each bar, but the stop-loss/take-profit for existing trades remain fixed
- Trade exits only when:
  - Take-profit is hit (profit target reached)
  - Stop-loss is hit (loss limit reached)

**How ATR Adapts to Volatility**:
- **Low Volatility**: ATR is small → Tighter stops (less risk per trade)
- **High Volatility**: ATR is large → Wider stops (more room for price movement)
- **Example**: 
  - If ATR = 0.0010 (10 pips), Stop-Loss = 0.0013 (13 pips)
  - If ATR = 0.0020 (20 pips), Stop-Loss = 0.0026 (26 pips)

**Pros**: 
- Adapts to market volatility automatically
- Wider stops in volatile markets prevent premature exits
- Tighter stops in calm markets reduce risk
- Better risk/reward ratio (1.3:1) than Strategy 1

**Cons**: 
- May have larger losses in high volatility periods
- Stop-loss can be quite wide during volatile market conditions
- Fixed position sizing (no recovery mechanism like Martingale)

---

#### Strategy 3: Trailing Stop with ATR (`Strategy3_TrailingStop`)

**Risk Management**:
- **Initial Stop-Loss**: **1.5 × ATR** (wider than Strategy 2 to allow for more movement)
- **Trailing Stop**: **Continuously updates** as price moves favorably (locks in profits)
- **Exit Conditions**: 
  1. Trailing stop is hit (price reverses)
  2. Opposite signal appears (trend reversal signal)
- **Position Sizing**: Fixed 0.2 units (no Martingale)

**Entry Logic**:
```python
sltr = 1.5 * self.data.ATR[-1]  # Trailing stop distance = 1.5 × ATR

# BUY Signal
if self.signal1 == 2 and len(self.trades) == 0:
    sl1 = self.data.Close[-1] - sltr  # Initial stop-loss below entry
    self.buy(sl=sl1, size=self.mysize)  # NO take-profit (trailing stop manages exit)

# SELL Signal
elif self.signal1 == 1 and len(self.trades) == 0:
    sl1 = self.data.Close[-1] + sltr  # Initial stop-loss above entry
    self.sell(sl=sl1, size=self.mysize)  # NO take-profit
```

**Stop-Loss Modification - Trailing Stop Mechanism**:

This is the **KEY DIFFERENCE** from Strategies 1 and 2. The stop-loss is **actively modified** during the trade:

**For LONG Positions**:
```python
for trade in self.trades:
    if trade.is_long:
        # Calculate new trailing stop level
        new_sl = self.data.Close[-1] - sltr  # Current price - 1.5×ATR
        
        # Update stop-loss ONLY if it moves up (locks in profit)
        trade.sl = max(trade.sl or -np.inf, new_sl)
        
        # Exit if opposite signal appears
        if self.signal1 == 1:  # SELL signal
            trade.close()
```

**For SHORT Positions**:
```python
    else:  # Short position
        # Calculate new trailing stop level
        new_sl = self.data.Close[-1] + sltr  # Current price + 1.5×ATR
        
        # Update stop-loss ONLY if it moves down (locks in profit)
        trade.sl = min(trade.sl or np.inf, new_sl)
        
        # Exit if opposite signal appears
        if self.signal1 == 2:  # BUY signal
            trade.close()
```

**How Trailing Stop Works**:

1. **At Entry**: Stop-loss is set at entry price ± 1.5×ATR
   - LONG: Entry - 1.5×ATR
   - SHORT: Entry + 1.5×ATR

2. **As Price Moves Favorably**:
   - **LONG Example**: If price moves from 1.1000 → 1.1050
     - Initial SL: 1.1000 - (1.5×ATR) = 1.0985
     - New SL: 1.1050 - (1.5×ATR) = 1.1035
     - Stop-loss **moves up** from 1.0985 to 1.1035 (locks in profit)
   
   - **SHORT Example**: If price moves from 1.1000 → 1.0950
     - Initial SL: 1.1000 + (1.5×ATR) = 1.1015
     - New SL: 1.0950 + (1.5×ATR) = 1.0965
     - Stop-loss **moves down** from 1.1015 to 1.0965 (locks in profit)

3. **Stop-Loss Only Moves in Favorable Direction**:
   - Uses `max()` for longs (only moves up)
   - Uses `min()` for shorts (only moves down)
   - **Never moves against you** - once profit is locked in, it stays locked

4. **Exit Conditions**:
   - **Trailing stop hit**: Price reverses and hits the trailing stop (profit locked in)
   - **Opposite signal**: New signal appears in opposite direction (trend reversal)

**Visual Example of Trailing Stop**:
```
LONG Position:
Price: 1.1000 (Entry)
SL:    1.0985 (Initial)

Price: 1.1020 ↑
SL:    1.1005 ↑ (moved up, locks in profit)

Price: 1.1040 ↑
SL:    1.1025 ↑ (moved up again)

Price: 1.1010 ↓ (reversal)
SL:    1.1025 (unchanged - doesn't move down)
→ Trade exits at 1.1025 (profit locked in)
```

**Pros**: 
- **Locks in profits** as price moves favorably
- Can capture **larger moves** (no fixed take-profit limit)
- Adapts to volatility (uses ATR)
- Protects against reversals while allowing profits to run

**Cons**: 
- May exit early on temporary pullbacks (trailing stop gets hit)
- No fixed take-profit (relies on trailing stop for exit)
- Can give back profits if price reverses quickly
- More complex than fixed stop-loss strategies

---

### Stop-Loss Modification Summary

| Strategy | Stop-Loss Type | Modification During Trade | How It Works |
|----------|---------------|---------------------------|-------------|
| **Strategy 1** | Fixed | ❌ **NO** - Set at entry, never changes | Stop-loss and take-profit remain fixed until trade closes |
| **Strategy 2** | ATR-Based Fixed | ❌ **NO** - Set at entry based on ATR, never changes | Stop-loss calculated from ATR at entry, but remains fixed |
| **Strategy 3** | Trailing Stop | ✅ **YES** - Continuously updates | Stop-loss moves in favorable direction only, locks in profits |

**Key Differences**:

1. **Strategy 1 (Fixed)**: 
   - Stop-loss = Entry ± 45 pips (fixed)
   - Never changes during trade
   - Simple but doesn't adapt to market conditions

2. **Strategy 2 (ATR-Based Fixed)**: 
   - Stop-loss = Entry ± (1.3 × ATR) (calculated at entry)
   - Adapts to volatility **at entry**, but remains fixed during trade
   - Better than Strategy 1 for volatility adaptation

3. **Strategy 3 (Trailing Stop)**: 
   - Stop-loss = Current Price ± (1.5 × ATR) (recalculated each bar)
   - **Only moves in favorable direction** (locks in profits)
   - Most sophisticated - allows profits to run while protecting gains

**When to Use Each**:
- **Strategy 1**: Simple markets, predictable volatility, quick scalps
- **Strategy 2**: Volatile markets where you want wider stops but fixed risk
- **Strategy 3**: Trending markets where you want to capture large moves

---

### 6. Backtest Execution (`run_backtest`)

**Process**:
1. Creates a closure function `SIGNAL()` that returns the signal Series
2. Creates a `CustomStrategy` subclass that injects the signal into the strategy
3. Runs backtest with:
   - Initial capital: $100
   - Margin: 1/50 (50:1 leverage)
   - Commission: 0% (can be modified)
4. Saves results:
   - Statistics CSV file
   - Detailed text report
   - Interactive HTML plot (if bokeh available)

**Backtest Parameters** (in `main()`):
- `cash=100`: Starting capital
- `margin=1/50`: 50:1 leverage (forex standard)
- `commission=.00`: No commission (modify for realistic costs)
- `BACKTEST_MONTHS=30`: Number of months to backtest

---

### 7. Main Execution Flow (`main`)

```
1. Load and preprocess data
   ↓
2. Calculate indicators (EMA200, RSI, ATR)
   ↓
3. Generate EMA trend signals
   ↓
4. Generate total trading signals (EMA + RSI)
   ↓
5. Prepare backtest data subset
   ↓
6. Run all three strategies
   ↓
7. Generate comparison summary
   ↓
8. Save all results to 'backtest' folder
```

---

## 📁 Output Structure

After running the backtest, results are saved in the `backtest/` folder:

```
backtest/
├── Strategy1_FixedSLTP_Martingale_stats_YYYYMMDD_HHMMSS.csv
├── Strategy1_FixedSLTP_Martingale_detailed_YYYYMMDD_HHMMSS.txt
├── Strategy1_FixedSLTP_Martingale_plot_YYYYMMDD_HHMMSS.html
├── Strategy2_ATRBased_stats_YYYYMMDD_HHMMSS.csv
├── Strategy2_ATRBased_detailed_YYYYMMDD_HHMMSS.txt
├── Strategy2_ATRBased_plot_YYYYMMDD_HHMMSS.html
├── Strategy3_TrailingStop_ATR_stats_YYYYMMDD_HHMMSS.csv
├── Strategy3_TrailingStop_ATR_detailed_YYYYMMDD_HHMMSS.txt
├── Strategy3_TrailingStop_ATR_plot_YYYYMMDD_HHMMSS.html
└── Strategy_Comparison_YYYYMMDD_HHMMSS.csv
```

### Output Files Explained:

1. **`*_stats_*.csv`**: Key performance metrics in CSV format
   - Return [%]
   - Sharpe Ratio
   - Max Drawdown [%]
   - # Trades
   - Win Rate [%]
   - And more...

2. **`*_detailed_*.txt`**: Complete backtest statistics and trade history

3. **`*_plot_*.html`**: Interactive Bokeh plot showing:
   - Price chart with entry/exit points
   - Equity curve
   - Drawdown chart
   - Trade markers

4. **`Strategy_Comparison_*.csv`**: Side-by-side comparison of all three strategies

---

## ⚙️ Configuration

### Recent Changes - Modular Configuration

The code has been refactored to be **fully modular** with all parameters configurable at the top of `main.py`. You can now easily customize:

- **EMA Period**: Change the EMA calculation period (default: 200)
- **RSI Period**: Change the RSI calculation period (default: 3)
- **RSI Thresholds**: Adjust oversold/overbought levels (default: 10/90)
- **Backcandles**: Number of candles to check for EMA trend confirmation (default: 8)
- **Strategy Names**: Customize strategy names for your backtest runs

All configuration is now in the **CONFIGURATION section** at the top of `main.py` (lines 17-40):

```python
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
```

**Example**: To test with EMA50 and RSI5, simply change:
```python
EMA_PERIOD = 50
RSI_PERIOD = 5
```

**Example**: To customize strategy names with your parameters:
```python
STRATEGY_NAMES = {
    'Strategy1': 'Strategy1_EMA50_RSI5_FixedSLTP',
    'Strategy2': 'Strategy1_EMA50_RSI5_ATRBased',
    'Strategy3': 'Strategy1_EMA50_RSI5_TrailingStop'
}
```

### Backtest Parameters:

In `run_backtest()` function:
```python
cash=100          # Starting capital
margin=1/50       # Leverage (50:1)
commission=.00     # Commission rate (0% = no commission)
```

### Strategy-Specific Parameters:

**Strategy 1**:
```python
initsize = 0.2           # Initial position size
sl_tp_pips = 45          # Fixed stop-loss/take-profit in pips
```

**Strategy 2**:
```python
initsize = 0.2
slatr_multiplier = 1.3   # Stop-loss = 1.3 × ATR
tp_sl_ratio = 1.3        # Take-profit = 1.3 × Stop-loss
```

**Strategy 3**:
```python
initsize = 0.2
sltr_multiplier = 1.5    # Trailing stop = 1.5 × ATR
```

---

## 🔧 Troubleshooting

### Error: "Could not find data file"
**Solution**: Ensure `EURUSD_Candlestick_5_M_Data.csv` is in the same directory as `main.py`

### Error: "ModuleNotFoundError"
**Solution**: 
1. Activate virtual environment: `.venv\Scripts\Activate.ps1`
2. Install requirements: `pip install -r requirements.txt`

### Error: "Execution Policy" (PowerShell)
**Solution**: Run in Command Prompt instead, or execute:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Plot not saving
**Note**: Plot saving is optional. If bokeh is not properly configured, the script will continue and save CSV/text results.

### Out of Memory
**Solution**: Reduce `BACKTEST_MONTHS` in `main()` function to backtest fewer months.

### No signals generated
**Possible causes**:
- RSI thresholds (10/90) are too extreme - try adjusting in `generate_total_signal()`
- EMA trend filter too strict - reduce `backcandles` parameter
- Data quality issues - check for missing values

---

## 📊 Understanding the Results

### Key Metrics:

- **Return [%]**: Total percentage return over the backtest period
- **Sharpe Ratio**: Risk-adjusted return (higher is better, >1 is good)
- **Max Drawdown [%]**: Largest peak-to-trough decline
- **# Trades**: Total number of trades executed
- **Win Rate [%]**: Percentage of profitable trades
- **Avg. Trade [%]**: Average return per trade

### Interpreting Results:

- **High Return + Low Drawdown**: Best combination
- **High Sharpe Ratio**: Good risk-adjusted returns
- **High Win Rate**: Strategy is consistent
- **Many Trades**: Strategy is active (good for scalping)

---

## 📝 Notes

- This is a **backtesting system** for educational/research purposes
- Past performance does not guarantee future results
- Always test strategies on out-of-sample data before live trading
- Consider transaction costs, slippage, and market impact in real trading
- The 5-minute data file will generate more signals than 15-minute data

---

## 📄 License

This project is for educational purposes. Use at your own risk.

---

## 🤝 Contributing

Feel free to modify and experiment with:
- Different RSI periods
- Different EMA periods
- Different stop-loss/take-profit ratios
- Additional indicators
- Different timeframes

---

## 📧 Support

For issues or questions:
1. Check the Troubleshooting section
2. Verify all requirements are installed
3. Ensure data file format matches expected structure

---

**Happy Backtesting! 📈**
