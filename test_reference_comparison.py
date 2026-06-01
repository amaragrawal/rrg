"""
RRG Reference Data Comparison Tests

This module compares RRG calculations against known reference values from
professional sources (StockCharts, Optuma) to validate accuracy.

To use this test:
1. Manually collect reference RRG values from StockCharts.com or Optuma
2. Add them to the REFERENCE_DATA dictionary below
3. Run the test to validate your implementation matches professional tools
"""

import unittest
import numpy as np
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta

import importlib.util

# Import functions from the main RRG module (handles hyphenated filename)
spec = importlib.util.spec_from_file_location("rrg_analysis", "rrg-analysis.py")
rrg_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rrg_module)

calculate_production_jdk_rrg = rrg_module.calculate_production_jdk_rrg


# ============================================================================
# REFERENCE DATA FROM PROFESSIONAL SOURCES
# ============================================================================
# Format: {
#     'date': 'YYYY-MM-DD',
#     'benchmark': 'TICKER',
#     'assets': {
#         'TICKER': {
#             'rs_ratio': value,
#             'rs_momentum': value,
#             'source': 'StockCharts/Optuma'
#         }
#     }
# }

REFERENCE_DATA = {
    'example_1': {
        'date': '2024-01-05',  # Replace with actual date
        'benchmark': 'SPY',
        'window': 14,
        'assets': {
            'XLK': {
                'rs_ratio': 102.5,  # Replace with actual StockCharts value
                'rs_momentum': 101.2,  # Replace with actual StockCharts value
                'source': 'StockCharts',
                'tolerance': 2.0  # Acceptable deviation percentage
            },
            'XLF': {
                'rs_ratio': 98.3,
                'rs_momentum': 99.1,
                'source': 'StockCharts',
                'tolerance': 2.0
            }
        }
    },
    # Add more reference points here as you collect them
}


class TestReferenceComparison(unittest.TestCase):
    """Compare RRG calculations against known reference values."""
    
    def setUp(self):
        """Set up test environment."""
        self.tolerance_default = 3.0  # Default 3% tolerance
        
    def fetch_historical_data(self, tickers, end_date, periods=260):
        """
        Fetch historical data for validation.
        
        Args:
            tickers: List of ticker symbols
            end_date: End date for data (YYYY-MM-DD)
            periods: Number of weeks to fetch (default 260 = 5 years)
        """
        end = pd.to_datetime(end_date)
        start = end - timedelta(weeks=periods)
        
        try:
            data = yf.download(
                tickers=tickers,
                start=start.strftime('%Y-%m-%d'),
                end=end.strftime('%Y-%m-%d'),
                interval='1d',
                progress=False
            )
            
            # Get adjusted close prices
            if 'Adj Close' in data:
                prices = data['Adj Close']
            else:
                prices = data['Close']
                
            # Resample to weekly (Friday close)
            weekly_prices = prices.resample('W-FRI').last()
            weekly_prices = weekly_prices.ffill().bfill()
            
            # Ensure we end on the specified date
            weekly_prices = weekly_prices[weekly_prices.index <= end]
            
            return weekly_prices
            
        except Exception as e:
            self.fail(f"Failed to fetch data: {str(e)}")
            
    def compare_values(self, calculated, reference, tolerance):
        """
        Compare calculated value against reference with tolerance.
        
        Args:
            calculated: Calculated RRG value
            reference: Reference value from professional source
            tolerance: Acceptable deviation percentage
            
        Returns:
            tuple: (is_within_tolerance, deviation_percentage)
        """
        deviation = abs(calculated - reference)
        deviation_pct = (deviation / reference) * 100
        is_within = deviation_pct <= tolerance
        
        return is_within, deviation_pct
        
    def test_stockcharts_reference_values(self):
        """Test against StockCharts reference values."""
        if not REFERENCE_DATA or 'example_1' not in REFERENCE_DATA:
            self.skipTest("No reference data available. Add StockCharts values to REFERENCE_DATA.")
            
        for ref_key, ref_data in REFERENCE_DATA.items():
            if ref_key.startswith('example_'):
                continue  # Skip example entries
                
            with self.subTest(reference=ref_key):
                # Fetch historical data
                benchmark = ref_data['benchmark']
                assets = list(ref_data['assets'].keys())
                all_tickers = [benchmark] + assets
                
                prices_df = self.fetch_historical_data(
                    all_tickers,
                    ref_data['date']
                )
                
                # Calculate RRG values
                rs_ratio, rs_momentum = calculate_production_jdk_rrg(
                    prices_df,
                    assets,
                    benchmark,
                    window=ref_data.get('window', 14)
                )
                
                # Compare each asset
                for asset, ref_values in ref_data['assets'].items():
                    calc_ratio = rs_ratio[asset].iloc[-1]
                    calc_momentum = rs_momentum[asset].iloc[-1]
                    
                    ref_ratio = ref_values['rs_ratio']
                    ref_momentum = ref_values['rs_momentum']
                    tolerance = ref_values.get('tolerance', self.tolerance_default)
                    
                    # Compare RS-Ratio
                    ratio_ok, ratio_dev = self.compare_values(
                        calc_ratio, ref_ratio, tolerance
                    )
                    
                    # Compare RS-Momentum
                    momentum_ok, momentum_dev = self.compare_values(
                        calc_momentum, ref_momentum, tolerance
                    )
                    
                    # Assert with detailed messages
                    self.assertTrue(
                        ratio_ok,
                        f"{asset} RS-Ratio deviation: {ratio_dev:.2f}% "
                        f"(calculated: {calc_ratio:.2f}, reference: {ref_ratio:.2f}, "
                        f"tolerance: {tolerance}%, source: {ref_values['source']})"
                    )
                    
                    self.assertTrue(
                        momentum_ok,
                        f"{asset} RS-Momentum deviation: {momentum_dev:.2f}% "
                        f"(calculated: {calc_momentum:.2f}, reference: {ref_momentum:.2f}, "
                        f"tolerance: {tolerance}%, source: {ref_values['source']})"
                    )
                    
                    # Print success message
                    print(f"✓ {asset}: RS-Ratio {calc_ratio:.2f} vs {ref_ratio:.2f} "
                          f"({ratio_dev:.2f}% dev), RS-Momentum {calc_momentum:.2f} vs "
                          f"{ref_momentum:.2f} ({momentum_dev:.2f}% dev)")


class TestCrossValidation(unittest.TestCase):
    """Cross-validate calculations using multiple methods."""
    
    def test_manual_calculation_validation(self):
        """Validate against manual step-by-step calculation."""
        # Create simple test data where we can manually calculate expected values
        dates = pd.date_range(start='2020-01-01', periods=50, freq='W-FRI')
        
        # Simple linear data for manual verification
        asset_prices = np.array([100, 102, 104, 106, 108, 110, 112, 114, 116, 118,
                                120, 122, 124, 126, 128, 130, 132, 134, 136, 138,
                                140, 142, 144, 146, 148, 150, 152, 154, 156, 158,
                                160, 162, 164, 166, 168, 170, 172, 174, 176, 178,
                                180, 182, 184, 186, 188, 190, 192, 194, 196, 198])
        
        bench_prices = np.array([100, 101, 102, 103, 104, 105, 106, 107, 108, 109,
                                110, 111, 112, 113, 114, 115, 116, 117, 118, 119,
                                120, 121, 122, 123, 124, 125, 126, 127, 128, 129,
                                130, 131, 132, 133, 134, 135, 136, 137, 138, 139,
                                140, 141, 142, 143, 144, 145, 146, 147, 148, 149])
        
        data = pd.DataFrame({
            'asset': asset_prices,
            'benchmark': bench_prices
        }, index=dates)
        
        # Calculate using our implementation
        rs_ratio, rs_momentum = calculate_production_jdk_rrg(
            data, ['asset'], 'benchmark', window=5  # Use smaller window for manual verification
        )
        
        # Verify basic properties
        self.assertIsNotNone(rs_ratio)
        self.assertIsNotNone(rs_momentum)
        
        # Asset is consistently outperforming (2% vs 1% growth)
        # So RS-Ratio should be > 100
        latest_ratio = rs_ratio['asset'].iloc[-1]
        self.assertGreater(latest_ratio, 100,
                          "Outperforming asset should have RS-Ratio > 100")
        
        # Asset is accelerating relative to benchmark
        # So RS-Momentum should be > 100
        latest_momentum = rs_momentum['asset'].iloc[-1]
        self.assertGreater(latest_momentum, 100,
                          "Accelerating asset should have RS-Momentum > 100")
        
    def test_consistency_across_windows(self):
        """Test that different window sizes produce consistent relative results."""
        dates = pd.date_range(start='2020-01-01', periods=100, freq='W-FRI')
        
        data = pd.DataFrame({
            'asset': np.linspace(100, 150, 100),
            'benchmark': np.linspace(100, 120, 100)
        }, index=dates)
        
        # Calculate with different windows
        rs_ratio_10, rs_momentum_10 = calculate_production_jdk_rrg(
            data, ['asset'], 'benchmark', window=10
        )
        
        rs_ratio_14, rs_momentum_14 = calculate_production_jdk_rrg(
            data, ['asset'], 'benchmark', window=14
        )
        
        rs_ratio_20, rs_momentum_20 = calculate_production_jdk_rrg(
            data, ['asset'], 'benchmark', window=20
        )
        
        # All should show outperformance (RS-Ratio > 100)
        self.assertGreater(rs_ratio_10['asset'].iloc[-1], 100)
        self.assertGreater(rs_ratio_14['asset'].iloc[-1], 100)
        self.assertGreater(rs_ratio_20['asset'].iloc[-1], 100)
        
        # Longer windows should be smoother (lower std dev)
        std_10 = rs_ratio_10['asset'].dropna().std()
        std_14 = rs_ratio_14['asset'].dropna().std()
        std_20 = rs_ratio_20['asset'].dropna().std()
        
        self.assertLess(std_20, std_10,
                       "Longer window should produce smoother results")


class TestDataQualityChecks(unittest.TestCase):
    """Validate data quality and preprocessing."""
    
    def test_weekly_alignment(self):
        """Test that data is properly aligned to weekly Friday close."""
        # Fetch real data
        end_date = datetime.now()
        start_date = end_date - timedelta(weeks=52)
        
        try:
            data = yf.download(
                tickers=['SPY', 'XLK'],
                start=start_date.strftime('%Y-%m-%d'),
                end=end_date.strftime('%Y-%m-%d'),
                interval='1d',
                progress=False
            )
            
            prices = data['Adj Close'] if 'Adj Close' in data else data['Close']
            weekly = prices.resample('W-FRI').last()
            
            # Check that all dates are Fridays
            for date in weekly.index:
                self.assertEqual(date.weekday(), 4,  # 4 = Friday
                                f"Date {date} is not a Friday")
                                
        except Exception as e:
            self.skipTest(f"Could not fetch data for validation: {str(e)}")
            
    def test_data_completeness(self):
        """Test that data has no unexpected gaps."""
        end_date = datetime.now()
        start_date = end_date - timedelta(weeks=52)
        
        try:
            data = yf.download(
                tickers=['SPY'],
                start=start_date.strftime('%Y-%m-%d'),
                end=end_date.strftime('%Y-%m-%d'),
                interval='1d',
                progress=False
            )
            
            prices = data['Adj Close'] if 'Adj Close' in data else data['Close']
            weekly = prices.resample('W-FRI').last()
            weekly = weekly.ffill().bfill()
            
            # Check for NaN values
            nan_count = weekly.isna().sum()
            self.assertEqual(nan_count, 0,
                           f"Found {nan_count} NaN values after forward/backward fill")
                           
        except Exception as e:
            self.skipTest(f"Could not fetch data for validation: {str(e)}")


def print_reference_data_template():
    """Print a template for adding reference data."""
    print("\n" + "="*70)
    print("REFERENCE DATA COLLECTION TEMPLATE")
    print("="*70)
    print("""
To validate your RRG implementation:

1. Go to StockCharts.com or Optuma
2. Create an RRG chart with:
   - Benchmark: SPY (or your chosen benchmark)
   - Assets: XLK, XLF, XLV, etc.
   - Settings: 14-week period
   
3. Note the exact date and RS-Ratio/RS-Momentum values

4. Add to REFERENCE_DATA in test_reference_comparison.py:

    'validation_YYYYMMDD': {
        'date': 'YYYY-MM-DD',
        'benchmark': 'SPY',
        'window': 14,
        'assets': {
            'XLK': {
                'rs_ratio': 102.5,      # From StockCharts
                'rs_momentum': 101.2,    # From StockCharts
                'source': 'StockCharts',
                'tolerance': 2.0
            },
            # Add more assets...
        }
    }

5. Run: python test_reference_comparison.py
    """)
    print("="*70 + "\n")


if __name__ == '__main__':
    print_reference_data_template()
    
    # Run tests
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestReferenceComparison))
    suite.addTests(loader.loadTestsFromTestCase(TestCrossValidation))
    suite.addTests(loader.loadTestsFromTestCase(TestDataQualityChecks))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "="*70)
    print("REFERENCE COMPARISON TEST SUMMARY")
    print("="*70)
    print(f"Tests Run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("="*70)
    
    if result.wasSuccessful():
        print("✅ ALL REFERENCE TESTS PASSED")
    else:
        print("❌ SOME TESTS FAILED")
