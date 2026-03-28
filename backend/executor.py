import subprocess
import sys
import json
import re
import ast
from typing import List, Tuple, Dict


class CodeExecutor:
    def __init__(self, timeout: int = 2):
        self.timeout = timeout

    def execute(self, code: str, test_inputs: List[str]) -> List[Tuple[str, str, str, bool, list, str]]:
        results = []
        
        for test_input in test_inputs:
            actual_output = ""
            passed = False
            error_msg = ""
            error_type = "success"
            state_data = []
            
            try:
                wrapped_code = self._wrap_code(code)
                
                # Pass test_input directly into the subprocess stdin parameter
                result = subprocess.run(
                    [sys.executable, "-c", wrapped_code],
                    input=test_input,
                    capture_output=True,
                    text=True,
                    timeout=self.timeout
                )
                
                actual_output = result.stdout.strip()
                
                if "__STATE_DUMP__:" in actual_output:
                    parts = actual_output.split("__STATE_DUMP__:")
                    actual_output = parts[0].strip()
                    try:
                        state_data = json.loads(parts[1].strip())
                    except json.JSONDecodeError:
                        pass
                
                if result.stderr.strip() or result.returncode != 0:
                    error_msg = result.stderr.strip() if result.stderr.strip() else result.stdout.strip()
                    actual_output = f"Error: {error_msg}"
                    error_type = "runtime_error"
                else:
                    # Look for our custom traceback string thrown by try-except block
                    if actual_output.startswith("Error: "):
                        error_type = "runtime_error"
                        error_msg = actual_output
                
            except subprocess.TimeoutExpired:
                actual_output = "Error: Execution timeout (infinite loop detected)"
                error_msg = actual_output
                error_type = "timeout"
            except Exception as e:
                actual_output = f"Error: {str(e)}"
                error_msg = actual_output
                error_type = "runtime_error"
            
            results.append((test_input, actual_output, error_msg, passed, state_data, error_type))
        
        return results

    def _wrap_code(self, user_code: str) -> str:
        lines = user_code.split('\n')
        func_name = None
        for line in lines:
            if line.strip().startswith('def '):
                func_name = line.strip().split('(')[0].replace('def ', '')
                break
                
        wrapped = f'''
import sys
import json
import ast

__STATE__ = []

def visualize(**kwargs):
    __STATE__.append(kwargs)

# Read raw multiline input from stdin properly
raw_input = sys.stdin.read().strip()
try:
    _input = ast.literal_eval(raw_input)
except Exception:
    _input = raw_input

# User code starts here
{user_code}

# Execute and print result
try:
    if isinstance(_input, tuple):
        result = {func_name}(*_input)
    else:
        result = {func_name}(_input)
    if result is not None:
        if isinstance(result, bool):
            print(str(result).lower())
        else:
            print(result)
except Exception as e:
    import traceback
    print(f"Error: {{type(e).__name__}}: {{str(e)}}")
finally:
    print(f"\\n__STATE_DUMP__:{{json.dumps(__STATE__)}}")
'''
        return wrapped

def normalize_output(s: str) -> str:
    """Normalize output by converting to lowercase string, removing whitespace entirely."""
    if s is None:
        return ""
    # Strip whitespace globally and convert to lowercase
    s = str(s).replace(" ", "").replace("\\n", "").replace("\\r", "").strip().lower()
    return s

def execute_user_code(code: str, test_cases: List[dict]) -> dict:
    executor = CodeExecutor(timeout=2)
    results = []
    
    # Priority 1 & 7: Basic Security Filter
    dangerous_keywords = ["import os", "import sys", "import subprocess", "__import__", "eval(", "exec("]
    if any(kw in code for kw in dangerous_keywords):
        for tc in test_cases:
            results.append({
                "input": tc["input"],
                "expected": tc["expected"],
                "actual": "Security Error: Dangerous import or command detected.",
                "passed": False,
                "error_type": "runtime_error",
                "states": []
            })
        return {
            "passed": False,
            "error_type": "runtime_error",
            "results": results
        }
        
    overall_passed = True
    overall_error_type = "success"

    for test_case in test_cases:
        test_input = test_case["input"]
        expected = test_case["expected"]
        
        test_result = executor.execute(code, [test_input])
        
        if test_result:
            _, actual_output, error_msg, passed, state_data, error_type = test_result[0]
            
            # Priority 2: Normalize outputs before comparison
            if error_type == "success":
                norm_actual = normalize_output(actual_output)
                norm_expected = normalize_output(expected)
                passed = norm_actual == norm_expected
                if not passed:
                    error_type = "wrong_output"
            
            # Propagate error if failed
            if not passed:
                overall_passed = False
                if not overall_error_type:
                    overall_error_type = error_type
            
            results.append({
                "input": test_input,
                "expected": expected,
                "actual": actual_output,
                "passed": passed,
                "error_type": error_type,
                "states": state_data
            })
    
    return {
        "passed": overall_passed,
        "error_type": overall_error_type,
        "results": results
    }
