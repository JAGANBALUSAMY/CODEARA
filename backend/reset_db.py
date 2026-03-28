import asyncio
from database import attempts_collection, progress_collection, daily_tasks_collection

async def reset():
    print("Clearing attempts...")
    await attempts_collection.delete_many({})
    print("Clearing progress...")
    await progress_collection.delete_many({})
    print("Clearing daily tasks...")
    await daily_tasks_collection.delete_many({})
    print("Project reset successfully! All learning history has been wiped.")

if __name__ == "__main__":
    asyncio.run(reset())
