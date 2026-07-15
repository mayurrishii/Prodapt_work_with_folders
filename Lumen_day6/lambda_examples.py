from functools import reduce


def sort_employees_by_score(employees):
    return sorted(employees, key=lambda item: item[1], reverse=True)


def square_readings(readings):
    return list(map(lambda value: value ** 2, readings))


def odd_player_ids(player_ids):
    return list(filter(lambda value: value % 2 != 0, player_ids))


def product_of_dimensions(dimensions):
    return reduce(lambda left, right: left * right, dimensions)


def sort_students_by_marks(students):
    return sorted(students.items(), key=lambda item: item[1], reverse=True)
