import os
import re
import sys

# Enable ANSI color rendering on Windows terminals
if os.name == "nt":
    os.system("")

# ------------------------------------------------------------------
# Configuration & Constants
# ------------------------------------------------------------------

LAYOUT_MODE = "auto"       # "auto", "mobile", or "laptop"
CENTER_ON_LAPTOP = False   # Set True to center boxes on wide laptop screens

SCHOOL_NAME = "METRO BUSINESS COLLEGE"
PROJECT_TITLE = "STUDENT INFORMATION & GRADE MANAGEMENT SYSTEM"
MENU_SUBTITLE = "STUDENT GRADE MANAGEMENT"
PASSING_GRADE = 75

students = []  # In-memory database


class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    CYAN = "\033[36m"
    WHITE = "\033[97m"


ANSI_RE = re.compile(r"\033\[[0-9;]*m")


def visible_len(text):
    return len(ANSI_RE.sub("", text))


# ------------------------------------------------------------------
# Responsive Layout Helpers
# ------------------------------------------------------------------


def is_mobile():
    if LAYOUT_MODE == "mobile":
        return True
    if LAYOUT_MODE == "laptop":
        return False

    if any(k in os.environ for k in ("ANDROID_ROOT", "ANDROID_DATA", "TERMUX_VERSION")):
        return True
    if hasattr(sys, "getandroidapilevel"):
        return True

    try:
        cols, _ = os.get_terminal_size()
        if cols < 50:
            return True
    except Exception:
        pass

    return False


def get_layout_widths():
    return (32, 30) if is_mobile() else (52, 50)


def get_margin():
    if is_mobile():
        try:
            term_w = os.get_terminal_size().columns
            if 34 <= term_w <= 48:
                return " " * max((term_w - 32) // 2, 0)
        except Exception:
            pass
        return "  "

    if CENTER_ON_LAPTOP:
        try:
            term_w = os.get_terminal_size().columns
            if term_w > 52:
                return " " * max((term_w - 52) // 2, 0)
        except Exception:
            pass

    return ""


def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def pause():
    prompt = "Press Enter to continue..." if is_mobile() else "Press Enter to return to the menu..."
    input(f"\n{get_margin()}{Colors.CYAN}{prompt}{Colors.RESET}")


# ------------------------------------------------------------------
# Box & Border Helpers
# ------------------------------------------------------------------


def box_top(left="┌", right="┐"):
    _, inner_width = get_layout_widths()
    return f"{get_margin()}{Colors.WHITE}{left}{'─' * inner_width}{right}{Colors.RESET}"


def box_bottom():
    return box_top(left="└", right="┘")


def box_divider(left="├", right="┤"):
    _, inner_width = get_layout_widths()
    return f"{get_margin()}{Colors.WHITE}{left}{'─' * inner_width}{right}{Colors.RESET}"


def box_row(visible_text="", display_text=None, align="left"):
    _, inner_width = get_layout_widths()
    if display_text is None:
        display_text = visible_text

    # Auto-wrap words exceeding container width
    v_len = visible_len(visible_text)
    if v_len > inner_width:
        words = visible_text.split()
        lines = []
        curr = ""
        for w in words:
            if not curr:
                curr = w
            elif len(curr) + 1 + len(w) <= inner_width:
                curr += " " + w
            else:
                lines.append(curr)
                curr = w
        if curr:
            lines.append(curr)

        for line in lines:
            box_row(line, align=align)
        return

    padding = max(inner_width - v_len, 0)
    if align == "center":
        left_pad = padding // 2
        right_pad = padding - left_pad
        row = (" " * left_pad) + display_text + (" " * right_pad)
    else:
        row = display_text + (" " * padding)

    print(f"{get_margin()}{Colors.WHITE}│{Colors.RESET}{row}{Colors.WHITE}│{Colors.RESET}")


def print_header(section_title):
    print(box_top())
    box_row(SCHOOL_NAME, align="center")
    print(box_divider())
    box_row(PROJECT_TITLE, align="center")
    print(box_bottom())
    print()

    print(box_top())
    box_row(section_title, align="center")
    print(box_bottom())
    print()


def print_message_box(text, color=None):
    disp = text if color is None else f"{color}{text}{Colors.RESET}"
    print(box_top())
    box_row(text, disp, align="center")
    print(box_bottom())


# ------------------------------------------------------------------
# Grid / Table Helpers
# ------------------------------------------------------------------


def grid_border(col_widths, left, mid, right):
    parts = ["─" * w for w in col_widths]
    return f"{get_margin()}{Colors.WHITE}{left}{mid.join(parts)}{right}{Colors.RESET}"


def grid_top(col_widths):
    return grid_border(col_widths, "┌", "┬", "┐")


def grid_divider(col_widths):
    return grid_border(col_widths, "├", "┼", "┤")


def grid_bottom(col_widths):
    return grid_border(col_widths, "└", "┴", "┘")


def grid_row(col_widths, cells):
    sep = f"{Colors.WHITE}│{Colors.RESET}"
    parts = []
    for width, cell in zip(col_widths, cells):
        v_len = visible_len(cell)
        if v_len > width:
            plain = ANSI_RE.sub("", cell)
            if plain == cell:
                cell = cell[:width]
                v_len = len(cell)
        pad = max(width - v_len, 0)
        parts.append(cell + " " * pad)
    print(get_margin() + sep + sep.join(parts) + sep)


def status_display(status, width=None):
    text = status if width is None else f"{status:<{width}}"
    color = Colors.GREEN if "PASS" in status else Colors.RED
    return f"{color}{text}{Colors.RESET}"


def print_field_table(rows, closing_row=None):
    if is_mobile():
        col_widths = [12, 17]
        h_field = f"{Colors.YELLOW}{'FIELD':^12}{Colors.RESET}"
        h_value = f"{Colors.YELLOW}{'VALUE':^17}{Colors.RESET}"
    else:
        col_widths = [15, 34]
        h_field = f"{Colors.YELLOW}{'FIELD':^15}{Colors.RESET}"
        h_value = f"{Colors.YELLOW}{'VALUE':^34}{Colors.RESET}"

    last_index = len(rows) - 1

    print(grid_top(col_widths))
    grid_row(col_widths, [h_field, h_value])
    print(grid_divider(col_widths))

    for index, (label, value) in enumerate(rows):
        val_str = str(value)
        max_v = col_widths[1] - 2
        if len(val_str) > max_v:
            val_str = val_str[:max_v - 1] + "…"
        grid_row(col_widths, [f" {label}", f" {val_str}"])
        if index != last_index or closing_row is not None:
            print(grid_divider(col_widths))

    if closing_row is not None:
        label, value = closing_row
        grid_row(col_widths, [f" {label}", f" {value}"])

    print(grid_bottom(col_widths))


def print_student_card(student):
    avg_label = "Quiz Avg" if is_mobile() else "Quiz Average"
    rows = [
        ("Student ID", student["id"]),
        ("Name", student["name"]),
        ("Course", student["course"]),
        ("Quiz 1", f"{student['quiz1']:.2f}"),
        ("Quiz 2", f"{student['quiz2']:.2f}"),
        ("Quiz 3", f"{student['quiz3']:.2f}"),
        (avg_label, f"{student['quiz_avg']:.2f}"),
        ("Assignment", f"{student['assignment']:.2f}"),
        ("Project", f"{student['project']:.2f}"),
        ("Final Exam", f"{student['final_exam']:.2f}"),
        ("Final Grade", f"{student['final_grade']:.2f}"),
    ]
    print_field_table(rows, closing_row=("Status", status_display(student["status"])))


# ------------------------------------------------------------------
# Menu Display (Strict 5-Option Format)
# ------------------------------------------------------------------


def print_menu():
    print(box_top())
    box_row(SCHOOL_NAME, align="center")
    print(box_divider())
    box_row(PROJECT_TITLE, align="center")
    print(box_bottom())
    print()

    print(box_top())
    box_row(MENU_SUBTITLE, align="center")
    print(box_bottom())
    print()

    if is_mobile():
        col_widths = [6, 23]
        header_opt = f"{Colors.YELLOW}{'OPT':^6}{Colors.RESET}"
        header_action = f"{Colors.YELLOW}{'MENU ACTION':^23}{Colors.RESET}"
        key_fmt = lambda k: f"{Colors.YELLOW}{k:^6}{Colors.RESET}"
    else:
        col_widths = [10, 39]
        header_opt = f"{Colors.YELLOW}{'OPTION':^10}{Colors.RESET}"
        header_action = f"{Colors.YELLOW}{'MENU ACTION':^39}{Colors.RESET}"
        key_fmt = lambda k: f"{Colors.YELLOW}{k:^10}{Colors.RESET}"

    menu_items = [
        ("[1]", "Add Student"),
        ("[2]", "View All Students"),
        ("[3]", "Search Student"),
        ("[4]", "Show Highest Grade"),
        ("[5]", "Exit"),
    ]

    print(grid_top(col_widths))
    grid_row(col_widths, [header_opt, header_action])
    print(grid_divider(col_widths))

    for index, (key, label) in enumerate(menu_items):
        grid_row(col_widths, [key_fmt(key), f" {label}"])
        if index != len(menu_items) - 1:
            print(grid_divider(col_widths))

    print(grid_bottom(col_widths))
    print()


# ------------------------------------------------------------------
# Validation Helpers
# ------------------------------------------------------------------


def find_student(student_id):
    for student in students:
        if student["id"].lower() == student_id.lower():
            return student
    return None


def get_unique_student_id():
    margin = get_margin()
    while True:
        student_id = input(f"{margin}Student ID: ").strip()
        if student_id == "":
            print(f"\n{margin}{Colors.RED}ERROR: Student ID cannot be empty.{Colors.RESET}\n")
            continue
        if find_student(student_id) is not None:
            print(f"\n{margin}{Colors.RED}ERROR: Student ID already exists.{Colors.RESET}\n")
            continue
        return student_id


def get_valid_grade(prompt):
    margin = get_margin()
    while True:
        raw_value = input(f"{margin}{prompt}")
        try:
            grade = float(raw_value)
        except ValueError:
            print(f"\n{margin}{Colors.RED}ERROR: Please enter a valid number.{Colors.RESET}\n")
            continue

        if not (0 <= grade <= 100):
            print(f"\n{margin}{Colors.RED}ERROR: Grade must be between 0 and 100.{Colors.RESET}\n")
            continue

        return grade


def get_non_empty_text(prompt):
    margin = get_margin()
    while True:
        value = input(f"{margin}{prompt}").strip()
        if value == "":
            print(f"\n{margin}{Colors.RED}ERROR: This field cannot be empty.{Colors.RESET}\n")
            continue
        return value


# ------------------------------------------------------------------
# Grade Computation Functions
# ------------------------------------------------------------------


def calculate_quiz_average(quiz1, quiz2, quiz3):
    return round((quiz1 + quiz2 + quiz3) / 3, 2)


def calculate_final_grade(quiz_avg, assignment, project, final_exam):
    return round(
        (quiz_avg * 0.30)
        + (assignment * 0.10)
        + (project * 0.20)
        + (final_exam * 0.40),
        2,
    )


def get_status(final_grade):
    return "PASSED" if final_grade >= PASSING_GRADE else "FAILED"


# ------------------------------------------------------------------
# Primary Features
# ------------------------------------------------------------------


def add_student():
    clear_screen()
    print_header("ADD STUDENT")

    print(box_top())
    box_row("STUDENT DETAILS", align="center")
    print(box_bottom())
    print()

    student_id = get_unique_student_id()
    name = get_non_empty_text("Student Name: ")
    course = get_non_empty_text("Course: ")

    # Advance to grades screen
    input(f"\n{get_margin()}{Colors.CYAN}Press Enter to proceed to grades...{Colors.RESET}")
    clear_screen()
    print_header("ADD STUDENT")

    print(box_top())
    box_row("GRADES", align="center")
    print(box_bottom())
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

    # Show calculated card
    clear_screen()
    print_header("STUDENT SUMMARY")
    print_student_card(student)
    print()
    print_message_box("Student successfully added!", Colors.GREEN)
    pause()


def view_all_students():
    clear_screen()
    print_header("ALL STUDENTS")

    if not students:
        print_message_box("No students recorded yet.")
        pause()
        return

    print(f"{get_margin()}Total Students: {len(students)}\n")

    if is_mobile():
        col_widths = [6, 8, 6, 7]
        headers = [
            f"{Colors.YELLOW}{'ID':^6}{Colors.RESET}",
            f"{Colors.YELLOW}{'NAME':^8}{Colors.RESET}",
            f"{Colors.YELLOW}{'GRD':^6}{Colors.RESET}",
            f"{Colors.YELLOW}{'STAT':^7}{Colors.RESET}",
        ]
    else:
        col_widths = [12, 19, 8, 8]
        headers = [
            f"{Colors.YELLOW}{'ID':^12}{Colors.RESET}",
            f"{Colors.YELLOW}{'NAME':^19}{Colors.RESET}",
            f"{Colors.YELLOW}{'GRADE':^8}{Colors.RESET}",
            f"{Colors.YELLOW}{'STATUS':^8}{Colors.RESET}",
        ]

    print(grid_top(col_widths))
    grid_row(col_widths, headers)
    print(grid_divider(col_widths))

    for index, student in enumerate(students):
        if is_mobile():
            id_cell = f" {student['id'][:col_widths[0] - 1]}"
            name_cell = f" {student['name'][:col_widths[1] - 1]}"
            grade_cell = f"{student['final_grade']:^6.1f}"
            short_stat = "PASS" if student["status"] == "PASSED" else "FAIL"
            status_cell = f" {status_display(short_stat)}"
        else:
            id_cell = f" {student['id'][:col_widths[0] - 1]}"
            name_cell = f" {student['name'][:col_widths[1] - 1]}"
            grade_cell = f" {student['final_grade']:.2f}"
            status_cell = f" {status_display(student['status'])}"

        grid_row(col_widths, [id_cell, name_cell, grade_cell, status_cell])
        if index != len(students) - 1:
            print(grid_divider(col_widths))

    print(grid_bottom(col_widths))
    pause()


def search_student():
    clear_screen()
    print_header("SEARCH STUDENT")
    student_id = input(f"{get_margin()}Enter Student ID to search: ").strip()
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

    if not students:
        print_message_box("No students recorded yet.")
        pause()
        return

    top_student = max(students, key=lambda s: s["final_grade"])
    print_student_card(top_student)
    pause()


# ------------------------------------------------------------------
# Main Loop
# ------------------------------------------------------------------


def main():
    while True:
        clear_screen()
        print_menu()
        choice = input(f"{get_margin()}{Colors.BOLD}Enter choice: {Colors.RESET}").strip()

        if choice == "1":
            add_student()
        elif choice == "2":
            view_all_students()
        elif choice == "3":
            search_student()
        elif choice == "4":
            show_highest_grade()
        elif choice == "5":
            clear_screen()
            print(
                f"{get_margin()}{Colors.GREEN}Thank you for using the {SCHOOL_NAME} "
                f"Grade Management System. Goodbye!{Colors.RESET}"
            )
            break
        else:
            print()
            print_message_box("Invalid choice. Please select 1-5.", Colors.RED)
            pause()


if __name__ == "__main__":
    main()