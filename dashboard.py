"""
Dashboard Generator for Personal Expense Analyzer
====================================================
Generates a beautiful, interactive HTML dashboard from expense data
and serves it locally via an HTTP server.

Uses only:
    - NumPy, Pandas, Matplotlib (for data processing & chart generation)
    - Python standard library (http.server, io, base64, webbrowser, socket)

Run:
    python dashboard.py
    Opens: http://localhost:8050/
"""

import os
import io
import sys
import base64
import socket
import webbrowser
import http.server
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")  # Non-interactive backend for image generation
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

# ── Import config and helpers from main.py ────────────────────────────────────
from main import (
    CSV_FILE, MONTHLY_BUDGET, CATEGORY_BUDGETS,
    load_expense_data, format_inr, VIS_FOLDER
)

# Path for the generated HTML dashboard
DASHBOARD_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dashboard.html")

# Default HTTP server port
DEFAULT_PORT = 8050


# ──────────────────────────────────────────────────────────────────────────────
# Chart generation — returns base64-encoded PNG strings
# ──────────────────────────────────────────────────────────────────────────────

def _apply_dark_style():
    """Apply a consistent dark style for all charts."""
    plt.rcParams.update({
        "figure.facecolor": "#1a1a2e",
        "axes.facecolor": "#16213e",
        "axes.edgecolor": "#444466",
        "axes.labelcolor": "#e0e0e0",
        "text.color": "#e0e0e0",
        "xtick.color": "#b0b0c0",
        "ytick.color": "#b0b0c0",
        "grid.color": "#2a2a45",
        "grid.alpha": 0.6,
        "font.size": 11,
        "axes.titlesize": 14,
        "axes.titleweight": "bold",
    })


def _fig_to_base64(fig):
    """Convert a Matplotlib figure to a base64 PNG string."""
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=130, bbox_inches="tight",
                facecolor=fig.get_facecolor(), edgecolor="none")
    plt.close(fig)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode("utf-8")


def _inr_tick(x, pos):
    """Tick formatter for INR on axes."""
    if x >= 10000:
        return f"₹{x / 1000:.0f}K"
    return f"₹{x:,.0f}"


def gen_category_bar(df):
    """Generate category-wise horizontal bar chart."""
    _apply_dark_style()
    cat_totals = df.groupby("Category")["Amount"].sum().sort_values()

    colors = ["#6C5CE7", "#0984E3", "#00CEC9", "#00B894",
              "#FDCB6E", "#E17055", "#D63031", "#E84393"]

    fig, ax = plt.subplots(figsize=(8, 4.5))
    bars = ax.barh(cat_totals.index, cat_totals.values,
                   color=colors[:len(cat_totals)], edgecolor="#1a1a2e",
                   linewidth=1, height=0.6)

    for bar, val in zip(bars, cat_totals.values):
        ax.text(bar.get_width() + 200, bar.get_y() + bar.get_height() / 2,
                format_inr(val), va="center", fontsize=9, color="#e0e0e0")

    ax.set_xlabel("Total Amount (₹)")
    ax.set_title("Category-wise Total Expenses")
    ax.xaxis.set_major_formatter(ticker.FuncFormatter(_inr_tick))
    ax.grid(axis="x", linestyle="--")
    plt.tight_layout()
    return _fig_to_base64(fig)


def gen_monthly_line(df):
    """Generate monthly spending line chart."""
    _apply_dark_style()
    monthly = df.groupby("Month")["Amount"].sum()
    labels = [str(m) for m in monthly.index]
    values = monthly.values

    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.plot(labels, values, marker="o", markersize=7, linewidth=2.5,
            color="#00CEC9", markerfacecolor="#FDCB6E",
            markeredgecolor="#1a1a2e", markeredgewidth=2)
    ax.fill_between(labels, values, alpha=0.12, color="#00CEC9")

    for lbl, val in zip(labels, values):
        ax.annotate(format_inr(val), (lbl, val), textcoords="offset points",
                    xytext=(0, 12), ha="center", fontsize=9, color="#FDCB6E")

    avg = np.mean(values)
    ax.axhline(y=avg, color="#E17055", linestyle="--", linewidth=1, alpha=0.8)
    ax.text(labels[-1], avg + 200, f"Avg: {format_inr(avg)}",
            color="#E17055", fontsize=8, ha="right")

    ax.set_xlabel("Month")
    ax.set_ylabel("Total Spending (₹)")
    ax.set_title("Monthly Spending Trend")
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(_inr_tick))
    ax.grid(True, linestyle="--")
    plt.tight_layout()
    return _fig_to_base64(fig)


def gen_pie_chart(df):
    """Generate expense distribution pie chart."""
    _apply_dark_style()
    cat_totals = df.groupby("Category")["Amount"].sum().sort_values(ascending=False)
    total = cat_totals.sum()

    colors = ["#6C5CE7", "#0984E3", "#00CEC9", "#00B894",
              "#FDCB6E", "#E17055", "#D63031", "#E84393"]
    explode = [0.04 if i == 0 else 0 for i in range(len(cat_totals))]

    fig, ax = plt.subplots(figsize=(7, 5.5))
    wedges, texts, autotexts = ax.pie(
        cat_totals.values, labels=cat_totals.index,
        autopct=lambda p: f"{p:.1f}%", colors=colors[:len(cat_totals)],
        explode=explode, startangle=140, pctdistance=0.78,
        wedgeprops={"edgecolor": "#1a1a2e", "linewidth": 1.5})

    for at in autotexts:
        at.set_fontsize(8)
        at.set_color("#ffffff")
    for t in texts:
        t.set_fontsize(9)

    ax.set_title("Expense Distribution by Category", pad=15)
    plt.tight_layout()
    return _fig_to_base64(fig)


def gen_budget_chart(df):
    """Generate budget vs actual grouped bar chart."""
    _apply_dark_style()
    num_months = df["Month"].nunique()
    cat_totals = df.groupby("Category")["Amount"].sum()
    cat_avg = cat_totals / num_months

    categories = sorted(CATEGORY_BUDGETS.keys())
    budgets = [CATEGORY_BUDGETS[c] for c in categories]
    actuals = [cat_avg.get(c, 0) for c in categories]

    x = np.arange(len(categories))
    w = 0.35

    fig, ax = plt.subplots(figsize=(8, 4.5))
    b1 = ax.bar(x - w / 2, budgets, w, label="Budget", color="#0984E3",
                edgecolor="#1a1a2e", linewidth=1)
    b2 = ax.bar(x + w / 2, actuals, w, label="Actual (Avg/Month)",
                color="#E17055", edgecolor="#1a1a2e", linewidth=1)

    for i, (bv, av) in enumerate(zip(budgets, actuals)):
        if av > bv:
            b2[i].set_color("#D63031")
            b2[i].set_edgecolor("#FDCB6E")
            b2[i].set_linewidth(2)

    for bar in b1:
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 80,
                format_inr(bar.get_height()), ha="center", fontsize=7, color="#74b9ff")
    for bar in b2:
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 80,
                format_inr(bar.get_height()), ha="center", fontsize=7, color="#fab1a0")

    ax.set_xlabel("Category")
    ax.set_ylabel("Amount (₹)")
    ax.set_title("Budget vs. Actual Spending (Monthly Average)")
    ax.set_xticks(x)
    ax.set_xticklabels(categories, rotation=25, ha="right")
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(_inr_tick))
    ax.legend(loc="upper right", framealpha=0.7)
    ax.grid(axis="y", linestyle="--")
    plt.tight_layout()
    return _fig_to_base64(fig)


# ──────────────────────────────────────────────────────────────────────────────
# Data computation for dashboard cards & tables
# ──────────────────────────────────────────────────────────────────────────────

def compute_dashboard_data(df):
    """Compute all summary metrics needed for the HTML dashboard."""
    amounts = df["Amount"].values

    total = np.sum(amounts)
    avg = np.mean(amounts)
    median = np.median(amounts)
    std = np.std(amounts)
    count = len(amounts)

    highest_row = df.loc[df["Amount"].idxmax()]
    lowest_row = df.loc[df["Amount"].idxmin()]

    # Category summary
    cat_totals = df.groupby("Category")["Amount"].sum().sort_values(ascending=False)
    top_category = cat_totals.idxmax()

    # Monthly summary
    monthly_totals = df.groupby("Month")["Amount"].sum()
    num_months = len(monthly_totals)
    avg_monthly = np.mean(monthly_totals.values)
    highest_month = monthly_totals.idxmax()
    lowest_month = monthly_totals.idxmin()

    # Budget
    overall_diff = MONTHLY_BUDGET - avg_monthly
    utilization = (avg_monthly / MONTHLY_BUDGET) * 100

    # Monthly trend data
    month_labels = [str(m) for m in monthly_totals.index]
    month_vals = monthly_totals.values.tolist()

    # Category budget table
    budget_rows = []
    for cat in sorted(CATEGORY_BUDGETS.keys()):
        budget = CATEGORY_BUDGETS[cat]
        actual_avg = (cat_totals.get(cat, 0)) / num_months
        used_pct = (actual_avg / budget) * 100 if budget > 0 else 0
        diff = budget - actual_avg
        status = "within" if diff >= 0 else "over"
        budget_rows.append({
            "category": cat,
            "budget": format_inr(budget),
            "actual": format_inr(actual_avg),
            "pct": f"{used_pct:.1f}%",
            "status": status,
        })

    # Month-over-month change
    mom_rows = []
    for i, (lbl, val) in enumerate(zip(month_labels, month_vals)):
        if i == 0:
            mom_rows.append({"month": lbl, "amount": format_inr(val), "change": "—"})
        else:
            prev = month_vals[i - 1]
            pct = ((val - prev) / prev) * 100 if prev != 0 else 0
            arrow = "▲" if pct > 0 else "▼" if pct < 0 else "─"
            color_cls = "trend-up" if pct > 0 else "trend-down"
            mom_rows.append({
                "month": lbl,
                "amount": format_inr(val),
                "change": f'<span class="{color_cls}">{arrow} {abs(pct):.1f}%</span>',
            })

    # Category table rows
    cat_rows = []
    for cat, val in cat_totals.items():
        pct = (val / total) * 100
        cat_data = df[df["Category"] == cat]["Amount"].values
        cat_rows.append({
            "category": cat,
            "total": format_inr(val),
            "avg": format_inr(np.mean(cat_data)),
            "count": len(cat_data),
            "pct": f"{pct:.1f}%",
        })

    return {
        "total": format_inr(total),
        "avg": format_inr(avg),
        "median": format_inr(median),
        "std": format_inr(std),
        "count": count,
        "highest": format_inr(np.max(amounts)),
        "highest_desc": f"{highest_row['Description']} ({highest_row['Category']})",
        "lowest": format_inr(np.min(amounts)),
        "lowest_desc": f"{lowest_row['Description']} ({lowest_row['Category']})",
        "top_category": top_category,
        "top_category_val": format_inr(cat_totals[top_category]),
        "avg_monthly": format_inr(avg_monthly),
        "highest_month": str(highest_month),
        "highest_month_val": format_inr(monthly_totals[highest_month]),
        "lowest_month": str(lowest_month),
        "lowest_month_val": format_inr(monthly_totals[lowest_month]),
        "budget": format_inr(MONTHLY_BUDGET),
        "utilization": f"{utilization:.1f}%",
        "budget_status": "Within Budget ✔" if overall_diff >= 0 else "Over Budget ✖",
        "budget_status_cls": "card-green" if overall_diff >= 0 else "card-red",
        "budget_remaining": format_inr(abs(overall_diff)),
        "num_months": num_months,
        "budget_rows": budget_rows,
        "mom_rows": mom_rows,
        "cat_rows": cat_rows,
    }


# ──────────────────────────────────────────────────────────────────────────────
# HTML Template
# ──────────────────────────────────────────────────────────────────────────────

def build_html(data, chart_b64):
    """Build the complete HTML dashboard string."""

    # Build budget table rows
    budget_table_rows = ""
    for r in data["budget_rows"]:
        status_badge = (
            '<span class="badge badge-green">Within</span>'
            if r["status"] == "within"
            else '<span class="badge badge-red">Over!</span>'
        )
        budget_table_rows += f"""
        <tr>
            <td>{r['category']}</td>
            <td>{r['budget']}</td>
            <td>{r['actual']}</td>
            <td>{r['pct']}</td>
            <td>{status_badge}</td>
        </tr>"""

    # Build month-over-month rows
    mom_table_rows = ""
    for r in data["mom_rows"]:
        mom_table_rows += f"""
        <tr>
            <td>{r['month']}</td>
            <td>{r['amount']}</td>
            <td>{r['change']}</td>
        </tr>"""

    # Build category summary rows
    cat_table_rows = ""
    for r in data["cat_rows"]:
        cat_table_rows += f"""
        <tr>
            <td>{r['category']}</td>
            <td>{r['total']}</td>
            <td>{r['avg']}</td>
            <td>{r['count']}</td>
            <td>{r['pct']}</td>
        </tr>"""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Personal Expense Analyzer — Dashboard</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        /* ── Reset & Base ── */
        *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background: #0a0a1a;
            color: #e0e0f0;
            min-height: 100vh;
            line-height: 1.6;
        }}

        /* ── Background glow ── */
        body::before {{
            content: '';
            position: fixed;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: radial-gradient(circle at 30% 20%, rgba(108, 92, 231, 0.08) 0%, transparent 50%),
                        radial-gradient(circle at 70% 80%, rgba(0, 206, 201, 0.06) 0%, transparent 50%);
            z-index: -1;
        }}

        /* ── Header ── */
        .header {{
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            border-bottom: 1px solid rgba(108, 92, 231, 0.3);
            padding: 1.5rem 2rem;
            text-align: center;
        }}

        .header h1 {{
            font-size: 1.8rem;
            font-weight: 700;
            background: linear-gradient(135deg, #6C5CE7, #00CEC9);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 0.3rem;
        }}

        .header p {{
            color: #8888aa;
            font-size: 0.9rem;
            font-weight: 300;
        }}

        /* ── Container ── */
        .container {{
            max-width: 1280px;
            margin: 0 auto;
            padding: 1.5rem;
        }}

        /* ── Section Titles ── */
        .section-title {{
            font-size: 1.15rem;
            font-weight: 600;
            margin: 2rem 0 1rem 0;
            padding-left: 0.75rem;
            border-left: 3px solid #6C5CE7;
            color: #c0c0e0;
        }}

        /* ── KPI Cards ── */
        .kpi-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 1rem;
            margin-bottom: 1.5rem;
        }}

        .kpi-card {{
            background: linear-gradient(145deg, #1a1a2e, #16213e);
            border: 1px solid #2a2a45;
            border-radius: 12px;
            padding: 1.25rem;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }}

        .kpi-card:hover {{
            transform: translateY(-3px);
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
        }}

        .kpi-label {{
            font-size: 0.75rem;
            text-transform: uppercase;
            letter-spacing: 1px;
            color: #7777aa;
            margin-bottom: 0.5rem;
        }}

        .kpi-value {{
            font-size: 1.5rem;
            font-weight: 700;
            color: #ffffff;
        }}

        .kpi-sub {{
            font-size: 0.78rem;
            color: #8888aa;
            margin-top: 0.3rem;
        }}

        .kpi-card.card-purple .kpi-value {{ color: #a29bfe; }}
        .kpi-card.card-teal .kpi-value {{ color: #00CEC9; }}
        .kpi-card.card-orange .kpi-value {{ color: #FDCB6E; }}
        .kpi-card.card-pink .kpi-value {{ color: #fd79a8; }}
        .kpi-card.card-green .kpi-value {{ color: #55efc4; }}
        .kpi-card.card-red .kpi-value {{ color: #ff7675; }}
        .kpi-card.card-blue .kpi-value {{ color: #74b9ff; }}

        /* ── Charts Grid ── */
        .charts-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
            gap: 1.5rem;
            margin-bottom: 1.5rem;
        }}

        .chart-card {{
            background: linear-gradient(145deg, #1a1a2e, #16213e);
            border: 1px solid #2a2a45;
            border-radius: 12px;
            padding: 1rem;
            overflow: hidden;
        }}

        .chart-card img {{
            width: 100%;
            height: auto;
            border-radius: 8px;
        }}

        .chart-card h3 {{
            font-size: 0.95rem;
            font-weight: 600;
            color: #b0b0d0;
            margin-bottom: 0.75rem;
            padding-left: 0.5rem;
        }}

        /* ── Tables ── */
        .table-wrap {{
            background: linear-gradient(145deg, #1a1a2e, #16213e);
            border: 1px solid #2a2a45;
            border-radius: 12px;
            padding: 1.25rem;
            margin-bottom: 1.5rem;
            overflow-x: auto;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 0.88rem;
        }}

        th {{
            text-align: left;
            padding: 0.7rem 1rem;
            color: #8888bb;
            font-weight: 600;
            text-transform: uppercase;
            font-size: 0.72rem;
            letter-spacing: 0.8px;
            border-bottom: 2px solid #2a2a45;
        }}

        td {{
            padding: 0.65rem 1rem;
            border-bottom: 1px solid #1e1e35;
            color: #c0c0e0;
        }}

        tr:hover td {{
            background: rgba(108, 92, 231, 0.06);
        }}

        /* ── Badges ── */
        .badge {{
            display: inline-block;
            padding: 0.2rem 0.6rem;
            border-radius: 20px;
            font-size: 0.72rem;
            font-weight: 600;
        }}

        .badge-green {{
            background: rgba(85, 239, 196, 0.15);
            color: #55efc4;
        }}

        .badge-red {{
            background: rgba(255, 118, 117, 0.15);
            color: #ff7675;
        }}

        /* ── Trend arrows ── */
        .trend-up {{ color: #ff7675; font-weight: 600; }}
        .trend-down {{ color: #55efc4; font-weight: 600; }}

        /* ── Tabs ── */
        .tabs {{
            display: flex;
            gap: 0.5rem;
            margin-bottom: 1rem;
            flex-wrap: wrap;
        }}

        .tab-btn {{
            padding: 0.5rem 1.2rem;
            background: #16213e;
            border: 1px solid #2a2a45;
            border-radius: 8px;
            color: #8888aa;
            cursor: pointer;
            font-size: 0.85rem;
            font-family: inherit;
            transition: all 0.2s ease;
        }}

        .tab-btn:hover {{
            background: #1e2d50;
            color: #c0c0e0;
        }}

        .tab-btn.active {{
            background: #6C5CE7;
            color: #fff;
            border-color: #6C5CE7;
        }}

        .tab-panel {{
            display: none;
        }}

        .tab-panel.active {{
            display: block;
            animation: fadeIn 0.3s ease;
        }}

        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(8px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}

        /* ── Footer ── */
        .footer {{
            text-align: center;
            padding: 2rem 1rem;
            color: #555577;
            font-size: 0.8rem;
            border-top: 1px solid #1e1e35;
            margin-top: 2rem;
        }}

        /* ── Responsive ── */
        @media (max-width: 768px) {{
            .charts-grid {{
                grid-template-columns: 1fr;
            }}
            .kpi-grid {{
                grid-template-columns: repeat(2, 1fr);
            }}
            .header h1 {{
                font-size: 1.4rem;
            }}
        }}
    </style>
</head>
<body>

    <!-- Header -->
    <div class="header">
        <h1>💸 Personal Expense Analyzer</h1>
        <p>Dashboard &mdash; {data['num_months']} months &bull; {data['count']} transactions</p>
    </div>

    <div class="container">

        <!-- ══════════ KPI Cards ══════════ -->
        <h2 class="section-title">Overview</h2>
        <div class="kpi-grid">
            <div class="kpi-card card-purple">
                <div class="kpi-label">Total Expenditure</div>
                <div class="kpi-value">{data['total']}</div>
                <div class="kpi-sub">{data['count']} transactions</div>
            </div>
            <div class="kpi-card card-teal">
                <div class="kpi-label">Average / Transaction</div>
                <div class="kpi-value">{data['avg']}</div>
                <div class="kpi-sub">Median: {data['median']}</div>
            </div>
            <div class="kpi-card card-orange">
                <div class="kpi-label">Avg. Monthly Spending</div>
                <div class="kpi-value">{data['avg_monthly']}</div>
                <div class="kpi-sub">Budget: {data['budget']}</div>
            </div>
            <div class="kpi-card {data['budget_status_cls']}">
                <div class="kpi-label">Budget Status</div>
                <div class="kpi-value">{data['budget_status']}</div>
                <div class="kpi-sub">Utilization: {data['utilization']}</div>
            </div>
            <div class="kpi-card card-pink">
                <div class="kpi-label">Highest Expense</div>
                <div class="kpi-value">{data['highest']}</div>
                <div class="kpi-sub">{data['highest_desc']}</div>
            </div>
            <div class="kpi-card card-blue">
                <div class="kpi-label">Lowest Expense</div>
                <div class="kpi-value">{data['lowest']}</div>
                <div class="kpi-sub">{data['lowest_desc']}</div>
            </div>
            <div class="kpi-card card-teal">
                <div class="kpi-label">Top Category</div>
                <div class="kpi-value">{data['top_category']}</div>
                <div class="kpi-sub">{data['top_category_val']}</div>
            </div>
            <div class="kpi-card card-orange">
                <div class="kpi-label">Highest Month</div>
                <div class="kpi-value">{data['highest_month']}</div>
                <div class="kpi-sub">{data['highest_month_val']}</div>
            </div>
        </div>

        <!-- ══════════ Charts ══════════ -->
        <h2 class="section-title">Visualizations</h2>

        <div class="tabs">
            <button class="tab-btn active" onclick="switchTab(event, 'tab-all')">All Charts</button>
            <button class="tab-btn" onclick="switchTab(event, 'tab-category')">Category Analysis</button>
            <button class="tab-btn" onclick="switchTab(event, 'tab-trend')">Monthly Trend</button>
            <button class="tab-btn" onclick="switchTab(event, 'tab-pie')">Distribution</button>
            <button class="tab-btn" onclick="switchTab(event, 'tab-budget')">Budget Comparison</button>
        </div>

        <div id="tab-all" class="tab-panel active">
            <div class="charts-grid">
                <div class="chart-card">
                    <h3>📊 Category-wise Expenses</h3>
                    <img src="data:image/png;base64,{chart_b64['category_bar']}" alt="Category Bar Chart">
                </div>
                <div class="chart-card">
                    <h3>📈 Monthly Spending Trend</h3>
                    <img src="data:image/png;base64,{chart_b64['monthly_line']}" alt="Monthly Line Chart">
                </div>
                <div class="chart-card">
                    <h3>🍩 Expense Distribution</h3>
                    <img src="data:image/png;base64,{chart_b64['pie']}" alt="Pie Chart">
                </div>
                <div class="chart-card">
                    <h3>💰 Budget vs. Actual</h3>
                    <img src="data:image/png;base64,{chart_b64['budget']}" alt="Budget Chart">
                </div>
            </div>
        </div>

        <div id="tab-category" class="tab-panel">
            <div class="charts-grid">
                <div class="chart-card">
                    <h3>📊 Category-wise Expenses</h3>
                    <img src="data:image/png;base64,{chart_b64['category_bar']}" alt="Category Bar Chart">
                </div>
                <div class="table-wrap">
                    <table>
                        <thead>
                            <tr><th>Category</th><th>Total</th><th>Avg / Txn</th><th>Count</th><th>Share</th></tr>
                        </thead>
                        <tbody>{cat_table_rows}</tbody>
                    </table>
                </div>
            </div>
        </div>

        <div id="tab-trend" class="tab-panel">
            <div class="charts-grid">
                <div class="chart-card">
                    <h3>📈 Monthly Spending Trend</h3>
                    <img src="data:image/png;base64,{chart_b64['monthly_line']}" alt="Monthly Line Chart">
                </div>
                <div class="table-wrap">
                    <table>
                        <thead><tr><th>Month</th><th>Total Spending</th><th>Change</th></tr></thead>
                        <tbody>{mom_table_rows}</tbody>
                    </table>
                </div>
            </div>
        </div>

        <div id="tab-pie" class="tab-panel">
            <div class="charts-grid" style="max-width: 650px; margin: 0 auto;">
                <div class="chart-card">
                    <h3>🍩 Expense Distribution</h3>
                    <img src="data:image/png;base64,{chart_b64['pie']}" alt="Pie Chart">
                </div>
            </div>
        </div>

        <div id="tab-budget" class="tab-panel">
            <div class="charts-grid">
                <div class="chart-card">
                    <h3>💰 Budget vs. Actual</h3>
                    <img src="data:image/png;base64,{chart_b64['budget']}" alt="Budget Chart">
                </div>
                <div class="table-wrap">
                    <table>
                        <thead><tr><th>Category</th><th>Budget</th><th>Actual (Avg/Mo)</th><th>Used</th><th>Status</th></tr></thead>
                        <tbody>{budget_table_rows}</tbody>
                    </table>
                </div>
            </div>
        </div>

        <!-- ══════════ Footer ══════════ -->
        <div class="footer">
            Personal Expense Analyzer &bull; Built with Python, NumPy, Pandas & Matplotlib
        </div>

    </div>

    <script>
        function switchTab(e, tabId) {{
            document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            document.getElementById(tabId).classList.add('active');
            e.target.classList.add('active');
        }}
    </script>
</body>
</html>"""
    return html


# ──────────────────────────────────────────────────────────────────────────────
# Localhost HTTP Server
# ──────────────────────────────────────────────────────────────────────────────

class DashboardRequestHandler(http.server.SimpleHTTPRequestHandler):
    """Custom HTTP handler that serves dashboard.html from the project directory."""

    def __init__(self, *args, **kwargs):
        project_dir = os.path.dirname(os.path.abspath(__file__))
        super().__init__(*args, directory=project_dir, **kwargs)

    def do_GET(self):
        # Map root URL '/' directly to '/dashboard.html'
        if self.path in ("/", ""):
            self.path = "/dashboard.html"
        elif self.path == "/favicon.ico":
            self.send_response(204)
            self.send_header("Content-Length", "0")
            self.end_headers()
            return
        return super().do_GET()

    def log_message(self, format, *args):
        # Keep terminal clean; don't print routine GET/200 logs
        pass


def find_available_port(start_port=DEFAULT_PORT, max_attempts=20):
    """Find the first available port starting from start_port."""
    for port in range(start_port, start_port + max_attempts):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                s.bind(("127.0.0.1", port))
                return port
            except OSError:
                continue
    return start_port


def start_dashboard_server(port=None):
    """Start a local HTTP server and open the dashboard link in the browser."""
    if port is None:
        port = find_available_port(DEFAULT_PORT)

    http.server.ThreadingHTTPServer.allow_reuse_address = True
    server = http.server.ThreadingHTTPServer(("127.0.0.1", port), DashboardRequestHandler)
    localhost_url = f"http://localhost:{port}/"

    print("\n" + "═" * 65)
    print("  🚀  DASHBOARD SERVER RUNNING")
    print("═" * 65)
    print(f"\n  👉 Localhost Dashboard URL:")
    print(f"     {localhost_url}")
    print(f"\n     (Click the link above or copy-paste it into your browser)")
    print("  ─────────────────────────────────────────────────────────────")
    print("  Serving: dashboard.html")
    print("  Press [Ctrl+C] to stop the server.")
    print("═" * 65 + "\n")

    # Open localhost URL in user's default browser
    try:
        webbrowser.open(localhost_url)
    except Exception:
        pass

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n\n  🛑 Dashboard server stopped. Goodbye!\n")
    finally:
        server.server_close()


# ──────────────────────────────────────────────────────────────────────────────
# Main — Generate and serve the dashboard
# ──────────────────────────────────────────────────────────────────────────────

def generate_dashboard(serve=True):
    """Generate the HTML dashboard and optionally launch the localhost server."""
    print("\n" + "═" * 65)
    print("        📊  PERSONAL EXPENSE DASHBOARD GENERATOR")
    print("═" * 65)
    print("\n  ⏳ Loading expense data...")
    df = load_expense_data(CSV_FILE)
    if df is None:
        print("  ✖ Cannot generate dashboard without valid data.")
        return

    print("  📊 Generating charts (category bar, monthly line, pie, budget)...")
    chart_b64 = {
        "category_bar": gen_category_bar(df),
        "monthly_line": gen_monthly_line(df),
        "pie": gen_pie_chart(df),
        "budget": gen_budget_chart(df),
    }

    print("  📋 Computing summary metrics & KPI cards...")
    data = compute_dashboard_data(df)

    print("  🖥  Building HTML dashboard...")
    html = build_html(data, chart_b64)

    with open(DASHBOARD_FILE, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"\n  ✔ Dashboard saved to: {DASHBOARD_FILE}")

    if serve:
        start_dashboard_server()


if __name__ == "__main__":
    generate_dashboard(serve=True)
