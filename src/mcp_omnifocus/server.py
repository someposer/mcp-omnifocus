from textwrap import dedent
from typing import Annotated

import typer
from fastmcp import FastMCP
from pydantic import Field

from mcp_omnifocus.utils import omnifocus

# Initialize the app
app = typer.Typer(add_completion=False)

# Initialize the FastMCP Server
mcp = FastMCP(
    name="OmniFocus MCP Server",
    instructions="""
        This server provides tools to interact with OmniFocus.
        OmniFocus is a task management application that adheres to the Getting Things Done (GTD) methodology.
        Use the provide commends to help users to manage their tasks, projects, and tags in OmniFocus.

        You will help them to Collect new tasks into their Inbox, Organize tasks into Projects and Tags,
        Review their tasks and projects, and Execute tasks based on their context and priority.

        You can list the tasks, tags, and projects managed by OmniFocus.
        Use the provide tools to reivew project status and task completion, 
        create new tasks, projects, and tags, and manage your OmniFocus data effectively.
        """,
)


@mcp.tool
def list_perspectives() -> list[str]:
    """List all perspectives in OmniFocus."""
    return omnifocus.list_perspectives()


@mcp.tool
def list_projects() -> list[dict[str, str]]:
    """List all projects in OmniFocus."""
    return omnifocus.list_projects()


@mcp.tool
def list_tags() -> list[dict[str, str]]:
    """List all tags in OmniFocus."""
    return omnifocus.list_tags()


@mcp.tool
def list_tasks() -> list[dict[str, str]]:
    """List all tasks in OmniFocus. The task full name is the full heirarchy of the task, including parent tags."""
    return omnifocus.list_tasks()


@mcp.tool
def list_inbox() -> list[dict[str, str]]:
    """List all tasks in the OmniFocus Inbox."""
    return omnifocus.list_perspective_tasks("Inbox")


@mcp.tool
def update_task(
    task_id: Annotated[str, Field(description="The ID of the task to update")],
    name: Annotated[str | None, Field(description="The updated task name, None if unchanged")] = None,
    project_id: Annotated[
        str | None, Field(description="The project id to assign the task to, None if unchanged")
    ] = None,
    tag_ids: Annotated[
        list[str] | None,
        Field(
            description="A list of tag ids to assign to a task. None if unchanged. Cannot remove existing tags assigned to a task."
        ),
    ] = None,
    note: Annotated[str | None, Field(description="The updated task note, None if unchanged")] = None,
    defer_date: Annotated[
        str | None,
        Field(
            description="The updated task deferred date in ISO format YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS, None if unchanged"
        ),
    ] = None,
    due_date: Annotated[
        str | None,
        Field(
            description="The updated task due date in ISO format YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS, None if unchanged"
        ),
    ] = None,
    flagged: Annotated[bool | None, Field(description="The updated task flagged status, None if unchanged")] = None,
) -> dict[str, str]:
    """Update a task in OmniFocus with a new name, assigned project name, tags, note, due date, and/or defer date."""
    return omnifocus.update_task(
        task_id,
        task_name=name,
        task_project_id=project_id,
        task_tag_ids=tag_ids,
        task_note=note,
        task_defer_date=defer_date,
        task_due_date=due_date,
        task_flagged=flagged,
    )


@mcp.tool
def complete_task(task_id: Annotated[str, Field(description="The ID of the task to complete")]) -> dict[str, str]:
    """Complete a task in OmniFocus."""
    return omnifocus.complete_task(task_id)


@mcp.tool
def drop_task(task_id: Annotated[str, Field(description="The ID of the task to drop")]) -> dict[str, str]:
    """Drop a task in OmniFocus."""
    return omnifocus.drop_task(task_id)


@mcp.tool
def activate_task(task_id: Annotated[str, Field(description="The ID of the task to activate")]) -> dict[str, str]:
    """Activate (un-drop or un-complete) a task in OmniFocus."""
    return omnifocus.activate_task(task_id)


@mcp.tool
def create_task(
    name: Annotated[str, Field(description="The name of the task to create")],
    note: Annotated[str | None, Field(description="The note for the task, None if no note")] = None,
) -> dict[str, str]:
    """Create a new task in OmniFocus with a name and an optional note."""
    return omnifocus.create_task(task_name=name, task_note=note)


@mcp.prompt
def process_inbox() -> str:
    """Process tasks in the OmniFocus Inbox."""
    return dedent("""
    You are an assistant for processing my GTD inbox in OmniFocus. For each task in my inbox:
    
    1. Review the task name and note.
    2. Suggest the most relevant existing project to assigne the task to. If no suitable project exists, propose a new project name.
    3. Suggest the most relevant existing tag to assign the task to. If no suitable tag exists, propose a new tag name.
    
    Use the #list_inbox tool to get the list of tasks in the inbox.
    Use the tools #list_projects and #list_tags to get the list of existing projects and tags.
    Use the #update_task tool to update the task with the suggested project and tag.
    """)


@app.command()
def main():
    mcp.run(transport="stdio")
