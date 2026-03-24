import google.generativeai as genai
import os
import json

# Configure Gemini
api_key = os.getenv("GEMINI_API_KEY", "")
if api_key:
    genai.configure(api_key=api_key)

generation_config = {
    "temperature": 0.3,
    "top_p": 1,
    "top_k": 32,
    "max_output_tokens": 1024,
}

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config
)

async def get_ai_feedback(user_code: str, error_message: str, expected_output: str, actual_output: str) -> dict:
    if not api_key:
        return {
            "explanation": "AI Feedback is currently disabled because the GEMINI_API_KEY is not set in the environment.",
            "mistake_detection": "Please configure your API key to enable AI analysis.",
            "hint": "Try checking the difference between your expected output and actual output!"
        }
    
    prompt = f"""
You are an expert Python programming instructor on the Codara platform.
Your task is to analyze the student's incorrect code and provide helpful feedback.
DO NOT provide the full correct code solution under any circumstances.

Student's Code:
```python
{user_code}
```

Execution Details:
Expected Output: {expected_output}
Actual Output: {actual_output}
Error Message (if any): {error_message}

Provide your response strictly in the following JSON format:
{{
    "explanation": "A gentle, beginner-friendly explanation of what the code is attempting to do and why it might be failing.",
    "mistake_detection": "A concise sentence pointing out the exact line or concept that is causing the error.",
    "hint": "A guiding question or tip to help them fix the code themselves."
}}
"""
    try:
        response = model.generate_content(prompt)
        text = response.text
        # Clean markdown code blocks if present
        if text.startswith('```json'):
            text = text.replace('```json', '', 1)
        if text.endswith('```'):
            text = text[::-1].replace('```', '', 1)[::-1]
            
        result = json.loads(text.strip())
        return result
    except Exception as e:
        return {
            "explanation": "There was an error communicating with the AI service.",
            "mistake_detection": "Could not parse AI response.",
            "hint": str(e)
        }
