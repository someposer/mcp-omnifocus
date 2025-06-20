import json
import subprocess
from typing import Any


class JXAScriptError(Exception):
    """Exception raised when AppleScript execution fails."""

    pass


def run_jxa_script(script: str, timeout: int = 30) -> str:
    """
    Run JavaScript for Automation script and return the output.

    Args:
        script: JXA code to execute
        timeout: Maximum execution time in seconds

    Returns:
        Script output as string (empty string if no output)

    Raises:
        JXAScriptError: If script execution fails
    """
    try:
        result = subprocess.run(
            ["osascript", "-l", "JavaScript", "-e", script], capture_output=True, text=True, timeout=timeout
        )

        if result.returncode != 0:
            error_msg = result.stderr.strip() if result.stderr else "Unknown AppleScript error"
            raise JXAScriptError(f"AppleScript failed: {error_msg}")

        return result.stdout.strip() if result.stdout else ""

    except subprocess.TimeoutExpired as exp:
        raise JXAScriptError(f"AppleScript timed out after {timeout} seconds") from exp
    except FileNotFoundError:
        raise JXAScriptError("osascript not found - AppleScript not available on this system") from None
    except Exception as e:
        raise JXAScriptError(f"AppleScript execution error: {str(e)}") from e


def evaluate_javascript(script: str) -> Any:
    """Execute a JavaScript script in OmniFocus.

    See; https://www.omni-automation.com/omnifocus/index.html

    Args:
        script: The JavaScript code to execute.

    Returns:
        The output of the script as a string.
    """
    jxa_script = f'let script = `{script}`;\n(() => {{\n   return JSON.stringify(Application("OmniFocus").evaluateJavascript(script));\n}})();'

    output = run_jxa_script(jxa_script)
    return json.loads(output) if output else {}
