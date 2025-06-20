import pytest

from mcp_omnifocus.utils.scripting import run_jxa_script


def check_omnifocus_availability() -> bool:
    """Check if OmniFocus is available and responsive.

    Returns:
        True if OmniFocus is available, False otherwise.
    """
    try:
        # Simple script to test if OmniFocus is available
        script = """
        (() => {
            try {
                const omnifocus = Application("OmniFocus");
                return omnifocus.running() ? "available" : "not_running";
            } catch (e) {
                return "error";
            }
        })();
        """

        result = run_jxa_script(script)
        return result == "available"
    except Exception:
        return False


@pytest.fixture(scope="session")
def omnifocus_available():
    """Session-scoped fixture that checks OmniFocus availability once per test session."""
    return check_omnifocus_availability()


@pytest.fixture(scope="session")
def require_omnifocus(omnifocus_available):
    """Session-scoped fixture that skips tests if OmniFocus is not available."""
    if not omnifocus_available:
        pytest.skip("OmniFocus is not available or not running")
    return True


# Custom marker for tests that require OmniFocus
def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line("markers", "requires_omnifocus: mark test as requiring OmniFocus to be available")


def pytest_collection_modifyitems(config, items):
    """Automatically skip tests marked as requiring OmniFocus if it's not available."""
    if not check_omnifocus_availability():
        skip_omnifocus = pytest.mark.skip(reason="OmniFocus not available or not running")
        for item in items:
            if "requires_omnifocus" in item.keywords:
                item.add_marker(skip_omnifocus)
