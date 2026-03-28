from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class TestCase(BaseModel):
    input: str
    expected: str


class Level(BaseModel):
    id: str
    title: str
    concept: str
    problem: str
    starter_code: str
    solution: str
    test_cases: List[TestCase]


class ExecuteRequest(BaseModel):
    code: str
    level_id: str


class TestResult(BaseModel):
    input: str
    expected: str
    actual: str
    passed: bool
    error_type: Optional[str] = None
    states: Optional[List[dict]] = []


class ExecuteResponse(BaseModel):
    passed: bool
    error_type: Optional[str] = None
    results: List[TestResult]


class SubmitRequest(BaseModel):
    code: str
    level_id: str
    passed: bool
    failed_cases: List[str]


class Progress(BaseModel):
    user_id: str
    topic: str
    total_attempts: int
    successful_attempts: int
    accuracy: float
    last_practiced: Optional[str] = None
    levels_completed: List[str] = []


class DailyTask(BaseModel):
    user_id: str
    level_id: str
    date: str
    level: Optional[Level] = None

class FeedbackRequest(BaseModel):
    user_code: str
    error_message: str
    expected_output: str
    actual_output: str
