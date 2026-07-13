def logging_decoratorr(func):
    def wrapper():
        print("before the function is called")
        func()
        print("after the function is called")
    return wrapper


@logging_decoratorr
def greet():
    print("Hello, World!")

greet()

@logging_decoratorr
def say_goodbye():
    print("Goodbye, World!")


say_goodbye()