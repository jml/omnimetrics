"""Offer up OmniFocus tasks one at a time, recording excuses.

Command-line tool that shows exactly one OmniFocus task to do.
"""

import time
from dataclasses import dataclass
from typing import Any

from Foundation import NSURL
from ScriptingBridge import SBApplication

omniFocus = SBApplication.applicationWithURL_(
    NSURL.URLWithString_("file:///Applications/OmniFocus.app")
)
taskClass = omniFocus.classForScriptingClass_("task")


def itemsInView():  # pragma: no cover
    """Iterate over all of the items in view on one of the open windows.

    Items can be tasks, calendar items, or project markers. Only 'tasks' has a
    well-defined meaning.

    XXX: Which window?
    """
    content = omniFocus.defaultDocument().documentWindows()[0].content()
    for element in content.leaves():
        # XXX: Still unsure of the distinction between `.value()` and `.get()`
        yield element.value()


def isTask(item):  # pragma: no cover
    """Is the given item an OmniFocus task?"""
    return item.isKindOfClass_(taskClass)


def tasksInView():  # pragma: no cover
    """Iterate over all the tasks in view."""
    return filter(isTask, itemsInView())


@dataclass(frozen=True)
class Task:
    """A task from OmniFocus."""

    task: Any

    def defer(self, reason):
        return DeferredTask(self.task, reason)

    def start(self, startTime):
        return StartedTask(self.task, startTime)


@dataclass(frozen=True)
class StartedTask:
    """A task that has been started."""

    task: Any
    startTime: Any

    def complete(self, endTime):
        return CompletedTask(self.task, self.startTime, endTime)

    def abandon(self):
        """We don't want to work on this task any more."""
        return Task(self.task)


@dataclass(frozen=True)
class CompletedTask:
    """A task that has been completed."""

    task: Any
    startTime: Any
    endTime: Any


@dataclass(frozen=True)
class DeferredTask:
    """A task that we've decided not to do."""

    task: Any
    reason: Any


def attempt(task):  # pragma: no cover
    """Offer the user a single task to perform."""
    ui = UI()
    clock = time

    t = Task(task)
    wantToAttempt = ui.offerTask(task)
    if not wantToAttempt:
        # TODO: Do something with `reason`.
        reason = ui.requestReasonForDeferral(task)
        return t.defer(reason)
    # TODO: timer & completion logic
    started = t.start(clock.now())
    result = ui.waitUntilDone(task)
    if result == 'done':
        return started.complete(clock.now())
    elif result == 'abandoned':
        return started.abandon()
    else:
        raise ValueError('Unexpected response from UI (%r): %r' % (ui, result))


def qualifiedName(task):  # pragma: no cover
    """Return the full name of a task, including any projects that it's in.

    XXX: Doesn't include folders.
    """
    return " / ".join(reversed([t.name() for t in iterParents(task)]))


def iterParents(task):  # pragma: no cover
    """Get all the parents of a task, including the task itself."""
    eachTask = task
    while eachTask is not None:
        yield eachTask
        # Note: until we call `get()`, we have some sort of thunk. We cannot
        # decide whether it's null or not until we evaluate.
        eachTask = eachTask.parentTask().get()


def showTask(task):  # pragma: no cover
    """Show a task to the end-user."""
    return qualifiedName(task)


class UI:
    def offerTask(self, task):
        print(showTask(task))
        wantToAttempt = None
        while wantToAttempt is None:
            wantToAttempt = parseYesNo(input("Do this now? (y/n) "))
        return wantToAttempt

    def requestReasonForDeferral(self, task):
        reason = None
        while not reason:
            reason = input("Why not? ").strip()
        return reason


def parseYesNo(response):
    """Take a response from a user and interpret it as either 'yes' or 'no'.

    "Yes" means 'True', "no" means 'False'.
    """
    response = response.strip()
    if not response:
        return None
    first = response[0].lower()
    if first == "y":
        return True
    if first == "n":  # pragma: no cover
        return False
    return None  # pragma: no cover
