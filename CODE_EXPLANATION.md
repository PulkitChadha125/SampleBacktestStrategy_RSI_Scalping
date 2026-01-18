# RSI Scalping Strategy - Code Logic Explanation

## Overview
This notebook implements a **15-minute RSI (Relative Strength Index) scalping strategy** for forex trading (EUR/USD). The strategy combines:
- **EMA200** (200-period Exponential Moving Average) for trend identification
- **RSI** (3-period) for overbought/oversold signals
- **ATR** (Average True Range) for dynamic stop-loss and take-profit calculations

---

## Step-by-Step Logic Breakdown

### 1. **Data Loading and Preprocessing** (Cells 1-2)

```python
df = pd.read_csv("EURUSD_Candlestick_15_M_BID_31.01.2019-30.01.2022.csv")
```

**Purpose**: Loads historical EUR/USD 15-minute candlestick data.

**Data Cleaning**:
- Removes rows with zero volume (invalid data)
- Checks for missing values
- Resets index for clean sequential numbering

---

### 2. **Technical Indicators Calculation** (Cell 3)

```python
df["EMA200"] = ta.ema(df.Close, length=200)
df["RSI"] = ta.rsi(df.Close, length=3)
df['ATR'] = df.ta.atr()
```

**EMA200 (200-period Exponential Moving Average)**:
- Long-term trend filter
- If price is above EMA200 → uptrend
- If price is below EMA200 → downtrend

**RSI (3-period Relative Strength Index)**:
- Very short period (3) for scalping
- RSI > 70-90 → overbought (potential sell signal)
- RSI < 10-30 → oversold (potential buy signal)
- The strategy uses extreme levels: RSI ≥ 90 (sell) and RSI ≤ 10 (buy)

**ATR (Average True Range)**:
- Measures market volatility
- Used later for dynamic stop-loss and take-profit distances

---

### 3. **EMA Signal Generation** (Cell 6)

```python
emasignal = [0]*len(df)
backcandles = 8

for row in range(backcandles-1, len(df)):
    upt = 1  # uptrend flag
    dnt = 1  # downtrend flag
    
    # Check last 8 candles
    for i in range(row-backcandles, row+1):
        if df.High[row] >= df.EMA200[row]:
            dnt = 0  # Price touched above EMA → not pure downtrend
        if df.Low[row] <= df.EMA200[row]:
            upt = 0  # Price touched below EMA → not pure uptrend
    
    # Assign signal
    if upt == 1 and dnt == 1:
        emasignal[row] = 3  # Ambiguous/neutral
    elif upt == 1:
        emasignal[row] = 2  # Strong uptrend (price never touched EMA200)
    elif dnt == 1:
        emasignal[row] = 1  # Strong downtrend (price never touched EMA200)
```

**Logic**:
- Analyzes the last **8 candles** to determine trend strength
- **Signal = 2 (Uptrend)**: All highs and lows in the last 8 candles stayed **above** EMA200
- **Signal = 1 (Downtrend)**: All highs and lows in the last 8 candles stayed **below** EMA200
- **Signal = 3 (Neutral)**: Mixed signals (both flags remain 1, which shouldn't happen normally)
- **Signal = 0**: Price crossed EMA200 (weak trend)

**Purpose**: Ensures trades only occur in strong, clear trends.

---

### 4. **Total Signal Generation** (Cell 8)

```python
TotSignal = [0] * len(df)
for row in range(0, len(df)):
    if df.EMAsignal[row] == 1 and df.RSI[row] >= 90:
        TotSignal[row] = 1  # SELL signal
    if df.EMAsignal[row] == 2 and df.RSI[row] <= 10:
        TotSignal[row] = 2  # BUY signal
```

**Trading Rules**:
- **SELL Signal (1)**: 
  - Strong downtrend (EMAsignal = 1) **AND**
  - RSI ≥ 90 (extremely overbought → price likely to fall)
  
- **BUY Signal (2)**:
  - Strong uptrend (EMAsignal = 2) **AND**
  - RSI ≤ 10 (extremely oversold → price likely to rise)

**Strategy Philosophy**:
- **Mean Reversion**: When RSI is extreme (90+ or 10-), price tends to revert
- **Trend Confirmation**: Only trades in the direction of the strong trend
- **Contrarian Approach**: Sells when overbought in downtrend, buys when oversold in uptrend

---

### 5. **Visualization** (Cells 10-11)

Creates an interactive Plotly chart showing:
- Candlestick chart
- EMA200 line (red)
- Signal markers (purple dots) at entry points

---

### 6. **Backtesting - Strategy 1: Fixed SL/TP** (Cells 13-15)

```python
class MyStrat(Strategy):
    initsize = 0.2  # Initial position size
    mysize = initsize
    
    def next(self):
        # Martingale: Double position after loss
        if(self.signal1>0 and len(self.trades)==0 and 
           len(self.closed_trades)>0 and self.closed_trades[-1].pl < 0):
            self.mysize = self.mysize * 2
        elif len(self.closed_trades)>0 and self.closed_trades[-1].pl > 0:
            self.mysize = self.initsize  # Reset after win
        
        # BUY signal
        if self.signal1 == 2 and len(self.trades) == 0:
            sl1 = self.data.Close[-1] - 45e-4  # Stop loss: 45 pips below
            tp1 = self.data.Close[-1] + 45e-4  # Take profit: 45 pips above
            self.buy(sl=sl1, tp=tp1, size=self.mysize)
        
        # SELL signal
        elif self.signal1 == 1 and len(self.trades) == 0:
            sl1 = self.data.Close[-1] + 45e-4  # Stop loss: 45 pips above
            tp1 = self.data.Close[-1] - 45e-4  # Take profit: 45 pips below
            self.sell(sl=sl1, tp=tp1, size=self.mysize)
```

**Features**:
- **Fixed Risk/Reward**: 45 pips stop-loss and take-profit (1:1 ratio)
- **Martingale System**: Doubles position size after a loss (risky!)
- **No Overlapping Trades**: Only opens new trade if no existing position

---

### 7. **Backtesting - Strategy 2: ATR-Based SL/TP** (Cell 17)

```python
slatr = 1.3 * self.data.ATR[-1]
TPSLRatio = 1.3

if self.signal1 == 2:  # BUY
    sl1 = self.data.Close[-1] - slatr
    tp1 = self.data.Close[-1] + slatr * TPSLRatio
    self.buy(sl=sl1, tp=tp1, size=self.mysize)
```

**Improvements**:
- **Dynamic Stop-Loss**: Based on ATR (adapts to volatility)
- **Better Risk/Reward**: TP = 1.3 × SL (1.3:1 ratio)
- **Volatility-Adjusted**: In volatile markets, SL/TP widen automatically

**Why ATR?**
- High volatility → wider stops (prevents premature exits)
- Low volatility → tighter stops (better risk management)

---

### 8. **Backtesting - Strategy 3: Trailing Stop with ATR** (Cell 19)

```python
sltr = 1.5 * self.data.ATR[-1]

for trade in self.trades:
    if trade.is_long:  # Long position
        # Trailing stop: moves up as price rises
        trade.sl = max(trade.sl or -np.inf, self.data.Close[-1] - sltr)
        if self.signal1 == 1:  # Opposite signal → close
            trade.close()
    else:  # Short position
        # Trailing stop: moves down as price falls
        trade.sl = min(trade.sl or np.inf, self.data.Close[-1] + sltr)
        if self.signal1 == 2:  # Opposite signal → close
            trade.close()
```

**Advanced Features**:
- **Trailing Stop-Loss**: 
  - For long positions: SL follows price upward (locks in profits)
  - For short positions: SL follows price downward
  - Distance maintained at 1.5 × ATR
  
- **Signal-Based Exit**: Closes position when opposite signal appears
- **No Fixed Take-Profit**: Lets winners run with trailing stop

**Example**:
- Buy at 1.1000, SL at 1.0950 (50 pips)
- Price rises to 1.1050 → SL moves to 1.1000 (break-even)
- Price rises to 1.1100 → SL moves to 1.1050 (locks 50 pips profit)

---

## Strategy Summary

### Entry Conditions:
1. **Strong Trend Confirmation** (EMA200 filter)
2. **Extreme RSI** (≤10 for buy, ≥90 for sell)
3. **No Existing Position**

### Exit Conditions:
- **Strategy 1 & 2**: Fixed TP/SL hit
- **Strategy 3**: Trailing stop or opposite signal

### Risk Management:
- Initial position size: 0.2 units
- Martingale (Strategy 1 only): Doubles after loss
- ATR-based stops: Adapts to market volatility

---

## Key Concepts

### Why RSI 3-period?
- Very sensitive → catches quick reversals
- Good for scalping (15-min timeframe)
- Extreme readings (10/90) are rare but high-probability

### Why EMA200?
- Long-term trend filter
- Prevents counter-trend trades
- 8-candle check ensures strong trend

### Why ATR?
- Market volatility changes
- Fixed pips don't work in all conditions
- ATR adapts to current market state

---

## Potential Improvements

1. **Remove Martingale**: High risk of account blowup
2. **Add Commission**: Real trading has costs
3. **Optimize Parameters**: Test different RSI levels, ATR multipliers
4. **Add Filters**: Volume, time-of-day, news events
5. **Risk Management**: Maximum drawdown limits, position sizing rules

---

## Notes

- **Backtesting Parameters**:
  - Cash: $100
  - Margin: 1/50 (50:1 leverage)
  - Commission: 0 (unrealistic for real trading)
  
- **Data Requirements**: Needs CSV file with columns: Open, High, Low, Close, Volume

