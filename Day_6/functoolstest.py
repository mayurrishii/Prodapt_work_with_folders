# from functools import reduce
# numbers = [1, 2, 3, 4]
# result = reduce(lambda x, y: x * y, numbers)
# print(result)


# #partial
# from functools import partial

# multiply = lambda x, y: x * y
# double = partial(multiply, y=2)
# print(double(5))  # Output: 10

# from functools import lru_cache #used to cache the results of a function to improve performance for expensive or frequently called functions.

# @lru_cache(maxsize=None)
# def square(n):
#     print("Calculating ........")
#     return n * n

# print(square(4))  # Output: 16



from functools import cmp_to_key

def compare(a,b):
    return b-a

nums = [3,1,4,2]

sorted_nums = sorted(nums, key=cmp_to_key(compare))
print(sorted_nums)  # Output: [4, 3, 2, 1]