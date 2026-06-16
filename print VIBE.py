"""
Student Record Manager
Features:
1. Add new student records (name, ID, three test scores)
2. Automatically calculate average from the three scores
3. Automatically calculate letter grade from average
4. Display all students in a formatted table
5. Show class statistics (highest, lowest, class average)
6. Search for student by name (case-insensitive)
7. Save records to student_grades.txt
8. Load records from student_grades.txt on startup
9. Use ESC to exit from the main menu
"""

import csv
import os
import sys
from dataclasses import dataclass, field
from typing import List, Optional

DATA_FILE = "student_grades.txt"


@dataclass
class Student:
    student_id: str
    name: str
    scores: List[float] = field(default_factory=list)
    average: float = 0.0
    grade: str = "N/A"

    def __post_init__(self) -> None:
        self.recalc()

    def recalc(self) -> None:
        if not self.scores:
            self.average = 0.0
            self.grade = "N/A"
            return
        self.average = sum(self.scores) / len(self.scores)
        if self.average >= 90:
            self.grade = "A"
        elif self.average >= 80:
            self.grade = "B"
        elif self.average >= 70:
            self.grade = "C"
        elif self.average >= 60:
            self.grade = "D"
        else:
            self.grade = "F"

    def formatted_scores(self) -> str:
        return ", ".join(f"{score:.2f}" for score in self.scores)

    def formatted_row(self) -> List[str]:
        # Ensure values exist for three scores
        score_texts = [f"{s:.2f}" for s in self.scores]
        while len(score_texts) < 3:
            score_texts.append("0.0")
        return [self.student_id, self.name, score_texts[0], score_texts[1], score_texts[2], f"{self.average:.2f}", self.grade]


class StudentManager:
    def __init__(self) -> None:
        self.students: List[Student] = []
        self.load_students()

    def add_student(self, student: Student) -> None:
        self.students.append(student)

    def find_by_id(self, student_id: str) -> Optional[Student]:
        student_id = student_id.strip()
        return next((s for s in self.students if s.student_id == student_id), None)

    def search_by_name(self, query: str) -> List[Student]:
        query = query.strip().lower()
        return [s for s in self.students if query in s.name.lower()]

    def class_statistics(self) -> Optional[dict]:
        if not self.students:
            return None
        averages = [s.average for s in self.students]
        return {
            "highest": max(averages),
            "lowest": min(averages),
            "class_average": sum(averages) / len(averages),
        }

    def save_students(self) -> None:
        # Save using pipe-delimited format: name|id|test1|test2|test3|average|grade
        try:
            with open(DATA_FILE, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f, delimiter="|")
                writer.writerow(["name", "id", "test1", "test2", "test3", "average", "grade"])
                for student in self.students:
                    s1 = f"{student.scores[0]:.2f}" if len(student.scores) > 0 else "0.00"
                    s2 = f"{student.scores[1]:.2f}" if len(student.scores) > 1 else "0.00"
                    s3 = f"{student.scores[2]:.2f}" if len(student.scores) > 2 else "0.00"
                    writer.writerow([student.name, student.student_id, s1, s2, s3, f"{student.average:.2f}", student.grade])
            print(f"Saved {len(self.students)} student(s) to {DATA_FILE}.")
        except OSError as e:
            print(f"Error saving students to {DATA_FILE}: {e}")
        except Exception as e:
            print(f"Unexpected error while saving: {e}")

    def load_students(self) -> None:
        if not os.path.exists(DATA_FILE):
            return
        try:
            with open(DATA_FILE, "r", newline="", encoding="utf-8") as f:
                reader = csv.reader(f, delimiter="|")
                rows = list(reader)
                if not rows:
                    return
                # Detect header row (name and id present)
                start = 0
                header = [h.strip().lower() for h in rows[0]]
                if "name" in header and "id" in header:
                    start = 1
                for row in rows[start:]:
                    # Expect at least name,id,score1,score2,score3
                    if len(row) < 5:
                        continue
                    try:
                        name = row[0].strip()
                        sid = row[1].strip()
                        s1 = float(row[2])
                        s2 = float(row[3])
                        s3 = float(row[4])
                        scores = [s1, s2, s3]
                        student = Student(sid, name, scores)
                        self.students.append(student)
                    except (ValueError, IndexError):
                        print(f"Skipping invalid row in {DATA_FILE}: {row}")
                        continue
            print(f"Loaded {len(self.students)} student(s) from {DATA_FILE}.")
        except OSError as e:
            print(f"Error reading {DATA_FILE}: {e}")
        except Exception as e:
            print(f"Unexpected error while loading students: {e}")


def prompt_float(prompt: str) -> float:
    while True:
        value = input(prompt).strip()
        try:
            return float(value)
        except ValueError:
            print("Invalid number. Enter a numeric score.")


def prompt_student() -> Student:
    student_id = input("Student ID: ").strip()
    while not student_id:
        print("Student ID is required.")
        student_id = input("Student ID: ").strip()

    name = input("Student name: ").strip()
    while not name:
        print("Student name is required.")
        name = input("Student name: ").strip()

    scores = []
    for i in range(1, 4):
        scores.append(prompt_float(f"Test {i}: "))

    return Student(student_id=student_id, name=name.title(), scores=scores)


def print_table(rows: List[List[str]]) -> None:
    if not rows:
        print("No records to show.")
        return
    widths = [max(len(value) for value in column) for column in zip(*rows)]
    for row in rows:
        print(" | ".join(value.ljust(widths[i]) for i, value in enumerate(row)))


def show_all_students(manager: StudentManager) -> None:
    headers = ["ID", "Name", "Test 1", "Test 2", "Test 3", "Average", "Grade"]
    rows = [headers] + [student.formatted_row() for student in manager.students]
    print_table(rows)


def show_class_statistics(manager: StudentManager) -> None:
    stats = manager.class_statistics()
    if stats is None:
        print("No student records available.")
        return
    print(f"Highest Average: {stats['highest']:.2f}")
    print(f"Lowest Average:  {stats['lowest']:.2f}")
    print(f"Class Average:   {stats['class_average']:.2f}")


def show_search_results(students: List[Student]) -> None:
    if not students:
        print("No matching students found.")
        return
    headers = ["ID", "Name", "Test 1", "Test 2", "Test 3", "Average", "Grade"]
    rows = [headers] + [student.formatted_row() for student in students]
    print_table(rows)


def show_menu() -> None:
    print("\nStudent Record Manager")
    print("1. Add new student")
    print("2. Display all students")
    print("3. Show class statistics")
    print("4. Search student by name")
    print("ESC. Exit")


def main() -> None:
    manager = StudentManager()
    print("Loaded records from student_grades.txt." if manager.students else "No saved records found.")

    while True:
        show_menu()
        choice = input("Choose an option: ").strip()

        if choice == "1":
            student = prompt_student()
            manager.add_student(student)
            manager.save_students()
            print(f"Student {student.name} added and saved.")

        elif choice == "2":
            show_all_students(manager)

        elif choice == "3":
            show_class_statistics(manager)

        elif choice == "4":
            query = input("Enter name to search: ").strip()
            if not query:
                print("Search query cannot be blank.")
            else:
                matches = manager.search_by_name(query)
                show_search_results(matches)

        elif choice.lower() in {"esc", "exit"}:
            print("Exiting program.")
            sys.exit(0)

        else:
            print("Please choose a valid option.")


if __name__ == "__main__":
    main()
