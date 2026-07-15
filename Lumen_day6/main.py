from pathlib import Path

from banking.accounts import create_account, get_balance
from banking.transactions import deposit, transfer, withdraw
from ecommerce.cart import Cart
from ecommerce.payment import process_payment
from lambda_examples import (
    odd_player_ids,
    product_of_dimensions,
    sort_employees_by_score,
    sort_students_by_marks,
    square_readings,
)
from school.results import calculate_grade
from school.students import add_student, view_students
from school.teachers import assign_subject, view_teachers
from shapes.circle import area as circle_area, perimeter as circle_perimeter
from shapes.rectangle import area as rectangle_area, perimeter as rectangle_perimeter
from utilities.file_ops import read_file, search_in_file, write_file
from utilities.math_ops import mean, median, standard_deviation
from utilities.string_ops import count_vowels, remove_punctuation


def demo_shapes():
    print("Shapes Package")
    print("Circle area:", round(circle_area(5), 2))
    print("Circle perimeter:", round(circle_perimeter(5), 2))
    print("Rectangle area:", rectangle_area(10, 4))
    print("Rectangle perimeter:", rectangle_perimeter(10, 4))
    print()


def demo_ecommerce():
    print("Ecommerce Package")
    cart = Cart()
    cart.add_item("Laptop", 50000, 1)
    cart.add_item("Mouse", 800, 2)
    cart.remove_item("Mouse")
    total = cart.calculate_total()
    print("Cart total:", total)
    print(process_payment(total, simulate_success=True))
    print()


def demo_utilities():
    print("Utilities Package")
    text = "Hello, world! Python is fun."
    print("Clean text:", remove_punctuation(text))
    print("Vowel count:", count_vowels(text))

    numbers = [2, 4, 6, 8, 10]
    print("Mean:", mean(numbers))
    print("Median:", median(numbers))
    print("Standard deviation:", round(standard_deviation(numbers), 2))

    sample_file = Path(__file__).parent / "sample_report.txt"
    write_file(sample_file, "Sales report\nRevenue: 15000\nProfit: 3000")
    print("File content:")
    print(read_file(sample_file))
    print("Contains Revenue:", search_in_file(sample_file, "Revenue"))
    print()


def demo_school():
    print("School Package")
    student_list = []
    teacher_list = []
    add_student(student_list, "Asha", 1)
    add_student(student_list, "Bala", 2)
    assign_subject(teacher_list, "Mr. Kumar", "Maths")
    assign_subject(teacher_list, "Ms. Priya", "Science")
    print("Students:", view_students(student_list))
    print("Teachers:", view_teachers(teacher_list))
    print("Grade for 87 marks:", calculate_grade(87))
    print()


def demo_banking():
    print("Banking Package")
    accounts = {}
    create_account(accounts, "A101", "Ravi", 5000)
    create_account(accounts, "A102", "Meena", 2000)
    deposit(accounts, "A101", 1500)
    withdraw(accounts, "A102", 500)
    transfer(accounts, "A101", "A102", 1000)
    print("Balance A101:", get_balance(accounts, "A101"))
    print("Balance A102:", get_balance(accounts, "A102"))
    print()


def demo_lambdas():
    print("Lambda Examples")
    employees = [("Asha", 85), ("Bala", 92), ("Chitra", 78)]
    readings = [2, 3, 4]
    player_ids = [101, 102, 103, 104, 105]
    dimensions = [2, 3, 5]
    students = {"Asha": 78, "Bala": 90, "Chitra": 65}

    print("Sorted employees:", sort_employees_by_score(employees))
    print("Squared readings:", square_readings(readings))
    print("Odd player IDs:", odd_player_ids(player_ids))
    print("Product of dimensions:", product_of_dimensions(dimensions))
    print("Students by marks:", sort_students_by_marks(students))
    print()


def main():
    demo_shapes()
    demo_ecommerce()
    demo_utilities()
    demo_school()
    demo_banking()
    demo_lambdas()


if __name__ == "__main__":
    main()
