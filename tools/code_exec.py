from e2b_code_interpreter import Sandbox

def run_code(code: str) -> str:
    with Sandbox() as sandbox:
        execution = sandbox.run_code(code)
        if execution.error:
            return f"Error: {execution.error.name}: {execution.error.value}"
        logs = "".join(execution.logs.stdout)
        output = "\n".join(str(r.text) for r in execution.results if hasattr(r, "text"))
        return output or logs or "Code ran successfully with no output."