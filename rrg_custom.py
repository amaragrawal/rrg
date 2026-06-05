#!/usr/bin/env python3
"""
Custom RRG Analysis Tool
Allows analysis of custom ticker lists with flexible timeframes
"""

import sys
import argparse
import pandas as pd
import yfinance as yf
from datetime import datetime
import webbrowser
import os

# Import core functions from main module
try:
    import importlib.util
    spec = importlib.util.spec_from_file_location("rrg_analysis", "rrg-analysis.py")
    rrg_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(rrg_module)
    
    calculate_wma = rrg_module.calculate_wma
    calculate_production_jdk_rrg = rrg_module.calculate_production_jdk_rrg
    calculate_rotation_metrics = rrg_module.calculate_rotation_metrics
    generate_summary_table = rrg_module.generate_summary_table
    get_quadrant_info = rrg_module.get_quadrant_info
    build_plotly_div = rrg_module.build_plotly_div
except Exception as e:
    print(f"❌ Error importing from rrg-analysis.py: {e}")
    sys.exit(1)


def fetch_and_resample_data(tickers, period="5y", interval="1d", timeframe="weekly"):
    """
    Fetch data and resample to specified timeframe.
    
    Args:
        tickers: List of ticker symbols
        period: Data period (1y, 2y, 5y, 10y, max)
        interval: Data interval (1d, 1wk, 1mo)
        timeframe: Resampling timeframe (daily, weekly, monthly)
    
    Returns:
        DataFrame with resampled prices
    """
    print(f"📡 Fetching data for {len(tickers)} tickers...")
    print(f"   Period: {period}, Interval: {interval}, Timeframe: {timeframe}")
    
    # Download data
    raw_download = yf.download(tickers=tickers, period=period, interval=interval, progress=False)
    
    # Extract prices
    if "Adj Close" in raw_download:
        prices = raw_download["Adj Close"]
    elif "Close" in raw_download:
        prices = raw_download["Close"]
    else:
        raise ValueError("No price data available")
    
    # Fill missing values
    prices = prices.ffill().bfill()
    
    # Resample based on timeframe
    if timeframe.lower() == "daily":
        resampled = prices  # No resampling needed
        print(f"✅ Data fetched: {len(resampled)} daily periods")
    elif timeframe.lower() == "weekly":
        resampled = prices.resample('W-FRI').last()
        # Mid-week safeguard
        today = pd.Timestamp.now()
        if today.weekday() < 4:
            resampled = resampled.iloc[:-1]
        print(f"✅ Data fetched and resampled: {len(resampled)} weekly periods (Friday close)")
    elif timeframe.lower() == "monthly":
        resampled = prices.resample('M').last()
        print(f"✅ Data fetched and resampled: {len(resampled)} monthly periods (month-end)")
    else:
        raise ValueError(f"Invalid timeframe: {timeframe}. Must be 'daily', 'weekly', or 'monthly'")
    
    return resampled


def run_custom_rrg(tickers, benchmark, window=14, tail_length=6, timeframe="weekly", 
                   period="5y", output_file=None, title=None, open_browser=True):
    """
    Run custom RRG analysis with specified parameters.
    
    Args:
        tickers: List of ticker symbols to analyze
        benchmark: Benchmark ticker symbol
        window: WMA smoothing window (default 14)
        tail_length: Number of trail periods to display (default 6)
        timeframe: Data timeframe - 'daily', 'weekly', or 'monthly' (default 'weekly')
        period: Data fetch period (default '5y')
        output_file: Output HTML filename (default: auto-generated)
        title: Chart title (default: auto-generated)
        open_browser: Whether to open the result in browser (default True)
    
    Returns:
        Path to generated HTML file
    """
    # Validate inputs
    if not tickers:
        raise ValueError("Tickers list cannot be empty")
    if not benchmark:
        raise ValueError("Benchmark must be specified")
    
    # Combine all tickers for fetching
    all_tickers = list(set([benchmark] + tickers))
    
    # Fetch and resample data
    prices_df = fetch_and_resample_data(all_tickers, period=period, timeframe=timeframe)
    
    # Check if benchmark exists in data
    if benchmark not in prices_df.columns:
        raise ValueError(f"Benchmark {benchmark} not found in fetched data")
    
    # Calculate RRG
    print(f"🔄 Calculating RRG with {window}-period WMA...")
    rs_ratio, rs_momentum = calculate_production_jdk_rrg(
        prices_df, tickers, benchmark, window=window
    )
    
    if rs_ratio is None or rs_momentum is None:
        raise ValueError("RRG calculation failed - check data quality")
    
    print(f"✅ RRG calculated: {len(rs_ratio)} periods, {len(rs_ratio.columns)} valid tickers")
    
    # Generate chart title
    if title is None:
        timeframe_label = timeframe.capitalize()
        title = f"Custom RRG Analysis ({timeframe_label} Data) - Benchmark: {benchmark}"
    
    # Build chart
    print("🎨 Generating visualization...")
    chart_div = build_plotly_div(
        rs_ratio, rs_momentum, tickers, title, tail_length, is_macro=True
    )
    
    # Generate summary table
    summary_table = generate_summary_table(rs_ratio, rs_momentum, tickers)
    
    # Determine output filename
    if output_file is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"rrg_custom_{timeframe}_{timestamp}.html"
    
    # Generate HTML
    display_date = prices_df.index[-1].strftime('%Y-%m-%d')
    
    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Custom RRG Analysis - {benchmark}</title>
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap" rel="stylesheet">
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        
        body {{ 
            background: #FAFAFA;
            color: #212121; 
            font-family: 'Roboto', -apple-system, BlinkMacSystemFont, "Segoe UI", Arial, sans-serif;
            padding: 32px 24px;
            line-height: 1.6;
        }}
        
        .container {{
            max-width: 1800px;
            margin: 0 auto;
        }}
        
        .header {{ 
            background: #FFFFFF;
            border-radius: 8px;
            padding: 32px;
            margin-bottom: 24px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            border-left: 4px solid #2196F3;
        }}
        
        h1 {{ 
            margin: 0 0 12px 0; 
            font-size: 32px; 
            font-weight: 500; 
            color: #212121;
            letter-spacing: -0.5px;
        }}
        
        .subtitle {{
            display: flex;
            align-items: center;
            gap: 12px;
            flex-wrap: wrap;
            margin-top: 16px;
        }}
        
        .badge {{
            display: inline-flex;
            align-items: center;
            padding: 6px 16px;
            background: #E3F2FD;
            border-radius: 16px;
            font-size: 13px;
            color: #1976D2;
            font-weight: 500;
        }}
        
        .badge.green {{ background: #E8F5E9; color: #388E3C; }}
        .badge.orange {{ background: #FFF3E0; color: #F57C00; }}
        
        .macro-container {{
            background: #FFFFFF;
            border-radius: 8px;
            padding: 24px;
            margin-bottom: 24px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        
        .card {{
            background: #FFFFFF;
            border-radius: 8px;
            padding: 24px;
            margin-bottom: 24px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            transition: all 0.2s ease;
        }}
        
        .card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }}
        
        .footer {{
            text-align: center;
            margin-top: 48px;
            padding-top: 24px;
            border-top: 1px solid #E0E0E0;
            color: #757575;
            font-size: 13px;
        }}
        
        @media (max-width: 768px) {{
            body {{ padding: 16px; }}
            h1 {{ font-size: 24px; }}
            .subtitle {{ flex-direction: column; align-items: flex-start; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📈 Custom RRG Analysis</h1>
            <div class="subtitle">
                <span class="badge green">📅 {display_date}</span>
                <span class="badge">⚙️ {window}-Period WMA</span>
                <span class="badge">🎯 Benchmark: {benchmark}</span>
                <span class="badge orange">📊 {len(tickers)} Assets</span>
                <span class="badge">⏱️ {timeframe.capitalize()} Data</span>
            </div>
        </div>
        
        <div class="macro-container">
            {chart_div}
            {summary_table}
        </div>
        
        <div class="card">
            <h2 style="margin-bottom: 16px; color: #212121; font-size: 20px; font-weight: 500;">Analysis Parameters</h2>
            <p style="color: #616161; line-height: 1.8;">
                <strong>Tickers Analyzed:</strong> {', '.join(tickers)}<br>
                <strong>Benchmark:</strong> {benchmark}<br>
                <strong>Timeframe:</strong> {timeframe.capitalize()}<br>
                <strong>Smoothing Window:</strong> {window} periods<br>
                <strong>Trail Length:</strong> {tail_length} periods<br>
                <strong>Data Period:</strong> {period}<br>
                <strong>Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            </p>
        </div>
        
        <div class="footer">
            <p><strong>Julius de Kempenaer Professional RRG Methodology</strong></p>
            <p>Custom Analysis Generated with rrg_custom.py</p>
            <p style="margin-top: 8px;">© 2026 RRG Analysis Tool</p>
        </div>
    </div>
</body>
</html>
"""
    
    # Write HTML file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    full_path = os.path.abspath(output_file)
    print(f"\n✅ Generated Custom RRG Workspace: {full_path}")
    
    # Open in browser
    if open_browser:
        try:
            webbrowser.open('file://' + full_path)
            print("🌐 Opening in browser...")
        except Exception as e:
            print(f"⚠️  Could not open browser: {e}")
    
    return full_path


def main():
    """Command-line interface for custom RRG analysis."""
    parser = argparse.ArgumentParser(
        description='Generate custom RRG analysis with flexible parameters',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze tech stocks vs SPY (weekly data)
  python rrg_custom.py -t AAPL MSFT GOOGL NVDA -b SPY
  
  # Daily analysis with custom window and tail
  python rrg_custom.py -t AAPL MSFT GOOGL -b SPY --timeframe daily -w 20 --tail 10
  
  # Monthly analysis with 2-year period
  python rrg_custom.py -t XLK XLF XLV XLE -b SPY --timeframe monthly -p 2y
  
  # Crypto analysis (weekly)
  python rrg_custom.py -t BTC-USD ETH-USD BNB-USD -b ^GSPC -w 10
        """
    )
    
    parser.add_argument('-t', '--tickers', nargs='+', required=True,
                        help='List of ticker symbols to analyze')
    parser.add_argument('-b', '--benchmark', required=True,
                        help='Benchmark ticker symbol')
    parser.add_argument('-w', '--window', type=int, default=14,
                        help='WMA smoothing window (default: 14)')
    parser.add_argument('--tail', type=int, default=6,
                        help='Trail length to display (default: 6)')
    parser.add_argument('--timeframe', choices=['daily', 'weekly', 'monthly'], default='weekly',
                        help='Data timeframe (default: weekly)')
    parser.add_argument('-p', '--period', default='5y',
                        help='Data fetch period: 1y, 2y, 5y, 10y, max (default: 5y)')
    parser.add_argument('-o', '--output', default=None,
                        help='Output HTML filename (default: auto-generated)')
    parser.add_argument('--title', default=None,
                        help='Custom chart title')
    parser.add_argument('--no-browser', action='store_true',
                        help='Do not open browser after generation')
    
    args = parser.parse_args()
    
    print("\n🎯 Custom RRG Analysis Tool")
    print("=" * 50)
    
    try:
        output_path = run_custom_rrg(
            tickers=args.tickers,
            benchmark=args.benchmark,
            window=args.window,
            tail_length=args.tail,
            timeframe=args.timeframe,
            period=args.period,
            output_file=args.output,
            title=args.title,
            open_browser=not args.no_browser
        )
        
        print("\n✅ Analysis complete!")
        print(f"📄 Output: {output_path}")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
