# RSI Scalping Strategy - Backtesting System

A comprehensive backtesting system for an RSI (Relative Strength Index) scalping strategy on EUR/USD forex data. This project implements three different trading strategies with various risk management approaches and provides detailed backtest results.

## 📋 Table of Contents

- [Overview](#overview)
- [Requirements](#requirements)
- [Setup Instructions](#setup-instructions)
- [How to Run](#how-to-run)
- [Code Logic Explanation](#code-logic-explanation)
- [Output Structure](#output-structure)
- [Configuration](#configuration)
- [Troubleshooting](#troubleshooting)

---

## 🎯 Overview

This project implements a **15-minute RSI scalping strategy** for EUR/USD forex trading. The strategy combines:

- **EMA200** (200-period Exponential Moving Average) for trend identification
- **RSI(3)** (3-period Relative Strength Index) for overbought/oversold signals
- **ATR** (Average True Range) for dynamic stop-loss and take-profit calculations

The system backtests three different strategy variants and saves comprehensive results including statistics, trade history, and visualizations.

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

### 5. Backtesting Strategies

The system implements **three different risk management approaches**:

#### Strategy 1: Fixed SL/TP with Martingale (`Strategy1_FixedSLTP`)

**Risk Management**:
- **Stop-Loss**: Fixed 45 pips
- **Take-Profit**: Fixed 45 pips
- **Position Sizing**: Martingale system
  - Starts with 0.2 units
  - Doubles position size after a loss
  - Resets to 0.2 units after a win

**Entry Logic**:
```python
if self.signal1 == 2:  # BUY
    sl1 = self.data.Close[-1] - 45e-4  # 45 pips below
    tp1 = self.data.Close[-1] + 45e-4  # 45 pips above
    self.buy(sl=sl1, tp=tp1, size=self.mysize)
```

**Pros**: Simple, predictable risk/reward ratio
**Cons**: Fixed stops don't adapt to market volatility

---

#### Strategy 2: ATR-Based Dynamic SL/TP (`Strategy2_ATRBased`)

**Risk Management**:
- **Stop-Loss**: 1.3 × ATR (adapts to volatility)
- **Take-Profit**: 1.3 × Stop-Loss (1.69 × ATR)
- **Position Sizing**: Fixed 0.2 units

**Entry Logic**:
```python
slatr = 1.3 * self.data.ATR[-1]
TPSLRatio = 1.3
if self.signal1 == 2:  # BUY
    sl1 = self.data.Close[-1] - slatr
    tp1 = self.data.Close[-1] + slatr * TPSLRatio
    self.buy(sl=sl1, tp=tp1, size=self.mysize)
```

**Pros**: Adapts to market volatility, wider stops in volatile markets
**Cons**: May have larger losses in high volatility periods

---

#### Strategy 3: Trailing Stop with ATR (`Strategy3_TrailingStop`)

**Risk Management**:
- **Initial Stop-Loss**: 1.5 × ATR
- **Trailing Stop**: Continuously updates as price moves favorably
- **Exit Condition**: Closes on opposite signal or trailing stop hit
- **Position Sizing**: Fixed 0.2 units

**Entry Logic**:
```python
sltr = 1.5 * self.data.ATR[-1]
# Update trailing stop for existing trades
if trade.is_long:
    trade.sl = max(trade.sl, self.data.Close[-1] - sltr)
    if self.signal1 == 1:  # Opposite signal
        trade.close()
```

**Pros**: Locks in profits as price moves favorably, can capture larger moves
**Cons**: May exit early on temporary pullbacks

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

You can modify these parameters in `main()` function:

```python
# Data file name
CSV_FILE = "EURUSD_Candlestick_5_M_Data.csv"

# Output folder
BACKTEST_FOLDER = "backtest"

# Number of months to backtest
BACKTEST_MONTHS = 30

# Backtest parameters (in run_backtest function)
cash=100          # Starting capital
margin=1/50       # Leverage (50:1)
commission=.00    # Commission rate (0% = no commission)
```

### Strategy Parameters:

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

### Signal Parameters:

In `generate_ema_signal()`:
```python
backcandles = 8  # Number of candles to check for trend strength
```

In `generate_total_signal()`:
```python
RSI_BUY_THRESHOLD = 10   # RSI ≤ 10 for BUY signal
RSI_SELL_THRESHOLD = 90  # RSI ≥ 90 for SELL signal
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
