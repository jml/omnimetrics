"""Interface to an OmniFocus database.

Original code by Glyph Lefkowitz

Source:

- https://gist.github.com/glyph/e51d1809bf1edcb5e8f5dceb48f99ccb
- https://gist.github.com/glyph/24913ce5c9dac71b7a9c331f2a9d67fc
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pprint import pprint
from typing import Any, Callable, Iterable, Optional, TypeVar

from Foundation import NSURL
from ScriptingBridge import SBApplication

OMNIFOCUS = SBApplication.applicationWithURL_(
    NSURL.URLWithString_("file:///Applications/OmniFocus.app")
)

TASK_CLASS = OMNIFOCUS.classForScriptingClass_("task")


S = TypeVar("S")
T = TypeVar("T")


def optional(f: Callable[[S], T], x: Optional[S]) -> Optional[T]:
    """Apply ``f`` to ``x`` if ``x`` is not ``None``."""
    if x is None:
        return None
    return f(x)


def parse_date(date_str: str) -> datetime:
    # TODO: This should convert __NSTaggedDate, not str.
    return datetime.strptime(str(date_str), "%Y-%m-%d %H:%M:%S %z")


def parse_bool(value: int) -> bool:
    if value == 0:
        return False
    if value == 1:
        return True
    raise ValueError(f"Not a bool: {value}")


@dataclass(frozen=True)
class TagReference:
    name: str

    @classmethod
    def from_reference(cls, tag_reference) -> TagReference:
        return cls(name=tag_reference.name())


@dataclass(frozen=True)
class ProjectReference:
    name: str

    @classmethod
    def from_reference(cls, project_reference) -> ProjectReference:
        return cls(name=project_reference.name())


@dataclass(frozen=True)
class Task:
    """An OmniFocus Task.

    See https://omni-automation.com/omnifocus/task.html
    """
    id: str
    # The title of the task.
    name: str

    creation_date: datetime
    modification_date: datetime
    # If set, the Task should be completed by this date.
    due_date: Optional[datetime]
    # Returns the computed effective due date for the Task, based on its local dateDue and those of its containers.
    effective_due_date: Optional[datetime]
    next_due_date: Optional[datetime]
    # If set, the Task is not actionable until this date.
    defer_date: Optional[datetime]
    # Returns the computed effective defer date for the Task, based on its local deferDate and those of its containers.
    effective_defer_date: Optional[datetime]
    next_defer_date: Optional[datetime]
    # If set, the Task is dropped.
    dropped_date: Optional[datetime]
    # If set, the Task is completed.
    completion_date: Optional[datetime]

    primary_tag: Optional[TagReference]
    parent_task: Optional[TaskReference]
    # The estimated number of minutes this task will take to finish, or null if no estimate has been made.
    estimated_minutes: Optional[int]
    containing_project: Optional[ProjectReference]

    is_next: bool
    num_available_tasks: int
    num_completed_tasks: int
    num_tasks: int

    # Returns true if the task is a direct child of the inbox, but not if the task is contained by another task that is in the inbox.
    is_in_inbox: bool
    is_sequential: bool
    # The flagged status of the task.
    is_flagged: bool

    # True if the task has been marked completed.
    # Note that a task may be effectively considered completed if a containing task is marked completed.
    is_completed: bool
    is_dropped: bool
    is_blocked: bool

    # If set, the Task will be automatically marked completed when its last child Task is marked completed.
    is_completed_by_children: bool
    is_effectively_dropped: bool
    is_effectively_completed: bool
    should_use_floating_timezone: bool

    #repetition = "<null>"
    # The object holding the repetition properties for this task, or null if it is not repeating. See related documentation.
    #repetitionRule = "<null>";

    """Missing properties.

    This list comes from the OmniFocus Task documentation.
    They are properties of the task that are not returned by the ``properties`` method.

    after (Task.ChildInsertionLocation r/o) • A positional indicator that reference the list posotion directly following this task instance.
    assignedContainer (Project, Task, or Inbox or null) • For tasks in the inbox, the tentatively assigned project or parent task, which will be applied on cleanup.
    attachments (Array of FileWrapper) • An array of FileWrapper objects representing the attachments associated with the task. See related documentation.
    before (Task.ChildInsertionLocation r/o) • A positional indicator that references the list posotion immediately preceding this task instance.
    beginning (Task.ChildInsertionLocation r/o) • A positional indicator that references the very start of the task’s container object.
    children (Array of Task r/o) • Returns all the child tasks of this task, sorted by library order.
    containingProject (Project or null r/o) • The Project that this Task is contained in, either as the root of the project or indirectly from a parent task. If this task is in the inbox, then this will be null.
    effectiveCompletedDate (Date or null r/o) • (v3.8) Returns the computed effective completion date for the Task, based on its local completionDate and those of its containers.
    effectiveDropDate (Date or null r/o) • (v3.8) Returns the computed effective drop date for the Task, based on its local dropDate and those of its containers.
    effectiveFlagged (Boolean r/o) • Returns the computed effective flagged status for the Task, based on its local flagged and those of its containers.
    ending (Task.ChildInsertionLocation r/o) • A positional indicator that references the position at the very end of the task’s container object.
    flattenedChildren (TaskArray r/o) • An alias for flattenedTasks.
    flattenedTasks (TaskArray r/o) • Returns a flat array of all tasks contained within this task. Tasks are sorted by their order in the database. This flat array is often used for processing the entire task hierarchy of a specific task.
    hasChildren (Boolean r/o) • Returns true if this task has children, more efficiently than checking if children is empty.
    linkedFileURLs (Array of URL r/o) • The list of file URLs linked to this task. The files at these URLs are not present in the database, rather the database holds bookmarks leading to these files. These links can be read on iOS, but not written to.
    note (String) • The note of the task.
    notifications (Array of Task.Notification r/o) • An array of the notifications that are active for this task. (see related documentation)
    project (Project or null r/o) • The Project that this Task is the root task of, or null if this task is in the inbox or contained by another task.
    sequential (Boolean) • If true, then children of this task form a dependency chain. For example, the first task blocks the second one until the first is completed.
    shouldUseFloatingTimeZone (Boolean) • (v3.6) When set, the dueDate and deferDate properties will use floating time zones. (Note: if a Task has no due or defer dates assigned, this property will revert to the database’s default setting.)
    tags (TagArray r/o) • Returns the Tags associated with this Task.
    taskStatus (Task.Status r/o) • Returns the current status of the task.
    tasks (TaskArray r/o) • Returns all the tasks contained directly in this task, sorted by their library order.
    """

    @classmethod
    def from_omnifocus_task(cls, task) -> Task:
        properties = task.properties()
        try:
            return cls(
                id=properties["id"],
                name=properties["name"],
                creation_date=parse_date(properties["creationDate"]),
                modification_date=parse_date(properties["modificationDate"]),
                due_date=optional(parse_date, properties["dueDate"]),
                effective_due_date=optional(parse_date, properties["effectiveDueDate"]),
                next_due_date=optional(parse_date, properties["nextDueDate"]),
                defer_date=optional(parse_date, properties["deferDate"]),
                effective_defer_date=optional(parse_date, properties["effectiveDeferDate"]),
                next_defer_date=optional(parse_date, properties["nextDeferDate"]),
                dropped_date=optional(parse_date, properties["droppedDate"]),
                completion_date=optional(parse_date, properties["completionDate"]),

                primary_tag=optional(TagReference.from_reference, properties["primaryTag"]),
                parent_task=optional(TaskReference.from_reference, properties["parentTask"]),
                estimated_minutes=properties["estimatedMinutes"],
                containing_project=optional(ProjectReference.from_reference, properties["containingProject"]),

                is_next=parse_bool(properties["next"]),
                num_available_tasks=properties["numberOfAvailableTasks"],
                num_completed_tasks=properties["numberOfCompletedTasks"],
                num_tasks=properties["numberOfTasks"],

                is_in_inbox=parse_bool(properties["inInbox"]),
                is_sequential=parse_bool(properties["sequential"]),
                is_flagged=parse_bool(properties["flagged"]),
                is_completed=parse_bool(properties["completed"]),
                is_dropped=parse_bool(properties["dropped"]),
                is_blocked=parse_bool(properties["blocked"]),
                is_completed_by_children=parse_bool(properties["completedByChildren"]),
                is_effectively_dropped=parse_bool(properties["effectivelyDropped"]),
                is_effectively_completed=parse_bool(properties["effectivelyCompleted"]),
                should_use_floating_timezone=parse_bool(properties["shouldUseFloatingTimeZone"]),
            )
        except KeyError:
            pprint(properties)
            raise


@dataclass(frozen=True)
class TaskReference:
    id: str
    name: str

    @classmethod
    def from_reference(cls, task_reference) -> TaskReference:
        return cls(id=task_reference.id(), name=task_reference.name())


def load_tasks(omni_database: Any) -> Iterable[Task]:
    for task in omni_database.flattenedTasks():
        yield Task.from_omnifocus_task(task)
