from math import sqrt


def mean(numbers):
    return sum(numbers) / len(numbers)


def median(numbers):
    sorted_numbers = sorted(numbers)
    middle = len(sorted_numbers) // 2
    if len(sorted_numbers) % 2 == 0:
        return (sorted_numbers[middle - 1] + sorted_numbers[middle]) / 2
    return sorted_numbers[middle]


def standard_deviation(numbers):
    avg = mean(numbers)
    variance = sum((number - avg) ** 2 for number in numbers) / len(numbers)
    return sqrt(variance)
