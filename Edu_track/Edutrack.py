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

#temporary test data till now

if __name__ == "__main__":
    manager = StudentManager()
    manager.load_from_file()
    for s in manager.students:
        print(s)
    manager.save_to_file()