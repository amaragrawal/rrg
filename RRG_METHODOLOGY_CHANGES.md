# RRG Professional Methodology Reference

This document describes the Julius de Kempenaer (JDK) professional RRG methodology implemented in this tool.

---

## Overview

The Relative Rotation Graph (RRG) is a unique visualization tool that shows the relative strength and momentum of multiple assets compared to a benchmark. It was developed by Julius de Kempenaer and is used by professional platforms like Optuma and StockCharts.

---

## Core Calculations

### 1. Weighted Moving Average (WMA)

The WMA is the foundation of RRG calculations. It applies linear weighting to give more importance to recent data.

**Formula:**
```
WMA = (P₁×1 + P₂×2 + P₃×3 + ... + Pₙ×n) / (1 + 2 + 3 + ... + n)
```

**Implementation:**
```python
weights = np.arange(1, window + 1)
WMA = np.dot(prices, weights) / weights.sum()
```

**Standard Period:** 14 weeks for weekly data

---

### 2. RS-Ratio (X-Axis)

The RS-Ratio measures relative strength compared to the benchmark.

**Calculation Steps:**
1. Calculate Raw RS: `RS = (Asset Price / Benchmark Price) × 100`
2. Apply first smoothing: `RS_Smoothed = WMA(RS, 14)`
3. Apply second smoothing: `RS_Base = WMA(RS_Smoothed, 14)`
4. Calculate RS-Ratio: `RS-Ratio = (RS_Smoothed / RS_Base) × 100`

**Interpretation:**
- **RS-Ratio > 100**: Asset is outperforming the benchmark
- **RS-Ratio < 100**: Asset is underperforming the benchmark
- **RS-Ratio = 100**: Asset is performing in line with benchmark

---

### 3. RS-Momentum (Y-Axis)

The RS-Momentum measures the rate of change in relative strength.

**Calculation Steps:**
1. Start with RS-Ratio from above
2. Apply smoothing: `RS_Momentum_Base = WMA(RS-Ratio, 14)`
3. Calculate RS-Momentum: `RS-Momentum = (RS-Ratio / RS_Momentum_Base) × 100`

**Interpretation:**
- **RS-Momentum > 100**: Relative strength is accelerating (strengthening)
- **RS-Momentum < 100**: Relative strength is decelerating (weakening)
- **RS-Momentum = 100**: Relative strength is stable

---

## Quadrant System

The RRG chart is divided into four quadrants based on the 100,100 centerpoint:

### Leading Quadrant (↗)
- **Position:** RS-Ratio > 100, RS-Momentum > 100
- **Meaning:** Strong and strengthening
- **Action:** Buy/Hold - assets in this quadrant are outperforming and gaining momentum
- **Color:** Green

### Weakening Quadrant (↘)
- **Position:** RS-Ratio > 100, RS-Momentum < 100
- **Meaning:** Strong but weakening
- **Action:** Take Profits - assets are still outperforming but losing momentum
- **Color:** Orange

### Lagging Quadrant (↙)
- **Position:** RS-Ratio < 100, RS-Momentum < 100
- **Meaning:** Weak and weakening
- **Action:** Avoid - assets are underperforming and losing more ground
- **Color:** Red

### Improving Quadrant (↖)
- **Position:** RS-Ratio < 100, RS-Momentum > 100
- **Meaning:** Weak but strengthening
- **Action:** Watch - assets are underperforming but gaining momentum (potential entry)
- **Color:** Blue

---

## Rotation Pattern

### Clockwise Rotation (Healthy Trend)
```
Improving → Leading → Weakening → Lagging → Improving
```

This pattern indicates a complete trend cycle:
1. **Improving**: Asset starts gaining momentum
2. **Leading**: Asset breaks above benchmark and continues strengthening
3. **Weakening**: Asset remains above benchmark but momentum fades
4. **Lagging**: Asset falls below benchmark and continues weakening
5. **Improving**: Asset bottoms and starts recovering

### Counter-Clockwise Rotation (Reversal)
Indicates potential trend reversal or unusual market conditions.

---

## Rotation Metrics

### Rotation Angle
Measures the direction of movement in degrees:
- **0°**: Moving right (increasing RS-Ratio, stable RS-Momentum)
- **90°**: Moving up (stable RS-Ratio, increasing RS-Momentum)
- **180°**: Moving left (decreasing RS-Ratio, stable RS-Momentum)
- **270°**: Moving down (stable RS-Ratio, decreasing RS-Momentum)

**Formula:**
```python
angle = arctan2(ΔRS-Momentum, ΔRS-Ratio) × (180/π)
```

### Velocity
Measures the speed of rotation:

**Formula:**
```python
velocity = √(ΔRS-Ratio² + ΔRS-Momentum²)
```

Higher velocity indicates faster rotation through quadrants.

---

## Key Principles

### 1. Double Smoothing
Both RS-Ratio and RS-Momentum use double smoothing (WMA applied twice). This:
- Reduces noise and volatility
- Creates smoother rotation patterns
- Centers values around 100

### 2. Centerline at 100
Both axes are centered at 100, making interpretation intuitive:
- Above 100 = positive (outperforming/strengthening)
- Below 100 = negative (underperforming/weakening)

### 3. Relative, Not Absolute
RRG shows relative performance, not absolute returns:
- An asset in the Leading quadrant may still be declining in absolute terms
- An asset in the Lagging quadrant may still be rising in absolute terms
- Always consider absolute price action alongside RRG position

### 4. Time Frame Matters
Standard RRG uses 14-week periods for weekly data:
- Shorter periods (5-10 weeks): More responsive, noisier
- Standard period (14 weeks): Balanced, industry standard
- Longer periods (20+ weeks): Smoother, slower to react

---

## Professional Standards

This implementation matches:
- ✅ **Optuma RRG** calculation methodology
- ✅ **StockCharts RRG** standard formulas
- ✅ **JDK's original specification** (14-week WMA)
- ✅ **Professional quadrant positioning**

---

## Validation

To validate against professional tools:

1. **StockCharts.com**
   - Create RRG chart with same benchmark and date
   - Compare RS-Ratio and RS-Momentum values
   - Verify quadrant positions match

2. **Optuma**
   - Generate RRG with identical parameters
   - Check rotation patterns
   - Confirm clockwise movement for strengthening assets

3. **Expected Tolerances**
   - RS-Ratio: ±2-3% (due to data timing differences)
   - RS-Momentum: ±2-3% (due to smoothing variations)
   - Quadrant: Should match exactly

---

## Configuration Parameters

```python
JDK_WINDOW = 14      # Standard 14-week smoothing
TAIL_LENGTH = 6      # Number of historical trail points
```

### Adjusting the Window
While 14 weeks is standard, you can experiment:
- **5-week**: More responsive, suitable for short-term trading
- **10-week**: Balanced for medium-term analysis
- **14-week**: Standard (recommended for most use cases)
- **20-week**: Smoother, better for long-term trends

---

## Common Misconceptions

### ❌ "Leading quadrant means buy"
✅ Leading quadrant shows relative strength, not absolute performance. Always consider:
- Absolute price trends
- Market conditions
- Risk management
- Other technical/fundamental factors

### ❌ "RRG predicts future performance"
✅ RRG shows current relative strength and momentum. It's a tool for:
- Identifying rotation patterns
- Comparing multiple assets
- Timing sector allocation
- Not a standalone prediction tool

### ❌ "Longer trails are always better"
✅ Trail length depends on your analysis timeframe:
- Short trails (3-4 periods): Recent rotation focus
- Medium trails (6-8 periods): Balanced view (recommended)
- Long trails (10+ periods): Historical context

---

## Practical Applications

### Sector Rotation Strategy
1. Monitor sectors moving from Improving to Leading
2. Overweight sectors in Leading quadrant
3. Reduce exposure to sectors entering Weakening
4. Avoid or underweight sectors in Lagging

### Relative Strength Analysis
1. Compare multiple assets on same RRG
2. Identify strongest performers (Leading quadrant)
3. Watch for rotation changes (quadrant transitions)
4. Use velocity to gauge momentum strength

### Portfolio Rebalancing
1. Review RRG weekly after market close
2. Identify quadrant transitions
3. Adjust allocations based on rotation
4. Maintain diversification across quadrants

---

## References

- **Julius de Kempenaer**: Creator of RRG methodology
- **StockCharts**: https://stockcharts.com/school/doku.php?id=chart_school:technical_indicators:rrg
- **Optuma**: https://www.optuma.com/
- **RRG Research**: Official RRG methodology documentation

---

**Methodology Version:** JDK Professional Standard  
**Implementation Date:** 2026  
**Standard Compliance:** Optuma/StockCharts Compatible
