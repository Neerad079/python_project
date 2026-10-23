# 💸 Personal Expense Analyzer

A beginner-friendly Python project that helps users understand their spending habits by analyzing monthly expenses, comparing spending against budgets, and generating professional data visualizations.

---

## 📋 Table of Contents

- [Features](#-features)
- [Project Structure](#-project-structure)
- [Prerequisites](#-prerequisites)
- [Installation & Setup](#-installation--setup)
- [How to Run](#-how-to-run)
- [Usage Guide](#-usage-guide)
- [Libraries Used](#-libraries-used)
- [Sample Output](#-sample-output)
- [Visualizations](#-visualizations)
- [Presentation Outline](#-presentation-outline)
- [Viva Questions & Answers](#-viva-questions--answers)

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| **Expense Summary** | View total expenditure, average per transaction, highest/lowest expenses, and category-wise & month-wise totals |
| **Category Analysis** | Detailed breakdown with statistics (total, avg, min, max, percentiles) for each category |
| **Monthly Trends** | Track spending changes over time with percentage change calculations |
| **Budget Analysis** | Compare actual spending vs. configured budgets with utilization percentages |
| **Visualizations** | Four professional charts — bar, line, pie, and budget comparison |
| **Data Validation** | Automatic handling of missing values, invalid dates, and bad amounts |
| **INR Formatting** | All monetary values displayed in Indian Rupee format (₹) |

---

## 📁 Project Structure

```
Personal-Expense-Analyzer/
│
├── main.py               # Main application — menu, analysis, and charts
├── dashboard.py          # HTML dashboard generator (opens in browser)
├── expense_data.csv      # Sample expense records (6 months of data)
├── requirements.txt      # Python dependencies (NumPy, Pandas, Matplotlib)
├── README.md             # Project documentation (this file)
├── dashboard.html        # Auto-generated dashboard (open in browser)
└── visualizations/       # Auto-created folder for saved chart images
    ├── 1_category_bar_chart.png
    ├── 2_monthly_line_chart.png
    ├── 3_expense_pie_chart.png
    └── 4_budget_vs_actual.png
```

---

## 🛠 Prerequisites

- **Python 3.7** or higher
- **pip** (Python package manager)

---

## 📦 Installation & Setup

1. **Clone or download** this project to your local machine.

2. **Open a terminal** and navigate to the project folder:
   ```bash
   cd Personal-Expense-Analyzer
   ```

3. **Install the required libraries:**
   ```bash
   pip install -r requirements.txt
   ```
   This installs NumPy, Pandas, and Matplotlib — no other libraries are needed.

---

## ▶ How to Run

```bash
python main.py
```

The program will:
1. Load and validate `expense_data.csv`
2. Display an interactive menu
3. Let you explore summaries, trends, budgets, and charts

---

## 📖 Usage Guide

When you run the program, you'll see a menu:

```
  ┌─────────────────────────────────────┐
  │          MAIN MENU                  │
  ├─────────────────────────────────────┤
  │  1. View Expense Summary            │
  │  2. View Category-wise Analysis     │
  │  3. View Monthly Spending Trends    │
  │  4. Analyze Budget Usage            │
  │  5. Generate All Visualizations     │
  │  6. Exit                            │
  └─────────────────────────────────────┘
```

- **Option 1:** Shows total spending, averages, highest/lowest transactions, category totals, and monthly totals.
- **Option 2:** Provides per-category statistics including percentiles.
- **Option 3:** Shows month-over-month spending changes with percentage differences.
- **Option 4:** Compares your actual spending against the configured budgets.
- **Option 5:** Generates and saves all four charts to the `visualizations/` folder.
- **Option 6:** Exits the program.

### Web Dashboard (Localhost Link)

To open the interactive browser dashboard, run:
```bash
python dashboard.py
```
This generates the dashboard and starts a local web server, opening:
```
👉 http://localhost:8050/
```
You can also directly click the link printed in the terminal or copy-paste it into any web browser. Press `Ctrl+C` to stop the server when done.

### Customizing Budgets

Open `main.py` and edit the configuration section at the top:

```python
MONTHLY_BUDGET = 35000

CATEGORY_BUDGETS = {
    "Food": 8000,
    "Transport": 3000,
    "Shopping": 5000,
    "Education": 4000,
    "Entertainment": 3000,
    "Utilities": 4000,
    "Rent": 12000,
}
```

### Using Your Own Data

Replace `expense_data.csv` with your own file. Keep the same format:

```csv
Date,Category,Description,Amount
2026-01-03,Food,Grocery shopping,2450
```

---

## 📚 Libraries Used

### NumPy (Numerical Python)
- **Purpose:** Efficient numerical computations and statistical analysis.
- **Usage in project:**
  - `np.sum()`, `np.mean()`, `np.median()`, `np.std()` — for expense statistics
  - `np.min()`, `np.max()` — finding extreme values
  - `np.percentile()` — calculating 25th and 75th percentiles per category
  - `np.arange()` — generating evenly spaced values for bar chart positioning
  - NumPy arrays used internally for vectorized calculations

### Pandas (Python Data Analysis Library)
- **Purpose:** Loading, cleaning, filtering, grouping, and summarizing structured data.
- **Usage in project:**
  - `pd.read_csv()` — reading expense data from CSV
  - `pd.to_datetime()` — converting and validating date strings
  - `pd.to_numeric()` — validating and converting amounts
  - `df.dropna()` — handling missing values
  - `df.groupby()` — category-wise and month-wise aggregations
  - `df.sort_values()` — ordering data chronologically
  - `dt.to_period()`, `dt.strftime()` — extracting month information

### Matplotlib (Plotting Library)
- **Purpose:** Creating professional, publication-quality charts.
- **Usage in project:**
  - Horizontal bar chart for category-wise expenses
  - Line chart with area fill for monthly spending trends
  - Pie chart with percentage labels for expense distribution
  - Grouped bar chart for budget vs. actual comparison
  - Custom dark theme, INR formatting, annotations, and legends

---

## 📊 Sample Output

### Expense Summary (Option 1)
```
=================================================================
              📊  EXPENSE SUMMARY REPORT
=================================================================

  Total Expenditure          : ₹1,87,649.00
  Number of Transactions     : 90
  Average per Transaction    : ₹2,085.00
  Median Expense             : ₹1,100.00
  Standard Deviation         : ₹2,386.10

  💰 Highest Expense         : ₹12,000.00
     → Monthly house rent (Rent)
  💸 Lowest Expense          : ₹119.00
     → Spotify subscription (Entertainment)

-----------------------------------------------------------------
  Category-wise Total Expenditure
-----------------------------------------------------------------
    Rent              ₹72,000.00   (38.4%)
    Food              ₹44,370.00   (23.6%)
    Shopping          ₹21,000.00   (11.2%)
    ...
=================================================================
```

---

## 📈 Visualizations

The program generates four professional charts with a dark theme:

| Chart | Description |
|-------|-------------|
| **Category Bar Chart** | Horizontal bars comparing total spending across categories |
| **Monthly Line Chart** | Line plot showing spending trends over 6 months with average line |
| **Expense Pie Chart** | Proportional breakdown of spending by category |
| **Budget vs. Actual** | Side-by-side comparison of budget limits and actual spending |

Charts are automatically saved to the `visualizations/` folder as PNG images.

---

## 🎓 Presentation Outline

### Slide 1: Title Slide
- **Title:** Personal Expense Analyzer
- **Subtitle:** A Python-based Data Analysis Project
- **Name, Course, Date**

### Slide 2: Problem Statement
- Managing personal finances is challenging without proper tracking
- Manual calculations are error-prone and time-consuming
- Need for automated analysis and visual insights

### Slide 3: Objectives
- Develop a tool to load, clean, and analyze expense data
- Calculate meaningful financial statistics
- Compare spending against budgets
- Generate professional visualizations

### Slide 4: Methodology
- Data loaded from CSV using Pandas
- Data cleaning: handle missing values, validate dates/amounts
- Statistical analysis using NumPy
- Grouping and aggregation using Pandas
- Visualization using Matplotlib

### Slide 5: Implementation
- Menu-driven CLI application
- Modular function design
- Configuration-based budgets
- Dark-themed professional charts

### Slide 6: Results & Demo
- Live demonstration of all features
- Show each visualization
- Explain insights derived from the data

### Slide 7: Limitations
- No database storage (uses CSV files)
- No graphical user interface
- Budget configuration requires editing source code
- No multi-user or authentication support

### Slide 8: Future Scope
- Add a GUI using Tkinter
- Store data in SQLite database
- Export reports as PDF
- Add support for income tracking

### Slide 9: Conclusion
- Successfully demonstrates data analysis with Python
- Practical use of NumPy, Pandas, and Matplotlib
- Clean, modular, and easy-to-understand code

---

## ❓ Viva Questions & Answers

### About the Project

**Q1: What is the purpose of this project?**
> This project helps users analyze their personal expenses by loading transaction data, computing statistics, comparing spending against budgets, and generating visualizations — all using Python.

**Q2: Why did you use a CSV file instead of a database?**
> CSV files are simple, human-readable, and don't require any additional software. For a project of this scope, CSV is sufficient and keeps the setup straightforward.

**Q3: How does the program handle missing or invalid data?**
> The program uses `dropna()` to remove rows with missing values, `pd.to_datetime()` with `errors='coerce'` to handle invalid dates, and `pd.to_numeric()` with `errors='coerce'` to handle non-numeric amounts. All invalid rows are removed with warning messages.

**Q4: How is the budget comparison done?**
> Total spending per category is divided by the number of months to get a monthly average. This average is compared against the configured budget for each category to determine if spending is within or over budget.

**Q5: Can this project work with different data?**
> Yes. Users can replace `expense_data.csv` with their own data, as long as it follows the same format (Date, Category, Description, Amount columns).

### About NumPy

**Q6: What is NumPy and why is it used here?**
> NumPy (Numerical Python) is a library for efficient numerical computation. It provides fast array operations. We use it for calculating sum, mean, median, standard deviation, percentiles, and for generating array indices for chart positioning.

**Q7: What is the difference between a Python list and a NumPy array?**
> NumPy arrays are homogeneous (same data type), stored in contiguous memory, and support vectorized operations — making them much faster for numerical calculations than Python lists.

**Q8: What does `np.percentile()` do?**
> It calculates the value below which a given percentage of data falls. For example, `np.percentile(data, 25)` returns the value below which 25% of the data points lie (the first quartile).

### About Pandas

**Q9: What is a DataFrame in Pandas?**
> A DataFrame is a two-dimensional, labeled data structure with rows and columns — similar to a spreadsheet or SQL table. Each column can have a different data type.

**Q10: Explain `groupby()` in Pandas.**
> `groupby()` splits data into groups based on a column's values, applies an aggregation function (like `sum()` or `mean()`) to each group, and combines the results. For example, `df.groupby("Category")["Amount"].sum()` gives total spending per category.

**Q11: What does `pd.to_datetime()` do?**
> It converts strings to datetime objects. The `errors='coerce'` parameter converts invalid date strings to `NaT` (Not a Time) instead of raising an error, which we can then filter out.

**Q12: How does `dropna()` work?**
> `dropna()` removes rows (or columns) that contain missing values (`NaN`). The `subset` parameter lets you specify which columns to check for missing values.

### About Matplotlib

**Q13: What is Matplotlib and what types of charts did you use?**
> Matplotlib is a plotting library for creating static, animated, and interactive visualizations. We used bar charts, line charts, pie charts, and grouped bar charts.

**Q14: What is the difference between `plt.plot()` and `plt.bar()`?**
> `plt.plot()` creates a line chart connecting data points, useful for showing trends. `plt.bar()` creates a bar chart with rectangles, useful for comparing quantities across categories.

**Q15: What is `plt.tight_layout()` used for?**
> It automatically adjusts subplot parameters so that labels, titles, and tick marks don't overlap or get cut off at the edges of the figure.

**Q16: How do you save a chart as an image?**
> Using `fig.savefig('filename.png', dpi=150)`. The `dpi` parameter controls the resolution (dots per inch) of the saved image.

### General Python

**Q17: What is the `if __name__ == "__main__":` pattern?**
> It ensures that the `main()` function runs only when the script is executed directly, not when it's imported as a module by another script.

**Q18: What is error handling and how is it used here?**
> Error handling uses `try-except` blocks to catch and manage runtime errors gracefully. We use it when reading the CSV file to display a helpful message instead of crashing if the file is corrupted.

**Q19: What is the advantage of using functions in this project?**
> Functions make the code modular, reusable, and easier to understand. Each function has a single responsibility (e.g., one for loading data, one for budget analysis), which makes the code easier to test and maintain.

**Q20: How would you extend this project?**
> Possible extensions include: adding a GUI with Tkinter, storing data in an SQLite database, supporting multiple users, adding income tracking, generating PDF reports, or building a web interface with Flask.

---

## 📄 License

This project is created for educational purposes. Free to use and modify.
