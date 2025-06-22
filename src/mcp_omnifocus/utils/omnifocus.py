from string import Template
from textwrap import dedent
from typing import Literal

from mcp_omnifocus.utils.scripting import evaluate_javascript

TaskStatus = Literal["Available", "Blocked", "Completed", "Dropped", "DueSoon", "Next", "Overdue"]

__common_functions__ = dedent("""
function projectStatusToString(status) {
    // Handle null/undefined cases
    if (!status) {
        return 'Unknown';
    }
    
    // Map of status objects to their string representations
    const statusMap = {
        [Project.Status.Active]: 'Active',
        [Project.Status.Done]: 'Done', 
        [Project.Status.Dropped]: 'Dropped',
        [Project.Status.OnHold]: 'OnHold',
    };
    
    // Return the corresponding string or 'Unknown' if not found
    return statusMap[status] || 'Unknown';
}
                              
function taskStatusToString(status) {
    // Handle null/undefined cases
    if (!status) {
        return 'Unknown';
    }
    
    // Map of status objects to their string representations
    const statusMap = {
        [Task.Status.Available]: 'Available',
        [Task.Status.Blocked]: 'Blocked', 
        [Task.Status.Completed]: 'Completed',
        [Task.Status.Dropped]: 'Dropped',
        [Task.Status.DueSoon]: 'DueSoon',
        [Task.Status.Next]: 'Next',
        [Task.Status.Overdue]: 'Overdue'
    };
    
    // Return the corresponding string or 'Unknown' if not found
    return statusMap[status] || 'Unknown';
}
                              
function getFullTagName(tag) {
    const names = [];
    let currentTag = tag;
    // Traverse up the hierarchy
    while (currentTag) {
        names.unshift(currentTag.name);
        try {
            currentTag = currentTag.parent;
        } catch (e) {
            break;  // If we can't access parent, stop traversing
        }
    }
    return names.join(' : ');
};
                              
function getLeafNodes(node) {
    if (!node.children || node.children.length === 0) {
        return [node];
    }
    return node.children.flatMap(getLeafNodes);
}

function getPerspectiveByName(name) {
    let perspectives = new Array()
    perspectives = perspectives.concat(Perspective.BuiltIn.all)
    perspectives = perspectives.concat(Perspective.Custom.all)
    perspectiveNames = perspectives.map(perspective => perspective.name.toUpperCase())

    return perspectives[perspectiveNames.indexOf(name.toUpperCase())] || null;
}
                              
function formatTask(task) {
    return {
        id: task.id.primaryKey,
        name: task.name,
        projectName: task.containingProject ? task.containingProject.name : null,
        status: taskStatusToString(task.taskStatus),
        flagged: task.flagged,
        deferDate: task.deferDate ? task.deferDate.toString() : null,
        dueDate: task.dueDate ? task.dueDate.toString() : null,
        dropped: task.dropped,
        completed: task.completed,
        tags: task.tags ? task.tags.map(tt => tt.name) : [],
        note: task.note
    };
}
                              
function taskStatusFilter(task, allowedStatuses) {
    if (!allowedStatuses || allowedStatuses.length === 0) {
        return true;
    }
    return allowedStatuses.includes(taskStatusToString(task.taskStatus));
}
""")


def list_perspectives() -> list[str]:
    """List all perspectives in OmniFocus.

    Returns:
        A list containing the list of perspective names.
    """
    script = dedent("""
    (() => {
        let perspectives = new Array();
        perspectives = perspectives.concat(Perspective.BuiltIn.all);
        perspectives = perspectives.concat(Perspective.Custom.all);
        return perspectives.map(perspective => perspective.name);
    })();
    """)

    return evaluate_javascript(script)


def list_projects() -> list[dict[str, str]]:
    """List all projects in OmniFocus.

    Returns:
        A list of dictionaries containing project names, ids, statuses, etc.
    """
    script = Template(
        dedent("""
    ${__common_functions__}
    
    (() => {
        return flattenedProjects.map(project => {
            return {
                id: project.id.primaryKey,
                name: project.name,
                status: projectStatusToString(project.status),
                flagged: project.flagged,
                deferDate: project.deferDate ? project.deferDate.toString() : null,
                dueDate: project.dueDate ? project.dueDate.toString() : null,
                tags: project.tags ? project.tags.map(tt => tt.name) : [],
            };
        });
    })();
    """)
    )

    return evaluate_javascript(script.substitute(__common_functions__=__common_functions__))


def list_tags() -> list[dict[str, str]]:
    """List all tags in OmniFocus.

    Returns:
        A list of dictionaries containing tag names and ids, with full hierarchical names.
    """
    script = Template(
        dedent("""
    ${__common_functions__}    
    
    (() => {
        return flattenedTags.map(tag => {
            return {
                id: tag.id.primaryKey,
                name: tag.name,
                fullName: getFullTagName(tag),
            };
        });
    })();
    """)
    )

    return evaluate_javascript(script.substitute(__common_functions__=__common_functions__))


def list_tasks() -> list[dict[str, str]]:
    """List all tasks in OmniFocus.

    Returns:
        A list of dictionaries containing task names, ids, project ids, and tag ids.
    """
    script = Template(
        dedent("""
    ${__common_functions__}

    (() => {
        return flattenedTasks.map((task) => {
            try {
                return formatTask(task);
            } catch (e) {
                return null;
            }
        }).filter(Boolean);
    })();
    """)
    )

    return evaluate_javascript(script.substitute(__common_functions__=__common_functions__))


def list_perspective_tasks(perspective_name: str) -> list[dict[str, str]]:
    """List all tasks in a specific perspective in OmniFocus.

    Args:
        perspective_name: The name of the perspective to filter tasks by.

    Returns:
        A list of dictionaries containing task names, ids, project ids, and tag ids.
    """
    script = Template(
        dedent("""
    ${__common_functions__}                            

    (() => {
        let perspective = getPerspectiveByName("${perspective_name}");

        if (!perspective) {
            throw "Could not find perspective: " + perspective_name.toString();
        }

        win = document.windows[0];
        win.perspective = perspective;

        if (perspective == Perspective.BuiltIn.Forecast) {
            var now = new Date();
            var today = Calendar.current.startOfDay(now);
            var dc = new DateComponents();
            dc.day = -1;
            var yesterday = Calendar.current.dateByAddingDateComponents(today, dc);
            win.selectForecastDays([win.forecastDayForDate(yesterday), win.forecastDayForDate(today)]);
        }

        return getLeafNodes(win.content.rootNode).map((l) => {
            const task = l.object;
            try {
                return formatTask(task);
            } catch (e) {
                return null;
            }
        }).filter(Boolean);

    })();
    """)
    )

    return evaluate_javascript(
        script.substitute(__common_functions__=__common_functions__, perspective_name=perspective_name)
    )


def cleanup_perspective_name(perspective_name: str):
    """Cleanup perspective name to be used in the script.

    Args:
        perspective_name: The name of the perspective to clean up.
    """
    script = Template(
        dedent("""
    ${__common_functions__}
                    
    (() => {
        let perspective = getPerspectiveByName("${perspective_name}");

        if (!perspective) {
            throw "Could not find perspective: " + perspective_name.toString();
        }

        document.windows[0].perspective = perspective;
        cleanUp();
    })();
    """)
    )

    evaluate_javascript(script.substitute(__common_functions__=__common_functions__, perspective_name=perspective_name))


def update_task(
    task_id: str,
    task_name: str | None = None,
    task_note: str | None = None,
    task_tag_ids: list[str] | None = None,
    task_project_id: str | None = None,
    task_defer_date: str | None = None,
    task_due_date: str | None = None,
    task_flagged: bool | None = None,
) -> dict[str, str]:
    """Update a task in OmniFocus.

    Args:
        task_id: The ID of the task to update.

    Returns:
        A dictionary containing the updated task's details.
    """
    script = Template(
        dedent("""
    ${__common_functions__}
               
    (() => {
        let task = Task.byIdentifier("${task_id}");
        if (!task) {
            throw "Could not find task: " + task_id.toString();
        }
        let newName = ${task_name};
        let newNote = ${task_note};
        let newTags = ${task_tag_ids};
        let newProjectId = ${task_project_id};
        let newDeferDate = ${task_defer_date};
        let newDueDate = ${task_due_date};
        let newFlagged = ${task_flagged};
               
        try {
            if (newName) {
                task.name = newName;
            }
            
            if (newNote) {
                task.note = newNote;
            }
            
            if (newTags) {
                newTags.forEach(tagId => {
                    let tag = Tag.byIdentifier(tagId);
                    if (tag) {
                        task.addTag(tag);
                    }
                });
            }
                
            if (newProjectId) {
                let project = Project.byIdentifier(newProjectId);
                if (project) {
                    moveTasks([task], project);
                }
            }
            
            if (newDeferDate) {
                task.deferDate = new Date(newDeferDate);
            }
               
            if (newDueDate) {
                task.dueDate = new Date(newDueDate);
            }
               
            if (newFlagged !== null && newFlagged !== undefined) {
                task.flagged = newFlagged;
            }
        } catch (e) {
            throw "Error updating task: " + e.toString();
        }
               
        return formatTask(task);
    })();
    """)
    )
    return evaluate_javascript(
        script.substitute(
            __common_functions__=__common_functions__,
            task_id=task_id,
            task_name=f'"{task_name}"' if task_name else "null",
            task_note=f'"{task_note}"' if task_note else "null",
            task_tag_ids=f"[{', '.join([f'"{tag}"' for tag in task_tag_ids])}]" if task_tag_ids else "[]",
            task_project_id=f'"{task_project_id}"' if task_project_id else "null",
            task_defer_date=f'"{task_defer_date}"' if task_defer_date else "null",
            task_due_date=f'"{task_due_date}"' if task_due_date else "null",
            task_flagged="null" if task_flagged is None else str(task_flagged).lower(),
        )
    )


def get_task(task_id: str) -> dict[str, str]:
    """Get a task by its ID in OmniFocus.

    Args:
        task_id: The ID of the task to retrieve.

    Returns:
        A dictionary containing the task's details.
    """
    script = Template(
        dedent("""
    ${__common_functions__}
    
    (() => {
        let task = Task.byIdentifier("${task_id}");
        if (!task) {
            throw "Could not find task: " + task_id.toString();
        }
        
        return formatTask(task);
    })();
    """)
    )

    return evaluate_javascript(script.substitute(__common_functions__=__common_functions__, task_id=task_id))


def complete_task(task_id: str) -> dict[str, str]:
    """Complete a task in OmniFocus.

    Args:
        task_id: The ID of the task to complete.

    Returns:
        A dictionary containing the completed task's details.
    """
    script = Template(
        dedent("""
    ${__common_functions__}
    
    (() => {
        let task = Task.byIdentifier("${task_id}");
        if (!task) {
            throw "Could not find task: " + task_id.toString();
        }
        
        task.markComplete();
        return formatTask(task);
    })();
    """)
    )

    return evaluate_javascript(script.substitute(__common_functions__=__common_functions__, task_id=task_id))


def drop_task(task_id: str) -> dict[str, str]:
    """Complete a task in OmniFocus.

    Args:
        task_id: The ID of the task to complete.

    Returns:
        A dictionary containing the dropped task's details.
    """
    script = Template(
        dedent("""
    ${__common_functions__}
               
    (() => {
        let task = Task.byIdentifier("${task_id}");
        if (!task) {
            throw "Could not find task: " + task_id.toString();
        }
        
        task.drop(false);
        return formatTask(task);
    })();
    """)
    )

    return evaluate_javascript(script.substitute(__common_functions__=__common_functions__, task_id=task_id))


def activate_task(task_id: str) -> dict[str, str]:
    """Activate a task in OmniFocus.

    Args:
        task_id: The ID of the task to activate.

    Returns:
        A dictionary containing the activated task's details.
    """
    script = Template(
        dedent("""
    ${__common_functions__}
    
    (() => {
        let task = Task.byIdentifier("${task_id}");
        if (!task) {
            throw "Could not find task: " + task_id.toString();
        }
        
        task.active = true;
        return formatTask(task);
    })();
    """)
    )

    return evaluate_javascript(script.substitute(__common_functions__=__common_functions__, task_id=task_id))


def create_task(task_name: str, task_note: str | None = None) -> dict[str, str]:
    """Create a new task in OmniFocus.

    Args:
        task_name: The name of the task to create.
        task_note: An optional note for the task.

    Returns:
        A dictionary containing the created task's details.
    """
    script = Template(
        dedent("""
    ${__common_functions__}
    
    (() => {
        let task = new Task("${task_name}");
        let task_note = ${task_note};
        if (task_note) {
            task.note = task_note;
        }
        return formatTask(task);
    })();
    """)
    )

    return evaluate_javascript(
        script.substitute(
            __common_functions__=__common_functions__,
            task_name=task_name,
            task_note=f'"{task_note}"' if task_note else "null",
        )
    )


def list_tasks_by_project(project_id: str, task_status: list[TaskStatus] | None = None) -> list[dict[str, str]]:
    """List all tasks in a specific project in OmniFocus.

    Args:
        project_id: The ID of the project to filter tasks by.
        task_status: A list of task statuses to filter by. If None, all tasks are returned.

    Returns:
        A list of dictionaries containing task names, ids, project ids, and tag ids.
    """
    script = Template(
        dedent("""
    ${__common_functions__}
    
    (() => {
        let project = Project.byIdentifier("${project_id}");
        const allowedStatuses = ${task_status};

        if (!project) {
            throw "Could not find project: " + project_id.toString();
        }

        return project.tasks
            .filter(task => taskStatusFilter(task, allowedStatuses))
            .map((task) => {
                try {
                    return formatTask(task);
                } catch (e) {
                    return null;
                }
            }).filter(Boolean);
    })();
    """)
    )

    return evaluate_javascript(
        script.substitute(
            __common_functions__=__common_functions__,
            project_id=project_id,
            task_status=f"[{', '.join([f'"{status}"' for status in task_status])}]" if task_status else "null",
        )
    )


def list_tasks_by_tag(tag_id: str, task_status: list[TaskStatus] | None = None) -> list[dict[str, str]]:
    """List all tasks with a specific tag in OmniFocus.

    Args:
        tag_id: The ID of the tag to filter tasks by.
        task_status: A list of task statuses to filter by. If None, all tasks are returned.

    Returns:
        A list of dictionaries containing task names, ids, project ids, and tag ids.
    """
    script = Template(
        dedent("""
    ${__common_functions__}
    
    (() => {
        let tag = Tag.byIdentifier("${tag_id}");
        const allowedStatuses = ${task_status};

        if (!tag) {
            throw "Could not find tag: " + tag_id.toString();
        }
        
        return tag.tasks
            .filter(task => taskStatusFilter(task, allowedStatuses))
            .map((task) => {
                try {
                    return formatTask(task);
                } catch (e) {
                    return null;
                }
            }).filter(Boolean);
    })();
    """)
    )

    return evaluate_javascript(
        script.substitute(
            __common_functions__=__common_functions__,
            tag_id=tag_id,
            task_status=f"[{', '.join([f'"{status}"' for status in task_status])}]" if task_status else "null",
        )
    )
