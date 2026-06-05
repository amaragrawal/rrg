import os
import sys
import webbrowser
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import yfinance as yf
from datetime import datetime

# ==========================================
# CENTRAL PRODUCTION CONFIGURATION
# ==========================================
# JDK Professional RRG Parameters (Optuma/StockCharts Standard)
JDK_WINDOW = 14     # Standard JDK smoothing period (14 weeks for weekly data)
TAIL_LENGTH = 6     # Number of historical weekly trail periods to plot
MARKETS_TO_PROCESS = ["US", "INDIA"]


def get_global_market_registry():
    """Returns the expanded top-10 structural matrix schemas for both markets."""
    return {
        "US": {
            "broad_500": "SPY",  # S&P 500 Matrix Anchor
            "filename": "rrg_us_workspace.html",
            "sectors": {
                "Technology": "XLK",
                "Financials": "XLF",
                "Healthcare": "XLV",
                "Consumer Discretionary": "XLY",
                "Communication Services": "XLC",
                "Industrials": "XLI",
                "Consumer Staples": "XLP",
                "Energy": "XLE",
                "Materials": "XLB",
                "Utilities": "XLU"
            },
            "fallbacks": {
                "Technology": ["MSFT", "AAPL", "NVDA", "AVGO", "ORCL", "CRM", "AMD", "QCOM", "NOW", "INTC"],
                "Financials": ["JPM", "BAC", "WFC", "MS", "GS", "AXP", "BLK", "C", "V", "MA"],
                "Healthcare": ["LLY", "UNH", "JNJ", "ABV", "MRK", "TMO", "PFE", "AMGN", "ISRG", "GILD"],
                "Consumer Discretionary": ["AMZN", "TSLA", "HD", "MCD", "NKE", "LOW", "BKNG", "TJX", "SBUX", "CMG"],
                "Communication Services": ["META", "GOOGL", "GOOG", "NFLX", "TMUS", "DIS", "VZ", "CMCSA", "T", "EA"],
                "Industrials": ["GE", "CAT", "UNP", "HON", "ETN", "RTX", "LMT", "UPS", "DE", "BA"],
                "Consumer Staples": ["PG", "COST", "WMT", "KO", "PEP", "PM", "EL", "MO", "CL", "KMB"],
                "Energy": ["XOM", "CVX", "COP", "SLB", "EOG", "MPC", "PSX", "VLO", "WMB", "HAL"],
                "Materials": ["LIN", "APD", "SHW", "FCX", "ECL", "NEM", "CTVA", "DOW", "NUE", "ALB"],
                "Utilities": ["NEE", "SO", "DUK", "CEG", "SRE", "AEP", "D", "PEG", "ED", "WEC"]
            }
        },
        "INDIA": {
            "broad_500": "^CRSLDX",  # Nifty 500 Matrix Anchor
            "filename": "rrg_india_workspace.html",
            "sectors": {
                "Nifty Bank": "^NSEBANK",
                "Nifty IT": "^CNXIT",
                "Nifty Auto": "^CNXAUTO",
                "Nifty FMCG": "^CNXFMCG",
                "Nifty Pharma": "^CNXPHARMA",
                "Nifty Metal": "^CNXMETAL",
                "Nifty Realty": "^CNXREALTY",
                "Nifty Infra": "^CNXINFRA",
                "Nifty Energy": "^CNXENERGY",
                "Nifty Media": "^CNXMEDIA"
            },
            "fallbacks": {
                "Nifty Bank": ["HDFCBANK.NS", "ICICIBANK.NS", "SBIN.NS", "AXISBANK.NS", "KOTAKBANK.NS", "INDUSINDBK.NS", "BANKBARODA.NS", "PNB.NS", "FEDERALBNK.NS", "IDFCFIRSTB.NS"],
                "Nifty IT": ["TCS.NS", "INFY.NS", "HCLTECH.NS", "WIPRO.NS", "TECHM.NS", "LTM.NS", "PERSISTENT.NS", "COFORGE.NS", "MPHASIS.NS", "LTTS.NS", "OFSS.NS"],
                "Nifty Auto": ["TMPV.NS", "M&M.NS", "MARUTI.NS", "BAJAJ-AUTO.NS", "EICHERMOT.NS", "HEROMOTOCO.NS", "TIINDIA.NS", "BALKRISIND.NS", "ASHOKLEY.NS", "MRF.NS"],
                "Nifty FMCG": ["HINDUNILVR.NS", "ITC.NS", "NESTLEIND.NS", "BRITANNIA.NS", "TATACONSUM.NS", "DABUR.NS", "MARICO.NS", "GODREJCP.NS", "VBL.NS", "COLPAL.NS"],
                "Nifty Pharma": ["SUNPHARMA.NS", "CIPLA.NS", "DRREDDY.NS", "DIVISLAB.NS", "LUPIN.NS", "AUROPHARMA.NS", "TORNTPHARM.NS", "MANKIND.NS", "ZYDUSLIFE.NS", "BIOCON.NS"],
                "Nifty Metal": ["TATASTEEL.NS", "JSWSTEEL.NS", "HINDALCO.NS", "COALINDIA.NS", "VEDL.NS", "NMDC.NS", "SAIL.NS", "NATIONALUM.NS", "JINDALSTEL.NS", "APLAPOLLO.NS"],
                "Nifty Realty": ["DLF.NS", "GODREJPROP.NS", "OBEROIRLTY.NS", "PRESTIGE.NS", "LODHA.NS", "PHOENIXLTD.NS", "SOBHA.NS", "BRIGADE.NS", "SUNTECK.NS", "MAHLIFE.NS"],
                "Nifty Infra": ["LT.NS", "NTPC.NS", "POWERGRID.NS", "ADANIPORTS.NS", "GRASIM.NS", "ULTRACEMCO.NS", "BHARTIARTL.NS", "AMBUJACEM.NS", "TATAPOWER.NS", "GAIL.NS"],
                "Nifty Energy": ["RELIANCE.NS", "NTPC.NS", "ONGC.NS", "COALINDIA.NS", "POWERGRID.NS", "ADANIPOWER.NS", "TATAPOWER.NS", "GAIL.NS", "IOC.NS", "BPCL.NS"],
                "Nifty Media": ["PVRINOX.NS", "SUNTV.NS", "ZEEL.NS", "SAREGAMA.NS", "TIPSMUSIC.NS", "NETWORK18.NS", "PFOCUS.NS", "NAZARA.NS", "DBCORP.NS", "HATHWAY.NS"]
            }
        }
    }


def calculate_wma(df, window):
    """
    Vectorized Linearly Weighted Moving Average (WMA) for multi-column DataFrames.
    This is the JDK standard smoothing method used in professional RRG implementations.
    """
    weights = np.arange(1, window + 1)
    
    def wma_calc(x):
        if len(x) < window:
            return np.nan
        return np.dot(x, weights) / weights.sum()
    
    return df.rolling(window=window, min_periods=window).apply(wma_calc, raw=True)


def calculate_production_jdk_rrg(price_df, tickers, benchmark, window=14):
    """
    Julius de Kempenaer's Professional RRG Methodology (Optuma/StockCharts Standard).
    
    This implementation follows the exact JDK specification:
    1. Calculate Raw RS = (Price / Benchmark) × 100
    2. Apply WMA smoothing to RS
    3. RS-Ratio = (Smoothed RS / WMA(Smoothed RS)) × 100
    4. RS-Momentum = (RS-Ratio / WMA(RS-Ratio)) × 100
    
    Both axes are centered at 100, with values above indicating strength
    and values below indicating weakness relative to the benchmark.
    """
    valid_tickers = [t for t in tickers if t in price_df.columns]
    if len(valid_tickers) == 0 or benchmark not in price_df.columns:
        return None, None

    # Step 1: Calculate Raw Relative Strength (RS)
    # RS = (Asset Price / Benchmark Price) × 100
    rs_raw = price_df[valid_tickers].div(price_df[benchmark], axis=0) * 100

    # Step 2: First Smoothing Pass - Apply WMA to Raw RS
    rs_smoothed = calculate_wma(rs_raw, window)

    # Step 3: Calculate JdK RS-Ratio (X-Axis)
    # RS-Ratio = (Smoothed RS / WMA(Smoothed RS)) × 100
    rs_ratio_base = calculate_wma(rs_smoothed, window)
    rs_ratio = (rs_smoothed / rs_ratio_base) * 100

    # Step 4: Calculate JdK RS-Momentum (Y-Axis)
    # RS-Momentum = (RS-Ratio / WMA(RS-Ratio)) × 100
    rs_momentum_base = calculate_wma(rs_ratio, window)
    rs_momentum = (rs_ratio / rs_momentum_base) * 100
    
    return rs_ratio.dropna(how='all'), rs_momentum.dropna(how='all')


def calculate_rotation_metrics(x_df, y_df):
    """
    Calculate rotation angle and velocity for each ticker.
    
    Rotation Angle: Direction of movement in degrees (0° = right, 90° = up)
    Velocity: Speed of rotation (distance traveled per period)
    """
    angles = {}
    velocities = {}
    
    for ticker in x_df.columns:
        if ticker not in y_df.columns:
            continue
            
        x_vals = x_df[ticker].dropna()
        y_vals = y_df[ticker].dropna()
        
        if len(x_vals) < 2 or len(y_vals) < 2:
            continue
        
        # Calculate angle of movement (last 2 points)
        dx = x_vals.iloc[-1] - x_vals.iloc[-2]
        dy = y_vals.iloc[-1] - y_vals.iloc[-2]
        angle = np.degrees(np.arctan2(dy, dx))
        
        # Calculate velocity (Euclidean distance)
        velocity = np.sqrt(dx**2 + dy**2)
        
        angles[ticker] = angle
        velocities[ticker] = velocity
    
    return angles, velocities


def generate_summary_table(x_df, y_df, tickers):
    """Generate HTML summary table showing current positions and metrics."""
    if x_df is None or y_df is None:
        return ""
    
    angles, velocities = calculate_rotation_metrics(x_df, y_df)
    
    rows = []
    for ticker in tickers:
        if ticker not in x_df.columns or ticker not in y_df.columns:
            continue
        
        x_val = x_df[ticker].iloc[-1] if not x_df[ticker].empty else None
        y_val = y_df[ticker].iloc[-1] if not y_df[ticker].empty else None
        
        if pd.isna(x_val) or pd.isna(y_val):
            continue
        
        quadrant, color = get_quadrant_info(x_val, y_val)
        angle = angles.get(ticker, 0)
        velocity = velocities.get(ticker, 0)
        
        # Determine rotation direction
        if -22.5 <= angle < 22.5:
            direction = "→"
        elif 22.5 <= angle < 67.5:
            direction = "↗"
        elif 67.5 <= angle < 112.5:
            direction = "↑"
        elif 112.5 <= angle < 157.5:
            direction = "↖"
        elif angle >= 157.5 or angle < -157.5:
            direction = "←"
        elif -157.5 <= angle < -112.5:
            direction = "↙"
        elif -112.5 <= angle < -67.5:
            direction = "↓"
        else:
            direction = "↘"
        
        rows.append({
            'ticker': ticker.replace(".NS", "").replace("^", ""),
            'quadrant': quadrant,
            'color': color,
            'rs_ratio': x_val,
            'rs_momentum': y_val,
            'direction': direction,
            'velocity': velocity
        })
    
    if not rows:
        return ""
    
    # Sort by quadrant priority: Leading > Improving > Weakening > Lagging
    quadrant_order = {'Leading': 0, 'Improving': 1, 'Weakening': 2, 'Lagging': 3}
    rows.sort(key=lambda x: (quadrant_order.get(x['quadrant'], 4), -x['velocity']))
    
    table_html = """
    <div style="overflow-x: auto; margin-top: 16px;">
        <table style="width: 100%; border-collapse: collapse; font-size: 12px; background: #FFFFFF;">
            <thead>
                <tr style="background: #2196F3; color: #FFFFFF;">
                    <th style="padding: 12px; text-align: left; border: 1px solid #E0E0E0; font-weight: 500;">Asset</th>
                    <th style="padding: 12px; text-align: center; border: 1px solid #E0E0E0; font-weight: 500;">Quadrant</th>
                    <th style="padding: 12px; text-align: right; border: 1px solid #E0E0E0; font-weight: 500;">RS-Ratio</th>
                    <th style="padding: 12px; text-align: right; border: 1px solid #E0E0E0; font-weight: 500;">RS-Momentum</th>
                    <th style="padding: 12px; text-align: center; border: 1px solid #E0E0E0; font-weight: 500;">Direction</th>
                    <th style="padding: 12px; text-align: right; border: 1px solid #E0E0E0; font-weight: 500;">Velocity</th>
                </tr>
            </thead>
            <tbody>
    """
    
    for row in rows:
        table_html += f"""
                <tr style="background: #FAFAFA; border-bottom: 1px solid #E0E0E0; transition: background 0.2s;" 
                    onmouseover="this.style.background='#F5F5F5'" 
                    onmouseout="this.style.background='#FAFAFA'">
                    <td style="padding: 10px; font-weight: 500; color: #212121; border: 1px solid #E0E0E0;">{row['ticker']}</td>
                    <td style="padding: 10px; text-align: center; color: {row['color']}; font-weight: 600; border: 1px solid #E0E0E0;">{row['quadrant']}</td>
                    <td style="padding: 10px; text-align: right; color: {'#4CAF50' if row['rs_ratio'] >= 100 else '#F44336'}; font-weight: 500; border: 1px solid #E0E0E0;">{row['rs_ratio']:.2f}</td>
                    <td style="padding: 10px; text-align: right; color: {'#4CAF50' if row['rs_momentum'] >= 100 else '#F44336'}; font-weight: 500; border: 1px solid #E0E0E0;">{row['rs_momentum']:.2f}</td>
                    <td style="padding: 10px; text-align: center; font-size: 16px; border: 1px solid #E0E0E0;">{row['direction']}</td>
                    <td style="padding: 10px; text-align: right; color: #616161; border: 1px solid #E0E0E0;">{row['velocity']:.2f}</td>
                </tr>
        """
    
    table_html += """
            </tbody>
        </table>
    </div>
    """
    
    return table_html


def get_quadrant_info(x, y):
    """Determine which quadrant a point is in and return color/name."""
    if x >= 100 and y >= 100:
        return "Leading", "#4CAF50"  # Material Green
    elif x < 100 and y >= 100:
        return "Improving", "#2196F3"  # Material Blue
    elif x < 100 and y < 100:
        return "Lagging", "#F44336"  # Material Red
    else:
        return "Weakening", "#FF9800"  # Material Orange


def build_plotly_div(x_df, y_df, tickers, chart_title, tail_len, is_macro=False):
    """
    Modern flat material light theme RRG visualization.
    Clean, professional design with material design principles.
    """
    fig = go.Figure()
    
    # Material Design color palette - vibrant and clear
    colors = [
        "#E91E63", "#9C27B0", "#3F51B5", "#2196F3", "#00BCD4",
        "#009688", "#4CAF50", "#FF9800", "#FF5722", "#795548"
    ]
    
    valid_tickers = [t for t in tickers if t in x_df.columns and x_df[t].notna().any()]
    angles, velocities = calculate_rotation_metrics(x_df, y_df)

    all_visible_x = []
    all_visible_y = []

    # First pass: collect all visible points for intelligent scaling
    for ticker in valid_tickers:
        x_trail = x_df[ticker].tail(tail_len).dropna().values
        y_trail = y_df[ticker].tail(tail_len).dropna().values
        if len(x_trail) > 0:
            all_visible_x.extend(x_trail)
            all_visible_y.extend(y_trail)

    # Intelligent viewport calculation - ensure 100,100 is always visible
    if all_visible_x and all_visible_y:
        x_min, x_max = min(all_visible_x + [100]), max(all_visible_x + [100])
        y_min, y_max = min(all_visible_y + [100]), max(all_visible_y + [100])
        
        # Symmetric padding for professional appearance
        x_range = x_max - x_min
        y_range = y_max - y_min
        max_range = max(x_range, y_range)
        
        # 15% padding with minimum range of 5 units
        padding = max(max_range * 0.15, 2.5)
        
        x_center = (x_min + x_max) / 2
        y_center = (y_min + y_max) / 2
        
        axis_limits_x = [x_center - max_range/2 - padding, x_center + max_range/2 + padding]
        axis_limits_y = [y_center - max_range/2 - padding, y_center + max_range/2 + padding]
    else:
        axis_limits_x = [95, 105]
        axis_limits_y = [95, 105]

    # Add subtle quadrant background shading with material colors
    fig.add_trace(go.Scatter(
        x=[100, axis_limits_x[1], axis_limits_x[1], 100],
        y=[100, 100, axis_limits_y[1], axis_limits_y[1]],
        fill="toself", fillcolor="rgba(76, 175, 80, 0.04)",  # Material Green
        line=dict(width=0), showlegend=False, hoverinfo="skip"
    ))
    fig.add_trace(go.Scatter(
        x=[axis_limits_x[0], 100, 100, axis_limits_x[0]],
        y=[100, 100, axis_limits_y[1], axis_limits_y[1]],
        fill="toself", fillcolor="rgba(33, 150, 243, 0.04)",  # Material Blue
        line=dict(width=0), showlegend=False, hoverinfo="skip"
    ))
    fig.add_trace(go.Scatter(
        x=[axis_limits_x[0], 100, 100, axis_limits_x[0]],
        y=[axis_limits_y[0], axis_limits_y[0], 100, 100],
        fill="toself", fillcolor="rgba(244, 67, 54, 0.04)",  # Material Red
        line=dict(width=0), showlegend=False, hoverinfo="skip"
    ))
    fig.add_trace(go.Scatter(
        x=[100, axis_limits_x[1], axis_limits_x[1], 100],
        y=[axis_limits_y[0], axis_limits_y[0], 100, 100],
        fill="toself", fillcolor="rgba(255, 152, 0, 0.04)",  # Material Orange
        line=dict(width=0), showlegend=False, hoverinfo="skip"
    ))

    # Second pass: plot trails with enhanced styling
    for idx, ticker in enumerate(valid_tickers):
        x_trail = x_df[ticker].tail(tail_len).values
        y_trail = y_df[ticker].tail(tail_len).values
        dates = x_df.index[-tail_len:].strftime("%d %b '%y") if len(x_df) >= tail_len else []

        if len(x_trail) == 0 or np.isnan(x_trail[-1]) or np.isnan(y_trail[-1]):
            continue

        color = colors[idx % len(colors)]
        
        # Progressive marker sizing for depth perception
        marker_sizes = np.linspace(5, 14, len(x_trail)).tolist() if len(x_trail) > 1 else [14]
        
        # Get current quadrant for context
        current_quadrant, quad_color = get_quadrant_info(x_trail[-1], y_trail[-1])
        
        # Enhanced hover text with quadrant info
        angle_str = f"<br>Rotation: {angles.get(ticker, 0):.1f}°" if ticker in angles else ""
        velocity_str = f"<br>Velocity: {velocities.get(ticker, 0):.2f}" if ticker in velocities else ""
        
        hover_texts = []
        for i in range(len(x_trail)):
            quad_name, _ = get_quadrant_info(x_trail[i], y_trail[i])
            hover_text = (
                f"<b style='font-size:14px; color:#212121'>{ticker}</b><br>"
                f"<span style='color:#757575'>Week: {dates[i]}</span><br>"
                f"<span style='color:#2196F3'>RS-Ratio: {x_trail[i]:.2f}</span><br>"
                f"<span style='color:#4CAF50'>RS-Momentum: {y_trail[i]:.2f}</span><br>"
                f"<span style='color:#FF9800'>Quadrant: {quad_name}</span>"
            )
            if i == len(x_trail) - 1:
                hover_text += angle_str + velocity_str
            hover_texts.append(hover_text)

        # Clean trail with material design principles
        fig.add_trace(go.Scatter(
            x=x_trail, y=y_trail, 
            mode="lines+markers+text", 
            name=ticker,
            text=["" if i < len(x_trail) - 1 else ticker.replace(".NS", "").replace("^", "") for i in range(len(x_trail))],
            textposition="top center",
            textfont=dict(
                color="#212121",  # Material Dark Gray
                size=11 if is_macro else 10,
                family="Roboto, Arial, sans-serif",
                weight="bold"
            ),
            line=dict(
                color=color, 
                width=3.0 if is_macro else 2.5,
                shape="spline",
                smoothing=0.9
            ),
            marker=dict(
                size=marker_sizes,
                color=color,
                line=dict(color="#FFFFFF", width=2),
                opacity=[0.5 + (i / len(x_trail)) * 0.5 for i in range(len(x_trail))]
            ),
            hoverinfo="text",
            hovertext=hover_texts,
            hoverlabel=dict(
                bgcolor="#FFFFFF",
                bordercolor=color,
                font=dict(size=12, color="#212121", family="Roboto, Arial, sans-serif")
            )
        ))

    # Calculate viewport dimensions for annotations
    x_span = axis_limits_x[1] - axis_limits_x[0]
    y_span = axis_limits_y[1] - axis_limits_y[0]

    # Modern flat material light theme layout
    fig.update_layout(
        title=dict(
            text=f"<b>{chart_title}</b>",
            font=dict(color="#212121", size=18 if is_macro else 15, family="Roboto, Arial, sans-serif"),
            x=0.02,
            y=0.98
        ),
        paper_bgcolor="#FAFAFA",  # Material Light Background
        plot_bgcolor="#FFFFFF",   # Pure White Plot Area
        xaxis=dict(
            gridcolor="#E0E0E0",  # Material Light Gray Grid
            gridwidth=1,
            zeroline=False,
            color="#616161",  # Material Medium Gray
            range=axis_limits_x,
            title=dict(
                text="<b>JdK RS-Ratio®</b>" if is_macro else None,
                font=dict(size=13, color="#424242")
            ),
            tickfont=dict(size=11, color="#616161"),
            showline=True,
            linewidth=2,
            linecolor="#BDBDBD"
        ),
        yaxis=dict(
            gridcolor="#E0E0E0",
            gridwidth=1,
            zeroline=False,
            color="#616161",
            range=axis_limits_y,
            title=dict(
                text="<b>JdK RS-Momentum®</b>" if is_macro else None,
                font=dict(size=13, color="#424242")
            ),
            tickfont=dict(size=11, color="#616161"),
            showline=True,
            linewidth=2,
            linecolor="#BDBDBD"
        ),
        margin=dict(t=70, b=60, l=70, r=60),
        height=620 if is_macro else 440,
        showlegend=is_macro,
        legend=dict(
            font=dict(color="#424242", size=11, family="Roboto, Arial, sans-serif"),
            bgcolor="rgba(255, 255, 255, 0.95)",
            bordercolor="#E0E0E0",
            borderwidth=1,
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        hovermode="closest",
        shapes=[
            # Clean crosshairs at 100,100
            dict(
                type="line",
                x0=100, y0=axis_limits_y[0],
                x1=100, y1=axis_limits_y[1],
                line=dict(color="#9E9E9E", width=2, dash="dot")
            ),
            dict(
                type="line",
                x0=axis_limits_x[0], y0=100,
                x1=axis_limits_x[1], y1=100,
                line=dict(color="#9E9E9E", width=2, dash="dot")
            )
        ],
        annotations=[
            # Material design quadrant labels
            dict(
                x=axis_limits_x[0] + 0.88 * x_span,
                y=axis_limits_y[0] + 0.94 * y_span,
                text="<b>LEADING</b>",
                showarrow=False,
                font=dict(color="#4CAF50", size=13, family="Roboto, Arial, sans-serif", weight="bold"),
                bgcolor="rgba(76, 175, 80, 0.12)",
                borderpad=6,
                bordercolor="#4CAF50",
                borderwidth=1
            ),
            dict(
                x=axis_limits_x[0] + 0.12 * x_span,
                y=axis_limits_y[0] + 0.94 * y_span,
                text="<b>IMPROVING</b>",
                showarrow=False,
                font=dict(color="#2196F3", size=13, family="Roboto, Arial, sans-serif", weight="bold"),
                bgcolor="rgba(33, 150, 243, 0.12)",
                borderpad=6,
                bordercolor="#2196F3",
                borderwidth=1
            ),
            dict(
                x=axis_limits_x[0] + 0.12 * x_span,
                y=axis_limits_y[0] + 0.06 * y_span,
                text="<b>LAGGING</b>",
                showarrow=False,
                font=dict(color="#F44336", size=13, family="Roboto, Arial, sans-serif", weight="bold"),
                bgcolor="rgba(244, 67, 54, 0.12)",
                borderpad=6,
                bordercolor="#F44336",
                borderwidth=1
            ),
            dict(
                x=axis_limits_x[0] + 0.88 * x_span,
                y=axis_limits_y[0] + 0.06 * y_span,
                text="<b>WEAKENING</b>",
                showarrow=False,
                font=dict(color="#FF9800", size=13, family="Roboto, Arial, sans-serif", weight="bold"),
                bgcolor="rgba(255, 152, 0, 0.12)",
                borderpad=6,
                bordercolor="#FF9800",
                borderwidth=1
            )
        ]
    )
    
    return fig.to_html(full_html=False, include_plotlyjs='cdn', config={
        'displayModeBar': True,
        'displaylogo': False,
        'modeBarButtonsToRemove': ['lasso2d', 'select2d'],
        'toImageButtonOptions': {
            'format': 'png',
            'filename': 'rrg_chart',
            'height': 1200,
            'width': 1600,
            'scale': 2
        }
    })


# ==========================================
# DATA ACQUISITION & WORKSPACE COMPILER
# ==========================================
if __name__ == "__main__":
    market_registry = get_global_market_registry()
    
    for mkt_id in MARKETS_TO_PROCESS:
        print(f"\n🚀 RE-COMPILING INTEGRATED DATA NETWORK FOR: {mkt_id}")
        schema = market_registry[mkt_id]
        broad_index = schema["broad_500"]
        sector_trackers = schema["sectors"]
        
        # Build asset universe list
        sector_universe = {}
        for sect_name, tracker in sector_trackers.items():
            try:
                fund = yf.Ticker(tracker)
                if fund.funds_data and fund.funds_data.top_holdings is not None:
                    raw_ticks = [str(t).strip().upper() for t in fund.funds_data.top_holdings.index if pd.notna(t)]
                    clean_ticks = [t for t in raw_ticks if t and not any(c in t for c in ["^", "=", "CASH"])]
                    if len(clean_ticks) >= 5:
                        sector_universe[sect_name] = clean_ticks[:10]
                        continue
                raise ValueError()
            except Exception:
                sector_universe[sect_name] = schema["fallbacks"][sect_name]
        
        flat_tickers = list(set([broad_index] + list(sector_trackers.values()) + [t for s in sector_universe.values() for t in s]))
        
        print(f"📡 Fetching raw daily values over a 5-year trailing horizon...")
        raw_download = yf.download(tickers=flat_tickers, period="5y", interval="1d", progress=False)
        
        daily_prices = raw_download["Adj Close"] if "Adj Close" in raw_download else raw_download["Close"]
        daily_prices = daily_prices.ffill().bfill()
        
        # Resample onto strict Friday weekly data points
        prices_df = daily_prices.resample('W-FRI').last()
        
        # Mid-week safeguard: Truncate current week if accessed Monday through Thursday
        today = pd.Timestamp.now()
        if today.weekday() < 4:
            last_closed_friday = prices_df.index[-2]
            prices_df = prices_df.loc[:last_closed_friday]
            
        display_date = prices_df.index[-1].strftime('%Y-%m-%d')
        print(f"📅 Data cleanly aligned to closed Friday: {display_date}")

        # ------------------------------------------------------------
        # PROCESSING LAYER 1: SECTORS vs BROAD MARKET INDEX
        # ------------------------------------------------------------
        sector_symbols = list(sector_trackers.values())
        reversed_tracker_map = {v: k for k, v in sector_trackers.items()}
        
        macro_x, macro_y = calculate_production_jdk_rrg(prices_df, sector_symbols, broad_index, window=JDK_WINDOW)
        if macro_x is not None:
            macro_x = macro_x.rename(columns=reversed_tracker_map)
            macro_y = macro_y.rename(columns=reversed_tracker_map)
            
        macro_div = build_plotly_div(
            macro_x, macro_y, list(sector_trackers.keys()),
            f"Macro Sector Allocation Space (vs. Benchmark Index: {broad_index})",
            TAIL_LENGTH, is_macro=True
        )
        
        # Generate summary table for macro view
        macro_summary = generate_summary_table(macro_x, macro_y, list(sector_trackers.keys()))
        
        # ------------------------------------------------------------
        # PROCESSING LAYER 2: INTRA-SECTOR CONSTITUENTS vs SECTOR BENCHMARK
        # ------------------------------------------------------------
        micro_cards_html = []
        for sector_name, stocks in sector_universe.items():
            sect_benchmark = sector_trackers[sector_name]
            micro_x, micro_y = calculate_production_jdk_rrg(prices_df, stocks, sect_benchmark, window=JDK_WINDOW)
            
            if micro_x is not None and micro_y is not None:
                chart_div = build_plotly_div(
                    micro_x, micro_y, stocks,
                    f"Intra-Sector Equity Alpha: {sector_name} (vs. Index: {sect_benchmark})",
                    TAIL_LENGTH, is_macro=False
                )
                
                micro_cards_html.append(f'<div class="card">{chart_div}</div>')

        # ------------------------------------------------------------
        # HTML EXPORT LAYER
        # ------------------------------------------------------------
        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{mkt_id} Professional RRG Workspace</title>
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
                    font-weight: 500;
                    color: #1976D2;
                    border: 1px solid #BBDEFB;
                }}
                
                .date-badge {{
                    background: #E8F5E9;
                    border-color: #C8E6C9;
                    color: #388E3C;
                }}
                
                .count-badge {{
                    background: #FFF3E0;
                    border-color: #FFE0B2;
                    color: #F57C00;
                }}
                
                h2 {{ 
                    font-size: 18px; 
                    color: #1976D2; 
                    margin: 48px 0 20px 0; 
                    font-weight: 500; 
                    text-transform: uppercase; 
                    letter-spacing: 0.5px;
                    padding-left: 16px;
                    border-left: 4px solid #2196F3;
                }}
                
                p {{ 
                    margin: 8px 0 0 0; 
                    color: #616161; 
                    font-size: 14px; 
                    font-weight: 400;
                }}
                
                .methodology {{ 
                    background: #FFFFFF;
                    border-radius: 8px;
                    padding: 24px; 
                    margin-bottom: 24px; 
                    font-size: 13px; 
                    line-height: 1.8;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    border-left: 4px solid #4CAF50;
                }}
                
                .methodology strong {{ 
                    color: #1976D2; 
                    font-weight: 500;
                }}
                
                .methodology-title {{
                    font-size: 16px;
                    font-weight: 500;
                    color: #212121;
                    margin-bottom: 16px;
                    display: flex;
                    align-items: center;
                    gap: 10px;
                }}
                
                .methodology-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                    gap: 16px;
                    margin-top: 16px;
                }}
                
                .methodology-item {{
                    padding: 16px;
                    background: #F5F5F5;
                    border-radius: 4px;
                    border-left: 3px solid #2196F3;
                }}
                
                .macro-container {{ 
                    background: #FFFFFF;
                    border-radius: 8px;
                    padding: 20px; 
                    margin-bottom: 24px;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                    transition: box-shadow 0.3s ease;
                }}
                
                .macro-container:hover {{
                    box-shadow: 0 4px 12px rgba(33, 150, 243, 0.2);
                }}
                
                .grid {{ 
                    display: grid; 
                    grid-template-columns: repeat(auto-fit, minmax(520px, 1fr)); 
                    gap: 24px;
                }}
                
                .card {{ 
                    background: #FFFFFF;
                    border-radius: 8px;
                    overflow: hidden;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                    transition: transform 0.2s ease, box-shadow 0.3s ease;
                }}
                
                .card:hover {{
                    transform: translateY(-4px);
                    box-shadow: 0 8px 16px rgba(0,0,0,0.15);
                }}
                
                .footer {{
                    margin-top: 48px;
                    padding-top: 24px;
                    border-top: 1px solid #E0E0E0;
                    text-align: center;
                    color: #757575;
                    font-size: 12px;
                }}
                
                code {{
                    background: #F5F5F5;
                    padding: 2px 6px;
                    border-radius: 3px;
                    font-family: 'Roboto Mono', monospace;
                    font-size: 12px;
                    color: #D32F2F;
                }}
                
                @media (max-width: 768px) {{ 
                    body {{ padding: 16px; }}
                    .grid {{ grid-template-columns: 1fr; }}
                    h1 {{ font-size: 24px; }}
                    .header {{ padding: 20px; }}
                    .subtitle {{ flex-direction: column; align-items: flex-start; }}
                }}
                
                @media print {{
                    body {{ background: white; }}
                    .card, .macro-container {{ break-inside: avoid; box-shadow: none; border: 1px solid #E0E0E0; }}
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>{mkt_id} Professional Technical Rotation Grid</h1>
                    <div class="subtitle">
                        <span class="badge date-badge">📅 {display_date}</span>
                        <span class="badge">⚙️ JdK 14-Week WMA</span>
                        <span class="badge count-badge">📈 Multiple Assets Tracked</span>
                    </div>
                    <p style="margin-top: 16px; color: #424242;">Real-time sector rotation analysis using Julius de Kempenaer's professional RRG methodology</p>
                </div>
                
                <div class="methodology">
                    <div class="methodology-title">📊 Calculation Methodology</div>
                    <div class="methodology-grid">
                        <div class="methodology-item">
                            <strong>RS-Ratio (X-Axis):</strong><br>
                            <code>(WMA(RS) / WMA(WMA(RS))) × 100</code><br>
                            <span style="color: #616161; font-size: 12px;">Measures relative strength position vs benchmark</span>
                        </div>
                        <div class="methodology-item">
                            <strong>RS-Momentum (Y-Axis):</strong><br>
                            <code>(RS-Ratio / WMA(RS-Ratio)) × 100</code><br>
                            <span style="color: #616161; font-size: 12px;">Measures rate of change in relative strength</span>
                        </div>
                        <div class="methodology-item">
                            <strong>Rotation Pattern:</strong><br>
                            <span style="color: #4CAF50; font-weight: 500;">Leading ↗</span> → 
                            <span style="color: #FF9800; font-weight: 500;">Weakening ↘</span> → 
                            <span style="color: #F44336; font-weight: 500;">Lagging ↙</span> → 
                            <span style="color: #2196F3; font-weight: 500;">Improving ↖</span><br>
                            <span style="color: #616161; font-size: 12px;">Clockwise rotation indicates strengthening trend</span>
                        </div>
                    </div>
                </div>
                
                <h2>Section I: Macro Allocation Landscape</h2>
                <div class="macro-container">
                    {macro_div}
                    {macro_summary}
                </div>
                
                <h2>Section II: Micro Sector Components Alpha Space</h2>
                <div class="grid">{"".join(micro_cards_html)}</div>
                
                <div class="footer">
                    <p style="font-weight: 500; color: #424242;">Generated using JdK Professional RRG Methodology</p>
                    <p style="margin-top: 8px;">Compatible with Optuma & StockCharts Standards | Data Source: Yahoo Finance | Visualization: Plotly</p>
                    <p style="margin-top: 8px;">© {pd.Timestamp.now().year} | Material Design Light Theme</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        output_file = os.path.abspath(schema["filename"])
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(html_content)
            
        print(f"✅ Generated Standalone Verified Workspace: {output_file}")
        webbrowser.open(f"file://{output_file}")