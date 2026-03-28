import subprocess
import sys
import json
import ast
import tempfile
import os
from typing import List, Tuple

def format_input(data):
    try:
        if isinstance(data, str):
            val = ast.literal_eval(data)
            if isinstance(val, list):
                return " ".join(map(str, val)) + "\n"
    except Exception:
        pass
        
    if isinstance(data, list):
        return " ".join(map(str, data)) + "\n"
    return str(data) + "\n"

def normalize(output):
    if output is None:
        return ""
    return str(output).strip().replace("\\n", "").replace(" ", "")

class CodeExecutor:
    def __init__(self, timeout: int = 2):
        self.timeout = timeout

    def execute(self, code: str, test_inputs: List[str]) -> List[Tuple[str, str, str, bool, list, str]]:
        results = []
        
        for test_input in test_inputs:
            actual_output = ""
            passed = False
            error_type = None
            state_data = []
            
            wrapped_code = self._wrap_code(code)
            input_data = format_input(test_input)
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as temp_file:
                temp_file.write(wrapped_code)
                temp_path = temp_file.name
                
            try:
                result = subprocess.run(
                    [sys.executable, temp_path],
                    input=input_data,
                    text=True,
                    capture_output=True,
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
                    if actual_output.startswith("Error: "):
                        error_type = "runtime_error"
                
            except subprocess.TimeoutExpired:
                actual_output = "Error: Execution timeout"
                error_type = "timeout"
            except Exception as e:
                actual_output = f"Error: {str(e)}"
                error_type = "runtime_error"
            finally:
                if os.path.exists(temp_path):
                    os.remove(temp_path)
            
            results.append((test_input, actual_output, "", passed, state_data, error_type))
        
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

raw_input = sys.stdin.read().strip()
try:
    _input = ast.literal_eval(raw_input)
except Exception:
    _input = raw_input

{user_code}

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

def execute_user_code(code: str, test_cases: List[dict]) -> dict:
    executor = CodeExecutor(timeout=2)
    results = []
    
    dangerous_keywords = ["import os", "import sys", "subprocess"]
    if any(kw in code for kw in dangerous_keywords):
        for tc in test_cases:
            results.append({
                "input": tc["input"],
                "expected": tc["expected"],
                "actual": "Security Error: Dangerous command detected.",
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
    overall_error_type = None

    for test_case in test_cases:
        test_input = test_case["input"]
        expected = test_case["expected"]
        
        test_result = executor.execute(code, [test_input])
        
        if test_result:
            _, actual_output, _, passed, state_data, error_type = test_result[0]
            
            if error_type is None:
                norm_actual = normalize(actual_output)
                norm_expected = normalize(expected)
                passed = norm_actual == norm_expected
                if not passed:
                    error_type = "wrong_output"
            else:
                passed = False
            
            if not passed:
                overall_passed = False
                if overall_error_type is None:
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
