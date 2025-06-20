import pytest

from mcp_omnifocus.utils.omnifocus import list_perspectives, list_projects, list_tags, list_tasks
from mcp_omnifocus.utils.scripting import run_jxa_script


@pytest.mark.requires_omnifocus
def test_omnifocus_availability():
    """Test that OmniFocus is available and responsive."""
    # This test will be automatically skipped if OmniFocus is not available
    script = """
    (() => {
        const omnifocus = Application("OmniFocus");
        return omnifocus.name();
    })();
    """

    result = run_jxa_script(script)
    assert result == "OmniFocus"


@pytest.mark.requires_omnifocus
def test_list_perspectives():
    """Test listing perspectives in OmniFocus."""

    perspectives = list_perspectives()

    assert isinstance(perspectives, list)
    assert all(isinstance(perspective, str) for perspective in perspectives)
    assert all(perspective for perspective in perspectives)  # Ensure no empty strings
    assert "Inbox" in perspectives  # Check for a known perspective


@pytest.mark.requires_omnifocus
def test_list_projects():
    """Test listing projects in OmniFocus."""

    projects = list_projects()

    assert isinstance(projects, list)
    assert all(isinstance(project, dict) for project in projects)
    assert all("id" in project and "name" in project and "status" in project for project in projects)
    assert all(
        isinstance(project["id"], str) and isinstance(project["name"], str) and isinstance(project["status"], str)
        for project in projects
    )


@pytest.mark.requires_omnifocus
def test_list_tags():
    """Test listing tags in OmniFocus."""

    tags = list_tags()

    assert isinstance(tags, list)
    assert all(isinstance(tag, dict) for tag in tags)
    assert all("id" in tag and "name" in tag for tag in tags)
    assert all(isinstance(tag["id"], str) and isinstance(tag["name"], str) for tag in tags)


@pytest.mark.requires_omnifocus
@pytest.mark.slow
def test_list_tasks():
    """Test listing tasks in OmniFocus."""

    tasks = list_tasks()

    assert isinstance(tasks, list)
    assert all(isinstance(task, dict) for task in tasks)
    assert all("id" in task and "name" in task and "status" in task for task in tasks)
    assert all(
        isinstance(task["id"], str) and isinstance(task["name"], str) and isinstance(task["status"], str)
        for task in tasks
    )
