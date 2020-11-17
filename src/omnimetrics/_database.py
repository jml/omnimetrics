"""Interface to an OmniFocus database.

Original code by Glyph Lefkowitz

Source:

- https://gist.github.com/glyph/e51d1809bf1edcb5e8f5dceb48f99ccb
- https://gist.github.com/glyph/24913ce5c9dac71b7a9c331f2a9d67fc
"""
from __future__ import annotations

from datetime import datetime
from pprint import pprint
from typing import Any, Callable, Iterable, Optional, TypeVar

import attr
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


@attr.frozen
class Tag:
    name: str

    @classmethod
    def from_reference(cls, tag_reference) -> Tag:
        return cls(name=tag_reference.name())


@attr.frozen
class Project:
    name: str

    @classmethod
    def from_reference(cls, project_reference) -> Project:
        return cls(name=project_reference.name())


@attr.frozen
class Task:
    id: str
    name: str

    creation_date: datetime
    modification_date: datetime
    due_date: Optional[datetime]
    effective_due_date: Optional[datetime]
    next_due_date: Optional[datetime]
    defer_date: Optional[datetime]
    effective_defer_date: Optional[datetime]
    next_defer_date: Optional[datetime]
    dropped_date: Optional[datetime]
    completion_date: Optional[datetime]

    primary_tag: Optional[Tag]
    parent_task: Optional[TaskReference]
    estimated_minutes: Optional[int]
    containing_project: Optional[Project]

    is_next: bool
    num_available_tasks: int
    num_completed_tasks: int
    num_tasks: int

    is_in_inbox: bool
    is_sequential: bool
    is_flagged: bool
    is_completed: bool
    is_dropped: bool
    is_blocked: bool
    is_completed_by_children: bool
    is_effectively_dropped: bool
    is_effectively_completed: bool
    should_use_floating_timezone: bool

    #repetition = "<null>"
    #repetitionRule = "<null>";

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

                primary_tag=optional(Tag.from_reference, properties["primaryTag"]),
                parent_task=optional(TaskReference.from_reference, properties["parentTask"]),
                estimated_minutes=properties["estimatedMinutes"],
                containing_project=optional(Project.from_reference, properties["containingProject"]),

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


@attr.frozen
class TaskReference:
    id: str
    name: str

    @classmethod
    def from_reference(cls, task_reference) -> TaskReference:
        return cls(id=task_reference.id(), name=task_reference.name())
        # TODO: Make a TaskReference type
        # TODO: Figure out why the heck emacs is so slow


def load_tasks(omni_database: Any) -> Iterable[Task]:
    for task in omni_database.flattenedTasks():
        yield Task.from_omnifocus_task(task)
