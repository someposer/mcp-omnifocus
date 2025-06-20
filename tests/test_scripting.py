from textwrap import dedent
from unittest.mock import MagicMock, patch

import pytest

from mcp_omnifocus.utils.scripting import run_jxa_script


def test_successful_script_execution():
    """Test successful AppleScript execution."""
    # Mock successful subprocess.run
    mock_result = MagicMock()
    mock_result.returncode = 0
    mock_result.stdout = "Hello World\n"
    mock_result.stderr = ""

    with patch("subprocess.run", return_value=mock_result) as mock_run:
        script = dedent("""
        (() => {
            return "Hello World";
        })();""")
        output = run_jxa_script(script)

        # Verify subprocess.run was called correctly
        mock_run.assert_called_once_with(
            ["osascript", "-l", "JavaScript", "-e", script], capture_output=True, text=True, timeout=30
        )

        # Verify results
        assert output == "Hello World"


@pytest.mark.requires_omnifocus
def test_evaluate_javascript():
    """Test evaluate_javascript function."""
    script = dedent("""
    (() => {
        return "Hello from OmniFocus";
    })();""")

    output = run_jxa_script(script)
    assert output == "Hello from OmniFocus"
