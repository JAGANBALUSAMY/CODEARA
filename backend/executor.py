import subprocess
import sys
import json
import io
from typing import List, Tuple


class CodeExecutor:
    def __init__(self, timeout: int = 2):
        self.timeout = timeout

    def execute(self, code: str, test_inputs: List[str]) -> List[Tuple[str, str, str, bool, list]]:
        results = []
        
        for test_input in test_inputs:
            actual_output = ""
            passed = False
            error_msg = ""
            
            try:
                wrapped_code = self._wrap_code(code, test_input)
                
                result = subprocess.run(
                    [sys.executable, "-c", wrapped_code],
                    capture_output=True,
                    text=True,
                    timeout=self.timeout
                )
                
                actual_output = result.stdout.strip()
                state_data = []
                
                if "__STATE_DUMP__:" in actual_output:
                    parts = actual_output.split("__STATE_DUMP__:")
                    actual_output = parts[0].strip()
                    try:
                        state_data = json.loads(parts[1].strip())
                    except json.JSONDecodeError:
                        pass
                
                if result.returncode != 0:
                    error_msg = result.stderr if result.stderr else result.stdout
                    actual_output = f"Error: {error_msg}"
                
            except subprocess.TimeoutExpired:
                actual_output = "Error: Execution timeout (infinite loop detected)"
                state_data = []
            except Exception as e:
                actual_output = f"Error: {str(e)}"
                state_data = []
            
            results.append((test_input, actual_output, error_msg, passed, state_data))
        
        return results

    def _wrap_code(self, user_code: str, test_input: str) -> str:
        lines = user_code.split('\n')
        func_name = None
        for line in lines:
            if line.strip().startswith('def '):
                func_name = line.strip().split('(')[0].replace('def ', '')
                break
        
        wrapped = f'''
import json

_input = {test_input}
__STATE__ = []

def visualize(**kwargs):
    __STATE__.append(kwargs)

# User code starts here
{user_code}

# Execute and print result
try:
    if isinstance(_input, tuple):
        result = {func_name}(*_input)
    else:
        result = {func_name}(_input)
    print(result)
except Exception as e:
    print(f"Error: {{type(e).__name__}}: {{str(e)}}")
finally:
    print(f"\\n__STATE_DUMP__:{{json.dumps(__STATE__)}}")
'''
        return wrapped



def execute_user_code(code: str, test_cases: List[dict]) -> List[dict]:
    executor = CodeExecutor(timeout=2)
    results = []
    
    for test_case in test_cases:
        test_input = test_case["input"]
        expected = test_case["expected"]
        
        test_result = executor.execute(code, [test_input])
        
        if test_result:
            _, actual_output, error_msg, _, state_data = test_result[0]
            
            if error_msg and "Error:" in actual_output:
                passed = False
            else:
                passed = actual_output.strip() == expected.strip()
            
            results.append({
                "input": test_input,
                "expected": expected,
                "actual": actual_output,
                "passed": passed,
                "states": state_data
            })
    
    return results
