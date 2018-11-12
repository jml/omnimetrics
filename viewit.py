# From https://gist.github.com/glyph/24913ce5c9dac71b7a9c331f2a9d67fc
from ScriptingBridge import SBApplication
from Foundation import NSURL

omniFocus = SBApplication.applicationWithURL_(
    NSURL.URLWithString_("file:///Applications/OmniFocus.app")
)
taskClass = omniFocus.classForScriptingClass_('task')


def itemsInView():
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


def qualifiedName(item):
    """Return the full name of an item, including any projects that it's in.

    If the item does not have a name, return ``None``.

    XXX: Doesn't include folders.
    """
    names = []
    # Note: assumes that the presence of a single null name in the parent tree
    # means that the item is not properly named.
    for i in iterParents(item):
        name = i.name()
        if name is None:
            return None
        names.append(name)
    return " / ".join(reversed(names))


def isTask(item):
    """Is the given item an OmniFocus task?"""
    return item.isKindOfClass_(taskClass)


def reportEstimates(items):
    """Given a list of items, show how much time we expect to spend doing them.

    Assumes items have names. Report has a list of all items with estimates,
    along with a total, and all items without estimates.
    """
    total = 0
    unestimatedItems = []
    for item in items:
        name = qualifiedName(item)
        estimated = item.estimatedMinutes().get()
        if estimated is None:
            unestimatedItems.append(name)
        else:
            total += estimated
            print(name, formatMinutes(estimated))
    print('-' * 40)
    print('Total estimated:', formatMinutes(total))
    print()
    for name in unestimatedItems:
        print(name)
    print('-' * 40)
    print('Items without estimates:', len(unestimatedItems))


def formatMinutes(m):
    """Format a number of minutes for human reading.

    More or less follows Go-style convention of XhYm.
    """
    hours, minutes = divmod(m, 60)
    if hours:
        return '%sh%sm' % (hours, minutes)
    return '%sm' % (m,)


def main():
    activeTasks = (i for i in itemsInView() if isTask(i) and not i.blocked())
    reportEstimates(activeTasks)


if __name__ == '__main__':
    main()
