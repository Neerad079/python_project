
import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker


# Overall monthly budget (in ₹)
MONTHLY_BUDGET = 35000

# Category-wise budget limits (in ₹ per month)
CATEGORY_BUDGETS = {
    "Food": 8000,
    "Transport": 3000,
    "Shopping": 5000,
    "Education": 4000,
    "Entertainment": 3000,
    "Utilities": 4000,
    "Rent": 12000,
}

# Path to the expense CSV file (relative to this script)
CSV_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "expense_data.csv")

# Folder where chart images are saved
VIS_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "visualizations")



def format_inr(amount):
    """Return a string formatted as Indian Rupees, e.g. ₹1,23,456.00"""
    # Indian numbering: last 3 digits separated, then groups of 2
    sign = "-" if amount < 0 else ""
    amount = abs(amount)
    integer_part = int(amount)
    decimal_part = f"{amount - integer_part:.2f}"[1:]  # ".xx"

    s = str(integer_part)
    if len(s) <= 3:
        formatted = s
    else:
        # Last three digits
        last3 = s[-3:]
        rest = s[:-3]
        # Group remaining digits in pairs from the right
        groups = []
        while rest:
            groups.append(rest[-2:])
            rest = rest[:-2]
        groups.reverse()
        formatted = ",".join(groups) + "," + last3

    return f"{sign}₹{formatted}{decimal_part}"


def load_expense_data(filepath):
    """
    Load expense records from a CSV file using Pandas.

    Expected columns: Date, Category, Description, Amount

    Performs the following validations:
      1. File existence check.
      2. Required columns check.
      3. Date format validation and conversion.
      4. Amount validation (must be a positive number).
      5. Missing value handling.

    Returns a cleaned Pandas DataFrame, or None if loading fails.
    """
    # --- Check if file exists ---
    if not os.path.exists(filepath):
        print(f"\n  ✖ Error: File not found → {filepath}")
        print("    Please make sure 'expense_data.csv' is in the project folder.")
        return None

    # --- Read CSV ---
    try:
        df = pd.read_csv(filepath)
    except Exception as e:
        print(f"\n  ✖ Error reading CSV file: {e}")
        return None

    # --- Check required columns ---
    required_columns = {"Date", "Category", "Description", "Amount"}
    if not required_columns.issubset(df.columns):
        missing = required_columns - set(df.columns)
        print(f"\n  ✖ Error: Missing required columns → {missing}")
        return None

    # --- Report and drop rows with missing values ---
    rows_before = len(df)
    df = df.dropna(subset=["Date", "Category", "Amount"])
    rows_dropped = rows_before - len(df)
    if rows_dropped > 0:
        print(f"\n  ⚠ Warning: {rows_dropped} row(s) with missing values were removed.")

    # --- Validate and convert Date ---
    df["Date"] = pd.to_datetime(df["Date"], format="%Y-%m-%d", errors="coerce")
    invalid_dates = df["Date"].isna().sum()
    if invalid_dates > 0:
        print(f"  ⚠ Warning: {invalid_dates} row(s) with invalid dates were removed.")
        df = df.dropna(subset=["Date"])

    # --- Validate Amount (must be numeric and positive) ---
    df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce")
    invalid_amounts = df["Amount"].isna().sum()
    if invalid_amounts > 0:
        print(f"  ⚠ Warning: {invalid_amounts} row(s) with invalid amounts were removed.")
        df = df.dropna(subset=["Amount"])

    negative_amounts = (df["Amount"] <= 0).sum()
    if negative_amounts > 0:
        print(f"  ⚠ Warning: {negative_amounts} row(s) with non-positive amounts were removed.")
        df = df[df["Amount"] > 0]

    # --- Check if any data remains ---
    if df.empty:
        print("\n  ✖ Error: No valid expense records found after cleaning.")
        return None

    # --- Add helper columns for analysis ---
    df["Month"] = df["Date"].dt.to_period("M")        # e.g. 2026-01
    df["MonthName"] = df["Date"].dt.strftime("%b %Y")  # e.g. Jan 2026

    # Sort by date
    df = df.sort_values("Date").reset_index(drop=True)

    print(f"\n  ✔ Successfully loaded {len(df)} expense records.")
    return df


# ──────────────────────────────────────────────────────────────────────────────
# FEATURE A — Expense Summary
# ──────────────────────────────────────────────────────────────────────────────

def show_expense_summary(df):
    """
    Display a comprehensive summary of all expenses:
      - Total expenditure
      - Average expense per transaction
      - Highest and lowest individual expenses
      - Category-wise totals
      - Top spending category
      - Month-wise totals
    Uses NumPy for statistical calculations.
    """
    amounts = df["Amount"].values  # NumPy array for calculations

    # --- Basic statistics using NumPy ---
    total = np.sum(amounts)
    average = np.mean(amounts)
    median = np.median(amounts)
    std_dev = np.std(amounts)
    highest = np.max(amounts)
    lowest = np.min(amounts)

    print("\n" + "=" * 65)
    print("              📊  EXPENSE SUMMARY REPORT")
    print("=" * 65)

    print(f"\n  Total Expenditure          : {format_inr(total)}")
    print(f"  Number of Transactions     : {len(df)}")
    print(f"  Average per Transaction    : {format_inr(average)}")
    print(f"  Median Expense             : {format_inr(median)}")
    print(f"  Standard Deviation         : {format_inr(std_dev)}")

    # Highest and lowest with details
    highest_row = df.loc[df["Amount"].idxmax()]
    lowest_row = df.loc[df["Amount"].idxmin()]

    print(f"\n  💰 Highest Expense         : {format_inr(highest)}")
    print(f"     → {highest_row['Description']} ({highest_row['Category']})")
    print(f"  💸 Lowest Expense          : {format_inr(lowest)}")
    print(f"     → {lowest_row['Description']} ({lowest_row['Category']})")

    # --- Category-wise summary using Pandas ---
    print("\n" + "-" * 65)
    print("  Category-wise Total Expenditure")
    print("-" * 65)

    category_totals = df.groupby("Category")["Amount"].sum().sort_values(ascending=False)

    for category, cat_total in category_totals.items():
        percentage = (cat_total / total) * 100
        print(f"    {category:<16} {format_inr(cat_total):>14}   ({percentage:5.1f}%)")

    top_category = category_totals.idxmax()
    print(f"\n  🏆 Top Spending Category   : {top_category} ({format_inr(category_totals[top_category])})")

    # --- Month-wise summary ---
    print("\n" + "-" * 65)
    print("  Month-wise Total Expenditure")
    print("-" * 65)

    monthly_totals = df.groupby("Month")["Amount"].sum()

    for month, month_total in monthly_totals.items():
        print(f"    {str(month):<12} {format_inr(month_total):>14}")

    print("=" * 65)


# ──────────────────────────────────────────────────────────────────────────────
# FEATURE B — Category-wise Analysis
# ──────────────────────────────────────────────────────────────────────────────

def show_category_analysis(df):
    """
    Display detailed analysis for each expense category:
      - Total, average, count, min, and max per category
      - Uses NumPy percentile for deeper insights
    """
    print("\n" + "=" * 65)
    print("              📂  CATEGORY-WISE ANALYSIS")
    print("=" * 65)

    categories = sorted(df["Category"].unique())

    for category in categories:
        cat_data = df[df["Category"] == category]
        cat_amounts = cat_data["Amount"].values  # NumPy array

        cat_total = np.sum(cat_amounts)
        cat_avg = np.mean(cat_amounts)
        cat_count = len(cat_amounts)
        cat_min = np.min(cat_amounts)
        cat_max = np.max(cat_amounts)
        # 25th and 75th percentile using NumPy
        q25 = np.percentile(cat_amounts, 25)
        q75 = np.percentile(cat_amounts, 75)

        print(f"\n  ▸ {category}")
        print(f"    Transactions : {cat_count}")
        print(f"    Total        : {format_inr(cat_total)}")
        print(f"    Average      : {format_inr(cat_avg)}")
        print(f"    Min / Max    : {format_inr(cat_min)} / {format_inr(cat_max)}")
        print(f"    25th / 75th  : {format_inr(q25)} / {format_inr(q75)}")

    print("\n" + "=" * 65)


# ──────────────────────────────────────────────────────────────────────────────
# FEATURE C — Monthly Spending Trends
# ──────────────────────────────────────────────────────────────────────────────

def show_monthly_trends(df):
    """
    Analyze how spending changes month to month:
      - Month-wise totals
      - Highest and lowest spending months
      - Month-over-month percentage change
      - Category contribution per month
    """
    print("\n" + "=" * 65)
    print("              📈  MONTHLY SPENDING TRENDS")
    print("=" * 65)

    monthly_totals = df.groupby("Month")["Amount"].sum()
    months_array = monthly_totals.values  # NumPy array

    # Highest and lowest months
    highest_month = monthly_totals.idxmax()
    lowest_month = monthly_totals.idxmin()

    print(f"\n  📅 Highest Spending Month  : {highest_month}  ({format_inr(monthly_totals[highest_month])})")
    print(f"  📅 Lowest Spending Month   : {lowest_month}  ({format_inr(monthly_totals[lowest_month])})")
    print(f"\n  Average Monthly Spending   : {format_inr(np.mean(months_array))}")

    # Month-over-month change
    print("\n" + "-" * 65)
    print("  Month-over-Month Change")
    print("-" * 65)

    month_labels = [str(m) for m in monthly_totals.index]
    month_values = monthly_totals.values

    for i in range(len(month_labels)):
        if i == 0:
            print(f"    {month_labels[i]:<12} {format_inr(month_values[i]):>14}   (baseline)")
        else:
            prev = month_values[i - 1]
            curr = month_values[i]
            if prev != 0:
                pct_change = ((curr - prev) / prev) * 100
                direction = "▲" if pct_change > 0 else "▼" if pct_change < 0 else "─"
                print(f"    {month_labels[i]:<12} {format_inr(curr):>14}   {direction} {abs(pct_change):5.1f}%")
            else:
                print(f"    {month_labels[i]:<12} {format_inr(curr):>14}   (N/A)")

    # Top contributing categories per month
    print("\n" + "-" * 65)
    print("  Top Spending Category Each Month")
    print("-" * 65)

    for month in monthly_totals.index:
        month_data = df[df["Month"] == month]
        top_cat = month_data.groupby("Category")["Amount"].sum().idxmax()
        top_val = month_data.groupby("Category")["Amount"].sum().max()
        print(f"    {str(month):<12} {top_cat:<16} {format_inr(top_val):>14}")

    print("=" * 65)


# ──────────────────────────────────────────────────────────────────────────────
# FEATURE D — Budget Analysis
# ──────────────────────────────────────────────────────────────────────────────

def show_budget_analysis(df):
    """
    Compare actual spending against budgets:
      - Overall monthly budget vs actual (averaged)
      - Category-wise budget vs actual per month
      - Identify over-budget categories
      - Show budget utilization percentages
    """
    print("\n" + "=" * 65)
    print("              💰  BUDGET ANALYSIS REPORT")
    print("=" * 65)

    monthly_totals = df.groupby("Month")["Amount"].sum()
    num_months = len(monthly_totals)
    avg_monthly_spend = np.mean(monthly_totals.values)

    print(f"\n  Monthly Budget             : {format_inr(MONTHLY_BUDGET)}")
    print(f"  Avg. Monthly Spending      : {format_inr(avg_monthly_spend)}")

    diff = MONTHLY_BUDGET - avg_monthly_spend
    utilization = (avg_monthly_spend / MONTHLY_BUDGET) * 100

    if diff >= 0:
        print(f"  Remaining (avg.)           : {format_inr(diff)}")
        print(f"  Budget Utilization         : {utilization:.1f}%  ✔ Within budget")
    else:
        print(f"  Over Budget (avg.)         : {format_inr(abs(diff))}")
        print(f"  Budget Utilization         : {utilization:.1f}%  ✖ Over budget!")

    # --- Per-month budget check ---
    print("\n" + "-" * 65)
    print("  Month-wise Budget Status")
    print("-" * 65)
    print(f"    {'Month':<12} {'Actual':>12}  {'Budget':>12}  {'Status':>12}")
    print("    " + "-" * 52)

    for month, actual in monthly_totals.items():
        status_diff = MONTHLY_BUDGET - actual
        if status_diff >= 0:
            status = f"✔ +{format_inr(status_diff)}"
        else:
            status = f"✖ {format_inr(status_diff)}"
        print(f"    {str(month):<12} {format_inr(actual):>12}  {format_inr(MONTHLY_BUDGET):>12}  {status}")

    # --- Category-wise budget analysis ---
    print("\n" + "-" * 65)
    print("  Category-wise Budget Analysis (Monthly Average)")
    print("-" * 65)

    category_totals = df.groupby("Category")["Amount"].sum()
    # Calculate average monthly spending per category
    category_monthly_avg = category_totals / num_months

    over_budget_categories = []

    print(f"    {'Category':<16} {'Avg/Month':>12}  {'Budget':>12}  {'Used%':>7}  {'Status'}")
    print("    " + "-" * 65)

    for category in sorted(CATEGORY_BUDGETS.keys()):
        budget = CATEGORY_BUDGETS[category]
        actual_avg = category_monthly_avg.get(category, 0)
        used_pct = (actual_avg / budget) * 100 if budget > 0 else 0
        diff_val = budget - actual_avg

        if diff_val >= 0:
            status = "✔ Within"
        else:
            status = "✖ OVER!"
            over_budget_categories.append(category)

        print(f"    {category:<16} {format_inr(actual_avg):>12}  {format_inr(budget):>12}  {used_pct:5.1f}%  {status}")

    # Check for categories in data but not in budget config
    for category in category_totals.index:
        if category not in CATEGORY_BUDGETS:
            actual_avg = category_monthly_avg[category]
            print(f"    {category:<16} {format_inr(actual_avg):>12}  {'(no budget)':>12}  {'N/A':>7}  ⚠ Untracked")

    # --- Over-budget warning ---
    if over_budget_categories:
        print(f"\n  ⚠ Over-budget categories: {', '.join(over_budget_categories)}")
        print("    Consider reviewing spending in these areas.")
    else:
        print(f"\n  ✔ All categories are within their budget limits (on average).")

    print("=" * 65)


# ──────────────────────────────────────────────────────────────────────────────
# VISUALIZATIONS
# ──────────────────────────────────────────────────────────────────────────────

def ensure_vis_folder():
    """Create the visualizations folder if it doesn't exist."""
    if not os.path.exists(VIS_FOLDER):
        os.makedirs(VIS_FOLDER)


def setup_chart_style():
    """Apply a consistent, professional look to all charts."""
    plt.rcParams.update({
        "figure.facecolor": "#1e1e2e",
        "axes.facecolor": "#2b2b3d",
        "axes.edgecolor": "#555577",
        "axes.labelcolor": "#e0e0e0",
        "text.color": "#e0e0e0",
        "xtick.color": "#c0c0d0",
        "ytick.color": "#c0c0d0",
        "grid.color": "#3a3a50",
        "grid.alpha": 0.5,
        "font.size": 11,
        "axes.titlesize": 14,
        "axes.titleweight": "bold",
        "figure.titlesize": 16,
        "figure.titleweight": "bold",
    })


def inr_formatter(x, pos):
    """Matplotlib tick formatter for Indian Rupees."""
    if x >= 10000:
        return f"₹{x / 1000:.0f}K"
    return f"₹{x:,.0f}"


def chart_category_bar(df):
    """
    Chart 1: Category-wise Expense Bar Chart
    Shows total expenses across each category as a horizontal bar chart.
    """
    setup_chart_style()

    category_totals = df.groupby("Category")["Amount"].sum().sort_values()

    # Color palette — distinct gradient
    colors = ["#6C5CE7", "#0984E3", "#00CEC9", "#00B894",
              "#FDCB6E", "#E17055", "#D63031", "#E84393"]
    bar_colors = colors[:len(category_totals)]

    fig, ax = plt.subplots(figsize=(10, 6))

    bars = ax.barh(category_totals.index, category_totals.values, color=bar_colors,
                   edgecolor="#1e1e2e", linewidth=1.2, height=0.6)

    # Add value labels on bars
    for bar, value in zip(bars, category_totals.values):
        ax.text(bar.get_width() + 200, bar.get_y() + bar.get_height() / 2,
                format_inr(value), va="center", fontsize=10, color="#e0e0e0")

    ax.set_xlabel("Total Amount (₹)")
    ax.set_title("Category-wise Total Expenses", pad=15)
    ax.xaxis.set_major_formatter(ticker.FuncFormatter(inr_formatter))
    ax.grid(axis="x", linestyle="--")

    plt.tight_layout()
    ensure_vis_folder()
    fig.savefig(os.path.join(VIS_FOLDER, "1_category_bar_chart.png"), dpi=150, bbox_inches="tight")
    print("  ✔ Saved: visualizations/1_category_bar_chart.png")
    plt.show()


def chart_monthly_line(df):
    """
    Chart 2: Monthly Spending Line Chart
    Shows how total expenditure changes over time.
    """
    setup_chart_style()

    monthly_totals = df.groupby("Month")["Amount"].sum()
    month_labels = [str(m) for m in monthly_totals.index]
    values = monthly_totals.values

    fig, ax = plt.subplots(figsize=(10, 6))

    ax.plot(month_labels, values, marker="o", markersize=8, linewidth=2.5,
            color="#00CEC9", markerfacecolor="#FDCB6E", markeredgecolor="#1e1e2e",
            markeredgewidth=2)

    # Fill area under the line
    ax.fill_between(month_labels, values, alpha=0.15, color="#00CEC9")

    # Annotate each point
    for i, (label, val) in enumerate(zip(month_labels, values)):
        ax.annotate(format_inr(val), (label, val),
                    textcoords="offset points", xytext=(0, 14),
                    ha="center", fontsize=9, color="#FDCB6E")

    # Average line
    avg_val = np.mean(values)
    ax.axhline(y=avg_val, color="#E17055", linestyle="--", linewidth=1.2, alpha=0.8)
    ax.text(month_labels[-1], avg_val + 300, f"Avg: {format_inr(avg_val)}",
            color="#E17055", fontsize=9, ha="right")

    ax.set_xlabel("Month")
    ax.set_ylabel("Total Spending (₹)")
    ax.set_title("Monthly Spending Trend", pad=15)
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(inr_formatter))
    ax.grid(True, linestyle="--")

    plt.tight_layout()
    ensure_vis_folder()
    fig.savefig(os.path.join(VIS_FOLDER, "2_monthly_line_chart.png"), dpi=150, bbox_inches="tight")
    print("  ✔ Saved: visualizations/2_monthly_line_chart.png")
    plt.show()


def chart_expense_pie(df):
    """
    Chart 3: Expense Distribution Pie Chart
    Shows the proportion of total spending for each category.
    """
    setup_chart_style()

    category_totals = df.groupby("Category")["Amount"].sum().sort_values(ascending=False)
    total = category_totals.sum()

    colors = ["#6C5CE7", "#0984E3", "#00CEC9", "#00B894",
              "#FDCB6E", "#E17055", "#D63031", "#E84393"]
    pie_colors = colors[:len(category_totals)]

    # Explode the largest slice slightly
    explode = [0.05 if i == 0 else 0 for i in range(len(category_totals))]

    fig, ax = plt.subplots(figsize=(9, 7))

    wedges, texts, autotexts = ax.pie(
        category_totals.values,
        labels=category_totals.index,
        autopct=lambda pct: f"{pct:.1f}%\n({format_inr(pct / 100 * total)})",
        colors=pie_colors,
        explode=explode,
        startangle=140,
        pctdistance=0.75,
        wedgeprops={"edgecolor": "#1e1e2e", "linewidth": 1.5},
    )

    # Style the percentage text
    for autotext in autotexts:
        autotext.set_fontsize(8)
        autotext.set_color("#ffffff")

    for text in texts:
        text.set_fontsize(10)

    ax.set_title("Expense Distribution by Category", pad=20)

    plt.tight_layout()
    ensure_vis_folder()
    fig.savefig(os.path.join(VIS_FOLDER, "3_expense_pie_chart.png"), dpi=150, bbox_inches="tight")
    print("  ✔ Saved: visualizations/3_expense_pie_chart.png")
    plt.show()


def chart_budget_vs_actual(df):
    """
    Chart 4: Budget vs. Actual Spending Chart
    Compares actual expenditure with budget limits for each category.
    """
    setup_chart_style()

    num_months = df["Month"].nunique()
    category_totals = df.groupby("Category")["Amount"].sum()
    category_monthly_avg = category_totals / num_months

    # Only chart categories that have a defined budget
    budget_categories = sorted(CATEGORY_BUDGETS.keys())
    budget_vals = [CATEGORY_BUDGETS[c] for c in budget_categories]
    actual_vals = [category_monthly_avg.get(c, 0) for c in budget_categories]

    x = np.arange(len(budget_categories))
    width = 0.35

    fig, ax = plt.subplots(figsize=(11, 6))

    bars_budget = ax.bar(x - width / 2, budget_vals, width, label="Budget",
                         color="#0984E3", edgecolor="#1e1e2e", linewidth=1)
    bars_actual = ax.bar(x + width / 2, actual_vals, width, label="Actual (Avg/Month)",
                         color="#E17055", edgecolor="#1e1e2e", linewidth=1)

    # Highlight over-budget bars
    for i, (bv, av) in enumerate(zip(budget_vals, actual_vals)):
        if av > bv:
            bars_actual[i].set_color("#D63031")
            bars_actual[i].set_edgecolor("#FDCB6E")
            bars_actual[i].set_linewidth(2)

    # Value labels
    for bar in bars_budget:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2, height + 100,
                format_inr(height), ha="center", va="bottom", fontsize=8, color="#74b9ff")

    for bar in bars_actual:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width() / 2, height + 100,
                format_inr(height), ha="center", va="bottom", fontsize=8, color="#fab1a0")

    ax.set_xlabel("Category")
    ax.set_ylabel("Amount (₹)")
    ax.set_title("Budget vs. Actual Spending (Monthly Average)", pad=15)
    ax.set_xticks(x)
    ax.set_xticklabels(budget_categories, rotation=30, ha="right")
    ax.yaxis.set_major_formatter(ticker.FuncFormatter(inr_formatter))
    ax.legend(loc="upper right", framealpha=0.7)
    ax.grid(axis="y", linestyle="--")

    plt.tight_layout()
    ensure_vis_folder()
    fig.savefig(os.path.join(VIS_FOLDER, "4_budget_vs_actual.png"), dpi=150, bbox_inches="tight")
    print("  ✔ Saved: visualizations/4_budget_vs_actual.png")
    plt.show()


def generate_all_charts(df):
    """Generate and display all four visualizations."""
    print("\n  📊 Generating all visualizations...\n")
    chart_category_bar(df)
    chart_monthly_line(df)
    chart_expense_pie(df)
    chart_budget_vs_actual(df)
    print(f"\n  ✔ All charts saved to '{VIS_FOLDER}/'")


# ──────────────────────────────────────────────────────────────────────────────
# MAIN MENU
# ──────────────────────────────────────────────────────────────────────────────

def print_banner():
    """Print the application header."""
    print("\n" + "═" * 65)
    print("        💸  PERSONAL EXPENSE ANALYZER  💸")
    print("        ─────────────────────────────────")
    print("        Analyze · Compare · Visualize")
    print("═" * 65)


def print_menu():
    """Print the main menu options."""
    print("\n  ┌─────────────────────────────────────┐")
    print("  │          MAIN MENU                  │")
    print("  ├─────────────────────────────────────┤")
    print("  │  1. View Expense Summary            │")
    print("  │  2. View Category-wise Analysis     │")
    print("  │  3. View Monthly Spending Trends    │")
    print("  │  4. Analyze Budget Usage            │")
    print("  │  5. Generate All Visualizations     │")
    print("  │  6. Exit                            │")
    print("  └─────────────────────────────────────┘")


def main():
    """Main function — loads data and runs the interactive menu loop."""
    print_banner()

    # Load and validate data
    df = load_expense_data(CSV_FILE)
    if df is None:
        print("\n  Cannot proceed without valid data. Exiting.")
        sys.exit(1)

    # Menu loop
    while True:
        print_menu()
        choice = input("\n  Enter your choice (1-6): ").strip()

        if choice == "1":
            show_expense_summary(df)
        elif choice == "2":
            show_category_analysis(df)
        elif choice == "3":
            show_monthly_trends(df)
        elif choice == "4":
            show_budget_analysis(df)
        elif choice == "5":
            generate_all_charts(df)
        elif choice == "6":
            print("\n  👋 Thank you for using Personal Expense Analyzer!")
            print("  Goodbye!\n")
            break
        else:
            print("\n  ⚠ Invalid choice. Please enter a number from 1 to 6.")


# ──────────────────────────────────────────────────────────────────────────────
# ENTRY POINT
# ──────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    main()
