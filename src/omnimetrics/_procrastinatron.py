"""Offer up OmniFocus tasks one at a time, recording excuses.

Command-line tool that shows exactly one OmniFocus task to do.
"""

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


class Procrastinatron:
    def __init__(self, tasks):
        # XXX: this is wrong. Rather than a fixed iterator of tasks, we want
        # to refetch the task list from OmniFocus, ignoring the ones that have
        # been discarded, as our actions may reveal more tasks. However, at
        # this stage, we just want to test out the workflow.
        self._tasks = iter(tasks)
        self._currentTask = None
        self._deferred = set()

    def next(self):
        if not self._currentTask:
            self._currentTask = next(self._tasks)
        return self._currentTask

    def defer(self, reason):
        self._deferred.add(self._currentTask.id())
        self._currentTask = None

    def completed(self):
        self._currentTask.complete()
        self._currentTask = None

    def interrupted(self):
        self._currentTask = None


def attempt(task):  # pragma: no cover
    """Offer the user a single task to perform."""
    ui = UI()
    wantToAttempt = ui.offerTask(task)
    if not wantToAttempt:
        # TODO: Do something with `reason`.
        reason = ui.requestReasonForDeferral(task)
        # `False` is code for not done. Really want an enum type
        # instead.
        return False
    # TODO: timer & completion logic
    return True


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
