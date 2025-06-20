# mcp-omnifocus

A Model Context Protocol (MCP) server for controlling [OmniFocus](https://www.omnigroup.com/omnifocus) from VS Code, the command line, or any MCP-compatible client. This tool enables automation and management of your OmniFocus tasks, projects, and tags using natural language and programmable interfaces.

## Features

- List all tasks, projects, tags, and perspectives in OmniFocus
- Create, update, complete, drop, and activate tasks
- Assign tasks to projects and tags
- Process and organize your GTD inbox
- Integrate with VS Code and other MCP clients

## Requirements

- macOS with [OmniFocus](https://www.omnigroup.com/omnifocus) installed
- Python 3.12+
- [uv](https://github.com/astral-sh/uv) for fast Python package management

## Installation

Clone the repository and install dependencies using `uv`:

```sh
git clone https://github.com/YOUR_USERNAME/mcp-omnifocus.git
cd mcp-omnifocus
uv venv
uv pip install -e .
```

## Usage

Add the following to your mcp configuration:

```json
{
    "servers": {
        "mcp-omnifocus": {
            "type": "stdio",
            "command": "uvx",
            "args": [
                "--from",
                "git+https://github.com/somposer/mcp-omnifocus",
                "mcp-omnifocus",
            ]
        }
    }
}
```

## Capabilities

The MCP OmniFocus server exposes the following tools, prompts, and resources:

- `list_perspectives`: List all perspectives
- `list_projects`: List all projects
- `list_tags`: List all tags
- `list_tasks`: List all tasks (with full hierarchy)
- `list_inbox`: List all tasks in the Inbox
- `create_task`: Create a new task
- `update_task`: Update a task (name, project, tags, note, defer/due date, flagged)
- `complete_task`: Mark a task as complete
- `drop_task`: Drop a task
- `activate_task`: Reactivate a dropped or completed task
- `process_inbox`: A reusable prompt for processing your GTD inbox

## Development

For development change your mcp.json to the following:

```json
{
    "servers": {
        "mcp-omnifocus": {
            "type": "stdio",
            "command": "uv",
            "args": [
                "run",
                "--project",
                "${workspaceFolder}/",
                "python",
                "-m",
                "mcp_omnifocus",
            ],
            "dev": {
                "watch": "src/**/*.py",
                "debug": {
                    "type": "python"
                }
            }
        }
    }
}
```

## License

MIT
