# Personal Expense Analyzer — Presentation & Viva Script
## Walkthrough of NumPy, Pandas, and Matplotlib Use-Cases

> **How to use this guide:**  
> Use this script during your presentation or viva. It tells you **what to say**, **which file to open**, **which lines to point to**, and **why that library was chosen**.

---

## 🎙️ 1-Minute Introduction (Opening Speech)

> *"Good morning/afternoon respected professors and examiners.*  
>  
> *Today I am presenting my project: the **Personal Expense Analyzer**.*  
> *The objective of this project is to provide automated financial analytics, budget tracking, and visual insights into personal spending habits.*  
>  
> *To keep the architecture clean and performant, the entire project is built using only three foundational Python data science libraries:*  
> 1. ***Pandas*** — *for data loading, automated data cleaning, datetime engineering, and grouping.*  
> 2. ***NumPy*** — *for high-performance numerical computing, statistical calculations, percentiles, and coordinate array math.*  
> 3. ***Matplotlib*** — *for data visualization across four distinct chart types, as well as headless base64 rendering for our interactive web dashboard served on localhost.*  
>  
> *Let me walk you through exactly where and how each library is utilized in our codebase."*

---

## 🐼 Library 1: Pandas (`pd`) — Data Wrangling & Aggregation

### 🗣️ What to Say:
> *"Pandas is the data backbone of the application. It handles everything from CSV ingestion and data sanitization to complex relational grouping."*

### 📍 Where it is in the Code:

| Feature / Use-Case | File & Location | Code Snippet | What it Does & Why Pandas was Used |
| :--- | :--- | :--- | :--- |
| **1. Data Ingestion** | [`main.py` (Line 105)](file:///home/neerad/Desktop/python_project_2/main.py#L105) | `df = pd.read_csv(filepath)` | Reads the CSV into a DataFrame in a single step instead of writing manual file-reading loops. |
| **2. Column Validation** | [`main.py` (Line 111)](file:///home/neerad/Desktop/python_project_2/main.py#L111) | `set(REQUIRED_COLUMNS).issubset(df.columns)` | Uses DataFrame column indexing to guarantee the CSV contains required headers (`Date`, `Category`, `Amount`, `Description`). |
| **3. Type Coercion & Sanitization** | [`main.py` (Lines 125, 132)](file:///home/neerad/Desktop/python_project_2/main.py#L125-L132) | `df["Date"] = pd.to_datetime(...)`<br>`df["Amount"] = pd.to_numeric(..., errors="coerce")` | `errors="coerce"` turns malformed strings or invalid dates into `NaN` so the program never crashes on dirty data. |
| **4. Missing & Corrupted Data Handling** | [`main.py` (Lines 126, 133)](file:///home/neerad/Desktop/python_project_2/main.py#L126-L133) | `df["Date"].isna().sum()`<br>`df = df.dropna(...)` | Detects nulls using boolean series and drops corrupt records cleanly. |
| **5. Boolean Masking / Outlier Filtering** | [`main.py` (Line 141)](file:///home/neerad/Desktop/python_project_2/main.py#L141) | `df = df[df["Amount"] > 0]` | Filters out negative or zero amounts using vector boolean filtering. |
| **6. Datetime Feature Engineering** | [`main.py` (Lines 149–150)](file:///home/neerad/Desktop/python_project_2/main.py#L149-L150) | `df["Month"] = df["Date"].dt.to_period("M")`<br>`df["MonthName"] = df["Date"].dt.strftime("%b %Y")` | Uses the `.dt` accessor to extract monthly periods (e.g. `2026-01`) for time-series aggregation. |
| **7. GroupBy Aggregations** | [`main.py` (Lines 208, 222, 285)](file:///home/neerad/Desktop/python_project_2/main.py#L208) | `df.groupby("Category")["Amount"].sum()`<br>`df.groupby("Month")["Amount"].sum()` | The Split-Apply-Combine pattern: groups rows by Category or Month and aggregates total spending. |
| **8. Extremum Row Lookups** | [`main.py` (Lines 195–196)](file:///home/neerad/Desktop/python_project_2/main.py#L195-L196) | `df.loc[df["Amount"].idxmax()]`<br>`df.loc[df["Amount"].idxmin()]` | `idxmax()` and `idxmin()` find the exact row index of the highest and lowest expense transactions. |
| **9. Month-over-Month Delta Analysis** | [`main.py` (Line 290)](file:///home/neerad/Desktop/python_project_2/main.py#L290) | `monthly_totals.pct_change() * 100` | Calculates percentage growth or reduction in spending between consecutive months. |

---

## 🔢 Library 2: NumPy (`np`) — Numerical & Statistical Computation

### 🗣️ What to Say:
> *"While Pandas structures our tables, NumPy powers the mathematical and statistical core of the project. We convert Pandas Series directly into NumPy C-arrays (`df['Amount'].values`) for optimized numeric calculations."*

### 📍 Where it is in the Code:

| Feature / Use-Case | File & Location | Code Snippet | What it Does & Why NumPy was Used |
| :--- | :--- | :--- | :--- |
| **1. Series to Array Conversion** | [`main.py` (Line 174)](file:///home/neerad/Desktop/python_project_2/main.py#L174) | `amounts = df["Amount"].values` | Extracts raw contiguous memory 1D NumPy array for fast mathematical operations. |
| **2. Fundamental Statistics** | [`main.py` (Lines 177–182)](file:///home/neerad/Desktop/python_project_2/main.py#L177-L182) | `total = np.sum(amounts)`<br>`average = np.mean(amounts)`<br>`median = np.median(amounts)`<br>`highest = np.max(amounts)`<br>`lowest = np.min(amounts)` | Computes central tendency and extremes using vectorized functions rather than manual iteration. |
| **3. Variance & Standard Deviation** | [`main.py` (Line 180)](file:///home/neerad/Desktop/python_project_2/main.py#L180) | `std_dev = np.std(amounts)` | Measures transaction spending volatility and dispersion around the mean. |
| **4. Quartile & Percentile Distribution** | [`main.py` (Lines 256–257)](file:///home/neerad/Desktop/python_project_2/main.py#L256-L257) | `q25 = np.percentile(cat_amounts, 25)`<br>`q75 = np.percentile(cat_amounts, 75)` | Computes the 25th (Q1) and 75th (Q3) percentiles to determine the Interquartile Range (IQR) for spending in each category. |
| **5. Cross-Period Mean Benchmark** | [`main.py` (Line 349, 523)](file:///home/neerad/Desktop/python_project_2/main.py#L349) | `avg_monthly_spend = np.mean(monthly_totals.values)` | Calculates overall monthly baseline to draw benchmark threshold lines in plots. |
| **6. Coordinate Vector Math for Multi-Bar Charts** | [`main.py` (Line 604)](file:///home/neerad/Desktop/python_project_2/main.py#L604) | `x = np.arange(len(budget_categories))` | Generates an evenly spaced array of indices `[0, 1, 2, ...]` to allow offsetting bars: `x - width/2` (Actual) and `x + width/2` (Budget) side by side. |

---

## 📊 Library 3: Matplotlib (`plt`) — Visualizations & Dashboard Engine

### 🗣️ What to Say:
> *"For visualization, we used Matplotlib to create four distinct, publication-grade charts. We also used Matplotlib in a headless configuration to generate base64 images that render directly inside our standalone web dashboard."*

### 📍 Where it is in the Code:

| Feature / Use-Case | File & Location | Code Snippet | What it Does & Why Matplotlib was Used |
| :--- | :--- | :--- | :--- |
| **1. Global Style Customization** | [`main.py` (Lines 435–458)](file:///home/neerad/Desktop/python_project_2/main.py#L435-L458) | `plt.rcParams.update({...})` | Configures dark theme (`#1a1a2e`), font sizes, grid opacity, tick colors, and canvas paddings for visual consistency. |
| **2. Horizontal Bar Chart (Category Breakdown)** | [`main.py` (Lines 465–494)](file:///home/neerad/Desktop/python_project_2/main.py#L465-L494) | `fig, ax = plt.subplots(...)`<br>`bars = ax.barh(...)`<br>`ax.bar_label(...)` | `barh()` displays category totals sorted by size. `bar_label()` adds automatic currency text tags directly on the bars. |
| **3. Time-Series Line Plot (Monthly Trend)** | [`main.py` (Lines 501–539)](file:///home/neerad/Desktop/python_project_2/main.py#L501-L539) | `ax.plot(months, values, marker="o")`<br>`ax.axhline(avg_val, linestyle="--")`<br>`ax.annotate(...)` | Plots spending trajectory over time; `axhline` adds a 6-month average reference line; `annotate()` marks highest and lowest spending points. |
| **4. Donut Pie Chart (Expense Share)** | [`main.py` (Lines 546–586)](file:///home/neerad/Desktop/python_project_2/main.py#L546-L586) | `ax.pie(..., explode=..., autopct=...)`<br>`donut = plt.Circle((0,0), 0.55, ...)` | Displays percentage distribution of expenses. Explodes the highest category slice; adds a center circle patch to create a modern donut chart. |
| **5. Grouped Dual-Series Bar Chart (Budget vs Actual)** | [`main.py` (Lines 593–646)](file:///home/neerad/Desktop/python_project_2/main.py#L593-L646) | `ax.bar(x - w/2, actuals, ...)`<br>`ax.bar(x + w/2, budgets, ...)`<br>`ax.set_xticks(x)` | Plots actual spending directly against monthly budget limits side-by-side with color-coded variances. |
| **6. Number Formatting with Tickers** | [`main.py` (Lines 484, 529, 631)](file:///home/neerad/Desktop/python_project_2/main.py#L484) | `ax.yaxis.set_major_formatter(ticker.FuncFormatter(...))` | Formats raw axis numbers into Indian Rupee labels (`₹10k`, `₹20k`). |
| **7. High-Resolution File Export** | [`main.py` (Lines 491, 536, 583, 643)](file:///home/neerad/Desktop/python_project_2/main.py#L491) | `fig.savefig(filepath, dpi=150, bbox_inches="tight")` | Automatically saves all charts into the `visualizations/` directory. |
| **8. Headless Web Rendering (Dashboard)** | [`dashboard.py` (Lines 21, 57–67)](file:///home/neerad/Desktop/python_project_2/dashboard.py#L21) | `matplotlib.use("Agg")`<br>`buf = io.BytesIO()`<br>`base64.b64encode(buf.getvalue())` | Switches backend to `Agg` (non-interactive) so Matplotlib runs in the background, writes charts to RAM, and encodes them into Base64 strings for the HTML dashboard. |

---

## 🌐 4. Bonus Architecture: Python Standard Library Localhost Server

> *"In addition to the three core data science libraries, we utilized Python's built-in `http.server` and `webbrowser` in [`dashboard.py`](file:///home/neerad/Desktop/python_project_2/dashboard.py):*
> - *Generates a self-contained modern HTML/CSS dashboard with KPI cards and tab navigation.*
> - *Spawns an asynchronous localhost HTTP server on port `8050`.*
> - *Displays the clickable link in the terminal and automatically opens the user's browser, without needing any heavy web frameworks like Flask or Django."*

---

## 🎯 5. Examiner Q&A Cheat Sheet (Top Viva Questions)

### Q1: Why did you use both NumPy and Pandas? Isn't Pandas enough?
> **Answer:**  
> *"Pandas is built on top of NumPy. While Pandas is superior for tabular operations, indexing, and grouping, NumPy provides raw C-level performance on numeric arrays (`df['Amount'].values`). Furthermore, NumPy offers specialized mathematical routines like `np.percentile()` for quartile distribution analysis, and `np.arange()` for coordinate generation when calculating offsets for side-by-side bar charts."*

### Q2: How did you handle bad, missing, or negative values?
> **Answer:**  
> *"In `load_expense_data()` in [`main.py`](file:///home/neerad/Desktop/python_project_2/main.py#L100), we used `pd.to_datetime(..., errors='coerce')` and `pd.to_numeric(..., errors='coerce')`. Any corrupted text is converted to `NaN`. We then report the number of bad records using `.isna().sum()` and drop them using `.dropna()`. Finally, we use boolean indexing `df[df['Amount'] > 0]` to discard negative amounts."*

### Q3: How do the two bars sit side-by-side in the Budget vs Actual chart?
> **Answer:**  
> *"In [`main.py` line 604](file:///home/neerad/Desktop/python_project_2/main.py#L604), we generate index coordinates using `x = np.arange(len(categories))`. We set a bar width (e.g. `width = 0.38`). The Actual spending bars are drawn at `x - width/2`, and the Budget bars are drawn at `x + width/2`. We then place the x-axis tick labels at `x` using `ax.set_xticks(x)`."*

### Q4: How does `dashboard.py` embed Matplotlib charts inside HTML?
> **Answer:**  
> *"We set `matplotlib.use('Agg')` for headless execution. Instead of saving image files to disk and linking them, we save the plot into an in-memory buffer using `io.BytesIO()`. Then we encode that binary buffer into a Base64 string using `base64.b64encode()` and embed it directly into the HTML `<img src='data:image/png;base64,...'>` tag. This creates a completely portable, single-file dashboard."*

---

## 🎬 Live Demonstration Steps to Show the Examiner

1. **Terminal 1 — CLI Analysis & Visualizations:**
   ```bash
   python main.py
   ```
   - Press `1` -> Show NumPy statistical summary (Total, Mean, Median, Std Dev, Min, Max).
   - Press `2` -> Show Pandas category grouping & NumPy quartiles (Q1, Q3).
   - Press `4` -> Show Budget utilization calculations.
   - Press `5` -> Show all 4 Matplotlib charts popping up and saving to `visualizations/`.
   - Press `6` -> Exit cleanly.

2. **Terminal 2 — Web Dashboard:**
   ```bash
   python dashboard.py
   ```
   - Show the localhost link printed: `http://localhost:8050/`.
   - Show the browser opening automatically with KPI cards, interactive tabs, and embedded Matplotlib charts!
