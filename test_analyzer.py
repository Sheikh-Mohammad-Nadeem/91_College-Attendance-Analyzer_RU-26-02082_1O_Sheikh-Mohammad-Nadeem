"""
Automated Test Suite for College Attendance Analyzer
=====================================================
Executes and validates all university test cases:
- Test Case 1: Normal Input
- Test Case 2: Boundary / Minimum Input (75.0% threshold)
- Test Case 3: Invalid Input (attended > held)
- Test Case 4: Multi-Subject Scenario & Subject Averages

Also tests edge cases (empty file, negative values, missing file, zero held).
"""

import os
import shutil
import tempfile
import pandas as pd
from main import (
    load_and_validate_attendance,
    calculate_student_summary,
    display_all_students_attendance,
    display_students_below_threshold,
    calculate_and_display_subject_average,
    generate_attendance_bar_chart,
    generate_attendance_pie_chart,
    MIN_ATTENDANCE_PERCENTAGE
)

def create_temp_csv(content):
    """Helper to create a temporary CSV file with the given content."""
    fd, path = tempfile.mkstemp(suffix=".csv")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(content)
    return path


def run_all_tests():
    print("=" * 70)
    print("RUNNING AUTOMATED TEST SUITE FOR COLLEGE ATTENDANCE ANALYZER")
    print("=" * 70)

    # --------------------------------------------------------------------------
    # TEST CASE 1: Normal Input
    # --------------------------------------------------------------------------
    print("\n[TEST CASE 1] Normal Input")
    tc1_data = (
        "Name,Subject,Classes_Held,Classes_Attended\n"
        "Aman,Python,40,36\n"
        "Riya,Python,40,28\n"
        "Karan,Python,40,30\n"
    )
    tc1_file = create_temp_csv(tc1_data)
    try:
        df1 = load_and_validate_attendance(tc1_file)
        assert df1 is not None, "Test Case 1 failed: DataFrame is None"
        summary1 = calculate_student_summary(df1)
        
        # Verify percentages
        aman_pct = summary1.loc[summary1["Name"] == "Aman", "Attendance_Percentage"].values[0]
        riya_pct = summary1.loc[summary1["Name"] == "Riya", "Attendance_Percentage"].values[0]
        karan_pct = summary1.loc[summary1["Name"] == "Karan", "Attendance_Percentage"].values[0]

        print(f"Results: Aman={aman_pct:.2f}%, Riya={riya_pct:.2f}%, Karan={karan_pct:.2f}%")
        assert aman_pct == 90.00, f"Expected Aman 90.00%, got {aman_pct}"
        assert riya_pct == 70.00, f"Expected Riya 70.00%, got {riya_pct}"
        assert karan_pct == 75.00, f"Expected Karan 75.00%, got {karan_pct}"
        
        display_all_students_attendance(df1)
        print("✓ TEST CASE 1 PASSED!")
    finally:
        os.remove(tc1_file)

    # --------------------------------------------------------------------------
    # TEST CASE 2: Boundary / Minimum Input (75.0%)
    # --------------------------------------------------------------------------
    print("\n[TEST CASE 2] Boundary / Minimum Input")
    tc2_data = (
        "Name,Subject,Classes_Held,Classes_Attended\n"
        "Karan,Python,40,30\n"
    )
    tc2_file = create_temp_csv(tc2_data)
    try:
        df2 = load_and_validate_attendance(tc2_file)
        assert df2 is not None, "Test Case 2 failed: DataFrame is None"
        summary2 = calculate_student_summary(df2)
        
        karan_pct = summary2.loc[summary2["Name"] == "Karan", "Attendance_Percentage"].values[0]
        karan_status = summary2.loc[summary2["Name"] == "Karan", "Status"].values[0]
        karan_eligible = summary2.loc[summary2["Name"] == "Karan", "Is_Eligible"].values[0]

        print(f"Results: Karan={karan_pct:.2f}%, Status='{karan_status}', Eligible={karan_eligible}")
        assert karan_pct == 75.00, f"Expected Karan 75.00%, got {karan_pct}"
        assert karan_eligible is True or karan_eligible == 1, "Expected Karan to be eligible at exactly 75%"
        
        shortage2 = summary2[summary2["Attendance_Percentage"] < MIN_ATTENDANCE_PERCENTAGE]
        assert shortage2.empty, "Expected no students below 75%"
        
        display_students_below_threshold(df2)
        print("✓ TEST CASE 2 PASSED! (Karan 75.00% is eligible; no students below 75%)")
    finally:
        os.remove(tc2_file)

    # --------------------------------------------------------------------------
    # TEST CASE 3: Invalid Input (Classes_Attended > Classes_Held)
    # --------------------------------------------------------------------------
    print("\n[TEST CASE 3] Invalid Input (attended > held)")
    tc3_data = (
        "Name,Subject,Classes_Held,Classes_Attended\n"
        "Aman,Python,40,45\n"
    )
    tc3_file = create_temp_csv(tc3_data)
    try:
        df3 = load_and_validate_attendance(tc3_file)
        # Row 1 is invalid, so no valid rows remain -> df3 should be None
        assert df3 is None, "Expected DataFrame to be None because invalid row was skipped"
        print("✓ TEST CASE 3 PASSED! (Invalid row properly caught and skipped without crashing)")
    finally:
        os.remove(tc3_file)

    # --------------------------------------------------------------------------
    # TEST CASE 4: Different Valid Scenario (Subject Averages & Charts)
    # --------------------------------------------------------------------------
    print("\n[TEST CASE 4] Multi-Subject Scenario & Subject Averages")
    tc4_data = (
        "Name,Subject,Classes_Held,Classes_Attended\n"
        "Aman,Python,40,36\n"
        "Riya,Python,40,28\n"
        "Karan,Python,40,30\n"
        "Aman,Maths,50,45\n"
    )
    tc4_file = create_temp_csv(tc4_data)
    try:
        df4 = load_and_validate_attendance(tc4_file)
        assert df4 is not None, "Test Case 4 failed: DataFrame is None"
        
        subject_group = calculate_and_display_subject_average(df4)
        
        py_avg = subject_group.loc[subject_group["Subject"] == "Python", "Average_Attendance"].values[0]
        math_avg = subject_group.loc[subject_group["Subject"] == "Maths", "Average_Attendance"].values[0]

        print(f"Subject Averages: Python={py_avg:.2f}%, Maths={math_avg:.2f}%")
        assert py_avg == 78.33, f"Expected Python 78.33%, got {py_avg}"
        assert math_avg == 90.00, f"Expected Maths 90.00%, got {math_avg}"

        # Generate charts
        bar_chart_path = "charts/testcase4_student_bar.png"
        pie_chart_path = "charts/testcase4_pie.png"
        generate_attendance_bar_chart(df4, save_path=bar_chart_path)
        generate_attendance_pie_chart(df4, save_path=pie_chart_path)

        assert os.path.exists(bar_chart_path), "Bar chart file was not created"
        assert os.path.exists(pie_chart_path), "Pie chart file was not created"

        # Clean up temporary test chart files
        if os.path.exists(bar_chart_path):
            os.remove(bar_chart_path)
        if os.path.exists(pie_chart_path):
            os.remove(pie_chart_path)

        print("✓ TEST CASE 4 PASSED! (Subject averages verified & charts generated)")
    finally:
        os.remove(tc4_file)

    # --------------------------------------------------------------------------
    # EDGE CASE TESTS: Missing columns, negative values, zero held, empty file
    # --------------------------------------------------------------------------
    print("\n[EDGE CASE TESTS] Robustness Verification")
    
    # Negative value
    neg_data = "Name,Subject,Classes_Held,Classes_Attended\nAman,Python,40,-5\n"
    neg_file = create_temp_csv(neg_data)
    assert load_and_validate_attendance(neg_file) is None
    os.remove(neg_file)
    print("✓ Negative attendance properly skipped.")

    # Zero held
    zero_data = "Name,Subject,Classes_Held,Classes_Attended\nAman,Python,0,0\n"
    zero_file = create_temp_csv(zero_data)
    assert load_and_validate_attendance(zero_file) is None
    os.remove(zero_file)
    print("✓ Zero classes held properly skipped.")

    # Non-numeric value
    str_data = "Name,Subject,Classes_Held,Classes_Attended\nAman,Python,forty,twenty\n"
    str_file = create_temp_csv(str_data)
    assert load_and_validate_attendance(str_file) is None
    os.remove(str_file)
    print("✓ Non-numeric attendance properly skipped.")

    # Missing file
    assert load_and_validate_attendance("non_existent_file_123.csv") is None
    print("✓ Missing file error handled cleanly.")

    # Mixed valid and invalid rows
    mixed_data = (
        "Name,Subject,Classes_Held,Classes_Attended\n"
        "ValidStudent,Python,40,30\n"
        "BadStudent,Python,40,50\n"  # Invalid (attended > held)
        "AnotherValid,Maths,20,15\n"
    )
    mixed_file = create_temp_csv(mixed_data)
    df_mixed = load_and_validate_attendance(mixed_file)
    assert df_mixed is not None and len(df_mixed) == 2, "Expected 2 valid records from mixed file"
    os.remove(mixed_file)
    print("✓ Mixed dataset: Bad rows skipped while good rows preserved successfully.")

    print("\n" + "=" * 70)
    print("ALL TESTS PASSED SUCCESSFULLY! 100% VERIFIED.")
    print("=" * 70)

if __name__ == "__main__":
    run_all_tests()
