# RRG Testing Guide

Complete guide for testing and validating the RRG implementation.

---

## Quick Start

### Run All Tests
```bash
python test_rrg_validation.py
```

**Expected Output:**
```
✅ ALL TESTS PASSED - RRG Implementation Validated
Tests Run: 25
Successes: 25
Failures: 0
Errors: 0
```

**Runtime:** ~0.25 seconds

---

## Test Suite Overview

### Test Coverage (25 Tests)

| Category | Tests | Description |
|----------|-------|-------------|
| WMA Calculation | 3 | Validates weighted moving average algorithm |
| RS-Ratio Computation | 4 | Tests relative strength ratio calculations |
| RS-Momentum Computation | 3 | Tests momentum calculations |
| Quadrant Logic | 2 | Validates quadrant classification |
| Rotation Metrics | 4 | Tests angle and velocity calculations |
| Edge Cases | 4 | Tests error handling and edge conditions |
| Real World Scenarios | 2 | Tests with realistic market data |
| Methodology Compliance | 3 | Validates JDK standard compliance |

---

## Test Files

### 1. test_rrg_validation.py
Comprehensive validation test suite covering all aspects of RRG calculations.

**Run:**
```bash
python test_rrg_validation.py
```

**Features:**
- Unit tests for individual functions
- Integration tests for complete workflows
- Edge case testing
- Methodology compliance validation

### 2. test_reference_comparison.py
Cross-validation framework for comparing against professional tools (StockCharts, Optuma).

**Setup Required:**
1. Collect reference data from professional tools
2. Add to `REFERENCE_DATA` dictionary
3. Run comparison tests

**Run:**
```bash
python test_reference_comparison.py
```

---

## Running Tests

### Run All Tests
```bash
python test_rrg_validation.py
```

### Run Specific Test Class
```bash
python -m unittest test_rrg_validation.TestWMACalculation
```

### Run Specific Test Method
```bash
python -m unittest test_rrg_validation.TestWMACalculation.test_wma_basic_calculation
```

### Run with Verbose Output
```bash
python -m unittest test_rrg_validation -v
```

---

## Test Details

### WMA Calculation Tests

**test_wma_basic_calculation**
- Validates WMA against hand-calculated values
- Precision: ±0.00001

**test_wma_14_period**
- Verifies 14-period WMA (JDK standard)
- Checks correct number of NaN values

**test_wma_monotonic_increase**
- Confirms WMA follows trend in monotonic data
- Tests trend-following behavior

### RS-Ratio Tests

**test_rs_ratio_outperformer**
- Outperforming asset has RS-Ratio > 100
- Tests relative strength detection

**test_rs_ratio_underperformer**
- Underperforming asset has RS-Ratio < 100
- Tests weakness detection

**test_rs_ratio_matched_performance**
- Matched performance has RS-Ratio ≈ 100
- Tests centerline behavior

**test_rs_ratio_centerline**
- RS-Ratio centers around 100 baseline
- Validates normalization

### RS-Momentum Tests

**test_momentum_positive_acceleration**
- Accelerating outperformance has positive momentum
- Tests momentum detection

**test_momentum_negative_deceleration**
- Decelerating performance has negative momentum
- Tests deceleration detection

**test_momentum_centerline**
- RS-Momentum centers around 100
- Validates momentum normalization

### Quadrant Logic Tests

**test_leading_quadrant**
- Strong outperformer in leading quadrant
- RS-Ratio > 100, RS-Momentum > 100

**test_lagging_quadrant**
- Weak underperformer in lagging quadrant
- RS-Ratio < 100, RS-Momentum < 100

### Rotation Metrics Tests

**test_rotation_angle_rightward**
- Rightward movement ≈ 0°
- Tests angle calculation

**test_rotation_angle_upward**
- Upward movement ≈ 90°
- Tests vertical movement

**test_rotation_angle_diagonal**
- Diagonal movement ≈ 45°
- Tests combined movement

**test_velocity_calculation**
- Velocity = √(dx² + dy²)
- Tests Euclidean distance

### Edge Case Tests

**test_insufficient_data**
- Handles < 14 periods gracefully
- Returns NaN appropriately

**test_missing_benchmark**
- Returns None for missing benchmark
- Proper error handling

**test_nan_handling**
- Handles NaN values without errors
- Robust data processing

**test_zero_prices**
- Handles division by zero
- Produces inf/nan without crashes

### Real World Scenario Tests

**test_sector_rotation_pattern**
- Typical sector rotation through quadrants
- Tests realistic market behavior

**test_volatile_asset**
- High volatility asset handling
- Tests stability with extreme values

### Methodology Compliance Tests

**test_double_smoothing_applied**
- Double smoothing reduces volatility
- Validates smoothing implementation

**test_centerline_at_100**
- Both axes center at 100
- Validates JDK standard

**test_14_period_standard**
- 14-period window is standard
- Validates parameter compliance

---

## Adding Reference Data

### Step 1: Collect Data from StockCharts

1. Visit https://stockcharts.com/freecharts/rrg.html
2. Create RRG chart:
   - Benchmark: SPY (or your benchmark)
   - Assets: XLK, XLF, XLV, etc.
   - Period: 14 weeks
3. Note the exact date (Friday close)
4. Record RS-Ratio and RS-Momentum for each asset

### Step 2: Add to Test File

Edit `test_reference_comparison.py`:

```python
REFERENCE_DATA = {
    'validation_20260530': {
        'date': '2026-05-30',
        'benchmark': 'SPY',
        'window': 14,
        'assets': {
            'XLK': {
                'rs_ratio': 102.5,
                'rs_momentum': 101.2,
                'source': 'StockCharts',
                'tolerance': 2.0
            },
            'XLF': {
                'rs_ratio': 98.3,
                'rs_momentum': 99.1,
                'source': 'StockCharts',
                'tolerance': 2.0
            }
            # Add more assets...
        }
    }
}
```

### Step 3: Run Comparison

```bash
python test_reference_comparison.py
```

**Expected Output:**
```
✓ XLK: RS-Ratio 102.48 vs 102.50 (0.02% dev), RS-Momentum 101.18 vs 101.20 (0.02% dev)
✓ XLF: RS-Ratio 98.31 vs 98.30 (0.01% dev), RS-Momentum 99.12 vs 99.10 (0.02% dev)
```

---

## Understanding Test Results

### Success Indicators

✅ **All tests pass**
- Calculations match expected values
- Edge cases handled properly
- Methodology compliant

### Tolerance Guidelines

| Test Type | Tolerance | Reason |
|-----------|-----------|--------|
| WMA calculation | 0.00001 | Precise math |
| RS-Ratio | ±5 units | Smoothing effects |
| RS-Momentum | ±0.5 units | Double smoothing |
| Rotation angle | ±5 degrees | Numerical precision |
| Reference comparison | ±2% | Data/timing differences |

---

## Troubleshooting

### Import Errors

**Problem:** `ModuleNotFoundError: No module named 'rrg_analysis'`

**Solution:** The test file uses dynamic import:
```python
import importlib.util
spec = importlib.util.spec_from_file_location("rrg_analysis", "rrg-analysis.py")
rrg_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rrg_module)
```

### Data Fetch Errors

**Problem:** `Failed to fetch data` in reference comparison tests

**Solution:**
- Check internet connection
- Verify ticker symbols are valid
- Ensure yfinance is installed: `pip install yfinance`
- Try with different date range

### Assertion Errors

**Problem:** Test fails with value mismatch

**Solution:**
- Check if test data is realistic
- Verify smoothing window is appropriate
- Adjust tolerance if needed
- Review test assumptions

---

## Best Practices

### 1. Run Tests Before Commits
Always validate changes don't break calculations:
```bash
python test_rrg_validation.py
```

### 2. Add Tests for New Features
When adding functionality:
1. Write test first (TDD approach)
2. Implement feature
3. Verify test passes
4. Add to test suite

### 3. Document Test Assumptions
Each test should clearly state:
- What is being tested
- Expected behavior
- Acceptable tolerances
- Why tolerance is set

### 4. Keep Reference Data Updated
- Collect new reference data quarterly
- Test against multiple dates
- Use different market conditions
- Document data sources

### 5. Monitor Test Performance
- Tests should run in < 1 second
- Optimize slow tests
- Use mocking for external dependencies
- Cache expensive calculations

---

## Continuous Integration

### Pre-commit Hook

Add to `.git/hooks/pre-commit`:

```bash
#!/bin/bash
echo "Running RRG validation tests..."
python test_rrg_validation.py
if [ $? -ne 0 ]; then
    echo "❌ Tests failed. Commit aborted."
    exit 1
fi
echo "✅ All tests passed."
```

Make executable:
```bash
chmod +x .git/hooks/pre-commit
```

### GitHub Actions

Create `.github/workflows/test.yml`:

```yaml
name: RRG Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: |
          pip install numpy pandas yfinance plotly
      - name: Run tests
        run: python test_rrg_validation.py
```

---

## Test Maintenance

### Monthly Tasks
- [ ] Run full test suite
- [ ] Check for deprecated dependencies
- [ ] Update reference data
- [ ] Review test coverage

### Quarterly Tasks
- [ ] Collect new StockCharts reference data
- [ ] Test with latest market data
- [ ] Review and update tolerances
- [ ] Add new edge case tests

### Annual Tasks
- [ ] Comprehensive backtest validation
- [ ] Cross-platform comparison (Optuma, Bloomberg)
- [ ] Performance benchmarking
- [ ] Documentation update

---

## Resources

### External Tools
- **StockCharts RRG**: https://stockcharts.com/freecharts/rrg.html
- **Optuma RRG**: https://www.optuma.com/
- **JDK Methodology**: https://stockcharts.com/school/doku.php?id=chart_school:technical_indicators:rrg

### Python Testing
- **unittest docs**: https://docs.python.org/3/library/unittest.html
- **pytest**: https://docs.pytest.org/ (alternative framework)
- **coverage.py**: https://coverage.readthedocs.io/ (code coverage)

---

## Getting Help

### Test Failures
1. Read error message carefully
2. Check test assumptions
3. Verify input data quality
4. Review methodology documentation

### Adding New Tests
1. Follow existing test patterns
2. Use descriptive test names
3. Add docstrings explaining purpose
4. Include expected behavior

### Reference Data Issues
1. Verify date alignment (Friday close)
2. Check ticker symbols
3. Confirm data source settings
4. Allow 2-3% tolerance for timing differences

---

**Test Suite Version:** 1.0  
**Last Updated:** June 1, 2026  
**Status:** ✅ All Tests Passing  
**Coverage:** 100% of core functions
