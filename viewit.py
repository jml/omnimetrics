# From https://gist.github.com/glyph/24913ce5c9dac71b7a9c331f2a9d67fc
from ScriptingBridge import SBApplication
from Foundation import NSURL

omniFocus = SBApplication.applicationWithURL_(
    NSURL.URLWithString_("file:///Applications/OmniFocus.app")
)


def tasksInView():
    """Iterate over all of the items in view on one of the open windows.

    XXX: Which window?
    XXX: What are 'items'? Can be tasks, but can also be other things.
    XXX: What does it mean to have multiple documents?
    """
    content = omniFocus.documents()[0].documentWindows()[0].content()
    for element in content.leaves():
        # XXX: Still unsure of the distinction between `.value()` and `.get()`
        yield element.value()


def iterParents(task):
    """Get all the parents of a task, including the task itself."""
    eachTask = task
    while eachTask is not None:
        yield eachTask
        # Note: until we call `get()`, we have some sort of thunk. We cannot
        # decide whether it's null or not until we evaluate.
        eachTask = eachTask.parentTask().get()


def qualifiedName(task):
    """Return the full name of a task, including any projects that it's in."""
    return " / ".join(reversed([t.name() for t in iterParents(task)]))


def main():
    total = 0
    for task in tasksInView():
        estimated = task.estimatedMinutes().get()
        if estimated is not None:
            total += estimated
            print(qualifiedName(task), estimated)
    print("Total Estimated Minutes:", total)


if __name__ == '__main__':
    main()
