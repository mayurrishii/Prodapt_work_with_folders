# a = int(input("Enter a number: "))
# b = int(input("Enter another number: "))

# div = a/b


def read_file(filename):
    try:
        file = open(filename, 'r')
        data = file.read()
        print(data)
        file.close()
        return dataDay_7/students.txt
    except FileNotFoundError:
        print("File not found.")
        return None
    except IOError:
        print("An error occurred while reading the file.")
    finally:
        if file:
            file.close()

x = input("Enter a file name: ")
read_file(x)