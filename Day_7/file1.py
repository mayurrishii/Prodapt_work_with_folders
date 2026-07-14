file = open('Day_7/students.txt', 'r')

data = file.read()
print(data)
file.close()

file = open('Day_7/students.txt', 'a+')
file.write("this is a new line of text.\n")
file.write("this is another new line of text.\n")

file.seek(0)  # Move the cursor to the beginning of the file
print(file.read())
file.close()

# file = open('Day_7/students.txt', 'r')
# x = file.read()
# print(x)
# file.close()