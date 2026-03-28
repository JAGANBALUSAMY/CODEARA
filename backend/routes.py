from fastapi import APIRouter, HTTPException
from typing import List, Optional
from datetime import datetime
from bson import ObjectId
import json

from database import (
    levels_collection,
    attempts_collection,
    progress_collection,
    daily_tasks_collection
)
from models import (
    Level,
    ExecuteRequest,
    ExecuteResponse,
    TestResult,
    SubmitRequest,
    Progress,
    DailyTask,
    TestCase,
    FeedbackRequest
)
from executor import execute_user_code
from ai_service import get_ai_feedback

router = APIRouter()

USER_ID = "default_user"


@router.get("/levels")
async def get_levels():
    levels = []
    async for level in levels_collection.find():
        level["id"] = str(level["_id"])
        del level["_id"]
        level["test_cases"] = [
            {"input": tc["input"], "expected": tc["expected"]}
            for tc in level.get("test_cases", [])
        ]
        levels.append(level)
    return levels


@router.get("/levels/{level_id}")
async def get_level(level_id: str):
    try:
        level = await levels_collection.find_one({"_id": ObjectId(level_id)})
    except:
        raise HTTPException(status_code=400, detail="Invalid level ID")
    
    if not level:
        raise HTTPException(status_code=404, detail="Level not found")
    
    level["id"] = str(level["_id"])
    del level["_id"]
    return level


@router.post("/execute")
async def execute_code(request: ExecuteRequest):
    try:
        level = await levels_collection.find_one({"_id": ObjectId(request.level_id)})
    except:
        raise HTTPException(status_code=400, detail="Invalid level ID")
    
    if not level:
        raise HTTPException(status_code=404, detail="Level not found")
    
    test_cases = [
        {"input": tc["input"], "expected": tc["expected"]}
        for tc in level.get("test_cases", [])
    ]
    
    response_data = execute_user_code(request.code, test_cases)
    
    return ExecuteResponse(
        passed=response_data["passed"],
        error_type=response_data["error_type"],
        results=[
            TestResult(
                input=r["input"],
                expected=r["expected"],
                actual=r["actual"],
                passed=r["passed"],
                error_type=r["error_type"],
                states=r.get("states", [])
            )
            for r in response_data["results"]
        ]
    )


@router.post("/submit")
async def submit_code(request: SubmitRequest):
    attempt_doc = {
        "user_id": USER_ID,
        "level_id": request.level_id,
        "code": request.code,
        "result": "passed" if request.passed else "failed",
        "failed_cases": request.failed_cases,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    await attempts_collection.insert_one(attempt_doc)
    
    progress = await progress_collection.find_one({"user_id": USER_ID})
    
    if not progress:
        progress_doc = {
            "user_id": USER_ID,
            "topic": "arrays",
            "total_attempts": 1,
            "successful_attempts": 1 if request.passed else 0,
            "accuracy": 100.0 if request.passed else 0.0,
            "last_practiced": datetime.utcnow().isoformat(),
            "levels_completed": [request.level_id] if request.passed else []
        }
        await progress_collection.insert_one(progress_doc)
    else:
        new_attempts = progress.get("total_attempts", progress.get("attempts", 0)) + 1
        new_successful = progress.get("successful_attempts", 0) + (1 if request.passed else 0)
        new_accuracy = (new_successful / new_attempts) * 100
        
        levels_completed = progress.get("levels_completed", [])
        if request.passed and request.level_id not in levels_completed:
            levels_completed.append(request.level_id)
        
        await progress_collection.update_one(
            {"user_id": USER_ID},
            {
                "$set": {
                    "total_attempts": new_attempts,
                    "successful_attempts": new_successful,
                    "accuracy": new_accuracy,
                    "last_practiced": datetime.utcnow().isoformat(),
                    "levels_completed": levels_completed
                }
            }
        )
    
    return {"message": "Submission recorded successfully"}


@router.get("/progress")
async def get_progress():
    progress = await progress_collection.find_one({"user_id": USER_ID})
    
    if not progress:
        return {
            "user_id": USER_ID,
            "topic": "arrays",
            "total_attempts": 0,
            "successful_attempts": 0,
            "accuracy": 0.0,
            "last_practiced": None,
            "levels_completed": []
        }
    
    return {
        "user_id": progress["user_id"],
        "topic": progress["topic"],
        "total_attempts": progress.get("total_attempts", progress.get("attempts", 0)),
        "successful_attempts": progress["successful_attempts"],
        "accuracy": progress["accuracy"],
        "last_practiced": progress.get("last_practiced"),
        "levels_completed": progress.get("levels_completed", [])
    }


@router.get("/daily-task")
async def get_daily_task():
    today = datetime.utcnow().strftime("%Y-%m-%d")
    
    existing_task = await daily_tasks_collection.find_one({
        "user_id": USER_ID,
        "date": today
    })
    
    if existing_task:
        level_id = existing_task["level_id"]
    else:
        progress = await progress_collection.find_one({"user_id": USER_ID})
        
        if not progress or progress.get("total_attempts", progress.get("attempts", 0)) == 0:
            level = await levels_collection.find_one({"difficulty": "easy"})
        else:
            levels = []
            async for lvl in levels_collection.find():
                levels.append(lvl)
            
            level_id = None
            max_score = -1.0
            now = datetime.utcnow()
            
            for lvl in levels:
                lvl_id_str = str(lvl["_id"])
                level_attempts = await attempts_collection.count_documents({
                    "user_id": USER_ID,
                    "level_id": lvl_id_str
                })
                
                level_success = await attempts_collection.count_documents({
                    "user_id": USER_ID,
                    "level_id": lvl_id_str,
                    "result": "passed"
                })
                
                # Priority 6: Calculate accuracy dynamically for the level
                if level_attempts == 0:
                    accuracy = 0.0
                else:
                    accuracy = level_success / level_attempts
                
                # Priority 6: Calculate inactivity days
                last_attempt = await attempts_collection.find_one(
                    {"user_id": USER_ID, "level_id": lvl_id_str},
                    sort=[("timestamp", -1)]
                )
                
                inactivity_days = 0
                if last_attempt and "timestamp" in last_attempt:
                    try:
                        last_time = datetime.fromisoformat(last_attempt["timestamp"].replace("Z", "+00:00"))
                        inactivity_days = (now - last_time).days
                    except:
                        pass
                elif level_attempts == 0:
                    # Treat unseen levels as having high inactivity to encourage exploration mathematically
                    inactivity_days = 30
                
                # Compute Strict Weakness Formula: score = 0.7 * (1 - accuracy) + 0.3 * inactivity_days
                score = 0.7 * (1.0 - accuracy) + 0.3 * inactivity_days
                
                if score > max_score:
                    max_score = score
                    level_id = lvl_id_str
            
            if not level_id and levels:
                level_id = str(levels[0]["_id"])
        
        await daily_tasks_collection.insert_one({
            "user_id": USER_ID,
            "level_id": level_id,
            "date": today
        })
    
    level = await levels_collection.find_one({"_id": ObjectId(level_id)})
    
    if not level:
        raise HTTPException(status_code=404, detail="No levels available")
    
    level["id"] = str(level["_id"])
    del level["_id"]
    
    return DailyTask(
        user_id=USER_ID,
        level_id=level_id,
        date=today,
        level=level
    )


@router.get("/attempts")
async def get_recent_attempts(limit: int = 10):
    attempts = []
    async for attempt in attempts_collection.find(
        {"user_id": USER_ID}
    ).sort("timestamp", -1).limit(limit):
        attempt["id"] = str(attempt["_id"])
        del attempt["_id"]
        attempts.append(attempt)
    return attempts

@router.post("/feedback")
async def get_feedback(request: FeedbackRequest):
    result = await get_ai_feedback(
        user_code=request.user_code,
        error_message=request.error_message,
        expected_output=request.expected_output,
        actual_output=request.actual_output
    )
    return result
