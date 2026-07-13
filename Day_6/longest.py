def longest_word(text):
    words = text.split()
    x = max(words, key=len)
    return x

x = input("Enter a sentence: ")
result = longest_word(x)
print(f"The longest word in the sentence is: {result}")