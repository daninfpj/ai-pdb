from collections import defaultdict
from typing import Dict, List

from ai_pdb.ai_pdb import AIPdb

debugger = AIPdb()


def process_grades(students: List[str], grades: List[int]) -> Dict[str, List[int]]:
    grade_book = defaultdict(int)  # Misuse: should be defaultdict(list)

    for student, grade in zip(students, grades):
        grade_book[student] += grade  # This will raise a TypeError

    return grade_book


def calculate_average(grade_book: Dict[str, List[int]]) -> Dict[str, float]:
    return {
        student: sum(grades) / len(grades) for student, grades in grade_book.items()
    }


def main():
    students = ["Alice", "Bob", "Charlie"]
    grades = [85, 92, 78]

    try:
        grade_book = process_grades(students, grades)
        debugger.set_trace()
        averages = calculate_average(grade_book)
        print("Average grades:", averages)
    except Exception as e:
        print(f"An error occurred: {e}")
        debugger.set_trace()


if __name__ == "__main__":
    main()
