"""
Student Information & Grade Management System
Metro Business College
------------------------------------------------
A console program that manages student records, computes quiz
averages and final grades, and generates a class report.

Features:
- Bordered / boxed sections for a cleaner console look
- Color-coded PASSED (green) / FAILED (red) status
- A Reset function that clears all student records (with confirmation)
- Screen clearing + "Press Enter" pauses for a smoother, less cluttered flow

Grade Computation:
    Quiz Average = (Quiz 1 + Quiz 2 + Quiz 3) / 3
    Final Grade  = Quiz Average * 30%
                  + Assignment   * 10%
                  + Project      * 20%
                  + Final Exam   * 40%

Passing grade: 75 and above.
"""

import os

# Enable ANSI color rendering on older Windows terminals (cmd.exe).
# Modern terminals (Linux, macOS, Windows Terminal, VS Code) already
# support ANSI color codes, so this only matters on legacy cmd.exe.
if os.name == "nt":
    os.system("")


# ------------------------------------------------------------------
# Configuration / constants
# ------------------------------------------------------------------
SCHOOL_NAME = "METRO BUSINESS COLLEGE"
PASSING_GRADE = 75
BOX_WIDTH = 48                  # total width of a bordered box (incl. borders)
INNER_WIDTH = BOX_WIDTH - 2     # usable width inside the left/right borders

students = []  # list of dictionaries -- the in-memory student database


class Colors:
    """ANSI escape codes used to color the console output."""
    RESET = "\033[0m"
    BOLD = "\033[1m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    CYAN = "\033[36m"


# ------------------------------------------------------------------
# Screen + border helpers
# ------------------------------------------------------------------
def clear_screen():
    """Clear the terminal so every section starts on a clean screen."""
    os.system("cls" if os.name == "nt" else "clear")


def pause():
    """Give the user a moment to read the result before the screen clears."""
    input(f"\n{Colors.CYAN}Press Enter to return to the menu...{Colors.RESET}")


def box_top(left="┌", right="┐"):
    return f"{Colors.CYAN}{left}{'─' * INNER_WIDTH}{right}{Colors.RESET}"


def box_bottom():
    return box_top(left="└", right="┘")


def box_divider():
    return box_top(left="├", right="┤")


def box_row(visible_text="", display_text=None, align="left"):
    """
    Print one bordered row.

    `visible_text` must be the PLAIN text (no color codes) -- it is used
    to work out how much padding is needed so the right border still
    lines up. `display_text` is what actually gets printed and may
    contain ANSI color codes; it defaults to `visible_text`.
    """
    if display_text is None:
        display_text = visible_text

    visible_text = visible_text[:INNER_WIDTH]
    padding = max(INNER_WIDTH - len(visible_text), 0)

    if align == "center":
        left_pad = padding // 2
        right_pad = padding - left_pad
        row = (" " * left_pad) + display_text + (" " * right_pad)
    else:
        row = display_text + (" " * padding)

    print(f"{Colors.CYAN}│{Colors.RESET}{row}{Colors.CYAN}│{Colors.RESET}")


def print_header(section_title):
    """Print a bordered header box: school name on top, section title below."""
    print(box_top())
    box_row(SCHOOL_NAME, align="center")
    print(box_divider())
    box_row(section_title, align="center")
    print(box_bottom())
    print()


def print_menu():
    print(box_top())
    box_row(SCHOOL_NAME, align="center")
    box_row("STUDENT GRADE MANAGEMENT", align="center")
    print(box_bottom())
    print()
    print(f"  {Colors.YELLOW}[1]{Colors.RESET} Add Student")
    print(f"  {Colors.YELLOW}[2]{Colors.RESET} View All Students")
    print(f"  {Colors.YELLOW}[3]{Colors.RESET} Search Student")
    print(f"  {Colors.YELLOW}[4]{Colors.RESET} Show Highest Grade")
    print(f"  {Colors.YELLOW}[5]{Colors.RESET} Reset All Data")
    print(f"  {Colors.YELLOW}[6]{Colors.RESET} Exit")
    print()


def status_display(status, width=None):
    """Return PASSED/FAILED text wrapped in green/red, ready to print."""
    text = status if width is None else f"{status:<{width}}"
    color = Colors.GREEN if status == "PASSED" else Colors.RED
    return f"{color}{text}{Colors.RESET}"


# ------------------------------------------------------------------
# Validation helpers (error handling lives here)
# ------------------------------------------------------------------
def find_student(student_id):
    """Linear search through the students list by Student ID."""
    for student in students:
        if student["id"].lower() == student_id.lower():
            return student
    return None


def get_unique_student_id():
    while True:
        student_id = input("Student ID: ").strip()

        if student_id == "":
            print(f"\n{Colors.RED}ERROR:{Colors.RESET}")
            print("Student ID cannot be empty.\n")
            continue

        if find_student(student_id) is not None:
            print(f"\n{Colors.RED}ERROR:{Colors.RESET}")
            print("Student ID already exists.")
            print("Please enter another ID.\n")
            continue

        return student_id


def get_valid_grade(prompt):
    while True:
        raw_value = input(prompt)
        try:
            grade = float(raw_value)
        except ValueError:
            print(f"\n{Colors.RED}ERROR:{Colors.RESET}")
            print("Please enter a valid number.\n")
            continue

        if grade < 0 or grade > 100:
            print(f"\n{Colors.RED}ERROR:{Colors.RESET}")
            print("Grade must be between 0 and 100.\n")
            continue

        return grade


def get_non_empty_text(prompt):
    while True:
        value = input(prompt).strip()
        if value == "":
            print(f"\n{Colors.RED}ERROR:{Colors.RESET}")
            print("This field cannot be empty.\n")
            continue
        return value


# ------------------------------------------------------------------
# Grade computation functions
# ------------------------------------------------------------------
def calculate_quiz_average(quiz1, quiz2, quiz3):
    return (quiz1 + quiz2 + quiz3) / 3


def calculate_final_grade(quiz_avg, assignment, project, final_exam):
    return (
        (quiz_avg * 0.30)
        + (assignment * 0.10)
        + (project * 0.20)
        + (final_exam * 0.40)
    )


def get_status(final_grade):
    if final_grade >= PASSING_GRADE:
        return "PASSED"
    else:
        return "FAILED"


# ------------------------------------------------------------------
# Shared bordered "card" used by both Search and Highest Grade
# ------------------------------------------------------------------
def print_student_card(student):
    label_width = 13
    rows = [
        ("Student ID", student["id"]),
        ("Name", student["name"]),
        ("Course", student["course"]),
        ("Quiz 1", f"{student['quiz1']:.2f}"),
        ("Quiz 2", f"{student['quiz2']:.2f}"),
        ("Quiz 3", f"{student['quiz3']:.2f}"),
        ("Quiz Average", f"{student['quiz_avg']:.2f}"),
        ("Assignment", f"{student['assignment']:.2f}"),
        ("Project", f"{student['project']:.2f}"),
        ("Final Exam", f"{student['final_exam']:.2f}"),
        ("Final Grade", f"{student['final_grade']:.2f}"),
    ]

    print(box_top())
    box_row(student["name"].upper(), align="center")
    print(box_divider())

    for label, value in rows:
        text = f" {label:<{label_width}}: {value}"
        box_row(text)

    status_label = f" {'Status':<{label_width}}: "
    visible = status_label + student["status"]
    display = status_label + status_display(student["status"])
    box_row(visible, display)

    print(box_bottom())


# ------------------------------------------------------------------
# Core menu actions
# ------------------------------------------------------------------
def add_student():
    clear_screen()
    print_header("ADD STUDENT")

    student_id = get_unique_student_id()
    name = get_non_empty_text("Student Name: ")
    course = get_non_empty_text("Course: ")
    print()

    quiz1 = get_valid_grade("Quiz 1: ")
    quiz2 = get_valid_grade("Quiz 2: ")
    quiz3 = get_valid_grade("Quiz 3: ")
    assignment = get_valid_grade("Assignment: ")
    project = get_valid_grade("Project: ")
    final_exam = get_valid_grade("Final Exam: ")

    quiz_avg = calculate_quiz_average(quiz1, quiz2, quiz3)
    final_grade = calculate_final_grade(quiz_avg, assignment, project, final_exam)
    status = get_status(final_grade)

    student = {
        "id": student_id,
        "name": name,
        "course": course,
        "quiz1": quiz1,
        "quiz2": quiz2,
        "quiz3": quiz3,
        "assignment": assignment,
        "project": project,
        "final_exam": final_exam,
        "quiz_avg": quiz_avg,
        "final_grade": final_grade,
        "status": status,
    }
    students.append(student)

    print(f"\n{Colors.GREEN}Student successfully added!{Colors.RESET}")
    pause()


def view_all_students():
    clear_screen()
    print_header("ALL STUDENTS")

    if len(students) == 0:
        print("No students recorded yet.")
        pause()
        return

    col_id, col_name, col_grade, col_status = 12, 18, 8, 8
    top = "┌" + "─" * col_id + "┬" + "─" * col_name + "┬" + "─" * col_grade + "┬" + "─" * col_status + "┐"
    mid = "├" + "─" * col_id + "┼" + "─" * col_name + "┼" + "─" * col_grade + "┼" + "─" * col_status + "┤"
    bot = "└" + "─" * col_id + "┴" + "─" * col_name + "┴" + "─" * col_grade + "┴" + "─" * col_status + "┘"

    print(f"Total Students: {len(students)}\n")
    print(f"{Colors.CYAN}{top}{Colors.RESET}")
    print(
        f"{Colors.CYAN}│{Colors.RESET}{'ID':<{col_id}}"
        f"{Colors.CYAN}│{Colors.RESET}{'NAME':<{col_name}}"
        f"{Colors.CYAN}│{Colors.RESET}{'GRADE':<{col_grade}}"
        f"{Colors.CYAN}│{Colors.RESET}{'STATUS':<{col_status}}"
        f"{Colors.CYAN}│{Colors.RESET}"
    )
    print(f"{Colors.CYAN}{mid}{Colors.RESET}")

    for student in students:
        id_cell = student["id"][:col_id].ljust(col_id)
        name_cell = student["name"][:col_name].ljust(col_name)
        grade_cell = f"{student['final_grade']:.2f}".ljust(col_grade)
        status_cell = status_display(student["status"], col_status)

        print(
            f"{Colors.CYAN}│{Colors.RESET}{id_cell}"
            f"{Colors.CYAN}│{Colors.RESET}{name_cell}"
            f"{Colors.CYAN}│{Colors.RESET}{grade_cell}"
            f"{Colors.CYAN}│{Colors.RESET}{status_cell}"
            f"{Colors.CYAN}│{Colors.RESET}"
        )

    print(f"{Colors.CYAN}{bot}{Colors.RESET}")
    pause()


def search_student():
    clear_screen()
    print_header("SEARCH STUDENT")
    student_id = input("Enter Student ID to search: ").strip()
    student = find_student(student_id)

    if student is None:
        print(f"\n{Colors.RED}Student not found.{Colors.RESET}")
        pause()
        return

    print()
    print_student_card(student)
    pause()


def show_highest_grade():
    clear_screen()
    print_header("HIGHEST FINAL GRADE")

    if len(students) == 0:
        print("No students recorded yet.")
        pause()
        return

    top_student = students[0]
    for student in students:
        if student["final_grade"] > top_student["final_grade"]:
            top_student = student

    print_student_card(top_student)
    pause()


def reset_data():
    clear_screen()
    print_header("RESET ALL DATA")

    if len(students) == 0:
        print("There is no data to reset.")
        pause()
        return

    print(
        f"{Colors.YELLOW}Warning: this will permanently delete all "
        f"{len(students)} student record(s).{Colors.RESET}"
    )
    confirm = input("Are you sure you want to continue? (y/n): ").strip().lower()

    if confirm == "y":
        students.clear()
        print(f"\n{Colors.GREEN}All student data has been reset successfully!{Colors.RESET}")
    else:
        print(f"\n{Colors.YELLOW}Reset cancelled. No data was changed.{Colors.RESET}")

    pause()


# ------------------------------------------------------------------
# Main program loop
# ------------------------------------------------------------------
def main():
    running = True

    while running:
        clear_screen()
        print_menu()
        choice = input(f"{Colors.BOLD}Enter choice: {Colors.RESET}").strip()

        if choice == "1":
            add_student()
        elif choice == "2":
            view_all_students()
        elif choice == "3":
            search_student()
        elif choice == "4":
            show_highest_grade()
        elif choice == "5":
            reset_data()
        elif choice == "6":
            clear_screen()
            print(
                f"{Colors.GREEN}Thank you for using the {SCHOOL_NAME} "
                f"Grade Management System. Goodbye!{Colors.RESET}"
            )
            running = False
        else:
            print(f"\n{Colors.RED}Invalid choice. Please select 1-6.{Colors.RESET}")
            pause()


if __name__ == "__main__":
    main()
