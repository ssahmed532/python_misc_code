#
# Refreshing my knowledge of Python 3.x dictionaries with code based on
# the following article:
#
#   https://towardsdatascience.com/5-expert-tips-to-skyrocket-your-dictionary-skills-in-python-1cf54b7d920d
#

# Creating an empty dictionary
empty_dict = {}
print(empty_dict)


# Standard way to create a dictionary
better_call_saul = {"Jimmy": 33, "Kim": 31, "Gus": 44}
print(better_call_saul)
print(id(better_call_saul))

# Can use the dictionary constructor function
better_call_saul2 = dict([("Jimmy", 33), ("Kim", 31), ("Gus", 44)])
print(better_call_saul2)
print(id(better_call_saul2))

print("Dictionary comparison: better_call_saul == better_call_saul2? ", better_call_saul == better_call_saul2)

better_call_saul2.update({"Saul" : 48})

print("Dictionary comparison: better_call_saul == better_call_saul2? ", better_call_saul == better_call_saul2)


for name in better_call_saul2.keys():
    print(f"name is {name}")


total_age = 0.00
# calculate the average age
for age in better_call_saul2.values():
    total_age += age
print(f"Average age is: {total_age / len(better_call_saul2)}")
print()

print(better_call_saul2.items())
print()

# another way to iterate over items in the dict
for name, age in better_call_saul2.items():
    print(f"{name} is {age} years old.")
print()

try:
    young_guy_age = better_call_saul2["Nacho"]
    print(f"Young guy's age is {young_guy_age}")
except KeyError:
    print("Ooops, no such key exists in better_call_saul2 dict")

# better and safer way to get a value from a dictionary when the key
# may or may not exist.
young_guy_age = better_call_saul2.get("Nacho", -1)
if young_guy_age < 0:
    print("Guy named Nacho doesn't exist in better_call_saul2 dict")

# TODO: also checkout and explore the dict.setdefault() method

# Dictionary comprehensions
squares = {num: (num ** 2) for num in range(10)}
print(f"Squares dictionary: {squares}")
print()


names = ["Shahnawaz", "Salman", "Zeeshan", "Hassan", "Osman", "Zia", "Mustansir"]
name_lengths = {name: len(name) for name in names}
print(f"Names and their lengths: {name_lengths}")
print()


# Merging 2 dictionaries
dict1 = {"a": 1, "b": 2, "c": 3, "d": 4, "e": 5}
dict2 = {"f": 6, "g": 7, "h": 8, "i": 9, "d": 20}
print(f"dict1: {dict1}")
print(f"dict2: {dict2}")
print()
# python < 3.9 syntax / method below:
#dict2.update(dict1)
#print(f"dict2 merged with dict1: {dict2}")
#print()

# Python 3.9 new '|' syntax for merging dictionaries
dict3 = dict1 | dict2
dict4 = dict2 | dict1
print(f"dict3: {dict3}")
print(f"dict4: {dict4}")
