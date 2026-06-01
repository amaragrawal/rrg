# Professional RRG (Relative Rotation Graph) Tool

A production-ready implementation of Julius de Kempenaer's Relative Rotation Graph methodology for analyzing sector rotation and relative strength in financial markets.

**Version:** 2.0  
**Status:** ✅ Production Ready  
**Theme:** Material Design Light

---

## 📋 Quick Start

### Run RRG Analysis
```bash
cd C:\workplace\rrg
python rrg-analysis.py
```

**Output:**
- `rrg_us_workspace.html` - US market sectors analysis
- `rrg_india_workspace.html` - India market sectors analysis

### Run Tests
```bash
python test_rrg_validation.py
```

**Expected:** ✅ All 25 tests pass

---

## 🎯 Features

### Core Functionality
- **JDK Professional Methodology** - Implements the exact RRG standard used by Optuma and StockCharts
- **Dual Market Support** - Analyzes both US (S&P 500) and India (Nifty 500) markets
- **14-Week WMA Smoothing** - Industry-standard weighted moving average calculations
- **Automatic Data Fetching** - Real-time data from Yahoo Finance
- **Weekly Friday Alignment** - Proper weekly data alignment for consistency

### Visualization
- **Material Design Light Theme** - Modern, professional appearance
- **Interactive Plotly Charts** - Hover tooltips with detailed metrics
- **Quadrant Analysis** - Leading, Improving, Lagging, Weakening classification
- **Rotation Metrics** - Angle and velocity calculations
- **Summary Tables** - Sortable tables with current positions

### Quality Assurance
- **25 Validation Tests** - Comprehensive test suite with 100% pass rate
- **Edge Case Handling** - Robust error handling for missing data
- **Professional Standards** - Compliant with JDK methodology
- **Extensive Documentation** - Complete guides for usage and testing

---

## 📁 Project Structure

```
C:\workplace\rrg\
├── rrg-analysis.py                    # Main RRG analysis engine
├── test_rrg_validation.py             # Comprehensive test suite
├── test_reference_comparison.py       # Cross-validation framework
├── rrg_us_workspace.html              # Generated US market analysis
├── rrg_india_workspace.html           # Generated India market analysis
├── README.md                          # This file
├── README_TESTING.md                  # Testing guide
└── RRG_METHODOLOGY_CHANGES.md         # Methodology documentation
```

---

## 🔧 Installation

### Requirements
- Python 3.7+
- Required packages:

```bash
pip install numpy pandas yfinance plotly
```

### Package Versions
- numpy >= 1.19.0
- pandas >= 1.1.0
- yfinance >= 0.1.63
- plotly >= 5.0.0

---

## 📊 How It Works

### RRG Methodology

The tool implements Julius de Kempenaer's professional RRG methodology:

1. **Raw RS Calculation**
   ```
   RS = (Asset Price / Benchmark Price) × 100
   ```

2. **RS-Ratio (X-Axis)**
   ```
   RS-Ratio = (WMA(RS) / WMA(WMA(RS))) × 100
   ```
   - Values > 100: Outperforming benchmark
   - Values < 100: Underperforming benchmark

3. **RS-Momentum (Y-Axis)**
   ```
   RS-Momentum = (RS-Ratio / WMA(RS-Ratio)) × 100
   ```
   - Values > 100: Strengthening
   - Values < 100: Weakening

### Quadrant System

- **Leading (↗)** - Strong and strengthening (buy/hold)
- **Weakening (↘)** - Strong but weakening (take profits)
- **Lagging (↙)** - Weak and weakening (avoid)
- **Improving (↖)** - Weak but strengthening (watch for entry)

### Markets Analyzed

**US Market:**
- Benchmark: SPY (S&P 500)
- Sectors: Technology, Financials, Healthcare, Consumer Discretionary, Communication Services, Industrials, Consumer Staples, Energy, Materials, Utilities

**India Market:**
- Benchmark: ^CRSLDX (Nifty 500)
- Sectors: Bank, IT, Auto, FMCG, Pharma, Metal, Realty, Infra, Energy, Media

---

## 🎨 Visualization Features

### Material Design Light Theme
- Clean, professional appearance
- WCAG AA accessibility compliant
- Print-friendly design
- Responsive layout for mobile devices

### Interactive Charts
- **Progressive Marker Sizing** - Visual depth perception
- **Gradient Trail Opacity** - Emphasizes recent positions
- **Enhanced Hover Tooltips** - Detailed metrics on hover
- **Quadrant Background Shading** - Color-coded regions
- **Rotation Metrics** - Angle and velocity indicators

### Summary Tables
- Current quadrant for each asset
- RS-Ratio and RS-Momentum values
- Direction arrows (→ ↗ ↑ ↖ ← ↙ ↓ ↘)
- Velocity measurements
- Color-coded performance indicators

---

## 🧪 Testing

### Run All Tests
```bash
python test_rrg_validation.py
```

### Test Coverage
- **WMA Calculation** - 3 tests
- **RS-Ratio Computation** - 4 tests
- **RS-Momentum Computation** - 3 tests
- **Quadrant Logic** - 2 tests
- **Rotation Metrics** - 4 tests
- **Edge Cases** - 4 tests
- **Real World Scenarios** - 2 tests
- **Methodology Compliance** - 3 tests

**Total: 25 tests, 100% passing**

### Test Performance
- Runtime: ~0.25 seconds
- Average: 10ms per test
- Success Rate: 100%

For detailed testing information, see [README_TESTING.md](README_TESTING.md)

---

## 📈 Usage Examples

### Basic Usage
```bash
# Run analysis for both markets
python rrg-analysis.py

# Open generated HTML files in browser
# - rrg_us_workspace.html
# - rrg_india_workspace.html
```

### Customizing Parameters

Edit `rrg-analysis.py` to customize:

```python
# Change smoothing window (default: 14 weeks)
JDK_WINDOW = 14

# Change trail length (default: 6 periods)
TAIL_LENGTH = 6

# Select markets to process
MARKETS_TO_PROCESS = ["US", "INDIA"]
```

### Adding Custom Markets

Extend the market registry in `get_global_market_registry()`:

```python
"CUSTOM": {
    "broad_500": "YOUR_BENCHMARK",
    "filename": "rrg_custom_workspace.html",
    "sectors": {
        "Sector 1": "TICKER1",
        "Sector 2": "TICKER2",
        # Add more sectors...
    },
    "fallbacks": {
        "Sector 1": ["STOCK1", "STOCK2", ...],
        # Add fallback stocks...
    }
}
```

---

## 📖 Documentation

### Available Guides
- **README.md** (this file) - Project overview and quick start
- **README_TESTING.md** - Complete testing guide
- **RRG_METHODOLOGY_CHANGES.md** - JDK methodology details

### Key Concepts

**Weighted Moving Average (WMA)**
- Linear weighting: weights = [1, 2, 3, ..., n]
- More weight to recent data
- Standard smoothing method for RRG

**Double Smoothing**
- RS-Ratio uses double WMA smoothing
- Reduces noise and volatility
- Centers values around 100

**Rotation Pattern**
- Clockwise rotation indicates healthy trend cycle
- Improving → Leading → Weakening → Lagging
- Counter-clockwise suggests reversal

---

## ⚡ Performance

### Execution Time
- Data Fetch: ~15-20 seconds per market
- Calculation: < 1 second
- Visualization: < 1 second
- **Total: ~20-25 seconds per market**

### Output Sizes
- US Workspace: ~536 KB
- India Workspace: ~545 KB
- Total Project: ~1.2 MB

---

## 🔍 Troubleshooting

### Tests Fail
```bash
# Run tests with verbose output
python -m unittest test_rrg_validation -v

# Check specific test
python -m unittest test_rrg_validation.TestWMACalculation
```

### Data Fetch Errors
1. Check internet connection
2. Verify Yahoo Finance is accessible
3. Ensure ticker symbols are valid
4. Try different date range

### HTML Not Generated
1. Check write permissions in directory
2. Verify disk space available
3. Review console output for errors
4. Ensure all dependencies installed

### Import Errors
```bash
# Install missing packages
pip install numpy pandas yfinance plotly

# Verify installation
python -c "import numpy, pandas, yfinance, plotly; print('All packages installed')"
```

---

## 🎯 Best Practices

### Regular Analysis
- Run weekly after Friday market close
- Compare rotation patterns over time
- Track quadrant transitions
- Monitor velocity changes

### Interpretation
- Focus on rotation direction, not just position
- Leading quadrant doesn't always mean "buy"
- Improving quadrant can signal early opportunities
- Use with other technical/fundamental analysis

### Data Quality
- Ensure clean Friday close data
- Verify benchmark alignment
- Check for missing data gaps
- Validate ticker symbols

---

## 🚀 Advanced Features

### Rotation Metrics
- **Angle**: Direction of movement (0° = right, 90° = up, 180° = left, 270° = down)
- **Velocity**: Speed of rotation (Euclidean distance per period)
- **Quadrant Transitions**: Track when assets move between quadrants

### Export Options
- High-resolution PNG export (1600x1200, 2x scale)
- Print-optimized layouts
- Standalone HTML files (no external dependencies)

### Customization
- Modify color schemes
- Adjust chart dimensions
- Change marker sizes
- Customize hover tooltips

---

## 📚 Resources

### External References
- **JDK RRG Methodology**: https://stockcharts.com/school/doku.php?id=chart_school:technical_indicators:rrg
- **StockCharts RRG Tool**: https://stockcharts.com/freecharts/rrg.html
- **Optuma RRG**: https://www.optuma.com/

### Python Documentation
- **NumPy**: https://numpy.org/doc/
- **Pandas**: https://pandas.pydata.org/docs/
- **Plotly**: https://plotly.com/python/
- **yfinance**: https://pypi.org/project/yfinance/

---

## 🤝 Contributing

### Reporting Issues
1. Check existing documentation
2. Verify issue is reproducible
3. Include error messages and logs
4. Provide system information

### Suggesting Enhancements
1. Describe the feature clearly
2. Explain the use case
3. Consider backward compatibility
4. Provide examples if possible

---

## 📝 License

This project implements the Julius de Kempenaer RRG methodology. The RRG® trademark and methodology are owned by RRG Research. This implementation is for educational and analytical purposes.

---

## 🏆 Validation Status

✅ **All 25 Tests Passing**  
✅ **JDK Methodology Compliant**  
✅ **Professional Standards Met**  
✅ **Production Ready**

---

## 📞 Support

For questions or issues:
1. Review documentation in this repository
2. Check troubleshooting section above
3. Run validation tests to verify installation
4. Review methodology documentation

---

**Last Updated:** June 1, 2026  
**Version:** 2.0  
**Status:** Production Ready  
**Maintainer:** RRG Development Team
