"""
College Attendance Analyzer
============================
A menu-driven console application built with Python 3, Pandas, and Matplotlib.
Designed for analyzing college student attendance records, checking 75% eligibility,
calculating subject-wise averages, and generating visual analytics charts.

Author: Senior Python Developer
Course: University Assignment
"""

import os
import sys
import pandas as pd
import matplotlib
# Use a non-blocking / reliable backend when running in headless or terminal environments
# but allow rendering to files smoothly.
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# ==============================================================================
# CONFIGURATION & CONSTANTS
# ==============================================================================
DEFAULT_CSV_PATH = "attendance.csv"
CHARTS_DIR = "charts"
OUTPUT_DIR = "output"
MIN_ATTENDANCE_PERCENTAGE = 75.0
REQUIRED_COLUMNS = ["Name", "Subject", "Classes_Held", "Classes_Attended"]


# ==============================================================================
# 1. DATA VALIDATION & LOADING
# ==============================================================================
def load_and_validate_attendance(file_path=DEFAULT_CSV_PATH):
    """
    Loads and validates the attendance CSV file row by row.

    Performs rigorous checks:
    - File existence and non-empty file check.
    - Header validation (required columns present).
    - Data type validation (numeric values for classes).
    - Logical validation:
        * Negative numbers are rejected.
        * Classes_Held == 0 is rejected (division by zero).
        * Classes_Attended > Classes_Held is rejected.
        * Empty/whitespace student names or subjects are rejected.

    Invalid rows are skipped with informative console messages.
    Never crashes due to single invalid records.

    Parameters:
        file_path (str): Path to the attendance CSV file.

    Returns:
        pd.DataFrame or None: Cleaned DataFrame containing valid rows,
                              or None if the file cannot be processed.
    """
    # 1. Check if file exists
    if not os.path.exists(file_path):
        print(f"\n[ERROR] File '{file_path}' was not found. Please verify the file path.")
        return None

    # 2. Check if file is empty (0 bytes)
    if os.path.getsize(file_path) == 0:
        print(f"\n[ERROR] The file '{file_path}' is completely empty (0 bytes).")
        return None

    # 3. Read raw CSV using pandas
    try:
        raw_df = pd.read_csv(file_path, skipinitialspace=True)
    except pd.errors.EmptyDataError:
        print(f"\n[ERROR] The file '{file_path}' contains no data or headers.")
        return None
    except Exception as exc:
        print(f"\n[ERROR] Could not read CSV file: {exc}")
        return None

    # Clean whitespace in column names
    raw_df.columns = [str(col).strip() for col in raw_df.columns]

    # 4. Check for missing or incorrect column names
    missing_cols = [col for col in REQUIRED_COLUMNS if col not in raw_df.columns]
    if missing_cols:
        print(f"\n[ERROR] Missing required column(s): {missing_cols}")
        print(f"       Expected columns: {REQUIRED_COLUMNS}")
        print(f"       Found columns: {list(raw_df.columns)}")
        return None

    if raw_df.empty:
        print(f"\n[ERROR] The file '{file_path}' contains only headers and no data rows.")
        return None

    print(f"\n>>> Validating '{file_path}' ({len(raw_df)} total row(s) read)...")

    valid_rows = []
    skipped_count = 0

    # 5. Row-by-row validation
    for idx, row in raw_df.iterrows():
        # Display row number as 1-based data index (matching user test expectations)
        row_num = idx + 1

        name_val = row.get("Name")
        subject_val = row.get("Subject")
        held_val = row.get("Classes_Held")
        attended_val = row.get("Classes_Attended")

        # Check empty or whitespace student name
        if pd.isna(name_val) or str(name_val).strip() == "":
            print(f"Row {row_num} invalid: student name cannot be empty. Row skipped.")
            skipped_count += 1
            continue

        # Check empty or whitespace subject
        if pd.isna(subject_val) or str(subject_val).strip() == "":
            print(f"Row {row_num} invalid: subject cannot be empty. Row skipped.")
            skipped_count += 1
            continue

        # Check numeric conversion for Classes_Held and Classes_Attended
        try:
            held = float(held_val)
            attended = float(attended_val)
        except (ValueError, TypeError):
            print(f"Row {row_num} invalid: numeric value expected for Classes_Held and Classes_Attended (got '{held_val}', '{attended_val}'). Row skipped.")
            skipped_count += 1
            continue

        # Check for NaN / Infinity
        if pd.isna(held) or pd.isna(attended):
            print(f"Row {row_num} invalid: missing numeric attendance data. Row skipped.")
            skipped_count += 1
            continue

        # Check negative attendance values
        if held < 0 or attended < 0:
            print(f"Row {row_num} invalid: attendance values cannot be negative (held={held_val}, attended={attended_val}). Row skipped.")
            skipped_count += 1
            continue

        # Check Classes_Held equal to zero
        if held == 0:
            print(f"Row {row_num} invalid: Classes_Held cannot be zero (division by zero). Row skipped.")
            skipped_count += 1
            continue

        # Check Classes_Attended greater than Classes_Held
        if attended > held:
            # Format integer if whole number for clean output matching test case
            held_str = int(held) if held.is_integer() else held
            attended_str = int(attended) if attended.is_integer() else attended
            print(f"Row {row_num} invalid: attended ({attended_str}) cannot exceed held ({held_str}). Row skipped.")
            skipped_count += 1
            continue

        # Calculate row-level attendance percentage
        pct = (attended / held) * 100.0

        valid_rows.append({
            "Name": str(name_val).strip(),
            "Subject": str(subject_val).strip(),
            "Classes_Held": int(held) if held.is_integer() else held,
            "Classes_Attended": int(attended) if attended.is_integer() else attended,
            "Attendance_Percentage": round(pct, 2)
        })

    if not valid_rows:
        print("\n[WARNING] No valid attendance records found after validation.")
        return None

    clean_df = pd.DataFrame(valid_rows)
    print(f"✓ Validation complete: {len(clean_df)} valid record(s) loaded ({skipped_count} row(s) skipped).\n")
    return clean_df


# ==============================================================================
# 2. DATA PROCESSING & SUMMARY HELPERS
# ==============================================================================
def calculate_student_summary(df):
    """
    Aggregates student records across all subjects to calculate overall attendance.

    Overall Student Attendance Formula:
        Total Attended = sum(Classes_Attended)
        Total Held = sum(Classes_Held)
        Overall Percentage = (Total Attended / Total Held) * 100

    Eligibility Criteria:
        - Percentage >= 75%: Eligible
        - Percentage < 75%: Shortage / Not eligible

    Parameters:
        df (pd.DataFrame): Validated attendance DataFrame.

    Returns:
        pd.DataFrame: Summary DataFrame indexed by student with overall totals,
                      percentage, and eligibility status.
    """
    summary = df.groupby("Name", as_index=False).agg(
        Total_Held=("Classes_Held", "sum"),
        Total_Attended=("Classes_Attended", "sum")
    )

    # Compute overall percentage
    summary["Attendance_Percentage"] = (
        summary["Total_Attended"] / summary["Total_Held"]
    ) * 100.0
    summary["Attendance_Percentage"] = summary["Attendance_Percentage"].round(2)

    # Determine eligibility status using boolean logic
    summary["Is_Eligible"] = summary["Attendance_Percentage"] >= MIN_ATTENDANCE_PERCENTAGE
    summary["Status"] = summary["Is_Eligible"].apply(
        lambda eligible: "Eligible" if eligible else "Shortage / Not eligible"
    )

    return summary


# ==============================================================================
# 3. MENU OPTION HANDLERS
# ==============================================================================
def display_all_students_attendance(df):
    """
    Menu Option 1:
    Calculates and displays attendance percentage and eligibility of every student.
    Also displays per-subject breakdown if students take multiple subjects.
    """
    if df is None or df.empty:
        print("[NOTICE] No attendance data available to display.")
        return

    summary = calculate_student_summary(df)

    print("\n" + "=" * 78)
    print("                STUDENT ATTENDANCE PERCENTAGE REPORT")
    print("=" * 78)
    print(f"{'Student Name':<18} | {'Classes Held':<12} | {'Attended':<10} | {'Attendance %':<14} | {'Status'}")
    print("-" * 78)

    for _, row in summary.iterrows():
        pct_str = f"{row['Attendance_Percentage']:.2f}%"
        print(f"{row['Name']:<18} | {int(row['Total_Held']):<12} | {int(row['Total_Attended']):<10} | {pct_str:<14} | {row['Status']}")

    print("-" * 78)

    # If dataset has multiple subjects, show detailed subject breakdown
    unique_subjects = df["Subject"].nunique()
    if unique_subjects > 1 or len(df) > len(summary):
        print("\n--- Detailed Subject-wise Breakdown per Student ---")
        for name, group in df.groupby("Name"):
            records = []
            for _, r in group.iterrows():
                records.append(f"{r['Subject']}: {r['Attendance_Percentage']:.2f}% ({int(r['Classes_Attended'])}/{int(r['Classes_Held'])})")
            print(f"• {name}: " + ", ".join(records))
    print("=" * 78 + "\n")


def display_students_below_threshold(df, threshold=MIN_ATTENDANCE_PERCENTAGE):
    """
    Menu Option 2:
    Identifies and displays students with attendance below 75% using Pandas boolean filtering.

    Parameters:
        df (pd.DataFrame): Validated attendance DataFrame.
        threshold (float): Attendance percentage threshold (default 75.0%).
    """
    if df is None or df.empty:
        print("[NOTICE] No attendance data available to display.")
        return

    summary = calculate_student_summary(df)

    # Boolean filtering in Pandas
    shortage_df = summary[summary["Attendance_Percentage"] < threshold]

    print("\n" + "=" * 78)
    print(f"       STUDENTS WITH ATTENDANCE SHORTAGE (BELOW {threshold:.0f}%)")
    print("=" * 78)

    if shortage_df.empty:
        print(f"✓ No students below {threshold:.0f}%. All students are eligible!")
        print("=" * 78 + "\n")
        return

    print(f"{'Student Name':<18} | {'Classes Held':<12} | {'Attended':<10} | {'Attendance %':<14} | {'Shortage Deficit'}")
    print("-" * 78)

    for _, row in shortage_df.iterrows():
        # Minimum classes required to reach 75%
        required_classes = int((threshold / 100.0) * row["Total_Held"])
        deficit = max(0, required_classes - int(row["Total_Attended"]))
        pct_str = f"{row['Attendance_Percentage']:.2f}%"
        deficit_str = f"Needs {deficit} more class(es)"
        print(f"{row['Name']:<18} | {int(row['Total_Held']):<12} | {int(row['Total_Attended']):<10} | {pct_str:<14} | {deficit_str}")

    print("-" * 78)
    print(f"⚠️  Total Students with Shortage: {len(shortage_df)} out of {len(summary)}")
    print("=" * 78 + "\n")


def calculate_and_display_subject_average(df):
    """
    Menu Option 3:
    Calculates and displays the subject-wise average attendance percentage.

    Formula:
        Subject Average % = Mean of attendance percentages across all students in that subject.
    """
    if df is None or df.empty:
        print("[NOTICE] No attendance data available to display.")
        return

    # Calculate average attendance percentage for each subject
    subject_group = df.groupby("Subject").agg(
        Total_Students=("Name", "nunique"),
        Total_Records=("Name", "count"),
        Average_Attendance=("Attendance_Percentage", "mean")
    ).reset_index()

    subject_group["Average_Attendance"] = subject_group["Average_Attendance"].round(2)

    print("\n" + "=" * 60)
    print("            SUBJECT-WISE AVERAGE ATTENDANCE")
    print("=" * 60)
    print(f"{'Subject':<22} | {'Students':<10} | {'Average Attendance %'}")
    print("-" * 60)

    for _, row in subject_group.iterrows():
        avg_str = f"{row['Average_Attendance']:.2f}%"
        print(f"{row['Subject']:<22} | {int(row['Total_Students']):<10} | {avg_str}")

    print("-" * 60)
    print("=" * 60 + "\n")

    return subject_group


# ==============================================================================
# 4. DATA VISUALIZATION (MATPLOTLIB)
# ==============================================================================
def ensure_directories():
    """Creates charts/ and output/ folders if they do not exist."""
    os.makedirs(CHARTS_DIR, exist_ok=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)


def generate_attendance_bar_chart(df, save_path=None):
    """
    Menu Option 4:
    Generates a student-wise attendance percentage bar chart using Matplotlib.
    - Bars are color-coded (Green for >= 75%, Red for < 75%).
    - A dashed horizontal red line marks the 75% threshold.
    - Saves the chart as an image in the charts/ directory.
    - Also generates a subject-wise average bar chart.

    Parameters:
        df (pd.DataFrame): Validated attendance DataFrame.
        save_path (str, optional): Custom path for saving the figure.
    """
    if df is None or df.empty:
        print("[NOTICE] No attendance data available to plot.")
        return

    ensure_directories()
    summary = calculate_student_summary(df)

    if save_path is None:
        save_path = os.path.join(CHARTS_DIR, "student_attendance_bar_chart.png")

    students = summary["Name"].tolist()
    percentages = summary["Attendance_Percentage"].tolist()

    # Colors: Green (#27ae60) for eligible, Red (#e74c3c) for shortage
    bar_colors = [
        "#27ae60" if p >= MIN_ATTENDANCE_PERCENTAGE else "#e74c3c"
        for p in percentages
    ]

    plt.figure(figsize=(10, 6))
    bars = plt.bar(students, percentages, color=bar_colors, edgecolor="#2c3e50", width=0.55, zorder=3)

    # 75% Minimum Attendance Threshold line
    plt.axhline(
        y=MIN_ATTENDANCE_PERCENTAGE,
        color="#c0392b",
        linestyle="--",
        linewidth=2,
        label=f"Minimum Required ({MIN_ATTENDANCE_PERCENTAGE:.0f}%)",
        zorder=4
    )

    # Styling and grid
    plt.title("Student Attendance Percentage Analysis", fontsize=15, fontweight="bold", pad=15)
    plt.xlabel("Student Name", fontsize=12, fontweight="bold", labelpad=10)
    plt.ylabel("Attendance Percentage (%)", fontsize=12, fontweight="bold", labelpad=10)
    plt.ylim(0, 110)
    plt.grid(axis="y", linestyle=":", alpha=0.7, zorder=0)

    # Add numeric percentage labels on top of each bar
    for bar, pct in zip(bars, percentages):
        height = bar.get_height()
        status_symbol = "✓" if pct >= MIN_ATTENDANCE_PERCENTAGE else "⚠"
        plt.text(
            bar.get_x() + bar.get_width() / 2.0,
            height + 2.0,
            f"{pct:.2f}%\n{status_symbol}",
            ha="center",
            va="bottom",
            fontsize=10,
            fontweight="bold",
            color="#2c3e50"
        )

    plt.legend(loc="upper right", frameon=True)
    plt.tight_layout()

    try:
        plt.savefig(save_path, dpi=300)
        print(f"✓ Student Attendance Bar Chart saved successfully to: '{save_path}'")
    except Exception as exc:
        print(f"[ERROR] Failed to save bar chart: {exc}")
    finally:
        plt.close()

    # Also generate subject-wise bar chart for additional analytical depth
    generate_subject_bar_chart(df)


def generate_subject_bar_chart(df, save_path=None):
    """
    Generates a subject-wise average attendance bar chart.

    Parameters:
        df (pd.DataFrame): Validated attendance DataFrame.
        save_path (str, optional): Custom path for saving the figure.
    """
    if df is None or df.empty:
        return

    ensure_directories()
    if save_path is None:
        save_path = os.path.join(CHARTS_DIR, "subject_attendance_bar_chart.png")

    subject_group = df.groupby("Subject")["Attendance_Percentage"].mean().reset_index()

    subjects = subject_group["Subject"].tolist()
    averages = subject_group["Attendance_Percentage"].tolist()

    plt.figure(figsize=(8, 5))
    bars = plt.bar(subjects, averages, color="#2980b9", edgecolor="#1a5276", width=0.5, zorder=3)

    plt.axhline(
        y=MIN_ATTENDANCE_PERCENTAGE,
        color="#c0392b",
        linestyle="--",
        linewidth=1.8,
        label=f"Benchmark ({MIN_ATTENDANCE_PERCENTAGE:.0f}%)",
        zorder=4
    )

    plt.title("Subject-wise Average Attendance", fontsize=14, fontweight="bold", pad=12)
    plt.xlabel("Subject", fontsize=11, fontweight="bold", labelpad=8)
    plt.ylabel("Average Attendance (%)", fontsize=11, fontweight="bold", labelpad=8)
    plt.ylim(0, 110)
    plt.grid(axis="y", linestyle=":", alpha=0.7, zorder=0)

    for bar, avg in zip(bars, averages):
        height = bar.get_height()
        plt.text(
            bar.get_x() + bar.get_width() / 2.0,
            height + 1.8,
            f"{avg:.2f}%",
            ha="center",
            va="bottom",
            fontsize=10,
            fontweight="bold"
        )

    plt.legend(loc="upper right")
    plt.tight_layout()

    try:
        plt.savefig(save_path, dpi=300)
        print(f"✓ Subject Attendance Bar Chart saved successfully to: '{save_path}'")
    except Exception as exc:
        print(f"[ERROR] Failed to save subject bar chart: {exc}")
    finally:
        plt.close()


def generate_attendance_pie_chart(df, save_path=None):
    """
    Menu Option 5:
    Generates an Eligible vs Shortage student distribution pie chart using Matplotlib.
    - Clearly illustrates the proportion of students who meet the 75% threshold.
    - Saves the chart in the charts/ directory.

    Parameters:
        df (pd.DataFrame): Validated attendance DataFrame.
        save_path (str, optional): Custom path for saving the figure.
    """
    if df is None or df.empty:
        print("[NOTICE] No attendance data available to plot.")
        return

    ensure_directories()
    summary = calculate_student_summary(df)

    if save_path is None:
        save_path = os.path.join(CHARTS_DIR, "attendance_eligibility_pie_chart.png")

    eligible_count = int(summary["Is_Eligible"].sum())
    shortage_count = len(summary) - eligible_count

    labels = []
    sizes = []
    colors = []
    explode = []

    if eligible_count > 0:
        labels.append(f"Eligible (≥75%)\n[{eligible_count} student(s)]")
        sizes.append(eligible_count)
        colors.append("#27ae60")
        explode.append(0.03)

    if shortage_count > 0:
        labels.append(f"Shortage (<75%)\n[{shortage_count} student(s)]")
        sizes.append(shortage_count)
        colors.append("#e74c3c")
        explode.append(0.08)

    plt.figure(figsize=(7, 7))
    plt.pie(
        sizes,
        explode=explode,
        labels=labels,
        colors=colors,
        autopct="%1.1f%%",
        startangle=140,
        textprops={"fontsize": 11, "fontweight": "bold"},
        wedgeprops={"edgecolor": "#2c3e50", "linewidth": 1.2}
    )

    plt.title("Student Attendance Eligibility Distribution", fontsize=14, fontweight="bold", pad=15)
    plt.tight_layout()

    try:
        plt.savefig(save_path, dpi=300)
        print(f"✓ Attendance Pie Chart saved successfully to: '{save_path}'")
    except Exception as exc:
        print(f"[ERROR] Failed to save pie chart: {exc}")
    finally:
        plt.close()


# ==============================================================================
# 5. REPORT EXPORT (TEXT SUMMARY)
# ==============================================================================
def export_summary_report(df, output_path=None):
    """
    Exports a comprehensive text analysis report into the output/ folder.

    Parameters:
        df (pd.DataFrame): Validated attendance DataFrame.
        output_path (str, optional): File path for saving the report.
    """
    if df is None or df.empty:
        return

    ensure_directories()
    if output_path is None:
        output_path = os.path.join(OUTPUT_DIR, "attendance_report.txt")

    summary = calculate_student_summary(df)
    subject_group = df.groupby("Subject")["Attendance_Percentage"].mean().reset_index()

    eligible_count = int(summary["Is_Eligible"].sum())
    shortage_count = len(summary) - eligible_count

    report_lines = [
        "=" * 70,
        "              COLLEGE ATTENDANCE ANALYZER - SUMMARY REPORT",
        "=" * 70,
        f"Total Valid Records Analyzed: {len(df)}",
        f"Total Unique Students:        {len(summary)}",
        f"Eligible Students (>= 75%):   {eligible_count}",
        f"Students with Shortage:       {shortage_count}",
        "-" * 70,
        "STUDENT BREAKDOWN:",
        "-" * 70,
        f"{'Name':<18} | {'Held':<8} | {'Attended':<10} | {'Percentage':<12} | {'Status'}",
        "-" * 70
    ]

    for _, r in summary.iterrows():
        report_lines.append(
            f"{r['Name']:<18} | {int(r['Total_Held']):<8} | {int(r['Total_Attended']):<10} | {r['Attendance_Percentage']:.2f}%{'':<6} | {r['Status']}"
        )

    report_lines.extend([
        "-" * 70,
        "SUBJECT-WISE AVERAGES:",
        "-" * 70
    ])

    for _, r in subject_group.iterrows():
        report_lines.append(f"• {r['Subject']:<20}: {r['Attendance_Percentage']:.2f}%")

    report_lines.append("=" * 70)

    try:
        with open(output_path, "w", encoding="utf-8") as file:
            file.write("\n".join(report_lines) + "\n")
        print(f"✓ Summary text report exported to: '{output_path}'")
    except Exception as exc:
        print(f"[ERROR] Could not export report: {exc}")


# ==============================================================================
# 6. CONSOLE MENU & CONTROLLER
# ==============================================================================
def print_menu():
    """Prints the application main menu."""
    print("=" * 65)
    print("                 COLLEGE ATTENDANCE ANALYZER")
    print("=" * 65)
    print("  1. Calculate & Display Attendance Percentage (All Students)")
    print("  2. Display Students Below 75% Attendance (Shortage)")
    print("  3. Calculate & Display Subject-Wise Average Attendance")
    print("  4. Generate Attendance Bar Chart")
    print("  5. Generate Attendance Pie Chart")
    print("  6. Exit the Application")
    print("=" * 65)


def run_analyzer(file_path=DEFAULT_CSV_PATH):
    """
    Main application loop driving the console interface.

    Parameters:
        file_path (str): CSV file path to process.
    """
    print("\nWelcome to College Attendance Analyzer!")
    ensure_directories()

    # Load and validate CSV at startup
    df = load_and_validate_attendance(file_path)

    while True:
        print_menu()
        choice = input("Enter your choice (1-6): ").strip()

        if choice == "1":
            display_all_students_attendance(df)

        elif choice == "2":
            display_students_below_threshold(df, MIN_ATTENDANCE_PERCENTAGE)

        elif choice == "3":
            calculate_and_display_subject_average(df)

        elif choice == "4":
            if df is not None and not df.empty:
                generate_attendance_bar_chart(df)
            else:
                print("[NOTICE] No valid attendance data available to generate bar chart.")

        elif choice == "5":
            if df is not None and not df.empty:
                generate_attendance_pie_chart(df)
            else:
                print("[NOTICE] No valid attendance data available to generate pie chart.")

        elif choice == "6":
            # Auto-export summary report upon exit if data was processed
            if df is not None and not df.empty:
                export_summary_report(df)
            print("\nThank you for using College Attendance Analyzer. Goodbye!\n")
            break

        else:
            print("\n[INVALID CHOICE] Please enter a valid number between 1 and 6.\n")


# ==============================================================================
# ENTRY POINT
# ==============================================================================
if __name__ == "__main__":
    # Allow passing a custom CSV file via command line argument (e.g. python main.py custom.csv)
    target_csv = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_CSV_PATH
    run_analyzer(target_csv)
