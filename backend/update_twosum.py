import asyncio
from database import levels_collection

async def update():
    new_test_cases = [
        {"input": "([2, 7, 11, 15], 9)", "expected": "[0, 1]"},
        {"input": "([3, 2, 4], 6)", "expected": "[1, 2]"},
        {"input": "([3, 3], 6)", "expected": "[0, 1]"},
        {"input": "([1, 5, 3], 8)", "expected": "[1, 2]"}
    ]
    result = await levels_collection.update_one(
        {"title": "Two Sum Problem"},
        {"$set": {"test_cases": new_test_cases}}
    )
    print(f"Updated Two Sum test cases: {result.modified_count} document(s) modified")

if __name__ == "__main__":
    asyncio.run(update())
