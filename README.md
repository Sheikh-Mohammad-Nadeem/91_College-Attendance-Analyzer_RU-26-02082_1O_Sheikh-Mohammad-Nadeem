# 🎓 College Attendance Analyzer

A complete, beginner-friendly, menu-driven Python console application designed to analyze college attendance records, enforce the mandatory 75% attendance rule, calculate subject-wise averages, and generate visual analytics charts using **Pandas** and **Matplotlib**.

---

## 📌 Project Overview

In universities and colleges, attendance tracking is a critical academic requirement. Students must maintain a minimum attendance of **75.00%** to be eligible for semester examinations. 

This project provides an automated, menu-driven tool that reads student attendance records from a standard CSV file, validates the data thoroughly (skipping corrupted rows without crashing), calculates individual and subject-wise metrics, and visualizes the results with clean, publication-ready charts.

---

## 🛠️ Technology Stack

| Technology | Purpose |
|---|---|
| **Python 3** | Core programming language |
| **Pandas** | High-performance CSV reading, data cleaning, aggregation, and boolean filtering |
| **Matplotlib** | Data visualization (bar charts and pie charts) |
| **CSV** | Plaintext, lightweight input data format |
| **Standard Library** | `os`, `sys`, `tempfile` for file and system management |

> **Note**: This application is strictly console-based and lightweight. It requires no databases, web frameworks (like Flask/Django/Streamlit), or complex dependencies.

---

## 📂 Project Folder Structure

```text
College-Attendance-Analyzer/
│
├── main.py                     # Main menu-driven application logic
├── attendance.csv              # Input CSV data file
├── requirements.txt            # Project dependencies (pandas, matplotlib)
├── README.md                   # Comprehensive documentation and guide
├── .gitignore                  # Git ignore rules for Python & OS files
├── test_analyzer.py            # Automated test suite for all university test cases
│
├── charts/                     # Generated visualization charts (PNG)
│   ├── student_attendance_bar_chart.png
│   ├── subject_attendance_bar_chart.png
│   └── attendance_eligibility_pie_chart.png
│
└── output/                     # Exported text summary reports
    └── attendance_report.txt
```

---

## 🚀 Installation & Setup

### Prerequisites
Make sure you have **Python 3.8+** installed on your system. Check your version with:
```bash
python3 --version
```

### Step 1: Navigate to the Project Directory
```bash
cd ~/Documents/Projects/91_College-Attendance-Analyzer_RU-26-02082_10_Sheikh-Mohammad-Nadeem
```

### Step 2: (Recommended) Create and Activate a Virtual Environment
```bash
# On macOS / Linux:
python3 -m venv venv
source venv/bin/activate

# On Windows:
python -m venv venv
venv\Scripts\activate
```

### Step 3: Install Required Dependencies
```bash
pip install -r requirements.txt
```

---

## 💻 How to Run the Application

### Standard Execution
Run the script using the default `attendance.csv`:
```bash
python3 main.py
```

### Custom CSV Execution
You can also analyze any custom CSV file by passing its path as a command-line argument:
```bash
python3 main.py path/to/my_attendance.csv
```

---

## 📋 CSV File Structure

The input file `attendance.csv` must contain a header row with the following exact column names:

```csv
Name,Subject,Classes_Held,Classes_Attended
Aman,Python,40,36
Riya,Python,40,28
Karan,Python,40,30
Aman,Maths,50,45
Riya,Maths,50,32
Karan,Maths,50,42
Neha,Python,40,38
Neha,Maths,50,35
Rahul,Python,40,15
Rahul,Maths,50,20
```

### Columns:
1. `Name`: Student's name (string).
2. `Subject`: Academic subject or course title (string).
3. `Classes_Held`: Total number of lecture/lab sessions conducted (positive number > 0).
4. `Classes_Attended`: Number of sessions attended by the student ($\le$ Classes Held).

---

## 🧮 Mathematical Formulas & Eligibility Rules

### 1. Attendance Percentage Formula
$$\text{Attendance Percentage} = \left(\frac{\text{Classes Attended}}{\text{Classes Held}}\right) \times 100$$

### 2. Eligibility Criteria
- **Minimum Threshold**: **75.00%**
- **Above 75.00%**: **Eligible** (Allowed to sit for examinations).
- **Exactly 75.00%**: **Eligible** (Meets boundary threshold).
- **Below 75.00%**: **Shortage / Not Eligible** (Debarred / Requires condonation).

### 3. Multi-Subject Overall Student Attendance
When a student has records across multiple subjects:
$$\text{Overall Attendance \%} = \left(\frac{\sum \text{Classes Attended}}{\sum \text{Classes Held}}\right) \times 100$$

---

## 🛡️ Input Validation & Fault Tolerance

The application incorporates robust validation to ensure it **never crashes** due to bad input data. Invalid records are reported with clear explanations and skipped:

| Validation Rule | Condition Checked | Action Taken |
|---|---|---|
| **Missing File** | File does not exist on disk | Displays error message and prompts user |
| **Empty File** | File has 0 bytes or 0 data rows | Skips processing safely |
| **Missing Columns** | Required headers missing | Reports missing columns and aborts |
| **Empty Values** | Name or Subject is blank/whitespace | `Row X invalid: student name cannot be empty. Row skipped.` |
| **Non-Numeric Data** | String passed instead of number | `Row X invalid: numeric value expected for Classes_Held and Classes_Attended. Row skipped.` |
| **Negative Numbers** | Values $< 0$ | `Row X invalid: attendance values cannot be negative. Row skipped.` |
| **Zero Classes Held** | `Classes_Held == 0` | `Row X invalid: Classes_Held cannot be zero (division by zero). Row skipped.` |
| **Excess Attendance** | `Classes_Attended > Classes_Held` | `Row X invalid: attended (X) cannot exceed held (Y). Row skipped.` |

---

## 🖥️ Menu Options Walkthrough

When you start `main.py`, you are presented with an interactive menu:

```text
=================================================================
                 COLLEGE ATTENDANCE ANALYZER
=================================================================
  1. Calculate & Display Attendance Percentage (All Students)
  2. Display Students Below 75% Attendance (Shortage)
  3. Calculate & Display Subject-Wise Average Attendance
  4. Generate Attendance Bar Chart
  5. Generate Attendance Pie Chart
  6. Exit the Application
=================================================================
Enter your choice (1-6):
```

### Option 1: Display Attendance Percentage of Every Student
- Computes each student's total classes held, attended, overall percentage formatted to **2 decimal places**, and eligibility status.
- Displays a clean ASCII table with a subject-wise breakdown for each student.

### Option 2: Display Students Below 75% Attendance (Shortage)
- Uses Pandas **boolean indexing** (`df[df["Attendance_Percentage"] < 75.0]`) to filter students who do not meet the minimum requirement.
- Calculates the exact number of additional classes each student needed to reach 75%.
- If all students meet the requirement, prints: `✓ No students below 75%. All students are eligible!`.

### Option 3: Calculate & Display Subject-Wise Average Attendance
- Groups data by `Subject` using Pandas `groupby()`.
- Calculates the mean attendance percentage across all students enrolled in each subject.

### Option 4: Generate Attendance Bar Chart
- Generates a bar chart where each bar represents a student's attendance percentage.
- **Color-coded**: Green (`#27ae60`) for eligible ($\ge 75\%$), Red (`#e74c3c`) for shortage ($< 75\%$).
- Displays a horizontal dashed threshold line at 75%.
- Adds numeric percentage labels directly above each bar.
- Also saves a subject-wise bar chart.
- Saved to: `charts/student_attendance_bar_chart.png` and `charts/subject_attendance_bar_chart.png`.

### Option 5: Generate Attendance Pie Chart
- Visualizes the proportion of eligible students vs students with attendance shortage.
- Uses distinct colors, exploded slices, and percentage callouts.
- Saved to: `charts/attendance_eligibility_pie_chart.png`.

### Option 6: Exit the Application
- Automatically writes a detailed summary report to `output/attendance_report.txt` and exits cleanly.

---

## 🧪 University Test Cases & Verification

An automated verification test script `test_analyzer.py` is included to verify all test cases:

```bash
python3 test_analyzer.py
```

### Test Case 1: Normal Input
- **Input**:
  ```csv
  Aman,Python,40,36
  Riya,Python,40,28
  Karan,Python,40,30
  ```
- **Expected Results**:
  - Aman: `90.00%` (Eligible)
  - Riya: `70.00%` (Shortage / Not eligible)
  - Karan: `75.00%` (Eligible)
- **Status**: ✅ **PASSED**

### Test Case 2: Boundary / Minimum Input (75.00%)
- **Input**:
  ```csv
  Karan,Python,40,30
  ```
- **Expected Results**:
  - Karan: `75.00%` (Eligible)
  - No students below 75%
- **Status**: ✅ **PASSED**

### Test Case 3: Invalid Input
- **Input**:
  ```csv
  Aman,Python,40,45
  ```
- **Expected Results**:
  - Console output: `Row 1 invalid: attended (45) cannot exceed held (40). Row skipped.`
  - Application does not crash; skips the row safely.
- **Status**: ✅ **PASSED**

### Test Case 4: Multi-Subject Scenario & Subject Averages
- **Input**: Test Case 1 plus:
  ```csv
  Aman,Maths,50,45
  ```
- **Expected Subject Averages**:
  - Python: `78.33%`
  - Maths: `90.00%`
  - Bar chart and pie chart generated successfully.
- **Status**: ✅ **PASSED**

---

## 💡 Beginner's Guide: How the Code Works

If you are new to Python and Pandas, here are the key concepts used in this project:

### 1. What is a Pandas DataFrame?
A `DataFrame` is essentially a 2-dimensional spreadsheet table in Python memory, with rows and labeled columns.
```python
import pandas as pd
df = pd.read_csv("attendance.csv")
```

### 2. Boolean Filtering
Instead of writing traditional `for` loops with `if` statements, Pandas allows boolean masks:
```python
# Create a True/False series:
mask = summary["Attendance_Percentage"] < 75.0

# Filter the DataFrame instantly:
students_in_shortage = summary[mask]
```

### 3. Grouping and Aggregation (`groupby`)
To calculate totals or averages per student or per subject:
```python
# Group by student and sum their classes across all subjects
summary = df.groupby("Name").agg(
    Total_Held=("Classes_Held", "sum"),
    Total_Attended=("Classes_Attended", "sum")
)
```

### 4. Matplotlib Visualizations
We plot data directly using coordinates and styling parameters:
```python
import matplotlib.pyplot as plt

plt.bar(students, percentages, color=bar_colors)
plt.axhline(75.0, color='red', linestyle='--', label='75% Minimum Required')
plt.savefig("charts/student_attendance_bar_chart.png")
plt.close()
```

---

## 📄 License
This project is prepared for educational and university coursework purposes.
