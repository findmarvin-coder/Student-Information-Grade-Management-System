"""
Student Information & Grade Management System
Metro Business College
------------------------------------------------
A console program that manages student records, computes quiz
averages and final grades, and generates a class report.

Features:
- Full grid borders (rows AND columns) on every screen: the menu,
  the student table, and the student detail card are all real
  bordered grids, not just boxed headers.
- Color-coded PASSED (green) / FAILED (red) status.
- A Reset function that clears all student records (with confirmation).
- Screen clearing + "Press Enter" pauses for a smoother, less cluttered flow.

Grade Computation:
    Quiz Average = (Quiz 1 + Quiz 2 + Quiz 3) / 3
    Final Grade  = Quiz Average * 30%
                  + Assignment   * 10%
                  + Project      * 20%
                  + Final Exam   * 40%

Passing grade: 75 and above.
"""

import os
import re

# Enable ANSI color rendering on older Windows terminals (cmd.exe).
# Modern terminals (Linux, macOS, Windows Terminal, VS Code) already
# support ANSI color codes, so this only matters on legacy cmd.exe.
if os.name == "nt":
    os.system("")


# ------------------------------------------------------------------
# Configuration / constants
# ------------------------------------------------------------------
SCHOOL_NAME = "METRO BUSINESS COLLEGE"
PROJECT_TITLE = "STUDENT INFORMATION & GRADE MANAGEMENT SYSTEM"
MENU_SUBTITLE = "STUDENT GRADE MANAGEMENT"
PASSING_GRADE = 75

BOX_WIDTH = 52                  # total width of every box/grid (incl. borders)
INNER_WIDTH = BOX_WIDTH - 2      # usable width inside a single-column box

students = []  # list of dictionaries -- the in-memory student database


class Colors:
    """ANSI escape codes used to color the console output."""
    RESET = "\033[0m"
    BOLD = "\033[1m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    CYAN = "\033[36m"


ANSI_RE = re.compile(r"\033\[[0-9;]*m")


def visible_len(text):
    """Length of `text` as it appears on screen, ignoring ANSI color codes."""
    return len(ANSI_RE.sub("", text))


# ------------------------------------------------------------------
# Screen helpers
# ------------------------------------------------------------------
def clear_screen():
    """Clear the terminal so every section starts on a clean screen."""
    os.system("cls" if os.name == "nt" else "clear")


def pause():
    """Give the user a moment to read the result before the screen clears."""
    input(f"\n{Colors.CYAN}Press Enter to return to the menu...{Colors.RESET}")


# ------------------------------------------------------------------
# Single-column box helpers (headers, banners, message boxes)
# ------------------------------------------------------------------
def box_top(left="┌", right="┐"):
    return f"{Colors.CYAN}{left}{'─' * INNER_WIDTH}{right}{Colors.RESET}"


def box_bottom():
    return box_top(left="└", right="┘")


def box_row(visible_text="", display_text=None, align="left"):
    """
    Print one bordered single-column row.

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
    """Print two separate bordered boxes: school name + project title on
    top, then the section title below -- the same banner style used on
    the main menu, kept consistent on every section."""
    print(box_top())
    box_row(SCHOOL_NAME, align="center")
    box_row(PROJECT_TITLE, align="center")
    print(box_bottom())
    print()

    print(box_top())
    box_row(section_title, align="center")
    print(box_bottom())
    print()


def print_message_box(text, color=None):
    """Print a short result / status message inside its own bordered box."""
    display_text = text if color is None else f"{color}{text}{Colors.RESET}"
    print(box_top())
    box_row(text, display_text, align="center")
    print(box_bottom())


# ------------------------------------------------------------------
# Multi-column grid helpers (menu, student table, student card)
# ------------------------------------------------------------------
def grid_border(col_widths, left, mid, right):
    parts = ["─" * w for w in col_widths]
    return f"{Colors.CYAN}{left}{mid.join(parts)}{right}{Colors.RESET}"


def grid_top(col_widths):
    return grid_border(col_widths, "┌", "┬", "┐")


def grid_divider(col_widths):
    return grid_border(col_widths, "├", "┼", "┤")


def grid_bottom(col_widths):
    return grid_border(col_widths, "└", "┴", "┘")


def grid_row(col_widths, cells):
    """
    Print one bordered row with a vertical border between every column.

    Each cell is padded (left-aligned) up to its column width, based on
    its VISIBLE length -- so cells may already contain ANSI color codes
    or be pre-padded/centered by the caller (e.g. for header rows).
    """
    sep = f"{Colors.CYAN}│{Colors.RESET}"
    parts = []
    for width, cell in zip(col_widths, cells):
        pad = max(width - visible_len(cell), 0)
        parts.append(cell + " " * pad)
    print(sep + sep.join(parts) + sep)


def grid_rule(col_widths):
    print(grid_divider(col_widths))


def status_display(status, width=None):
    """Return PASSED/FAILED text wrapped in green/red, ready to print."""
    text = status if width is None else f"{status:<{width}}"
    color = Colors.GREEN if status == "PASSED" else Colors.RED
    return f"{color}{text}{Colors.RESET}"


def print_menu():
    # First banner: school name + full project title.
    print(box_top())
    box_row(SCHOOL_NAME, align="center")
    box_row(PROJECT_TITLE, align="center")
    print(box_bottom())
    print()

    # Second banner: its own bordered box for the subtitle.
    print(box_top())
    box_row(MENU_SUBTITLE, align="center")
    print(box_bottom())
    print()

    # Menu options, shown as a fully bordered grid (rows + columns).
    col_widths = [10, 39]
    menu_items = [
        ("[1]", "Add Student"),
        ("[2]", "View All Students"),
        ("[3]", "Search Student"),
        ("[4]", "Show Highest Grade"),
        ("[5]", "Reset All Data"),
        ("[6]", "Exit"),
    ]

    print(grid_top(col_widths))
    grid_row(
        col_widths,
        [
            f"{Colors.YELLOW}{'OPTION':^10}{Colors.RESET}",
            f"{Colors.YELLOW}{'MENU ACTION':^39}{Colors.RESET}",
        ],
    )
    grid_rule(col_widths)

    for index, (key, label) in enumerate(menu_items):
        cell_key = f"{Colors.YELLOW}{key:^10}{Colors.RESET}"
        cell_label = f" {label}"
        grid_row(col_widths, [cell_key, cell_label])
        if index != len(menu_items) - 1:
            grid_rule(col_widths)

    print(grid_bottom(col_widths))
    print()


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
# Shared bordered grid "card" used by both Search and Highest Grade
# ------------------------------------------------------------------
def print_student_card(student):
    col_widths = [15, 34]

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

    print(grid_top(col_widths))
    grid_row(
        col_widths,
        [
            f"{Colors.YELLOW}{'FIELD':^15}{Colors.RESET}",
            f"{Colors.YELLOW}{'VALUE':^34}{Colors.RESET}",
        ],
    )
    grid_rule(col_widths)

    for label, value in rows:
        grid_row(col_widths, [f" {label}", f" {value}"])
        grid_rule(col_widths)

    grid_row(col_widths, [" Status", f" {status_display(student['status'])}"])
    print(grid_bottom(col_widths))


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

    print()
    print_message_box("Student successfully added!", Colors.GREEN)
    pause()


def view_all_students():
    clear_screen()
    print_header("ALL STUDENTS")

    if len(students) == 0:
        print_message_box("No students recorded yet.")
        pause()
        return

    print(f"Total Students: {len(students)}\n")

    col_widths = [12, 19, 8, 8]
    print(grid_top(col_widths))
    grid_row(
        col_widths,
        [
            f"{Colors.YELLOW}{'ID':^12}{Colors.RESET}",
            f"{Colors.YELLOW}{'NAME':^19}{Colors.RESET}",
            f"{Colors.YELLOW}{'GRADE':^8}{Colors.RESET}",
            f"{Colors.YELLOW}{'STATUS':^8}{Colors.RESET}",
        ],
    )
    grid_rule(col_widths)

    for index, student in enumerate(students):
        id_cell = f" {student['id'][:col_widths[0] - 1]}"
        name_cell = f" {student['name'][:col_widths[1] - 1]}"
        grade_cell = f" {student['final_grade']:.2f}"
        status_cell = f" {status_display(student['status'])}"

        grid_row(col_widths, [id_cell, name_cell, grade_cell, status_cell])
        if index != len(students) - 1:
            grid_rule(col_widths)

    print(grid_bottom(col_widths))
    pause()


def search_student():
    clear_screen()
    print_header("SEARCH STUDENT")
    student_id = input("Enter Student ID to search: ").strip()
    student = find_student(student_id)

    if student is None:
        print()
        print_message_box("Student not found.", Colors.RED)
        pause()
        return

    print()
    print_student_card(student)
    pause()


def show_highest_grade():
    clear_screen()
    print_header("HIGHEST FINAL GRADE")

    if len(students) == 0:
        print_message_box("No students recorded yet.")
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
        print_message_box("There is no data to reset.")
        pause()
        return

    print(
        f"{Colors.YELLOW}Warning: this will permanently delete all "
        f"{len(students)} student record(s).{Colors.RESET}"
    )
    confirm = input("Are you sure you want to continue? (y/n): ").strip().lower()
    print()

    if confirm == "y":
        students.clear()
        print_message_box("All student data has been reset successfully!", Colors.GREEN)
    else:
        print_message_box("Reset cancelled. No data was changed.", Colors.YELLOW)

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
            print()
            print_message_box("Invalid choice. Please select 1-6.", Colors.RED)
            pause()


if __name__ == "__main__":
    main()