import numpy as np
FILENAME = "students.csv"
MAX_MARKS = {"quiz": 30, "project": 40, "lab": 20, "attendance": 10}
GRADE_SCALE = (
    (90, "A+"), (85, "A"), (80, "B+"), (75, "B"),
    (70, "C+"), (65, "C"), (60, "D+"), (50, "D"), (0, "F"),
)
PASS_MARK = 50
CSV_FIELDS = ("student_id", "name", "quiz", "project", "lab", "attendance")
class Student:

    def __init__(self, student_id, name, quiz, project, lab, attendance):
        self.student_id = student_id
        self.name = name
        self.quiz = float(quiz)
        self.project = float(project)
        self.lab = float(lab)
        self.attendance = float(attendance)

    def total(self):
        return self.quiz + self.project + self.lab + self.attendance

    def grade(self):
        total = self.total()
        for minimum, letter in GRADE_SCALE:
            if total >= minimum:
                return letter
        return "F"

    def is_passing(self):
        return self.total() >= PASS_MARK

    def has_valid_marks(self):
        if self.quiz < 0 or self.quiz > MAX_MARKS["quiz"]:
            return False
        if self.project < 0 or self.project > MAX_MARKS["project"]:
            return False
        if self.lab < 0 or self.lab > MAX_MARKS["lab"]:
            return False
        if self.attendance < 0 or self.attendance > MAX_MARKS["attendance"]:
            return False
        return True

    def to_csv_line(self):
        return (f"{self.student_id},{self.name},{self.quiz},"
                f"{self.project},{self.lab},{self.attendance}")

    def __str__(self):
        return (f"{self.student_id:<6} {self.name:<18} "
                f"{self.total():>6.1f}  {self.grade():<3} "
                f"{'Pass' if self.is_passing() else 'Fail'}")

class StudentManager:

    def __init__(self, filename=FILENAME):
        self.filename = filename
        self.students = []
        self.id_set = set()

    def load_from_file(self):
        self.students = []
        self.id_set = set()

        try:
            with open(self.filename, "r") as file:
                file.readline()
                line_no = 1

                for line in file:
                    line_no = line_no + 1
                    line = line.strip()
                    if line == "":
                        continue

                    parts = line.split(",")
                    if len(parts) != 6:
                        print(f"Warning: line {line_no} needs 6 values, skipped.")
                        continue

                    try:
                        student = Student(parts[0].strip(), parts[1].strip(),
                                          parts[2], parts[3], parts[4], parts[5])
                    except ValueError:
                        print(f"Warning: line {line_no} has a non-numeric mark, skipped.")
                        continue

                    if student.student_id == "" or student.name == "":
                        print(f"Warning: line {line_no} has an empty ID or name, skipped.")
                        continue

                    if not student.has_valid_marks():
                        print(f"Warning: line {line_no} has a mark out of range, skipped.")
                        continue

                    if student.student_id in self.id_set:
                        print(f"Warning: line {line_no} repeats ID {student.student_id}, skipped.")
                        continue

                    self.students.append(student)
                    self.id_set.add(student.student_id)

        except FileNotFoundError:
            print(f"File '{self.filename}' not found. Starting with no records.")
        except OSError:
            print(f"Could not read '{self.filename}'. Starting with no records.")

        if len(self.students) == 0:
            print("No records loaded.")
        else:
            print(f"{len(self.students)} record(s) loaded.")

    def save_to_file(self):
        try:
            with open(self.filename, "w") as file:
                file.write(",".join(CSV_FIELDS) + "\n")
                for student in self.students:
                    file.write(student.to_csv_line() + "\n")
            return True
        except OSError:
            print("Error: could not save the data file.")
            return False

    def find_student(self, student_id):
        for student in self.students:
            if student.student_id == student_id:
                return student
        return None
    def search_by_name(self, text):
        text = text.lower()
        results = []
        for student in self.students:
            if text in student.name.lower():
                results.append(student)
        return results
    def add_student(self, student):
        if student.student_id in self.id_set:
            return False
        self.students.append(student)
        self.id_set.add(student.student_id)
        self.save_to_file()
        return True
    def update_mark(self, student_id, component, new_value):
        student = self.find_student(student_id)
        if student is None:
            return False
        if component == "quiz":
            student.quiz = float(new_value)
        elif component == "project":
            student.project = float(new_value)
        elif component == "lab":
            student.lab = float(new_value)
        elif component == "attendance":
            student.attendance = float(new_value)
        else:
            return False
        self.save_to_file()
        return True
    def delete_student(self, student_id):
        student = self.find_student(student_id)
        if student is None:
            return False
        self.students.remove(student)
        self.id_set.remove(student_id)
        self.save_to_file()
        return True

    def get_summary(self):
        if len(self.students) == 0:
            return None

        totals = []
        for student in self.students:
            totals.append(student.total())
        totals = np.array(totals)

        passed = totals >= PASS_MARK
        pass_count = int(np.sum(passed))

        summary = {
            "count": len(totals),
            "mean": np.mean(totals),
            "median": np.median(totals),
            "highest": np.max(totals),
            "lowest": np.min(totals),
            "std": np.std(totals),
            "pass_count": pass_count,
            "pass_rate": pass_count / len(totals) * 100,
        }
        return summary

    def component_averages(self):
        if len(self.students) == 0:
            return None

        rows = []
        for student in self.students:
            rows.append([student.quiz, student.project,
                         student.lab, student.attendance])
        data = np.array(rows)

        averages = np.mean(data, axis=0)

        result = {}
        index = 0
        for name in MAX_MARKS:
            result[name] = averages[index]
            index = index + 1
        return result

    def grade_distribution(self):
        counts = {}
        for minimum, letter in GRADE_SCALE:
            counts[letter] = 0

        for student in self.students:
            letter = student.grade()
            counts[letter] = counts[letter] + 1
        return counts

    def at_risk_students(self):
        at_risk = []
        for student in self.students:
            if not student.is_passing():
                at_risk.append(student)
        return at_risk

    def top_students(self, n):
        remaining = []
        for student in self.students:
            remaining.append(student)

        top = []
        while len(top) < n and len(remaining) > 0:
            best = remaining[0]
            for student in remaining:
                if student.total() > best.total():
                    best = student
            top.append(best)
            remaining.remove(best)
        return top


def get_text(prompt):
    while True:
        value = input(prompt).strip()
        if value == "":
            print("Error: this field cannot be empty.")
        elif "," in value:
            print("Error: commas are not allowed.")
        else:
            return value


def get_number(prompt, minimum, maximum):
    while True:
        try:
            value = float(input(prompt))
        except ValueError:
            print("Error: please enter a number.")
            continue
        if not (minimum <= value <= maximum):
            print(f"Error: value must be between {minimum} and {maximum}.")
        else:
            return value


def get_menu_choice(low, high):
    while True:
        text = input(f"Enter your choice ({low}-{high}): ")
        try:
            choice = int(text)
        except ValueError:
            print("Error: please enter a whole number.")
            continue
        if choice < low or choice > high:
            print(f"Error: choose a number from {low} to {high}.")
        else:
            return choice


def get_id(prompt):
    return get_text(prompt).upper()


def get_new_id(manager):
    while True:
        student_id = get_id("Enter new student ID: ")
        if student_id in manager.id_set:
            print("Error: this ID already exists.")
        else:
            return student_id


def get_component():
    names = []
    for name in MAX_MARKS:
        names.append(name)

    number = 1
    for name in names:
        print(f"  {number}. {name} (max {MAX_MARKS[name]})")
        number = number + 1

    choice = get_menu_choice(1, len(names))
    return names[choice - 1]


def show_menu():
    print()
    print("========== EduTrack ==========")
    print(" 1. Add student")
    print(" 2. View all students")
    print(" 3. Search student")
    print(" 4. Update a mark")
    print(" 5. Delete student")
    print(" 6. Class summary")
    print(" 7. Grade distribution")
    print(" 8. At-risk and top students")
    print(" 9. Save data")
    print("10. Reload data from file")
    print(" 0. Exit")

def print_table(students):
    if len(students) == 0:
        print("No students to show.")
        return
    print(f"{'ID':<6} {'Name':<18} {'Total':>6}  {'Gr':<3} Status")
    print("-" * 45)
    for student in students:
        print(student)

def add_student_option(manager):
    student_id = get_new_id(manager)
    name = get_text("Enter name: ")
    quiz = get_number(f"Enter quiz mark (0-{MAX_MARKS['quiz']}): ",
                      0, MAX_MARKS["quiz"])
    project = get_number(f"Enter project mark (0-{MAX_MARKS['project']}): ",
                         0, MAX_MARKS["project"])
    lab = get_number(f"Enter lab mark (0-{MAX_MARKS['lab']}): ",
                     0, MAX_MARKS["lab"])
    attendance = get_number(f"Enter attendance mark (0-{MAX_MARKS['attendance']}): ",
                            0, MAX_MARKS["attendance"])

    student = Student(student_id, name, quiz, project, lab, attendance)
    if manager.add_student(student):
        print("Student added and saved.")
    else:
        print("Error: could not add the student.")


def search_option(manager):
    print("1. Search by ID")
    print("2. Search by name")
    choice = get_menu_choice(1, 2)

    if choice == 1:
        student_id = get_id("Enter student ID: ")
        student = manager.find_student(student_id)
        if student is None:
            print("No student found with that ID.")
        else:
            print_table([student])
    else:
        text = get_text("Enter part of the name: ")
        results = manager.search_by_name(text)
        if len(results) == 0:
            print("No student found with that name.")
        else:
            print_table(results)


def update_option(manager):
    student_id = get_id("Enter student ID to update: ")
    student = manager.find_student(student_id)
    if student is None:
        print("No student found with that ID.")
        return

    print_table([student])
    component = get_component()
    new_value = get_number(
        f"Enter new {component} mark (0-{MAX_MARKS[component]}): ",
        0, MAX_MARKS[component])

    manager.update_mark(student_id, component, new_value)
    print("Mark updated and saved.")
    print_table([student])


def delete_option(manager):
    student_id = get_id("Enter student ID to delete: ")
    student = manager.find_student(student_id)
    if student is None:
        print("No student found with that ID.")
        return

    print_table([student])
    print("Delete this student?")
    print("1. Yes")
    print("2. No")
    if get_menu_choice(1, 2) == 1:
        manager.delete_student(student_id)
        print("Student deleted and saved.")
    else:
        print("Delete cancelled.")


def summary_option(manager):
    summary = manager.get_summary()
    if summary is None:
        print("No data to analyze.")
        return

    print("---------- Class Summary ----------")
    print(f"Students  : {summary['count']}")
    print(f"Mean      : {summary['mean']:.2f}")
    print(f"Median    : {summary['median']:.2f}")
    print(f"Highest   : {summary['highest']:.1f}")
    print(f"Lowest    : {summary['lowest']:.1f}")
    print(f"Std dev   : {summary['std']:.2f}")
    print(f"Pass rate : {summary['pass_rate']:.1f}% ({summary['pass_count']} passed)")

    print("Average mark per component:")
    averages = manager.component_averages()
    for name in averages:
        print(f"  {name:<11}: {averages[name]:.2f} / {MAX_MARKS[name]}")


def distribution_option(manager):
    if len(manager.students) == 0:
        print("No data to analyze.")
        return

    counts = manager.grade_distribution()
    print("---------- Grade Distribution ----------")
    for letter in counts:
        print(f"{letter:<3} {'#' * int(counts[letter])} {counts[letter]}")


def risk_and_top_option(manager):
    if len(manager.students) == 0:
        print("No data to analyze.")
        return

    print("---------- At-risk students (below pass mark) ----------")
    at_risk = manager.at_risk_students()
    if len(at_risk) == 0:
        print("None. Every student is passing.")
    else:
        print_table(at_risk)

    print()
    print("---------- Top 3 students ----------")
    print_table(manager.top_students(3))


def save_option(manager):
    if manager.save_to_file():
        print(f"Data saved to {manager.filename}.")


def main():
    manager = StudentManager()
    manager.load_from_file()

    try:
        while True:
            show_menu()
            choice = get_menu_choice(0, 10)

            if choice == 1:
                add_student_option(manager)
            elif choice == 2:
                print_table(manager.students)
            elif choice == 3:
                search_option(manager)
            elif choice == 4:
                update_option(manager)
            elif choice == 5:
                delete_option(manager)
            elif choice == 6:
                summary_option(manager)
            elif choice == 7:
                distribution_option(manager)
            elif choice == 8:
                risk_and_top_option(manager)
            elif choice == 9:
                save_option(manager)
            elif choice == 10:
                manager.load_from_file()
            else:
                print("Goodbye!")
                break
    except (KeyboardInterrupt, EOFError):
        print()
        print("Program interrupted. Your data is already saved.")


if __name__ == "__main__":
    main()