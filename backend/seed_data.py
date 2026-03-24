from database import levels_collection
from bson import ObjectId


LEVELS_DATA = [
    {
        "_id": ObjectId(),
        "title": "Array Basics",
        "difficulty": "easy",
        "concept": "Arrays are ordered collections of elements. In Python, we use lists to represent arrays. Each element has an index starting from 0.",
        "problem": "Write a function 'sum_array(arr)' that takes a list of numbers and returns the sum of all elements.",
        "starter_code": "def sum_array(arr):\n    # Write your code here\n    pass",
        "solution": "def sum_array(arr):\n    total = 0\n    for num in arr:\n        total += num\n    return total",
        "test_cases": [
            {"input": "[1, 2, 3, 4, 5]", "expected": "15"},
            {"input": "[10, 20, 30]", "expected": "60"},
            {"input": "[]", "expected": "0"},
            {"input": "[7]", "expected": "7"}
        ]
    },
    {
        "_id": ObjectId(),
        "title": "Find Maximum",
        "difficulty": "easy",
        "concept": "Finding the maximum value in an array is a common operation. You can iterate through the array and keep track of the largest value found.",
        "problem": "Write a function 'find_max(arr)' that takes a list of numbers and returns the maximum value. Assume the array is non-empty.",
        "starter_code": "def find_max(arr):\n    # Write your code here\n    pass",
        "solution": "def find_max(arr):\n    max_val = arr[0]\n    for num in arr[1:]:\n        if num > max_val:\n            max_val = num\n    return max_val",
        "test_cases": [
            {"input": "[1, 5, 3, 9, 2]", "expected": "9"},
            {"input": "[10, 10, 10]", "expected": "10"},
            {"input": "[-5, -3, -1]", "expected": "-1"},
            {"input": "[42]", "expected": "42"}
        ]
    },
    {
        "_id": ObjectId(),
        "title": "Array Reversal",
        "difficulty": "medium",
        "concept": "Reversing an array means changing the order of elements so that the first becomes last, second becomes second-to-last, etc. Python has built-in reversal, but let's implement it manually.",
        "problem": "Write a function 'reverse_array(arr)' that takes a list and returns a new list with elements in reverse order.",
        "starter_code": "def reverse_array(arr):\n    # Write your code here\n    pass",
        "solution": "def reverse_array(arr):\n    result = []\n    for i in range(len(arr) - 1, -1, -1):\n        result.append(arr[i])\n    return result",
        "test_cases": [
            {"input": "[1, 2, 3, 4, 5]", "expected": "[5, 4, 3, 2, 1]"},
            {"input": "['a', 'b', 'c']", "expected": "['c', 'b', 'a']"},
            {"input": "[1]", "expected": "[1]"},
            {"input": "[]", "expected": "[]"}
        ]
    },
    {
        "_id": ObjectId(),
        "title": "Two Sum Problem",
        "difficulty": "medium",
        "concept": "The Two Sum problem is a classic. Given an array and a target, find two numbers that add up to the target and return their indices.",
        "problem": "Write a function 'two_sum(arr, target)' that takes a list of numbers and a target sum. Return the indices of two numbers that add up to the target. Assume exactly one solution exists.",
        "starter_code": "def two_sum(arr, target):\n    # Write your code here\n    # Return indices as a list [i, j]\n    pass",
        "solution": "def two_sum(arr, target):\n    for i in range(len(arr)):\n        for j in range(i + 1, len(arr)):\n            if arr[i] + arr[j] == target:\n                return [i, j]\n    return []",
        "test_cases": [
            {"input": "([2, 7, 11, 15], 9)", "expected": "[0, 1]"},
            {"input": "([3, 2, 4], 6)", "expected": "[1, 2]"},
            {"input": "([3, 3], 6)", "expected": "[0, 1]"},
            {"input": "([1, 5, 3], 8)", "expected": "[1, 2]"}
        ]
    },
    {
        "_id": ObjectId(),
        "title": "Remove Duplicates",
        "difficulty": "hard",
        "concept": "Working with duplicates is common. Given a sorted array, remove duplicates in-place and return the new length.",
        "problem": "Write a function 'remove_duplicates(arr)' that takes a sorted list and removes duplicates in place. Return the new length of the array after removing duplicates.",
        "starter_code": "def remove_duplicates(arr):\n    # Write your code here\n    # Return the new length\n    pass",
        "solution": "def remove_duplicates(arr):\n    if not arr:\n        return 0\n    write = 0\n    for read in range(1, len(arr)):\n        if arr[read] != arr[write]:\n            write += 1\n            arr[write] = arr[read]\n    return write + 1",
        "test_cases": [
            {"input": "[1, 1, 2]", "expected": "2"},
            {"input": "[1, 1, 2, 2, 3]", "expected": "3"},
            {"input": "[1, 1, 1, 1]", "expected": "1"},
            {"input": "[1, 2, 3, 4]", "expected": "4"}
        ]
    }
]


async def seed_database():
    count = await levels_collection.count_documents({})
    
    if count == 0:
        await levels_collection.insert_many(LEVELS_DATA)
        print("Database seeded with 5 array levels")
    else:
        print(f"Database already has {count} levels")
